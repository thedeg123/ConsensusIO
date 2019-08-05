from django.utils import timezone
from NewsClassifier import ClassifierModels
from datetime import timedelta
from newsapi import NewsApiClient
import numpy as np
from web.models import Company, Article
from django.db import IntegrityError
from django.db.models.query import QuerySet

class NewsApiWrapper:
    def __init__(self):
        self.today = timezone.now().date()
    def update_company(self, company: Company, look_back:int=2, min_articles:int=2) -> bool:
        '''
        fills the database with articles for said company in the timerange of look_back days ago until today
            returns:
                - if it was able to populate the database with at least min_articles : bool
        '''
        if company.last_checked == self.today:
            return True

        self.start_date = self.today - timedelta(days=look_back)

        _ , article_set = self.__get_news_set__(company, min_articles = min_articles)
        company.last_checked = self.today
        company.p_neg,company.p_ind, company.p_pos = self.__get_avg_news_set__(article_set)
        company.save()
        return True

    def __get_avg_news_set__(self, article_set: QuerySet) -> np.ndarray:
        '''
        finds the proportion of set that is each val 
            returns:
                - an array thats [proportion negative, proportion indifferent, proportion positive] : np.array
        '''
        article_sentiment = np.zeros(3)
        for article in article_set:
            article_sentiment[article.sentiment]+=1
        article_sum = sum(article_sentiment)
        if article_sum==0:
            return article_sentiment
        return ((article_sentiment/article_sum)*100).astype(int)

    def __get_news_set__(self, company: Company, min_articles:int) -> (bool, QuerySet):
        '''
        fetches an article set for the company trying different word queries until it gets at lest min_articles
            returns:
                - if it got reuqested number of articles:bool
                - the set of articles: queryset
        '''
        article_set = []
        for query_val in [company.ticker, company.common_name, company.name]:
            if len(article_set) > min_articles:
                return True, article_set
            if not query_val:
                continue
            article_set = self.__query_database__(company, query_value=query_val, set_size=min_articles)
        print(article_set)
        return False, article_set
    def __query_database__(self, company: Company, query_value:str, set_size:int) -> QuerySet:
        '''
        populates the dbs with news from start_date till end_date
            returns 
                -- the query set of the newly added articles that are financial
        '''
        db_key = ''
        query_set = NewsApiClient(api_key=db_key).get_everything(
                                 q=query_value,
                                 from_param=self.start_date.strftime('%Y-%m-%d'),
                                 language='en',
                                 sort_by='relevancy',
                                 page_size=set_size,
                                 page=1
                                 )['articles']
        #the models expect an array but the api returns a dict, hence we must convert it
        query_list = np.array([[ article['source']['name'],article['title'], article['description'],article['content']] for article in query_set])
        fin_outcomes = self.__is_fin__(query_list)
        if len(fin_outcomes) ==0:
            #if none of what we got is financial
            company.article_set.filter(date__range = [self.start_date, self.today], isFin=True)
        sentiment_outcomes = np.zeros(len(query_list))
        sentiment_outcomes[fin_outcomes] = self.__get_sentiment__(query_list[fin_outcomes]) 
        for sentiment, is_fin, article in zip(sentiment_outcomes, fin_outcomes, query_set):
            try:
                Article(company_id = company, title = article['title'], source=article['source']['name'], date=article['publishedAt'].split('T',1)[0], 
                        subtitle=article['description'], content=article['content'], url=article['url'], isFin = is_fin,
                        sentiment = int(sentiment)).save()
            except IntegrityError:
                continue
        return company.article_set.filter(date__range = [self.start_date, self.today], isFin=True)

    def __is_fin__(self, article_set: np.ndarray) -> np.ndarray:
        '''
        for a list of articles, runs them through a model and decides if they are or are not finance related
        '''
        if len(article_set) ==0:
            return []
        return np.array(ClassifierModels.FinFilter().fit_predict(article_set))

    def __get_sentiment__(self, article_set: np.ndarray) -> np.ndarray:
        '''
        for a list of articles, runs them through a model and finds the sentiment
        '''
        if len(article_set) ==0:
            return []
        return  ClassifierModels.Classifier().fit_predict(article_set)
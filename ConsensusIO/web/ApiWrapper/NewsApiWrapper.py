from django.utils import timezone
from NewsClassifier import ClassifierModels
from datetime import timedelta
from newsapi import NewsApiClient
import numpy as np
from web.models import Company, Article
from django.db import IntegrityError

class NewsApiWrapper:
    def __init__(self):
        self.today = timezone.now().today()
        self.start_date = (self.today - timedelta(days=2)).strftime('%Y-%m-%d')
        self.time_delta = None
    def update_company(self, company: Company):
        '''
        either polling the database for news or if none is found, getting new news going back by week if none was found for that week.
        If no news was published in past month, returning none.
        '''
        if company.last_checked == self.today.date():
            return timedelta(days=2)
        article_set, time_delta = self.__get_avg_news_set__(company)
        if len(article_set)==0:
            return time_delta
        company.p_neg,company.p_ind, company.p_pos = article_set
        company.last_checked = self.today
        company.save()
        return time_delta

    def __get_avg_news_set__(self, company: Company):
        for time_change in [timedelta(days=2), timedelta(days=7), timedelta(days=14), timedelta(days=21), timedelta(days=27)]:
            self.time_delta = time_change
            self.start_date = (self.today - time_change).strftime('%Y-%m-%d')
            article_set = self.__get_avg_news_set_for_date__(company)
            if len(article_set)>0:
                return (article_set, self.time_delta)
        company.last_checked = self.today
        company.save()
        return ([], self.time_delta)
        
    def __get_avg_news_set_for_date__(self, company: Company):
        article_sent = np.zeros(3)
        news_set = self.__fetch_news_set__(company)
        if len(news_set)==0:
            return []
        for article in news_set:
            article_sent[article.sentiment]+=1
        return (article_sent/sum(article_sent)*100).astype(int)
    def __fetch_news_set__(self, company: Company):
        '''
        Checks the database to see if articles from today exist, if not dbs is populated
        '''
        article_set = Article.objects.filter(date = self.today, isFin=True, company_id = company.ticker)
        #try to find articles using the ticker
        if len(article_set) == 0:
            self.__populate_news__(company)
            article_set = Article.objects.filter(date__range = [self.start_date, self.today], isFin=True, company_id = company.ticker)
        #if that  didnt work, find articles using the company name
        if len(article_set) == 0:
            self.__populate_news__(company, query_tkr = False)
        return Article.objects.filter(date__range = [self.start_date, self.today], isFin=True, company_id = company.ticker)
    def __populate_news__(self, company: Company, query_tkr=True):
        '''
        populates the dbs with news
        '''
        db_key = '8e500c992adf43d680f652f336311b61'
        q_name = company.ticker if query_tkr else (company.common_name if company.common_name else company.name)
        query_set = NewsApiClient(api_key=db_key).get_everything(q= q_name,
                                 from_param=self.start_date,
                                 language='en',sort_by='relevancy', page_size=20, page=1)['articles']
        if len(query_set) < 3:
            return []
        #the models expect an array but the api returns a dict, hence we must convert it
        query_list = np.array([[ article['source']['name'],article['title'], article['description'],article['content']] for article in query_set])
        fin_outcomes = self.__is_fin__(query_list)
        if not fin_outcomes.any():
            #if none of what we got is financial
            return []
        sentiment_outcomes = np.zeros(len(query_list))
        sentiment_outcomes[fin_outcomes] = self.__get_sentiment__(query_list[fin_outcomes]) 
        for sentiment, is_fin, article in zip(sentiment_outcomes, fin_outcomes, query_set):
            try:
                Article(company_id = company, title = article['title'], source=article['source']['name'], date=article['publishedAt'].split('T',1)[0], 
                        subtitle=article['description'], content=article['content'], url=article['url'], isFin = is_fin,
                        sentiment = int(sentiment)).save()
            except IntegrityError:
                continue
    def __is_fin__(self, article_set):
        '''
        for a list of articles, runs them through a model and decides if they are or are not finance related
        '''
        return np.array(ClassifierModels.FinFilter().fit_predict(article_set))

    def __get_sentiment__(self, article_set):
        '''
        for a list of articles, runs them through a model and finds the sentiment
        '''
        return ClassifierModels.Classifier().fit_predict(article_set)
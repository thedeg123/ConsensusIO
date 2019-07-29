from django.utils import timezone
from NewsClassifier import ClassifierModels
from datetime import timedelta
from newsapi import NewsApiClient
import numpy as np
from web.models import Company, Article
from django.db import IntegrityError

class NewsApiWrapper:
    def __init__(self):
        self.date = timezone.now().date()
        self.yesterday = (self.date - timedelta(days=1)).strftime('%Y-%m-%d')
    
    def update_company(self, company: Company):
        company.p_neg,company.p_ind, company.p_pos = self.__get_avg_news_set__(company)
        company.save()
        return company
    def __get_avg_news_set__(self, company: Company):
        article_sent = np.zeros(3)
        news_set = self.__fetch_news_set__(company)
        if not news_set:
            return None
        for article in news_set:
            article_sent[int(article.sentiment)]+=1
        
        return article_sent/sum(article_sent)
    def __fetch_news_set__(self, company: Company):
        '''
        Checks the database to see if articles from today exist, if not dbs is populated
        '''
        article_set = Article.objects.filter(date__in = [self.date, self.yesterday], isFin=True, company_id = company.ticker)
        #try to find articles using the ticker
        if not article_set:
            self.__populate_news__(company)
            article_set = Article.objects.filter(date__in = [self.date, self.yesterday], isFin=True, company_id = company.ticker)
        #if that  didnt work, find articles using the company name
        if not article_set:
            self.__populate_news__(company, query_tkr = False)
            article_set = Article.objects.filter(date__in = [self.date, self.yesterday], isFin=True, company_id = company.ticker)
        return article_set
    def __populate_news__(self, company: Company, query_tkr=True):
        '''
        populates the dbs with news
        '''
        db_key = ''
        q_name = company.ticker if query_tkr else (company.common_name if company.common_name else company.name)
        query_set = NewsApiClient(api_key=db_key).get_everything(q= q_name,
                                 from_param=self.yesterday,
                                 language='en',sort_by='relevancy', page_size= 10, page=1)['articles']
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
                Article(company_id = company, title = article['title'], date=article['publishedAt'].split('T',1)[0], 
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
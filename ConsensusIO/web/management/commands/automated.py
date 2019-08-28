from django.core.management.base import BaseCommand, CommandError
from web.models import Article, Company
from NewsClassifier.ClassifierModels import *
from django.utils import timezone
from datetime import timedelta

import logging

class Command(BaseCommand):
    help='updates models as needed  and deletes news that is more than 30 days old'
    def handle(self, *args, **options):
        logging.basicConfig(filename='testing.log',level=logging.DEBUG)
        self.remove_old_news()
        self.update_models()

    def update_models(self):
        def prepare_set(X):
            '''
            converts the article set objects to 2 arrays (X,y) in the format neccecary for the models
            returns X,y
            '''
            return [[article.source, article.title, article.subtitle, article.content] for article in X],\
                    [article.sentiment for article in X]

        update_set = Article.objects.exclude(review__isnull=True)
        if len(update_set)!=0:
            update_not_fin_set, _ = prepare_set(update_set.filter(review=0))
            update_sentiment_set, update_sentiment_set_y = prepare_set(update_set.exclude(review=0))
            fin_set = update_not_fin_set+update_sentiment_set
            
            FinFilter().update(X=fin_set,
                            y=[0]*len(update_not_fin_set)+[1]*len(update_sentiment_set)
                            )
            logging.warning("updated fin_filter model, adding "+ \
                            str(len(update_not_fin_set+update_sentiment_set))+" datapoints at: "+str(timezone.now()))
            Classifier().update(X= update_sentiment_set,
                                y= update_sentiment_set_y
                            )
            logging.warning("updated classifier model, adding "+\
                            str(len(update_sentiment_set))+" datapoints at: "+str(timezone.now()))
            update_set.update(review=None)
        else:
            logging.warning("No updates to models at "+str(timezone.now()))
        
    def load_homescreen(self):
        return
    def remove_old_news(self):
        '''
        deletes all news from the database that is more than one month old
        '''
        one_month_ago = timezone.now().date() - timedelta(days=31)
        delete_set = Article.objects.filter(date__lt = one_month_ago)
        if not delete_set:
            logging.warning("no articles to delete at: "+str(timezone.now()))
            return
        logging.warning("deleted "+str(len(delete_set))+" articles at: "+str(timezone.now()))
        delete_set.delete()
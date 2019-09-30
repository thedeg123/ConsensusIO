from django.shortcuts import render
from .models import Company, Article, Price
from django.views.generic import ListView
from django.utils import timezone
from datetime import timedelta
from web.ApiWrapper.NewsApiWrapper import NewsApiWrapper
from web.ApiWrapper.PriceApiWrapper import get_price
from requests.exceptions import ConnectionError
from .forms import UpdateForm


#def migratedbs():
#     BASE = os.path.dirname(os.path.abspath(__file__))
#     with open(os.path.join(BASE, "static", "web", "lookup.pickle"), 'rb') as f:
#         lookupTable = load(f)
#     for (k,v) in lookupTable.items():
#         c = Company.objects.get(pk=v)
#         c.logo_img = ''.join(('https://storage.googleapis.com/iex/api/logos/',v,'.png'))
#         c.save()

class IndexView(ListView):
    template_name = 'web/index.html'
    context_object_name = 'home_stocks'
    today = timezone.now().date()

    def get_queryset(self):
        news_wrapper = NewsApiWrapper()
        company_set = Company.objects.filter(pk__in=['BABA', 'AAPL', 'MSFT', 'AMZN', 'FB', 'MS', 'GOOGL', 'JPM', 'BAC'])
        common_search_set = Company.objects.filter(pk__in=['SPY', 'BUSINESS', 'FED'])
        crypto_set = Company.objects.filter(pk__in=['BTCUSDT', 'ETHUSDT', 'XRPUSDT'])
        for company in company_set:
            news_wrapper.update_company(company, look_back=2, min_articles=10)
        for common in common_search_set:
            news_wrapper.update_company(common, look_back=2, min_articles=10)
        for crypto in crypto_set:
            news_wrapper.update_company(crypto, look_back=2, min_articles=10)
        company_set = company_set if type(company_set) is list else [company_set]
        return {'company_set': company_set,
                'common_set': common_search_set,
                'crypto_set': crypto_set}

class SearchView(ListView):
    template_name = 'web/search.html'
    model = Article
    context_object_name = 'user_search'
    today = timezone.now().date()
    def post(self, request, *args, **kwargs):
        '''
        Error form processing, marks in dbs for the corrisponding article to update models as needed
        '''
        company = self.fetch_company(self.request.GET.get('search_bar'))
        form = UpdateForm(request.POST)
        if form.is_valid():
            article = company.article_set.get(pk=form.cleaned_data['form_id']) #fetch the assoceated article
            article.review = form.cleaned_data['choice']                       #tag it as needing to be trained on ml
            if form.cleaned_data['choice'] == '0':                             #update the article based off user selection
                article.isFin = False  
                article.sentiment = 0                                       
            else:
                article.sentiment = int(form.cleaned_data['choice'])-1
                article.isFin = True 
            article.save()
        return render(request, 'web/search.html', {'user_search': self.get_queryset()})
    def get_queryset(self): 
        '''
        for a given company, fetches a news set if possible, otherwise returns an error view
        '''
        query = self.request.GET.get('search_bar')
        company = news_set = look_back_length = None
        company = self.fetch_company(query)
        if not company:
            return {'error_view':True,
                    'error_msg' : ' '.join(["No company found with name:", query]),
                    'error_submsg': 'To find this company exactly, try searching its',
                    'error_submsg_link': 'https://www.marketwatch.com/tools/quotes/lookup.asp',
                   }
        sentiment_set = self.fetch_sentiment_set(company)
        if not sentiment_set[0]:
            return sentiment_set[1]
        form_articles = self.fetch_form_article_set(sentiment_set[1])
        try:
            price = get_price(company, self.today)
        except ConnectionError:
            return {'error_view':True, 'error_msg' : "No internet connection :("} 
        return {'company':company,
                'form_articles': list(zip(['Positive', 'Indifferent', 'Negative', 'Non financial'],form_articles)),
                'price': price,
                'total_size': len(form_articles[0])+\
                              len(form_articles[1])+\
                              len(form_articles[2])\
                }
    def fetch_form_article_set(self, sentiment_set):
        '''
        each element in sentiment_set is joined with its corrisponding form 
            returns: [[(form, article)]] where each list is a sentiment, of an article and its corrisponding form
        '''
        ret = []
        for sentiment in sentiment_set:
            ret_s=[]
            for s in sentiment:
                ret_s.append((UpdateForm(initial={'form_id': s.id}), s))
            ret.append(ret_s)
        return ret
    def fetch_sentiment_set(self, company):
        news_wrapper = NewsApiWrapper()
        for look_back in range(2,31,7):
            if news_wrapper.update_company(company, look_back=look_back, min_articles=10):
                look_back_length = look_back
                break
        news_set = company.article_set.filter(date__range=[self.today - timedelta(days=look_back_length), self.today]).order_by('-date')
        if len(news_set) ==0:
            return (False, {'error_view':True,
                        'error_msg' : ''.join(["Could not find any any news for company \"", company.name, "\" in past 30 days"]),
                        'error_submsg': 'Not the company you were looking for? Try searching its',
                        'error_submsg_link': 'https://www.marketwatch.com/tools/quotes/lookup.asp',
                        })
        return (True, [news_set.filter(isFin=True, sentiment=2),    #positive set
                       news_set.filter(isFin=True, sentiment=1), #indifferent set
                       news_set.filter(isFin=True, sentiment=0),    #negative set
                       news_set.filter(isFin=False)            #non financial set
        ])
    def fetch_company(self, query:str):
        '''
        For a given query, returns that company from the database
        '''
        for query_result in [Company.objects.filter(ticker=query),
                            Company.objects.filter(common_name__icontains = query),
                            Company.objects.filter(name__icontains = query)
                        ]:
            if len(query_result)>0:
                return query_result[0]
def acknowledgments(request):
    return render(request, 'web/acknowledgments.html', {})

def about(request):
    return render(request, 'web/about.html', {})

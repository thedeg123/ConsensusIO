from django.shortcuts import render
from .models import Company, Article, Price
from django.views.generic import ListView
from django.utils import timezone
from datetime import timedelta
from web.ApiWrapper.NewsApiWrapper import NewsApiWrapper
from web.ApiWrapper.PriceApiWrapper import get_price
from requests.exceptions import ConnectionError

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
        company_set = Company.objects.filter(pk__in=['BABA', 'AAPL', 'MSFT', 'AMZN', 'FB', 'BRK.B', 'GOOGL', 'JPM', 'JNJ', 'BAC', 'PG', 'DIS'])
        for company in company_set:
            news_wrapper.update_company(company, look_back=2, min_articles=10)
        return company_set if type(company_set) is list else [company_set]

class SearchView(ListView):
    template_name = 'web/search.html'
    model = Article
    context_object_name = 'user_search'
    today = timezone.now().date()

    def get_queryset(self):
        query = self.request.GET.get('search_bar')
        company = news_set = look_back_length = None
        news_wrapper = NewsApiWrapper()
        for query_result in [Company.objects.filter(ticker=query),
                             Company.objects.filter(common_name__icontains = query),
                             Company.objects.filter(name__icontains = query)
                            ]:
            if len(query_result)>0:
                company = query_result[0]
                break
        if not company:
            return {'error_view':True,
                    'error_msg' : ' '.join(["No company found with name:", query]),
                    'error_submsg': 'To find this company exactly, try searching its',
                    'error_submsg_link': 'https://www.marketwatch.com/tools/quotes/lookup.asp',
                   }
        #querying the database for 
        for look_back in range(2,31,7):
            if news_wrapper.update_company(company, look_back=look_back, min_articles=10):
                look_back_length = look_back
                break
        news_set = company.article_set.filter(date__range=[self.today - timedelta(days=look_back_length), self.today]).order_by('-date')
        if len(news_set) ==0:
            return {'error_view':True,
                        'error_msg' : ''.join(["Could not find any any news for company \"", company.name, "\" in past 30 days"]),
                        'error_submsg': 'Not the company you were looking for? Try searching its',
                        'error_submsg_link': 'https://www.marketwatch.com/tools/quotes/lookup.asp',
                        }
        try:
            price = get_price(company, self.today)
        except ConnectionError:
            return {'error_view':True, 'error_msg' : "No internet connection :("}
        return {'company':company,
                'pos_set': news_set.filter(isFin=True, sentiment=2),
                'mixed_set': news_set.filter(isFin=True, sentiment=1),
                'neg_set': news_set.filter(isFin=True, sentiment=0),
                'non_fin_set': news_set.filter(isFin=False),
                'price': price,
                'total_size': len(news_set.filter(isFin=True))
                }
def acknowledgments(request):
    return render(request, 'web/acknowledgments.html', {})

def about(request):
    return render(request, 'web/about.html', {})

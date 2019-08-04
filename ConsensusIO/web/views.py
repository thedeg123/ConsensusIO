from django.shortcuts import render, get_object_or_404 #get list 404 is the same except raises error if len(list)==0
from .models import Company, Article, Price
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
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
            news_wrapper.update_company(company)
        return company_set if type(company_set) is list else [company_set]

class SearchView(ListView):
    template_name = 'web/search.html'
    model = Article
    context_object_name = 'user_search'
    today = timezone.now().date()

    def get_queryset(self):
        query = self.request.GET.get('search_bar')
        company = None
        for query_result in [Company.objects.filter(ticker=query),
                             Company.objects.filter(common_name__icontains = query),
                             Company.objects.filter(name__icontains = query)
                            ]:
            try:
                company = query_result[0]
                break
            except IndexError:
                continue
        if not company:
            return {'error_view':True,
                    'error_msg' : ' '.join(["No company found with name:", query]),
                    'error_submsg': 'To find this company exactly, try searching its',
                    'error_submsg_link': 'https://www.marketwatch.com/tools/quotes/lookup.asp',
                   }
        print(self.today)
        time_delta = NewsApiWrapper().update_company(company)
        news_set = company.article_set.filter(date__range=[self.today - time_delta, self.today], isFin=True).order_by('-date')
        if not news_set:
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
                'pos_set': news_set.filter(sentiment=2),
                'mixed_set': news_set.filter(sentiment=1),
                'neg_set': news_set.filter(sentiment=0),
                'non_fin_set': company.article_set.filter(date__range=[self.today - time_delta, self.today], isFin=False).order_by('-date'),
                'price': price,
                'total_size': len(news_set)
                }
def acknowledgments(request):
    return render(request, 'web/acknowledgments.html', {})

def about(request):
    return render(request, 'web/about.html', {})

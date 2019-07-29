from django.shortcuts import render, get_object_or_404 #get list 404 is the same except raises error if len(list)==0
from .models import Company, Article, Price
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from web.ApiWrapper.NewsApiWrapper import NewsApiWrapper

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

    def get_queryset(self):
        news_wrapper = NewsApiWrapper()
        company_set = Company.objects.filter(pk__in=['TWTR', 'AAPL'])
        for company in company_set:
            if not company:
                news_wrapper.update_company(company)
        return company_set if type(company_set) is list else [company_set]


class SearchView(ListView):
    template_name = 'web/search.html'
    model = Article
    context_object_name = 'user_search'
    date = timezone.now().date()
    yesterday = (date - timedelta(days=1)).strftime('%Y-%m-%d')
    def get_queryset(self):
        query = self.request.GET.get('search_bar')
        try:
            company = Company.objects.filter( Q(name__icontains = query)
                                            | Q(ticker=query)
                                            | Q(common_name__icontains = query))[0]
        except IndexError:
            return {'error_view':True, 'error_msg' : ' '.join(["No company found with name:", query])}
        NewsApiWrapper().update_company(company)
        news_set = company.article_set.filter(date__in=[self.date, self.yesterday], isFin=True)
        return {'company':company,
                'pos_set': news_set.filter(sentiment=2),
                'mixed_set': news_set.filter(sentiment=1),
                'neg_set': news_set.filter(sentiment=0),
                'non_fin_set': company.article_set.filter(isFin=False),
                'price': '$1'
                }
        

def acknowledgments(request):
    return render(request, 'web/acknowledgments.html', {})

def about(request):
    return render(request, 'web/about.html', {})

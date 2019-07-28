from django.shortcuts import render, get_object_or_404 #get list 404 is the same except raises error if len(list)==0
from .models import Company
from django.views import generic
from django.utils import timezone
from datetime import timedelta
from web.NewsWrapper.NewsApiWrapper import NewsApiWrapper

#def migratedbs():
#     BASE = os.path.dirname(os.path.abspath(__file__))
#     with open(os.path.join(BASE, "static", "web", "lookup.pickle"), 'rb') as f:
#         lookupTable = load(f)
#     for (k,v) in lookupTable.items():
#         c = Company.objects.get(pk=v)
#         c.logo_img = ''.join(('https://storage.googleapis.com/iex/api/logos/',v,'.png'))
#         c.save()

class IndexView(generic.ListView):
    template_name = 'web/index.html'
    context_object_name = 'home_stocks'
    date = timezone.now().date()
    yesterday = (date - timedelta(days=1)).strftime('%Y-%m-%d')

    def get_queryset(self):
        news_wrapper = NewsApiWrapper()
        company_set = Company.objects.filter(pk__in=['TWTR', 'AAPL'])
        for company in company_set:
            if not company:
                continue
            company.p_neg,company.p_ind, company.p_pos = news_wrapper.get_avg_news_set(company)
            company.save()
        return company_set if type(company_set) is list else [company_set]


def search(request):
    return render(request, 'web/search.html', {'search_val': request.POST['search']})

def acknowledgments(request):
    return render(request, 'web/acknowledgments.html', {})

def about(request):
    return render(request, 'web/about.html', {})

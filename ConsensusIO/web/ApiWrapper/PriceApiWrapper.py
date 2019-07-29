from iexfinance.stocks import Stock as iexStock
from iexfinance.utils.exceptions import IEXQueryError
from web.models import Company, Price
#Todo fix TypeError at /search/ 'NoneType' object is not iterable bug when no news is found (query back further like a week)
def get_price(Company, date):
    try:
        return Price.objects.filter(company_id = Company, date = date)[0]
    except IEXQueryError:
        return None
    except IndexError:
        key = ''
        query = iexStock(Company.ticker, token=key).get_book()['quote']
        Price(company_id = Company, date=date, price=query['latestPrice'], change_pct = query['changePercent']).save()
        return Price.objects.filter(company_id = Company, date = date)[0]
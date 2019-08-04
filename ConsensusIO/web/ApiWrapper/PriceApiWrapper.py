from iexfinance.stocks import Stock as iexStock
from iexfinance.utils.exceptions import IEXQueryError
from web.models import Company, Price
def get_price(company, date):
    try:
        return Price.objects.filter(company_id = company, date=date)[0]
    except IEXQueryError:
        return None
    except IndexError:
        print(date)
        key = ''
        query = iexStock(company.ticker, token=key).get_book()['quote']
        print(date)
        Price(company_id = company, date=date, price=query['latestPrice'], change_pct = query['changePercent']).save()
        return Price.objects.filter(company_id = company, date = date)[0]
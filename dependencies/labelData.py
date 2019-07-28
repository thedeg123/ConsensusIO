from newsapi import NewsApiClient
import pickle
#pylint: disable=unused-variable, unsubscriptable-object
class data_logger:
    PAGESIZE = 100
    def __init__(self, state_list: dict):
        self.keyword_num = state_list['cur_keyword']+1 #to know what query we left off on last time in the program and to go to next batch of data
        self.X = state_list['X']  #our raw dataset (article source name, title, description, content)
        self.y = state_list['y']  #our raw responses (0=bear/bad, 1=indifferent, 2=bull/good)
    def __dataRefreshDummy__(self, api: NewsApiClient, keyword: str) -> {}:
        '''
        Use in order not to make unneccicary calls to API, for testing use only.
        '''
        return {'status': 'ok',
                'totalResults': 463,
                'articles': [{'source': {'id': None, 'name': 'Marketwatch.com'},
                              'author': 'Jon Swartz',
                              'title': 'Facebook shares rise on Deutsche Bank price-target hike',
                              'description': 'Shares of Facebook Inc. are up 1% in mid-morning trading Thursday following two notes from financial analysts on additional advertising revenue streams for the social-media giant.',
                              'url': 'https://www.marketwatch.com/story/facebook-shares-rise-on-deutsche-bank-price-target-hike-2019-06-27',
                              'urlToImage': 'http://s.marketwatch.com/public/resources/MWimages/MW-HM328_Instag_ZG_20190627102926.jpg',
                              'publishedAt': '2019-06-27T15:50:39Z',
                              'content': 'Shares of Facebook Inc. are up 1% in mid-morning trading Thursday following two notes from financial analysts on additional advertising revenue streams for the social-media giant.\r\nDeutsche Bank analyst Lloyd Walmsley is bullish that the companys video platfo… [+1044 chars]'},
                             {'source': {'id': None, 'name': 'Marketwatch.com'},
                              'author': 'Simon Maierhofer',
                              'title': 'July’s first week will foreshadow the stock market’s performance in the second half',
                              'description': 'It’s right about 60% of the time, according to past years.',
                              'url': 'https://www.marketwatch.com/story/julys-first-week-will-foreshadow-the-stock-markets-performance-in-the-second-half-2019-06-28',
                              'urlToImage': 'http://s.marketwatch.com/public/resources/MWimages/MW-HL017_crysta_ZG_20190607110021.jpg',
                              'publishedAt': '2019-06-28T11:43:44Z',
                              'content': 'The first half of the year is in the rearview mirror. Although forecasting the stock market for the next six months is always tricky, I can say this for sure: There is an 84% chance the second half will start with a bang.\r\nWhy is that? \r\nHistorically, the fir… [+2312 chars]'}]}
    
    def establish_connection(self):
        KEY = '8e500c992adf43d680f652f336311b61'
        return NewsApiClient(api_key=KEY)

    def dataRefresh(self, api: NewsApiClient, keyword: str, random_news:bool = False) -> {}:
        from datetime import date, timedelta
        if random_news:
            return api.get_top_headlines(category=keyword,
                                         from_param=(date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                         language='en',
                                         sort_by='relevancy',
                                         page_size=self.PAGESIZE,
                                         page=1)
        return api.get_everything(q=keyword,
                                  from_param=(date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
                                language='en',
                                sort_by='relevancy',
                                page_size= self.PAGESIZE,
                                page=1)

    def printArticle(self, article: {}) -> None:
        if article['source']['name'] != None:
            print(article['source']['name'], '\n')
        if article['title'] != None:
            print(article['title'], '\n')
        if article['description']!= None: 
            print(article['description'], '\n')
        if article['content']!=None:
            print(article['content'][:259], '\n')

    def clean(self, article: {}) -> []:
        src_name = article['source']['name'] if article['source']['name'] else ""
        art_name,desc,cont = "", "",""
        if article['title']:
            art_name = article['title'].lower()
        if article['description']:
            desc = article['description'].lower()
        if article['content']:
            cont = article['content'][:259].lower()
        return [src_name, art_name, desc, cont]

    def handleAction(self, action: str, article: {}) -> bool:
        '''
        appends data and tag to x and y df respectively. Returns True if anything was added
        '''
        if action == 'e':
            return False
        elif action in ('0','1', '2'):
            self.X.append(self.clean(article))
            self.y.append(int(action))
            return True
        else:
            self.__quit__()
            return False
        
    def __quit__(self):
        with open('labled_data/meta', 'wb') as fp:
            pickle.dump({'cur_keyword': self.keyword_num, 'X': self.X, 'y': self.y}, fp)
        quit()
        return None

    def resume_log(self, random_news:bool = False) -> None:
        '''
        continues logging website from last state used 
        '''
        from dependencies.readb import _Getch

        api = self.establish_connection()
        if random_news:
            api_gather_keywords = ['entertainment', 'general', 'health', 'science', 'sports']
        else:
            api_gather_keywords = ['bullish', 'bearish', 'interest rates',
                                   'tech stocks', 'microsoft', 'industry', 'economy', 'investors']
        if self.keyword_num >= len(api_gather_keywords):
            self.keyword_num = -1
            print("No more keywords")
            self.__quit__()

        for i in range(self.keyword_num, len(api_gather_keywords)):

            keyword = api_gather_keywords[i]
            db_pull = self.dataRefresh(api, keyword)

            #for each article  assoceated with that keyword
            for i,article in enumerate(db_pull['articles']):
                print("\n", '-'*150, "0: negative, 1: indifferent, 2: positive, e: exclude, other_key: quit")
                print("Article number:", i+1 ,"of", self.PAGESIZE,"in batch", keyword)
                self.printArticle(article)
                inp = _Getch()()
                self.handleAction(inp, article)
            self.keyword_num+=1
        self.__quit__()

if __name__ == "__main__":
    try:
        with open('labled_data/meta', 'rb') as fp:
            state_list = pickle.load(fp)
    except FileNotFoundError:
        print("Could not find file meta file in dependencies. Setting defualt values.")
        state_list = {'cur_keyword': -1, 'X':[], 'y':[]} #-1 so we will toggle to the next keyword (0) when calling program
    #change this to load in from a file
    data_logger(state_list).resume_log()


from sklearn.pipeline import BaseEstimator, TransformerMixin, Pipeline
import numpy as np
import urlextract
from sklearn.feature_extraction.text import TfidfTransformer
import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer
from scipy.sparse import csr_matrix
import pickle
class Cleaner(BaseEstimator, TransformerMixin):
    def __init__(self, include_subj=True, replace_html=True, remove_punctuation=True, replace_urls=True, replace_numbers=True):
        self.include_subj = include_subj; self.replace_html = replace_html
        self.remove_punctuation = remove_punctuation; self.replace_urls = replace_urls;
        self.replace_numbers = replace_numbers  
    def fit(self, X, y=None):
        return self
    def __html_to_plain_text__(self, html: str) -> str:
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'html.parser').get_text()
    def transform(self, X, y=None):
        X_transformed = []
        for article in X:
            text = " ".join(article) if self.include_subj else " ".join(article[1:])
            if self.replace_html:
                text = self.__html_to_plain_text__(text)
            if self.replace_urls:
                url_extractor = urlextract.URLExtract() 
                urls = list(set(url_extractor.find_urls(text)))
                urls.sort(key=lambda url: len(url), reverse=True)
                for url in urls:
                    text = text.replace(url, " URL ")
            if self.replace_numbers:
                text = re.sub(r'\d+(?:\.\d*(?:[eE]\d+))?', ' NUMBER ', text)
            if self.remove_punctuation:
                text = text.replace("\'", "").replace("’", "") #Because we dont want these to be replaced by spaces
                text = re.sub(r'\W+', ' ', text, flags=re.M)
            X_transformed.append(text)
        return X_transformed

class CountVectorizerWithStemming(CountVectorizer):
    def build_analyzer(self):
        lemm = WordNetLemmatizer()
        analyzer = super(CountVectorizerWithStemming, self).build_analyzer()
        return lambda doc: (lemm.lemmatize(w) for w in analyzer(doc))

class SetBias(BaseEstimator, TransformerMixin):
    def __init__(self, bias_strength:float, bias_list_path:str = '../dependencies/word_list.sav',):
        with open(bias_list_path, 'rb') as f:
            self.bias_list = pickle.load(f)
        self.bias_strength = bias_strength
    def fit(self, X, y=None):
        return self
    def transform(self, X, y=None):
        if type(X) is csr_matrix:
            X = X.toarray()
        return csr_matrix(np.add(X, self.bias_list*self.bias_strength, where=X!=0))


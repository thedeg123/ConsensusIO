import warnings
import os
import numpy as np
warnings.simplefilter(action='ignore', category=FutureWarning)

from pickle import Unpickler
class CustomUnpickler(Unpickler):
    def find_class(self, module, name):
        if name == 'Cleaner':
            from .modelTransformers import Cleaner
            return Cleaner
        if name == 'CountVectorizerWithStemming':
            from .modelTransformers import CountVectorizerWithStemming
            return CountVectorizerWithStemming
        if name == 'SetBias':
            from .modelTransformers import SetBias
            return SetBias
        if name == 'RemoveNan':
            from .modelTransformers import RemoveNan
            return RemoveNan
        return super().find_class(module, name)

class AbstractModel:
        '''
        Classifies financial news as either positive, negative, or indifferent/mixed
        '''
        def __init__(self, model_path=None):
            import sys
            with open(model_path, 'rb') as f:
                raw_file = CustomUnpickler(f).load()
            try:
                self.model, self.transformer = raw_file['model'], raw_file['transformer']
            except KeyError:
                sys.stderr.write(\
                    "Please ensure the validity of binary file, expected model and transformer")
                raise KeyError
        def fit(self, X, y=None):
            return self.transformer.transform(X)
        
        def predict(self, X,y=None):
            return self.model.predict(np.nan_to_num(X.toarray()))

        def fit_predict(self, X, y=None):
            return self.predict(self.fit(X))
        
class FinFilter(AbstractModel):
    def __init__(self, model_path: str = './models/fin_not_fin_v3.model', precision_rate: float = 0.1):
        '''
        Filters text to financial data. returning a array of true/false corrisponding to each element in the original array
        model_path: path to the model which does the heavy lifting (saved as binary file)
        precision_rate: our threshold for news as "financial"
            -- as user keywords for companies will be cross-referenced wiht an API in advance, 
            -- this can be low, 0.1 worked best on test and validation sets
        '''
        self.precision_rate = precision_rate
        BASE = os.path.dirname(os.path.abspath(__file__))
        return super().__init__(os.path.join(BASE, 'models', 'fin_not_fin_v2.model'))
    def predict(self, X, y=None):
        '''
        returns a true/false for each index as to whether or not it is financial 
        '''
        return (self.model.predict_proba(X)[:, 1] > self.precision_rate)

class Classifier(AbstractModel):
    def __init__(self, model_path: str = './models/news_sentiment_v2.model'):
        '''
        predicts if a financial news article is positive, negative, or indiferent/mixed returning a array of true/false 
        corrisponding to each element in the original array
        model_path: path to the model which does the heavy lifting (saved as binary file)
        '''
        BASE = os.path.dirname(os.path.abspath(__file__))
        return super().__init__(os.path.join(BASE, 'models', 'news_sentiment.model'))
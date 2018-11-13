from collections import namedtuple

import pandas as pd

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


Model = namedtuple('Model', ['classifier', 'train_subset', 'train_accuracy', 'test_subset', 'test_accuracy'])


class ModelConstructor:

    def __init__(self, data_set):
        self.data_set = data_set
        self.model = self.select_best_model(self.data_set)

    @staticmethod
    def create_model(data_set, score):
        df = pd.DataFrame(data_set).dropna()
        df['Personal score'] = (df['Personal score'] > score).astype(int)
        initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
        labels = df['Personal score']
        x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
        forest = RandomForestClassifier(criterion='entropy', n_estimators=10, random_state=1, n_jobs=1)
        pipe_forest = Pipeline([('scl', StandardScaler()), ('рса', PCA(n_components=3)), ('clf', forest)])
        pipe_forest.fit(x_train, y_train)
        test_accuracy = pipe_forest.score(x_train, y_train)
        train_accuracy = pipe_forest.score(x_test, y_test)
        model = Model(pipe_forest, (x_train, y_train), train_accuracy, (x_test, y_test), test_accuracy)
        return model

    def select_best_model(self, data_set):
        models = [self.create_model(data_set, score) for score in range(5, 9)]
        model = [model for model in models if model.train_accuracy != 1 or model.test_accuracy != 1]
        best_model = max(model, key=lambda x: x.train_accuracy + x.test_accuracy) if model else None
        return best_model


class Predictor:

    def __init__(self, model):
        self.model = model

    def make_prediction(self, anime_data):
        sample = {'Episodes': [anime_data.episodes],
                  'Score': [anime_data.score],
                  'Genres': [anime_data.genre],
                  'Source': [anime_data.source],
                  'Studios': [anime_data.studio],
                  'Type': [anime_data.type]}
        df = pd.DataFrame(sample)
        categorical_data = pd.get_dummies((df[['Genres', 'Source', 'Studios', 'Type']]))
        initial_data = df[['Episodes', 'Score']].join(categorical_data)
        x_train, y_train = self.model.train_subset
        x_test, y_test = self.model.test_subset
        data = pd.concat([x_train, initial_data], axis=0, sort=True, keys=['train', 'test']).loc['test'].fillna(0)
        #  TODO: Columns in data and x_train might not match. Throws exception cases where rare sample provided.
        model = self.model.classifier
        prediction = model.predict(data)
        train_accuracy, test_accuracy = model.score(x_train, y_train), model.score(x_test, y_test)
        return prediction[0], train_accuracy, test_accuracy

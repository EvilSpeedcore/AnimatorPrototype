import collections

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Посмотреть блиэе на pipeline'ы (стр. 169 Рашка С.)

Model = collections.namedtuple('Model', ['model', 'train_subset', 'train_accuracy', 'test_subset', 'test_accuracy'])


class ModelConstructor:
    def __init__(self, data_set):
        self.date_set = data_set
        self.model = None
        self.train_set = None
        self.test_set = None

    def create_model(self):
        models = []
        for score in range(5, 9):
            print(self.date_set)
            df = pd.DataFrame(self.date_set).dropna()
            df['Personal score'] = (df['Personal score'] > score).astype(int)
            initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
            labels = df['Personal score']
            x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
            forest = RandomForestClassifier(criterion='entropy', n_estimators=10, random_state=1, n_jobs=1)
            pipe_forest = Pipeline([('scl', StandardScaler()), ('рса', PCA(n_components=3)), ('clf', forest)])
            pipe_forest.fit(x_train, y_train)
            train_set = (x_train, y_train)
            test_set = (x_test, y_test)
            print('-'*100)
            print("Правильность на обучающем наборе: {:.3f}".format(pipe_forest.score(x_train, y_train)))
            print('Верность на тестовом наборе: {:.3f}'.format(pipe_forest.score(x_test, y_test)))
            print('-' * 100)
            test_accuracy = pipe_forest.score(x_train, y_train)
            train_accuracy = pipe_forest.score(x_test, y_test)
            model = Model(pipe_forest, train_set, train_accuracy, test_set, test_accuracy)
            models.append(model)
        models = [x for x in models if x.train_accuracy != 1 or x.train_accuracy != 1]
        best_model = max(models, key=lambda x: x[2]+ [-1])
        self.model = best_model.model
        self.test_set = best_model.test_subset
        self.train_set = best_model.train_subset

    def predict(self, anime_data):
        sample = {'Episodes': [anime_data.episodes],
                  'Score': [anime_data.score],
                  'Genres': [anime_data.genre],
                  'Source': [anime_data.source],
                  'Studios': [anime_data.studio],
                  'Type': [anime_data.type]}
        df = pd.DataFrame(sample)
        categorical_data = pd.get_dummies((df[['Genres', 'Source', 'Studios', 'Type']]))
        initial_data = df[['Episodes', 'Score']].join(categorical_data)

        x_train, y_train = self.train_set
        x_test, y_test = self.test_set
        pipe_forest = self.model

        x = pd.concat([x_train, initial_data], axis=0, sort=True, keys=['train', 'test']).loc['test'].fillna(0)
        print(len(x.columns))
        print(len(x_train.columns))
        #  TODO: Количество колонок иногда не совпадает.
        prediction = pipe_forest.predict(x)
        train_accuracy, test_accuracy = pipe_forest.score(x_train, y_train), pipe_forest.score(x_test, y_test)
        return prediction[0], train_accuracy, test_accuracy


    def preprocess(self, filename):
        df = pd.read_csv(filename).dropna()
        df['Personal score'] = (df['Personal score'] > 7).astype(int)
        #  print("Исходные признаки:\n{0}". format(list(df.columns)))
        initial_data = pd.get_dummies((df[['Episodes', 'Genres', 'Score', 'Source', 'Studios', 'Type']]))
        labels = df['Personal score']
        x_train, x_test, y_train, y_test = train_test_split(initial_data, labels, random_state=0, test_size=0.3)
        forest = RandomForestClassifier(criterion='entropy', n_estimators=10, random_state=1, n_jobs=2)
        pipe_forest = Pipeline([('scl', StandardScaler()), ('рса', PCA(n_components=3)), ('clf', forest)])
        pipe_forest.fit(x_train, y_train)

        c = {'Episodes': ['12'],
             'Score': ['6.5'],
             'Genres': ['Comedy'],
             'Source': ['4-koma manga'],
             'Studios': ['LIDENFILMS'],
             'Type': ['TV']}
        h = pd.DataFrame(c)
        m = pd.get_dummies((h[['Genres', 'Source', 'Studios', 'Type']]))
        b = h[['Episodes', 'Score']].join(m)

        x = pd.concat([x_train, b], axis=0, keys=['train', 'test']).loc['test'].fillna(0)
        print(len(x.columns))
        print(len(x_train.columns))
        #  TODO: Количество колонок иногда не совпадает.
        prediction = pipe_forest.predict(x)
        print(c, prediction[0])
        print("Правильность на обучающем наборе: {:.3f}".format(pipe_forest.score(x_train, y_train)))
        print('Верность на тестовом наборе: {:.3f}'.format(pipe_forest.score(x_test, y_test)))
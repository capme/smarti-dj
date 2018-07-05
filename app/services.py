import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from matplotlib import style
import datetime as dt1
from datetime import datetime as dt
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
import math


class StockPredict:
    def __init__(self):
        self.df = None

    # def sample(self):
    #     board = []
    #     for i in range(6):  # create a list with nested lists
    #         board.append([])
    #         print(board)
    #         for n in range(6):
    #             board[i].append("O")
    #
    #     print(board)
    #     return board

    def get_data(self, filename='TLKM.csv'):
        self.df = pd.read_csv(filename)
        self.df = self.df[np.isfinite(self.df['Close'])]

    def predict(self):
        forecast_col = 'Close'
        self.df.fillna(value=-99999, inplace=True)
        forecast_out = int(math.ceil(0.01 * len(self.df)))
        self.df['label'] = self.df[forecast_col].shift(-forecast_out)

        X = np.array(self.df.drop(['label', 'Date'], axis=1))
        X = preprocessing.scale(X)
        X_lately = X[-forecast_out:]
        X = X[:-forecast_out]
        self.df.dropna(inplace=True)
        y = np.array(self.df['label'])
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

        # process using linear regression
        clf = LinearRegression(n_jobs=-1)
        clf.fit(X_train, y_train)
        confidence = clf.score(X_test, y_test)

        forecast_set = clf.predict(X_lately)
        self.df['Forecast'] = np.nan
        last_date = self.df.iloc[-1].Date
        last_date=dt.strptime(last_date, '%Y-%m-%d').timestamp()
        last_unix = last_date
        one_day = 86400
        next_unix = last_unix + one_day

        for i in forecast_set:
            next_date = dt.fromtimestamp(next_unix)
            next_unix += 86400
            self.df.loc[next_date] = [np.nan for _ in range(len(self.df.columns)-1)]+[i]
        self.df['Close'].plot()
        self.df['Forecast'].plot()
        print(self.df.head())
        print(self.df.tail())

        # plt.legend(loc=4)
        # plt.xlabel('Date')
        # plt.ylabel('Price')
        # plt.show()

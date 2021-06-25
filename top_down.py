import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

import utility


class SeasonData:
    """Takes the season data in csv format downloaded from ... and preprocesses it """

    def __init__(self, season_record):
        self.season = season_record

    def process_data(self):
        # get rid of "pk" value
        self.season['Close'] = np.where(self.season['Close'] == 'pk', 0, self.season['Close'])
        # split into home and away datasets
        df_home = self.season[self.season['VH'] == 'H']
        df_visitor = self.season[self.season['VH'] == 'V']
        # we'll key off of rot to flatten the dataframe
        df_home['Rot'] = df_home['Rot'] - 1
        self.season = pd.merge(df_home, df_visitor, left_on=['Date', 'Rot'], right_on=['Date', 'Rot'])
        # get the spread
        self.season['Spread'] = np.where(self.season.Close_y < self.season.Close_x, self.season.Close_y,
                                         self.season.Close_x)
        self.season['Spread_factor'] = np.where(self.season.ML_x < 0, 1, -1)
        self.season['Spread'] = self.season['Spread'] * self.season['Spread_factor']
        self.season['Spread_actual'] = self.season['Final_x'] - self.season['Final_y']
        self.season['Spread_delta'] = self.season['Spread_actual'] - self.season['Spread']
        self.season = self.season[['Spread', 'Spread_actual', 'Spread_delta']]


class AlternateLines:
    """Takes a set of historical data and allows you to compare alternate lines to find oppty"""

    def __init__(self, history_df, market_spread, sport=None, method='Empirical', center=None):
        self.history_df = history_df
        self.method = method
        self.market_spread = market_spread
        self.center = center
        self.sport = sport

        # check for basketball to adjust for no tie games
        if self.sport == 'Basketball':
            self.history_df['Spread_adjust'] = self.history_df['Spread'] * self.history_df['Spread_actual']
            self.history_df['Spread_adjust'] = np.where(self.history_df['Spread_adjust'] < 0, -1, 0)
            self.history_df['Spread_delta'] = self.history_df['Spread_delta'] + self.history_df['Spread_adjust']

    def plot_histogram(self):
        """Plot a histogram of the differences between the spread and the actual"""
        self.history_df['Spread_delta'].plot.hist(bins=40, density=True)
        plt.show()

    def fit(self):
        if self.center is None:
            try:
                self.center = self.market_spread.loc[self.market_spread['ml'] == -110, 'spread'].iloc[0]
            except:
                print('could not find center line.  review and and pass the center explicitly')
        self.market_spread['net_spread'] = self.market_spread['spread'] - self.center
        # adjust the net spread line to account for no ties if basketball
        if self.sport == 'Basketball':
            self.market_spread['net_spread'] = np.where(self.market_spread['spread'] < 0,
                                                        self.market_spread['net_spread'] + 1,
                                                        self.market_spread['net_spread'])
        # get overround
        self.market_spread['do1'] = self.market_spread['ml'].apply(lambda x: utility.ao_to_do(x))
        self.market_spread['do2'] = self.market_spread['ml2'].apply(lambda x: utility.ao_to_do(x))
        self.market_spread['over-round'] = 1 / self.market_spread['do1'] + 1 / self.market_spread['do2'] - 1
        # now get probabilities
        if self.method == 'Empirical':
            for index, row in self.market_spread.iterrows():
                threshold = row['net_spread']
                count = len(self.history_df[self.history_df['Spread_delta'] >= threshold])
                self.market_spread.loc[index, 'count'] = count
            self.market_spread['Prob'] = (1 - self.market_spread['count']/len(self.history_df)) \
                                         * (1 + self.market_spread['over-round'])
        elif self.method == "Gaussian":
            std_dev = self.history_df['Spread_delta'].std()
            dist = norm(loc=0, scale=std_dev)
            self.market_spread['Prob'] = self.market_spread['net_spread'].apply(lambda x: dist.cdf(x))
            self.market_spread['Prob'] = self.market_spread['Prob'] * (1 + self.market_spread['over-round'])
        else:
            print("unknown distribution type")
        # convert prob to decimal odds
        self.market_spread['Decimal_odds'] = 1 / self.market_spread['Prob']



    def plot_alt_lines(self):
        plot_df = self.market_spread.copy()
        plot_df['net_spread'] = plot_df['net_spread'].astype(str)
        plot_df[['net_spread', 'do1', 'Decimal_odds']].plot(x='net_spread')
        plt.show()





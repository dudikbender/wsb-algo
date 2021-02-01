import pandas as pd
import os
from dotenv import find_dotenv, load_dotenv
from datetime import datetime
import json
from typing import List, Optional
import quandl
import yfinance as yf
import praw

# Load the '.env' file with environment variables
env_loc = find_dotenv('.env')
load_dotenv(env_loc)

# Environment variables
# 1. Reddit
reddit_client = os.environ.get('REDDIT_CLIENT')
reddit_secret = os.environ.get('REDDIT_SECRET')
user_agent = 'python- wsb algo for fun by /u/dudik-bender'

# Set Quandl API Key
quandl_key = os.environ.get('QUANDL_KEY')
quandl.ApiConfig.api_key = quandl_key

class Base():
    def normalise_column(self, dataframe:object, normalise:bool = False, normalise_column: str = None):
        if (normalise == True) & (normalise_column is not None):
            try:
                first_value = dataframe.iloc[0][normalise_column]
                dataframe['Normalised'] = [ (x - first_value) / first_value for x in dataframe[normalise_column] ]
                return dataframe
            except:
                print('No normalisation column specified, returning original dataframe.')
                pass

class RedditAlgo(Base):
    def __init__(self, symbol, reddit_account):
        self.symbol = symbol
        self.reddit_account = reddit_account

        # Quandl Configuration
        self.database_code = 'FINRA'
        self.dataset_prefix = 'FNYX_' + self.symbol
        self.quandl_code = self.database_code + '/' + self.dataset_prefix
        self.quandl_api_key = quandl_key
        quandl.ApiConfig.api_key = self.quandl_api_key

        # Reddit Configuration
        self.reddit_client = os.environ.get('REDDIT_CLIENT')
        self.reddit_secret = os.environ.get('REDDIT_SECRET')
        self.user_agent = f'my-wsb-tracker by/u/{reddit_account}'
        self.reddit = praw.Reddit(client_id=self.reddit_client,
                                  client_secret=self.reddit_secret,
                                  user_agent=self.user_agent)

        # Quandl Functions
    def quandl_timeseries(self, start_date:str, end_date:str, normalise:bool = False,
                           normalise_column:str = None):
        df = quandl.get(self.quandl_code, start_date = start_date, end_date = end_date)
        self.normalise_column(df, normalise=normalise, normalise_column=normalise_column)
        return df
    
    def multiple_timeseries(self, codes: List, start_date: str, end_date: str):
            full_df = pd.DataFrame()
            for code in codes:
                df = quandl.get(code, start_date=start_date, end_date=end_date)
                df['ticker'] = code[code.find('/') + 1:]
                full_df = full_df.append(df)
            return full_df

        # Yahoo Finance Functions
    def ticker(self):
        ticker = yf.Ticker(self.symbol)
        return ticker

    def info(self):
        return self.ticker().info

    def history(self, start: str, end: str = None, interval:str = '1d', normalise:bool = True,
                    normalise_column:str = None):
        df = self.ticker().history(start=start, end=end, interval=interval)
        self.normalise_column(df, normalise=normalise, normalise_column=normalise_column)
        return df

    # Reddit Functions
    def subreddit_hot(self, subreddit:str = 'wallstreetbets', limit:int = 100):
        posts = self.reddit.subreddit(subreddit).hot(limit=limit)
        titles = []
        authors = []
        num_comments = []
        urls = []
        for post in posts:
            authors.append(post.author)
            titles.append(post.title)
            num_comments.append(post.num_comments)
            urls.append(post.url)

        df = pd.DataFrame({'title':titles,
                        'author':authors,
                        'comments':num_comments,
                        'url':urls})

        df['url'] = df['url'].apply(self.make_clickable)
        return df

    def subreddit_trending(self, subreddit:str = 'wallstreetbets', limit:int = 100):
        posts = self.reddit.subreddit(subreddit).rising(limit=limit)
        titles = []
        authors = []
        num_comments = []
        urls = []
        for post in posts:
            authors.append(post.author)
            titles.append(post.title)
            num_comments.append(post.num_comments)
            urls.append(post.url)

        df = pd.DataFrame({'title':titles,
                        'author':authors,
                        'comments':num_comments,
                        'url':urls})

        df['url'] = df['url'].apply(self.make_clickable)
        return df

    def make_clickable(self, url):
        return f'<a href="{url}">{url}</a>'

    def subreddit_new(self, subreddit:str = 'wallstreetbets', limit:int = 100):
        posts = self.reddit.subreddit(subreddit).new(limit=limit)
        titles = []
        authors = []
        num_comments = []
        urls = []
        for post in posts:
            authors.append(post.author)
            titles.append(post.title)
            num_comments.append(post.num_comments)
            urls.append(post.url)

        df = pd.DataFrame({'title':titles,
                        'author':authors,
                        'comments':num_comments,
                        'url':urls})

        df['url'] = df['url'].apply(self.make_clickable)
        return df
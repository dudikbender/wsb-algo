from app.models import RedditAlgo
from datetime import datetime, timedelta

def test_ticker(symbol):
    algo = RedditAlgo(symbol, 'dudik-bender')
    return algo.info()

print(test_ticker('TSLA'))
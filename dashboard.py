import streamlit as st
from app.models import RedditAlgo
import plotly.express as px
from datetime import datetime, timedelta

st.title("**The Short Squeeze is On!**")
st.write('This is purely intended for fun, so do not trade based on the information contained here.')
st.markdown('[Check out the code here](https://github.com/dudikbender/wsb-algo)')

# Add a selectbox to the sidebar:
stock_selectbox = st.sidebar.selectbox(
    'Which crazy stock would you like to inspect?',
    ('AMC', 'GME', 'BB')
)

# Add a slider to the sidebar:
time_slider = st.sidebar.slider(
    'Select a range of dates from today for prices and short interest...',
    365, 0, (0, -365)
)

algo = RedditAlgo('GME','dudik-bender')
algo.symbol = stock_selectbox

# Distance from today
beginning = (datetime.today() + timedelta(days=time_slider[0])).strftime('%Y-%m-%d')
ending = (datetime.today() + timedelta(days=time_slider[1])).strftime('%Y-%m-%d')

# Historical Stock Prices
prices_df = algo.history(start=beginning, end=ending)[['Open','Close','High','Low','Volume']]
price_plot = px.line(prices_df['Close'],title=f'Closing Share Price over Time for ${algo.symbol}')

# Short Interest
short_interest = algo.quandl_timeseries(beginning,ending)['TotalVolume']
short_interest_plot = px.line(short_interest,title='Short Interest over Time')

# Reddit Posts
wsb_posts = algo.subreddit_hot(limit=20)
wsb_posts.index +=1

# Line Charts
st.plotly_chart(price_plot)
st.plotly_chart(short_interest_plot)

# Share Price table
st.markdown(f'Share Price Details for *${algo.symbol}*')
st.dataframe(prices_df.sort_index(ascending=False))

# r/wallstreetbets posts
st.markdown('Top posts on r/wallstreetbets')
st.write(wsb_posts.to_html(escape=False), unsafe_allow_html=True)
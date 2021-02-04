import streamlit as st
from app.models import RedditAlgo
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import dash_cytoscape as cyto
import dash_html_components as html

stocks_list = ['GME', 'AMC', 'BB','NOK','TSLA','TWTR']

# Add a selectbox to the sidebar:
stock_selectbox = st.sidebar.selectbox(
    'Which crazy stock would you like to inspect?',
    (stocks_list)
)

# Add a slider to the sidebar:
time_slider = st.sidebar.slider(
    'Select a range of days from today for prices and short interest...',
    365, 0, (0, -365)
)

algo = RedditAlgo(stock_selectbox, 'dudik-bender')

# Distance from today
beginning = (datetime.today() + timedelta(days=time_slider[0])).strftime('%Y-%m-%d')
ending = (datetime.today() + timedelta(days=time_slider[1])).strftime('%Y-%m-%d')

# Header Text
st.title(f"**The Short Squeeze is On for... ${algo.symbol}**")
st.write('This is purely intended for fun, so do not trade based on the information contained here.')
st.markdown('[Check out the code here](https://github.com/dudikbender/wsb-algo)')

# Historical Stock Prices
prices_df = algo.history(start=beginning, end=ending)[['Open','Close','High','Low','Volume']]
candlestick = go.Figure(data=[go.Candlestick(x=prices_df.index,
                open=prices_df['Open'],
                high=prices_df['High'],
                low=prices_df['Low'],
                close=prices_df['Close'])])
candlestick.update_layout(title=f'${algo.symbol} Share Price Movement',
                          yaxis_title='Stock Price',
                          xaxis_title='Date',
                          hovermode="x unified", xaxis_rangeslider_visible=False)
st.plotly_chart(candlestick)

# Short Interest
short_interest = algo.quandl_timeseries(beginning,ending, normalise=True, normalise_column='TotalVolume')[['TotalVolume','Normalised']]
si_plot = go.Figure()
si_plot.add_trace(go.Bar(x=short_interest.index,
                         y= [ x / 1000 for x in short_interest.TotalVolume ]))
si_plot.update_layout(title='Short Interest',
                      yaxis_title='Share Units (000s)',
                      xaxis_title='Date',
                      hovermode='x unified')

#short_interest_plot = px.bar(short_interest)
si_plot.update_layout(hovermode="x unified")
st.plotly_chart(si_plot)

# Reddit Posts
wsb_posts = algo.subreddit_hot(limit=20)
wsb_posts.index +=1

# r/wallstreetbets posts
st.markdown('Top posts on [**r/wallstreetbets**](https://www.reddit.com/r/wallstreetbets/)')
st.write(wsb_posts.to_html(escape=False), unsafe_allow_html=True)

# Share Price table
st.markdown(f'Share Price Details for **${algo.symbol}**')
st.dataframe(prices_df.sort_index(ascending=False))

cyto = go.Figure(cyto.Cytoscape(
        id='cytoscape-two-nodes',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '400px'},
        elements=[
            {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
            {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'source': 'one', 'target': 'two'}}
        ]
    )
)
st.plotly_chart(cyto)
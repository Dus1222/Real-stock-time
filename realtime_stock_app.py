# Real-Time Stock Dashboard with Candlestick Chart and Price Alerts using Streamlit

# Install required packages:
# pip install yfinance plotly streamlit

import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import time

# Streamlit Page Configuration
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")

# Title
st.title("📈 Real-Time Stock Price Dashboard with Candlestick Charts & Price Alerts")

# Sidebar for user input
tickers = st.sidebar.multiselect(
    'Select stocks to track:',
    ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'META'],
    default=['AAPL', 'MSFT']
)

refresh_interval = st.sidebar.number_input('Refresh interval (seconds):', min_value=10, max_value=300, value=60)

# User-defined price alerts
price_alerts = {}
for ticker in tickers:
    price_alerts[ticker] = st.sidebar.number_input(f'Set alert price for {ticker}:', min_value=1.0, value=100.0)

# Function to fetch stock data
def get_stock_data(ticker, period='1d', interval='1m'):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data.dropna()

# Function to plot candlestick chart
def plot_candlestick(data, ticker):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    )])

    fig.update_layout(
        title=f'{ticker} - Candlestick Chart',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        width=1000,
        height=500
    )

    return fig

# Live update loop
placeholder = st.empty()

while True:
    all_data = {}
    triggered_alerts = []

    for ticker in tickers:
        all_data[ticker] = get_stock_data(ticker)

    with placeholder.container():
        for ticker in tickers:
            data = all_data[ticker]

            # Plot line chart with moving averages
            st.subheader(f'{ticker} - Real-Time Price Chart')
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price'
            ))

            # Calculate moving averages
            data['MA20'] = data['Close'].rolling(window=20).mean()
            data['MA50'] = data['Close'].rolling(window=50).mean()

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20'
            ))

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['MA50'],
                mode='lines',
                name='MA50'
            ))

            fig.update_layout(
                xaxis_title='Time',
                yaxis_title='Price (USD)',
                template='plotly_dark',
                width=1000,
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Plot candlestick chart
            st.subheader(f'{ticker} - Candlestick Chart')
            candle_fig = plot_candlestick(data, ticker)
            st.plotly_chart(candle_fig, use_container_width=True)

            # Check for price alerts
            current_price = data['Close'].iloc[-1]
            alert_price = price_alerts[ticker]

            if current_price >= alert_price:
                st.warning(f'🔔 Price Alert: {ticker} has reached ${current_price:.2f} (Alert: ${alert_price:.2f})')
                triggered_alerts.append((ticker, current_price, alert_price))

        st.write(f'⏱️ Last updated: {pd.Timestamp.now()}')

    time.sleep(refresh_interval)
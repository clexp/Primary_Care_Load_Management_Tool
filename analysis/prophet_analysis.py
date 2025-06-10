"""
Prophet Analysis Module for Call Center Forecasting

This module demonstrates the use of Facebook's Prophet library for forecasting
call center volumes with daily, weekly, and yearly seasonality patterns.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st

def create_sample_data():
    """
    Creates sample call center data for demonstration purposes.
    In production, this would be replaced with actual call center data.
    """
    # Create date range for one year
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='30min')
    
    # Create base pattern with daily, weekly, and yearly seasonality
    np.random.seed(42)  # for reproducibility
    
    # Base pattern
    base = 100 + 50 * np.sin(np.arange(len(dates)) * 2 * np.pi / (24 * 2))  # daily pattern
    
    # Weekly pattern
    weekly = 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / (24 * 2 * 7))  # weekly pattern
    
    # Yearly pattern
    yearly = 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / (24 * 2 * 365))  # yearly pattern
    
    # Add some noise
    noise = np.random.normal(0, 10, len(dates))
    
    # Combine patterns
    calls = base + weekly + yearly + noise
    calls = np.maximum(calls, 0)  # ensure non-negative values
    
    # Create DataFrame
    df = pd.DataFrame({
        'ds': dates,
        'y': calls
    })
    
    return df

def fit_prophet_model(df, changepoint_prior_scale=0.05):
    """
    Fits a Prophet model to the call center data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with columns 'ds' (datetime) and 'y' (call volume)
    changepoint_prior_scale : float
        Flexibility of the trend (higher values allow more flexibility)
    
    Returns:
    --------
    model : Prophet
        Fitted Prophet model
    """
    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    
    model.fit(df)
    return model

def make_forecast(model, periods=30):
    """
    Makes a forecast using the fitted Prophet model.
    
    Parameters:
    -----------
    model : Prophet
        Fitted Prophet model
    periods : int
        Number of periods to forecast (in days)
    
    Returns:
    --------
    forecast : pandas.DataFrame
        DataFrame containing the forecast
    """
    future = model.make_future_dataframe(periods=periods, freq='30min')
    forecast = model.predict(future)
    return forecast

def plot_forecast(df, forecast, title="Call Volume Forecast"):
    """
    Creates an interactive plot of the forecast using Plotly.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Historical data
    forecast : pandas.DataFrame
        Forecast data
    title : str
        Plot title
    """
    fig = go.Figure()
    
    # Add historical data
    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['y'],
        name='Historical',
        mode='lines',
        line=dict(color='blue')
    ))
    
    # Add forecast
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        name='Forecast',
        mode='lines',
        line=dict(color='red')
    ))
    
    # Add confidence intervals
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line=dict(color='rgba(255,0,0,0.1)'),
        name='Upper Bound'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line=dict(color='rgba(255,0,0,0.1)'),
        name='Lower Bound'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Call Volume',
        hovermode='x unified'
    )
    
    return fig

def analyze_seasonality(model):
    """
    Analyzes and returns the seasonality components of the model.
    
    Parameters:
    -----------
    model : Prophet
        Fitted Prophet model
    
    Returns:
    --------
    dict
        Dictionary containing seasonality components
    """
    components = model.plot_components()
    return components

if __name__ == "__main__":
    # Create sample data
    df = create_sample_data()
    
    # Fit model
    model = fit_prophet_model(df)
    
    # Make forecast
    forecast = make_forecast(model)
    
    # Create plot
    fig = plot_forecast(df, forecast)
    
    # Show plot (in Jupyter notebook)
    # fig.show()
    
    # Analyze seasonality
    components = analyze_seasonality(model)

    # Assuming df is your call center data with 'ds' (datetime) and 'y' (call volume) columns
    model = fit_prophet_model(df)
    forecast = make_forecast(model)
    fig = plot_forecast(df, forecast)
    st.plotly_chart(fig) 
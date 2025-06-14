import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime, timedelta
from prophet.make_holidays import make_holidays_df

st.title("Call Volume Forecasting 📈")
st.write("Predict future call volumes, wait times, and call durations using Prophet time series forecasting")

# Check if we have cleaned data
if 'processed_data' not in st.session_state or not st.session_state['processed_data'].get('data_loaded', False):
    st.warning("Please load and clean your data in the Data Loader page first.")
    st.stop()

# Initialize models and forecasts in session state if they don't exist
if 'models' not in st.session_state:
    st.session_state['models'] = {
        'call_volume': None,
        'wait_time': None,
        'call_duration': None
    }

if 'forecasts' not in st.session_state:
    st.session_state['forecasts'] = {
        'call_volume': None,
        'wait_time': None,
        'call_duration': None
    }

# Get the cleaned data
df = st.session_state['processed_data']['clean_df']

# Prepare data for Prophet
st.header("Data Preparation")
st.write("Preparing time series data for forecasting...")

# Create Prophet-compatible dataframes
prophet_df_calls = pd.DataFrame()
prophet_df_wait = pd.DataFrame()
prophet_df_duration = pd.DataFrame()

# Common datetime column
datetime_col = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'])

# Prepare data for each metric
prophet_df_calls['ds'] = datetime_col
prophet_df_calls['y'] = df['Total Calls']

prophet_df_wait['ds'] = datetime_col
prophet_df_wait['y'] = df['Avg Wait Time (s)']

prophet_df_duration['ds'] = datetime_col
prophet_df_duration['y'] = df['Avg Call Length (s)']

# Filter for working hours (8am to 6pm)
working_hours_mask = (datetime_col.dt.hour >= 8) & (datetime_col.dt.hour < 18)
prophet_df_calls = prophet_df_calls[working_hours_mask]
prophet_df_wait = prophet_df_wait[working_hours_mask]
prophet_df_duration = prophet_df_duration[working_hours_mask]

# Filter for working weekdays (Monday to Friday)
working_days_mask = datetime_col.dt.dayofweek < 5
prophet_df_calls = prophet_df_calls[working_days_mask]
prophet_df_wait = prophet_df_wait[working_days_mask]
prophet_df_duration = prophet_df_duration[working_days_mask]

# Add floor and cap for logistic growth
for df in [prophet_df_calls, prophet_df_wait, prophet_df_duration]:
    df['floor'] = 0
    df['cap'] = df['y'].max() * 3.0

# Add UK holidays
years = [2024, 2025]
uk_holidays = make_holidays_df(year_list=years, country='UK')
uk_holidays['lower_window'] = -1
uk_holidays['upper_window'] = 1

# Model Configuration
st.header("Model Configuration")

# Create tabs for different metrics
metric_tabs = st.tabs(["Call Volume", "Wait Time", "Call Duration"])
metrics = ["Call Volume", "Wait Time", "Call Duration"]
dataframes = [prophet_df_calls, prophet_df_wait, prophet_df_duration]
model_keys = ['call_volume', 'wait_time', 'call_duration']
forecast_keys = ['call_volume', 'wait_time', 'call_duration']

for i, (tab, metric, df, model_key, forecast_key) in enumerate(zip(metric_tabs, metrics, dataframes, model_keys, forecast_keys)):
    with tab:
        st.subheader(f"{metric} Forecasting")
        
        # Check if model exists in session state
        if st.session_state['models'][model_key] is None:
            st.info(f"No {metric.lower()} model trained yet. Click the button below to train.")
        else:
            st.success(f"{metric} model is trained and ready for forecasting.")
        
        # Train button
        if st.button(f"Train {metric} Model"):
            with st.spinner(f"Training {metric} model..."):
                # Initialize and configure the model
                model = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=False,
                    changepoint_prior_scale=0.05,
                    seasonality_prior_scale=15.0,
                    interval_width=0.95,
                    growth='logistic',
                    holidays=uk_holidays
                )
                
                # Add custom seasonality
                model.add_seasonality(
                    name='daily',
                    period=1,
                    fourier_order=10
                )
                
                # Fit the model
                model.fit(df)
                
                # Store model in session state
                st.session_state['models'][model_key] = model
                
                st.success(f"{metric} model trained successfully!")
        
        # Generate forecast if model exists
        if st.session_state['models'][model_key] is not None:
            # Show existing forecast if it exists
            if st.session_state['forecasts'][forecast_key] is not None:
                st.success(f"Existing {metric} forecast available. Click 'Generate New Forecast' to update.")
                
                # Display existing forecast results
                st.subheader(f"{metric} Forecast Results")
                
                # Plot the existing forecast
                model = st.session_state['models'][model_key]
                forecast = st.session_state['forecasts'][forecast_key]
                
                fig = model.plot(forecast)
                st.pyplot(fig)
                
                # Plot the components
                st.subheader("Forecast Components")
                fig_components = model.plot_components(forecast)
                st.pyplot(fig_components)
                
                # Display forecast metrics
                st.subheader("Forecast Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Mean Forecast",
                        f"{forecast['yhat'].mean():.1f}"
                    )
                
                with col2:
                    st.metric(
                        "Max Forecast",
                        f"{forecast['yhat'].max():.1f}"
                    )
                
                with col3:
                    st.metric(
                        "Min Forecast",
                        f"{forecast['yhat'].min():.1f}"
                    )
                
                # Add a button to generate new forecast
                if st.button(f"Generate New {metric} Forecast"):
                    with st.spinner(f"Generating new {metric} forecast..."):
                        model = st.session_state['models'][model_key]
                        
                        # Create future dataframe
                        future = pd.DataFrame()
                        future['ds'] = pd.date_range(
                            start=df['ds'].max(),
                            periods=30 * 48,  # 30 days of 30-minute intervals
                            freq='30min'
                        )
                        
                        # Filter for working hours and days
                        future = future[
                            (future['ds'].dt.hour >= 8) & 
                            (future['ds'].dt.hour < 18) &
                            (future['ds'].dt.dayofweek < 5)
                        ]
                        
                        # Add floor and cap
                        future['floor'] = 0
                        future['cap'] = df['y'].max() * 3.0
                        
                        # Make predictions
                        forecast = model.predict(future)
                        
                        # Store forecast in session state
                        st.session_state['forecasts'][forecast_key] = forecast
                        
                        st.success("New forecast generated successfully!")
                        st.experimental_rerun()
            else:
                # If no forecast exists, show the generate forecast button
                if st.button(f"Generate {metric} Forecast"):
                    with st.spinner(f"Generating {metric} forecast..."):
                        model = st.session_state['models'][model_key]
                        
                        # Create future dataframe
                        future = pd.DataFrame()
                        future['ds'] = pd.date_range(
                            start=df['ds'].max(),
                            periods=30 * 48,  # 30 days of 30-minute intervals
                            freq='30min'
                        )
                        
                        # Filter for working hours and days
                        future = future[
                            (future['ds'].dt.hour >= 8) & 
                            (future['ds'].dt.hour < 18) &
                            (future['ds'].dt.dayofweek < 5)
                        ]
                        
                        # Add floor and cap
                        future['floor'] = 0
                        future['cap'] = df['y'].max() * 3.0
                        
                        # Make predictions
                        forecast = model.predict(future)
                        
                        # Store forecast in session state
                        st.session_state['forecasts'][forecast_key] = forecast
                        
                        st.success("Forecast generated successfully!")
                        st.experimental_rerun()

# Add help text
st.markdown("""
### About Time Series Forecasting
This page uses Facebook's Prophet library to forecast future call center metrics based on historical data.

Key features:
- Daily and weekly seasonality
- Working hours only (8am to 6pm)
- Working weekdays only (Monday to Friday)
- Separate models for call volume, wait time, and call duration
- Detailed daily patterns and statistics
""")
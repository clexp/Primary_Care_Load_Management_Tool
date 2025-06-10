import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.title("Call Volume Forecasting 📈")
st.write("Predict future call volumes using Prophet time series forecasting")

# File uploader for data
uploaded_file = st.file_uploader("Upload your historical call data (CSV)", type=['csv'])

if uploaded_file is not None:
    try:
        # Read the data
        df = pd.read_csv(uploaded_file)
        st.success("Data loaded successfully!")
        
        # Data preparation section
        st.header("Data Preparation")
        
        # Convert date and time columns
        df['ds'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M')
        df['y'] = df['Total Calls']
        
        # Prophet model configuration
        st.header("Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            forecast_days = st.number_input(
                "Days to Forecast",
                min_value=1,
                max_value=90,
                value=30,
                help="Number of days to forecast into the future"
            )
            
            changepoint_prior_scale = st.slider(
                "Trend Flexibility",
                min_value=0.001,
                max_value=0.5,
                value=0.05,
                help="How flexible the trend is allowed to be"
            )
        
        with col2:
            seasonality_prior_scale = st.slider(
                "Seasonality Strength",
                min_value=0.01,
                max_value=20.0,
                value=10.0,
                help="How strong the seasonal patterns are"
            )
            
            fourier_order = st.slider(
                "Seasonality Complexity",
                min_value=1,
                max_value=20,
                value=10,
                help="How complex the seasonal patterns can be"
            )
        
        # Model training
        if st.button("Train Model"):
            with st.spinner("Training Prophet model..."):
                # Initialize and configure the model
                model = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=False,
                    changepoint_prior_scale=changepoint_prior_scale,
                    seasonality_prior_scale=seasonality_prior_scale
                )
                
                # Add custom seasonality
                model.add_seasonality(
                    name='daily',
                    period=1,
                    fourier_order=fourier_order
                )
                
                # Fit the model
                model.fit(df)
                
                # Create future dataframe
                future = model.make_future_dataframe(
                    periods=forecast_days * 48,  # 48 30-minute intervals per day
                    freq='30min'
                )
                
                # Make predictions
                forecast = model.predict(future)
                
                # Display results
                st.header("Forecast Results")
                
                # Plot the forecast
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
                        f"{forecast['yhat'].mean():.1f} calls"
                    )
                
                with col2:
                    st.metric(
                        "Max Forecast",
                        f"{forecast['yhat'].max():.1f} calls"
                    )
                
                with col3:
                    st.metric(
                        "Min Forecast",
                        f"{forecast['yhat'].min():.1f} calls"
                    )
                
                # Download forecast data
                csv = forecast.to_csv(index=False)
                st.download_button(
                    "Download Forecast Data",
                    csv,
                    "forecast.csv",
                    "text/csv",
                    key='download-csv'
                )
    
    except Exception as e:
        st.error(f"Error in forecasting: {str(e)}")
else:
    st.info("Please upload a CSV file to begin forecasting")

# Add help text
st.markdown("""
### About Call Volume Forecasting
This page uses Facebook's Prophet library to forecast future call volumes based on historical data.

Key features:
- Daily and weekly seasonality
- Customizable trend flexibility
- Adjustable seasonality strength
- Configurable forecast horizon

The forecast takes into account:
- Time of day patterns
- Day of week patterns
- Overall trends
- Special events (if configured)

Use the sliders to adjust the model parameters and see how they affect the forecast.
""") 
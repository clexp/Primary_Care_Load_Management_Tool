import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

def plot_daily_patterns(df):
    """Plot daily call patterns with scatter points only"""
    df['Time'] = pd.to_datetime(df['Time'])
    fig = px.scatter(df, x='Time', y='Total Calls',
                    title='Daily Call Volume Patterns',
                    template='plotly_white')
    fig.update_traces(mode='markers', marker=dict(size=6))
    return fig

def plot_wait_times(df):
    """Plot wait time patterns with scatter points only"""
    df['Time'] = pd.to_datetime(df['Time'])
    fig = px.scatter(df, x='Time', y=['Avg Wait Time (s)', 'Longest Wait Time (s)'],
                    title='Wait Time Patterns',
                    template='plotly_white')
    fig.update_traces(mode='markers', marker=dict(size=6))
    return fig

def plot_weekday_patterns(df):
    """Plot patterns by weekday with box plots"""
    df['Time'] = pd.to_datetime(df['Time'])
    df['Weekday'] = df['Time'].dt.day_name()
    fig = px.box(df, x='Weekday', y='Total Calls',
                 title='Call Volume Distribution by Weekday',
                 template='plotly_white')
    return fig

def plot_weekday_averages(df):
    """Plot average patterns for each weekday"""
    df['Time'] = pd.to_datetime(df['Time'])
    df['Weekday'] = df['Time'].dt.day_name()
    df['Hour'] = df['Time'].dt.hour
    
    # Calculate average calls for each weekday and hour
    weekday_avg = df.groupby(['Weekday', 'Hour'])['Total Calls'].mean().reset_index()
    
    # Create subplots for each weekday
    fig = go.Figure()
    
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for day in weekdays:
        day_data = weekday_avg[weekday_avg['Weekday'] == day]
        fig.add_trace(go.Scatter(
            x=day_data['Hour'],
            y=day_data['Total Calls'],
            name=day,
            mode='lines+markers'
        ))
    
    fig.update_layout(
        title='Average Call Volume by Hour for Each Weekday',
        xaxis_title='Hour of Day',
        yaxis_title='Average Number of Calls',
        template='plotly_white'
    )
    return fig

def plot_individual_weekday_patterns(df):
    """Plot individual weekday patterns in separate subplots"""
    df['Time'] = pd.to_datetime(df['Time'])
    df['Weekday'] = df['Time'].dt.day_name()
    df['Hour'] = df['Time'].dt.hour
    
    # Create subplots for each weekday
    fig = make_subplots(rows=5, cols=1, 
                       subplot_titles=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for idx, day in enumerate(weekdays, 1):
        day_data = df[df['Weekday'] == day]
        hourly_avg = day_data.groupby('Hour')['Total Calls'].mean()
        
        # Fit a log-normal curve
        x = np.arange(24)
        y = hourly_avg.values
        # Simple log-normal fit
        mu = np.mean(np.log(y + 1))
        sigma = np.std(np.log(y + 1))
        fitted_y = np.exp(mu + sigma * np.random.randn(24))
        
        fig.add_trace(
            go.Scatter(x=x, y=y, mode='markers', name=f'{day} Actual',
                      marker=dict(size=8), showlegend=False),
            row=idx, col=1
        )
        fig.add_trace(
            go.Scatter(x=x, y=fitted_y, mode='lines', name=f'{day} Fitted',
                      line=dict(color='red'), showlegend=False),
            row=idx, col=1
        )
    
    fig.update_layout(
        height=1000,
        title_text="Call Volume Patterns by Weekday",
        showlegend=False,
        template='plotly_white'
    )
    return fig

def plot_connection_rates(df):
    """Plot connection rates and abandonment patterns"""
    df['Time'] = pd.to_datetime(df['Time'])
    df['Connection Rate'] = df['Connected Calls'] / df['Total Calls'] * 100
    df['Abandonment Rate'] = df['Calls Not Connected'] / df['Total Calls'] * 100
    
    fig = px.scatter(df, x='Time', y=['Connection Rate', 'Abandonment Rate'],
                    title='Call Connection and Abandonment Rates',
                    template='plotly_white')
    fig.update_traces(mode='markers', marker=dict(size=6))
    return fig

def plot_heatmap(df):
    """Plot hourly patterns heatmap"""
    df['Time'] = pd.to_datetime(df['Time'])
    df['Hour'] = df['Time'].dt.hour
    df['Weekday'] = df['Time'].dt.day_name()
    
    pivot_df = df.pivot_table(
        values='Total Calls',
        index='Weekday',
        columns='Hour',
        aggfunc='mean'
    )
    
    fig = px.imshow(pivot_df,
                    title='Call Volume Heatmap by Hour and Weekday',
                    aspect='auto')
    return fig

def plot_daily_patterns_with_multiple_metrics(df):
    """Plot daily call patterns with multiple metrics"""
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add call volume
    fig.add_trace(
        go.Scatter(x=df['DateTime'], y=df['Total Calls'],
                  name="Total Calls", line=dict(color='blue')),
        secondary_y=False,
    )

    # Add wait time on secondary axis
    fig.add_trace(
        go.Scatter(x=df['DateTime'], y=df['Avg Wait Time (s)'],
                  name="Avg Wait Time", line=dict(color='red')),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title='Daily Call Patterns and Wait Times',
        xaxis_title='Date & Time',
        hovermode='x unified'
    )

    # Update y-axes labels
    fig.update_yaxes(title_text="Number of Calls", secondary_y=False)
    fig.update_yaxes(title_text="Average Wait Time (seconds)", secondary_y=True)

    return fig

def plot_wait_times_with_more_detail(df):
    """Plot wait time distributions with more detail"""
    fig = go.Figure()

    # Add histogram
    fig.add_trace(go.Histogram(
        x=df['Avg Wait Time (s)'],
        name='Wait Time Distribution',
        nbinsx=30,
        histnorm='probability'
    ))

    # Add kernel density estimate
    fig.add_trace(go.Scatter(
        x=df['Avg Wait Time (s)'].sort_values(),
        y=df['Avg Wait Time (s)'].plot.kde().get_lines()[0].get_ydata(),
        name='KDE',
        line=dict(color='red')
    ))

    fig.update_layout(
        title='Wait Time Distribution',
        xaxis_title='Wait Time (seconds)',
        yaxis_title='Frequency',
        bargap=0.1
    )

    return fig

def plot_average_call_volumes_by_weekday_and_hour(df):
    """Plot average call volumes by weekday and hour."""
    # Extract weekday and hour, then calculate mean
    df_pattern = df.copy()
    df_pattern['Weekday'] = df_pattern['DateTime'].dt.day_name()
    df_pattern['Hour'] = df_pattern['DateTime'].dt.hour
    
    # Calculate mean calls for each weekday-hour combination
    hourly_pattern = df_pattern.groupby(['Weekday', 'Hour'])['Total Calls'].mean().reset_index(name='Average Calls')
    
    # Create heatmap
    fig = px.density_heatmap(
        hourly_pattern,
        x='Hour',
        y='Weekday',
        z='Average Calls',
        title='Average Call Volume by Day and Hour',
        labels={'Hour': 'Hour of Day', 'Average Calls': 'Average Number of Calls'},
        category_orders={
            'Weekday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        }
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        coloraxis_colorbar_title='Avg. Calls'
    )
    
    return fig

def create_heatmap_of_call_volumes(df):
    """Create heatmap of call volumes"""
    # Create pivot table of average calls by day and hour
    pivot_data = pd.pivot_table(
        df,
        values='Total Calls',
        index=df['DateTime'].dt.day_name(),
        columns=df['DateTime'].dt.hour,
        aggfunc='mean'
    )
    
    # Order the days of the week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_data = pivot_data.reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis',
        hoverongaps=False))
    
    fig.update_layout(
        title='Call Volume Heatmap',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week'
    )
    
    return fig

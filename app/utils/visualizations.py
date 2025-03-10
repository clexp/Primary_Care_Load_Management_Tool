import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_daily_patterns(df):
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

def plot_wait_times(df):
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

def plot_weekday_patterns(df):
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

def plot_heatmap(df):
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

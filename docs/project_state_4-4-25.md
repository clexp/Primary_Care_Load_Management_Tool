# Project Overview: Primary Care Load Management Tool

This is a web-based decision support tool designed to help primary care practices manage call volume and staffing efficiently. The tool is built using Streamlit and aims to minimize patient wait times by providing insights into call patterns and staffing requirements.

## Current Implementation

The application has three main components:

### Data Upload: Allows users to upload CSV files with call data, processes them, and provides basic data quality checks.

### Quick Insights: Provides visualizations of call patterns, including:

- Daily call volume patterns
- Wait time patterns
- Weekday distribution of calls
- Connection rates
- Key metrics like average wait time, max wait time, and drop rate

### Staff Planning: Implements an Erlang C calculator to determine required staffing levels based on:

- Call volumes
- Average handle time
- Target wait time
- Target service level
  The application uses a modular structure with utility functions for data processing and visualization.

## Analysis of the Notebooks

The two notebooks (predict-call-volume.ipynb and process-call-data.ipynb) appear to be experimental prototypes that were used to develop the core functionality now implemented in the Streamlit app.

### Bayesian Analysis Implementation

From what I can see in the notebooks, there was an attempt to implement Bayesian analysis for call volume prediction. However, I don't see a complete implementation of Bayesian analysis in the notebooks I examined. The notebooks primarily focus on:
Data Processing: Cleaning and preparing call data
Exploratory Analysis: Understanding call patterns and trends
Basic Statistical Analysis: Using curve fitting and other statistical methods

### Assessment of the Approach

#### Was Bayesian analysis the right tool?

For call volume prediction, Bayesian analysis could be valuable, especially for:

- Incorporating uncertainty in predictions
- Updating predictions as new data arrives
- Modeling complex relationships between variables
- Providing confidence intervals for predictions

#### Was it implemented correctly?

From what I can see, the Bayesian analysis was not fully implemented or integrated into the final application
The current implementation uses simpler methods like curve fitting and the Erlang C formula
The "ML Predictor" tab in the Staff Planning page is marked as "Coming Soon"

## Recommendations for the Next Week

To get the application to a deliverable state in the next week, I recommend focusing on:

### Complete the Core Functionality:

Finish implementing the data processing pipeline
Ensure all visualizations work correctly
Complete the Erlang C calculator implementation

### Add Basic Predictive Capabilities:

Implement simple time series forecasting for call volumes
Add seasonal decomposition to identify patterns
Create a basic ML model for call volume prediction

### Improve User Experience:

Add clear instructions and tooltips
Ensure the interface is intuitive
Add export functionality for reports

### Testing and Validation:

Test with real data
Validate predictions against historical data
Get feedback from the call center manager

### Documentation:

Create user documentation
Document the code
Prepare a presentation for the customer

# CL User notes

### Upload page

- Option to download an empty excel file as a template
- Yes can upload multiple files
- Yes can download joined files
- Yes Downloaded data looks well formatted
- Data upload on front page and on the upload page
- Upload page uses broken
- rename the front page and add a graphic
- Daily Patterns need to show week days only, and have lines and confidence intervals
- Wait times 'averages' but what are they really?
- Weekday Distribution, is this meaningful?
- Weekday Averages, is this meaningful?
- Connection rates? What dose this mean?
- recalculates everything each time we click quick insights.
- add a 'download template' button to get a sample excel file
- add a staffing upload button.
- Percentage slider does not show the percent on the staffing pane.

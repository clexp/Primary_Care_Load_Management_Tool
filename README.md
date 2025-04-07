# Primary Care Load Management Tool

A comprehensive tool for analyzing call center data, visualizing patterns, and optimizing staffing levels for primary care practices. This application helps healthcare providers manage call volume efficiently and minimize patient wait times.

## Project Structure

```
Primary_Care_Load_Management_Tool/
├── streamlit_app/           # Main Streamlit application
│   ├── app.py               # Main application entry point
│   ├── pages/               # Streamlit pages
│   │   ├── 01_Data_Management.py
│   │   ├── 02_Call_Analytics.py
│   │   └── 03_Staff_Optimization.py
│   ├── utils/               # Utility functions
│   │   ├── data_processor.py
│   │   └── visualizations.py
│   ├── data/                # Sample data and templates
│   └── static/              # Static assets
├── analysis/                # Analysis notebooks and scripts
│   ├── predict-call-volume.ipynb
│   ├── process-call-data.ipynb
│   └── erlang-c.py
├── data/                    # Data directory
│   ├── raw/                 # Raw data files
│   └── templates/           # Data templates
├── docs/                    # Documentation
├── requirements.txt         # Main requirements file
└── README.md                # This file
```

## Features

### Data Management

- Upload and process call center data from CSV or Excel files
- Combine multiple data files
- Data quality checks and validation
- Download processed data

### Call Analytics

- Visualize daily call patterns
- Analyze wait time distributions
- Examine weekday patterns
- Track connection and abandonment rates
- Identify correlations between wait times and abandonment

### Staff Optimization

- Calculate required staffing levels using Erlang models:
  - Erlang A (with abandonment)
  - Erlang B (without queuing)
  - Erlang C (with queuing)
- Account for finite queue sizes
- Use actual abandonment data from your call center
- Visualize staffing requirements with heatmaps
- Perform gap analysis between current and required staffing

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/Primary_Care_Load_Management_Tool.git
cd Primary_Care_Load_Management_Tool
```

2. Create a virtual environment and activate it:

```bash
python -m venv streamlit_env
source streamlit_env/bin/activate  # On Mac/Linux
# or
.\streamlit_env\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
cd streamlit_app
streamlit run app.py
```

### Data Requirements

The application expects call data with the following columns:

- `Time`: Datetime values
- `Total Calls`: Number of calls received
- `Connected Calls`: Number of calls answered
- `Calls Not Connected`: Number of abandoned calls
- `Avg Wait Time (s)`: Average wait time in seconds
- `Longest Wait Time (s)`: Maximum wait time in seconds
- `Avg Talk Time (s)`: Average talk time in seconds

You can download a template from the Data Management page.

### Workflow

1. **Data Management**: Upload and process your call data
2. **Call Analytics**: Analyze patterns and identify insights
3. **Staff Optimization**: Calculate optimal staffing levels based on your data

## Mathematical Background

The application uses various Erlang models for queueing theory:

- **Erlang A**: Accounts for caller abandonment behavior, providing realistic predictions for call centers with high abandonment rates
- **Erlang B**: Assumes calls are blocked if all agents are busy, suitable for systems without queuing
- **Erlang C**: Assumes calls wait in queue if all agents are busy, suitable for call centers with low abandonment rates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```

```

# Call Center Waiting Time Calculator

A Streamlit web application that calculates expected waiting times and service levels for call centers using the Erlang-A formula. This tool helps call center managers optimize staffing levels while accounting for caller abandonment.

## Features

- Calculates expected waiting times using Erlang-A formula
- Accounts for caller abandonment behavior
- Provides key performance metrics:
  - Average waiting time
  - Abandonment rate
  - Service level (% calls answered within 20 seconds)
  - Offered load in Erlangs

## Installation

1. Clone this repository:

```bash
git clone https://github.com/clexp/Primary_Care_Load_Management_Tool.git
cd Primary_Care_Load_Management_Tool
```

2. Create a virtual environment and activate it:

```bash
python -m venv phones
source phones/bin/activate  # On Mac/Linux
# or
.\phones\Scripts\activate  # On Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Enter your parameters in the sidebar:

- Arrival Rate (calls per hour)
- Average Service Time (hours)
- Number of Agents
- Average Patience Time (minutes)

The results will update automatically showing:

- Expected waiting times
- Abandonment rates
- Service levels

## Mathematical Background

The calculator uses the Erlang-A (Erlang + Abandonment) model, which extends the classic Erlang-C formula by incorporating caller abandonment behavior. This provides more realistic predictions for call center performance, especially in high-traffic situations.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```

```

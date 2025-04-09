# Cucina intelligente di MASsimo

## Introduction

This program simulates a restaurant with a focus on optimizing shift planning, balancing workload distribution during shifts, and interpreting restaurant statistics. By utilizing mathematical optimization, heuristics, and machine learning techniques, the program ensures efficient staffing and maximizes profitability through optimal coordination of personnel.

<br>

## Requirements

### Python Version

This software requires **Python 3.12**. Newer versions are not supported because TensorFlow is used for an LSTM model that predicts the increasing number of customers in future iterations. LSTM (Long Short-Term Memory) is a type of recurrent neural network (RNN) designed for processing sequential data and capturing long-term dependencies, making it effective for time-series forecasting. Currently, **TensorFlow only works with Python 3.12**, and using a different version may cause compatibility issues or unexpected behavior.

Ensure that the Python installation is exactly **3.12.x** before proceeding.

### Dependencies

To install all required Python packages, use the requirements.txt file with the following commands:

```bash
pip cache purge
pip install -r requirements.txt
pip install acopy==0.7.0 --no-deps
```

The pip cache will be purged to avoid any issues with the installation of the packages.

The package `acopy` must be installed separately without its nested dependencies. This is necessary to prevent the `click` package from being installed in a version that is incompatible with `dash`. The `dash` package requires a newer version of `click`, and since no functionality from `acopy` that depends on `click` is used, `acopy` can be safely installed without dependencies.

### Ollama and LLM

The software includes functionality to generate reports based on statistical calculations for the restaurant. To enable this feature, **Ollama must be installed**.

Ollama is a local inference engine for running large language models (LLMs) efficiently on personal machines. It provides a streamlined interface for interacting with AI models, allowing applications to process natural language queries and generate text-based outputs. By integrating Ollama, the software can leverage AI-generated insights to create detailed, data-driven reports.

If Ollama is not installed, the LLM-based reporting feature will be disabled during program execution. Other functionalities of the software will continue to work, but automatic report generation using the LLM will not be available.

Ensure Ollama is installed before running the software if this feature is required. More information and installation instructions can be found on the official [Ollama website](https://ollama.com).

## Parameters in `data/config.json`

### Rating
- `rating_default` (int): Default rating value for new customers that have not finished eating (and provided a real rating) yet.
- `rating_min` (int): Minimal possible rating value.
- `rating_max` (int): Maximal possible rating value

### Orders
- `order_correctness` (float): Percentage of orders that are correct. A random number is generated during the rating - if it is above the `order_correctness` value, a penalty is subtracted from the rating.

### Weights
- `time_exceeding` (float): Weight for the time exceedance penalty during the rating.
- `order_error` (float): Weight for the order error penalty during the rating.
- `rating_profit` (float): Weight for the expected profit (basically the customer's bill) in the sort function for the service agent seat / serve route.
- `rating_time_spent` (float): Weight for the customer's total spent time in the sort function for the service agent seat / serve route.
- `rating_time_left` (float): Weight for the customer's time left (until reaching his personal limit) in the sort function for the service agent seat / serve route.
- `rating_time_food_preparation` (float): Weight for the preparation time for the selected dish in the sort function for the service agent seat / serve route.

### Restaurant
- `grid_width` (int): Width of the grid - amount of table columns.
- `grid_height` (int): Height of the grid - amount of table rows.

### Customers
- `max_new_customer_agents_per_step` (int): Maximum amount of new customer agent to be spawned per time step.
- `max_customers_per_agent` (int): Maximum amount of people per customer agent. Plays a role for the rating and the expected profit.
- `time_min` (int): Minimum time a customer agent can have until they want to leave.
- `time_max` (int): Maximum time a customer agent can have until they want to leave.

### Service
- `service_agents` (int): Amount of service agents available. Not every service agent will work - it's just the amount of possibly available agents.
- `service_agent_capacity` (int): Default service agent capacity (amount of customers a service agent can serve in one step). Is used as a default value for the constructor if no capacity is provided and for the salary calculation.
- `service_agent_capacity_min` (int): Minimum possible capacity a service agent can have (amount of customers a service agent can serve in one step).
- `service_agent_capacity_max` (int): Maximum possible capacity a service agent can have (amount of customers a service agent can serve in one step).
- `service_agent_salary_per_tick` (float): Salary a service agent with the default `service_agent_capacity` will earn per time step. The salary is proportional to the service agent's personal capacity.
- `route_algorithm` (string): The algorithm to use for the serve route of the customer. Possible values are `ACO` and `WEIGHTED_SORT`.

### Research
- `llm_model` (string): The LLM model installed locally on the PC via ollama.

### Run
- `step_amount` (int): The amount of steps to run in the simulation. Can be overwritten with `endless_mode` parameter.
- `endless_mode` (bool): If set to `true`, it will overwrite the `step_amount` parameter and rund endlessly.
- `full_day_cycle_period` (int): The amount of steps that equal to a full day. 
  - After 1 day, the optimizer will re-calculate the shift plan for the next day.
  - After 1 day, the research agent will create a report.
  - After 5 days, the employee pool is recycled.
  - The LSTM model does a forecast of the customers for the time span of 1 day.
  - The customer spawn function is using the period for creating a periodical spawn rate through the day.
- `window_size` (int): The window size used in the LSTM model. Recommended value: `Recommended value:`$-1$.
- `retrain_interval` (int): The time after which the LSTM should be retrained with new data. Recommended value: `full_day_cycle_period`
- `pretrain_epochs` (int): Number of epochs to use to train the LSTM before having real data with a provided csv file of historical data.
- `use_heuristic_for_first_step_prediction` (bool): Use a heuristic for the first prediction of customers (based on 80% of the grid size). Is useful since we don't have good data yet before the first run.
- `overwrite_lstm_training_dataset` (bool): Save the data created during the simulation run to a file for pre-training the LSTM the next time with that data.
- `reject_unservable_customers` (bool): Reject customers that can't be served (dish preparation time $+$ dish eating time $>$ customer's available time).
- `clear_old_logs` (bool): Remove old log files and reports before starting a new run.
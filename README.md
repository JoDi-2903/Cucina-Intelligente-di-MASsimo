# Cucina intelligente di MASsimo

## Introduction

This program simulates a restaurant with a focus on optimizing shift planning, balancing workload distribution during
shifts, and interpreting restaurant statistics. By utilizing mathematical optimization, heuristics, and machine learning
techniques, the program ensures efficient staffing and maximizes profitability through optimal coordination of
personnel.

<br>

## Requirements

### Python Version

This software requires **Python 3.12**. Newer versions are not supported because TensorFlow is used for an LSTM model
that predicts the increasing number of customers in future iterations. LSTM (Long Short-Term Memory) is a type of
recurrent neural network (RNN) designed for processing sequential data and capturing long-term dependencies, making it
effective for time-series forecasting. Currently, **TensorFlow only works with Python 3.12**, and using a different
version may cause compatibility issues or unexpected behavior.

Ensure that the Python installation is exactly **3.12.x** before proceeding.

### Dependencies

To install all required Python packages, use the requirements.txt file with the following commands:

```bash
pip cache purge
pip install -r requirements.txt
pip install acopy==0.7.0 --no-deps
```

The pip cache will be purged to avoid any issues with the installation of the packages.

The package `acopy` must be installed separately without its nested dependencies. This is necessary to prevent the
`click` package from being installed in a version that is incompatible with `dash`. The `dash` package requires a newer
version of `click`, and since no functionality from `acopy` that depends on `click` is used, `acopy` can be safely
installed without dependencies.

### LSTM Model for Customer Flow Prediction

The restaurant simulation employs a Long Short-Term Memory (LSTM) neural network to forecast customer counts and
satisfaction ratings across future timesteps. This recurrent neural network architecture excels at capturing temporal
dependencies in sequential data, making it ideal for time-series prediction tasks. The implemented `LSTMModel` class
features a dual-layer architecture (64 and 32 units respectively) with dropout regularization to prevent overfitting.
Input data undergoes normalization to the [0,1] range, improving training stability and convergence. The model supports
both pretraining from historical data and online learning through incremental updates at configurable intervals,
allowing it to continuously adapt to emerging patterns in customer behavior. Predictions are generated using a sliding
window approach where each forecast is fed back into the input sequence to predict further timesteps. This predictive
capability enables the manager agent to anticipate customer influx and optimize staffing and resource allocation
proactively.

### Ollama and LLM

The software includes functionality to generate reports based on statistical calculations for the restaurant. To enable
this feature, **Ollama must be installed**.

Ollama is a local inference engine for running large language models (LLMs) efficiently on personal machines. It
provides a streamlined interface for interacting with AI models, allowing applications to process natural language
queries and generate text-based outputs. By integrating Ollama, the software can leverage AI-generated insights to
create detailed, data-driven reports.

If Ollama is not installed, the LLM-based reporting feature will be disabled during program execution. Other
functionalities of the software will continue to work, but automatic report generation using the LLM will not be
available.

Ensure Ollama is installed before running the software if this feature is required. More information and installation
instructions can be found on the official [Ollama website](https://ollama.com).

<br>

## Parameters in `data/config.json`

### Rating

- `rating_default` (int): Default rating value for new customers that have not finished eating (and provided a real
  rating) yet.
- `rating_min` (int): Minimal possible rating value.
- `rating_max` (int): Maximal possible rating value.
- `rating_strategy`(string): The strategy to use for the calculation of the rating. Possible values are `MAX` and `RANDOM`.
  - `MAX`: Take the maximal **possible rating value** and subtract the penalties and variability.
  - `RANDOM`: Take a **random rating value** and subtract the penalties and variability.

### Orders

- `order_correctness` (float): Percentage of orders that are correct. A random number is generated during the rating -
  if it is above the `order_correctness` value, a penalty is subtracted from the rating.

### Weights

- `time_exceeding` (float): Weight for the time exceedance penalty during the rating.
- `order_error` (float): Weight for the order error penalty during the rating.
- `rating_profit` (float): Weight for the expected profit (basically the customer's bill) in the sort function for the
  service agent seat / serve route.
- `rating_time_spent` (float): Weight for the customer's total spent time in the sort function for the service agent
  seat / serve route.
- `rating_time_left` (float): Weight for the customer's time left (until reaching his personal limit) in the sort
  function for the service agent seat / serve route.
- `rating_time_food_preparation` (float): Weight for the preparation time for the selected dish in the sort function for
  the service agent seat / serve route.

### Restaurant

- `grid_width` (int): Width of the grid - amount of table columns.
- `grid_height` (int): Height of the grid - amount of table rows.

### Customers

- `max_new_customer_agents_per_step` (int): Maximum amount of new customer agent to be spawned per time step.
- `max_customers_per_agent` (int): Maximum amount of people per customer agent. Plays a role for the rating and the
  expected profit.
- `time_min` (int): Minimum time a customer agent can have until they want to leave.
- `time_max` (int): Maximum time a customer agent can have until they want to leave.

### Service

- `service_agents` (int): Amount of service agents available. Not every service agent will work - it's just the amount
  of possibly available agents.
- `service_agent_capacity` (int): Default service agent capacity (amount of customers a service agent can serve in one
  step). Is used as a default value for the constructor if no capacity is provided and for the salary calculation.
- `service_agent_capacity_min` (int): Minimum possible capacity a service agent can have (amount of customers a service
  agent can serve in one step).
- `service_agent_capacity_max` (int): Maximum possible capacity a service agent can have (amount of customers a service
  agent can serve in one step).
- `service_agent_salary_per_tick` (float): Salary a service agent with the default `service_agent_capacity` will earn
  per time step. The salary is proportional to the service agent's personal capacity.
- `route_algorithm` (string): The algorithm to use for the serve route of the customer. Possible values are `ACO` and
  `WEIGHTED_SORT`.

> #### Note:
>
>The **constraints** of the `pyoptinterface` optimizer require that enough service agents are employed to serve the
> maximum number of guests in each iteration. To calculate the number of service agents, here is an example:
>
>**Given**:
>
>- 90 guests can be in the restaurant at the same time. (e.g.: 9x10 grid)
>- 1 waiter can serve at least 5 guests at the same time. (`service_agent_capacity_min`)
>- Open 24 hours (i.e. 144 time units of 10 minutes each).
>- A waiter may work a maximum of 8 hours = 48 time units of 10 minutes each per day.
>
>**Step 1: How many waiters are required per 10-minute interval?**
>
>- 90 guests ÷ 5 guests/waiter = **18 waiters at the same time**.
>
>This means that **18 waiters are needed at the same time** in each 10-minute block.
>
>**Step 2: How many waiter units are required per day?**
>
>- There are 144 time steps (10 minutes each) per day:
   >
- 144 time steps × 18 waiters = **2,592 waiter time units**.
>
>**Step 3: A waiter can work 48 time units (8 hours) per day**.
>
>- 2,592 waiter time units ÷ 48 units/waiter = **54 waiters**.
>
>There should be set minimum **54 waiters** (`service_agents`) in order to fulfill the constraints of the
> `pyoptinterface`.

### Research

- `llm_model` (string): The LLM model installed locally on the PC via ollama.

### Run

- `step_amount` (int): The amount of steps to run in the simulation. Can be overridden with the `endless_mode`
  parameter.
- `endless_mode` (bool): If set to `true`, it will overwrite the `step_amount` parameter and rund endlessly.
- `full_day_cycle_period` (int): The amount of steps that equal to a full day.
    - After 1 day, the optimizer will re-calculate the shift plan for the next day.
    - After 1 day, the research agent will create a report.
    - After 5 days, the employee pool is recycled.
    - The LSTM model does a forecast of the customers for the time span of 1 day.
    - The customer spawn function is using the period for creating a periodical spawn rate through the day.
- `window_size` (int): The window size used in the LSTM model. <br>_Recommended value:_ `full_day_cycle_period`$-1$
- `retrain_interval` (int): The time after which the LSTM should be retrained with new data.<br>_Recommended value:_
  `full_day_cycle_period`
- `pretrain_epochs` (int): Number of epochs to use to train the LSTM with a provided csv file of historical data (*
  *pretraining**), before having data of the current simulation (**online learning**).
- `use_heuristic_for_first_step_prediction` (bool): Use a heuristic for the first prediction of customers (based on 80%
  of the grid size). Is useful since we don't have good data yet before the first run and could only rely on synthetic
  input data with average values. Although this second approach (`use_heuristic_for_first_step_prediction` = `False`)
  provides a good approximation for the first `full_day_cycle_period` steps, it substantially reduces the prediction
  quality of all further predictions due to the constant synthetic data in the history.
- `overwrite_lstm_training_dataset` (bool): Save the data created during the simulation run to a csv file for
  pre-training the LSTM the next time the simulation is started. This overwrites the existing file.
- `reject_unservable_customers` (bool): Reject customers that can't be served (dish preparation time $+$ dish eating
  time $>$ customer's available time).
- `clear_old_logs` (bool): Remove old log files and reports before starting a new run.

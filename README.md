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

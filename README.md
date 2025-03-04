# Cucina intelligente di MASsimo
## Requirements
Make sure you have **Python 3.11** installed.

Install the required packages with the following commands:
```bash
pip cache purge
pip install -r requirements.txt
pip install acopy==0.7.0 --no-deps
```
The pip cache will be purged to avoid any issues with the installation of the packages.

The package `acopy` has to be installed without dependencies because otherwise it will install an older version of `click`
which is not compatible with the latest version of `dash`. Since there is no problem in using the latest version of `click`,
we can safely install `acopy` without dependencies.

## Hugging Face and LLM
The research agent uses a pre-trained GPT-2 large language model to interpret the statistics of the restaurant.
The LLM will be handled using the `transformers` library from **Hugging Face**, which provides an efficient interface for loading and interacting with the model.
The model itself will be downloaded from Hugging Face, **requiring a Hugging Face access token**.
To use this setup, you must provide a Hugging Face access token in the `config.json` file. To create an access token:

- Sign up or log in to your account on the Hugging Face website.
- Navigate to the `Access Tokens` section in your profile.
- Generate a new token with read access.

This token will be used to authenticate and download the required model from Hugging Face.
# Cucina intelligente di MASsimo
# Requirements
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
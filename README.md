# PWP SUMMER 2020
# Climbing route tracker and training planner
# Group information
* Student 1. Jarkko Laine, jarkko.laine@kapsi.fi

With one final deadline, and single meeting in August.


## How to setup environment

### Python virtual environment

For example for python 3:

python3 -m venv PWP-Summer2020-JL

Then activate the environment

source path-to-PWP-Summer2020-JL/bin/activate

### Setup environment variables

export FLASK_ENV=DEVELOPMENT

### Python version and dependencies

Project has been coded using Python version 3.8.2, which necessitated changing some of the course requirements to newer versions (namely werkzeug from 0.15.1 to 0.15.5). Install the required packages with:

pip3 install -r requirements.txt

For testing pytest is used, and can be installed with the commands:

pip3 install pytest
pip3 install pytest-cov

## Initialize and populate the database in terminal with the command:

./init_db.sh

## How to run tests

### To test the database construction run the following command in src folder:
pytest test_db.py

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

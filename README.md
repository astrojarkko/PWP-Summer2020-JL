# PWP SUMMER 2020: Climbing route tracker (and training planner)

## Group information

* Student 1. Jarkko Laine, jarkko.laine@kapsi.fi

With one final deadline, and single meeting in August.

## Setup project and database

Note: all the instructions below assume you are using Linux, in which the project
has been constructed in.

### Clone the project

    git clone https://github.com/astrojarkko/PWP-Summer2020-JL.git

### Python virtual environment

Use the command below in a terminal to create virtual environment:

    python -m venv PWP-Summer2020-JL

Then activate it:

    source path-to-PWP-Summer2020-JL/bin/activate

### Python version and dependencies

Project has been coded with Python version 3.8.2, which necessitated changing some of the packages to newer versions
than what used during the course otherwise (namely werkzeug from 0.15.1 to 0.15.5). Install the required packages with:

    pip install -r requirements.txt

And to install the project run the following command in the project main folder:

    pip install -e .

### Environment variables

Again in a terminal:

    export FLASK_APP=routetracker
    export FLASK_ENV=DEVELOPMENT

Or use the script:

    source dev_env.sh

### Initializing database and running API

Next initialize the database and populate it:

    flask init-db
    flask testgen

After this the API can be run with the command:

    flask run

## Accessing API with client

After flask server is running, the API client can be accessed by pointing your favourite web browser to the address:

    http://localhost:5000/login/

The API client is rather rudimentary, but shows functionality of all the main features of the API. Follow the instructions on screen.
The API client has pretty much same interface and code design as in the example client given in the course exercise 4.

## Running tests

For testing pytest is used, and can be installed to the virtual environment with the commands:

    pip install pytest
    pip install pytest-cov

The tests can then be run with:

    pytest -W ignore::DeprecationWarning

Or with coverage information:

    pytest --cov-report term-missing --cov=routetracker -W ignore::DeprecationWarning

The option "-W ignore::DeprecationWarning" is added to ignore the literal thousands of deprecation warnings,
which are raised by the (old) libraries used in the course with Python version 3.8.


## Sources used

Much of the code is based on, or at the very least heavily motivated by, the examples given in the
[course material](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-summer-2020/), and the
[sensorhub example API](https://github.com/enkwolf/pwp-course-sensorhub-api-example).

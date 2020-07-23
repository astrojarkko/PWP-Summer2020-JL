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

    export FLASK_APP=routetracker
    export FLASK_ENV=DEVELOPMENT

Or use the script:

    source dev_env.sh

### Python version and dependencies

Project has been coded using Python version 3.8.2, which necessitated changing some of the course requirements to newer versions (namely werkzeug from 0.15.1 to 0.15.5). Install the required packages with:

    pip3 install -r requirements.txt

To install the project run the following command in the project main folder:

    pip3 install -e .

Next initialize the database and populate it:

    flask init-db
    flask testgen

For testing pytest is used, and can be installed with the commands:

    pip3 install pytest
    pip3 install pytest-cov

Run the test with:

    pytest

Or with coverage information:

    TODO


## Sources used

Much of the code is based or motivated by the examples given in the [course material](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-summer-2020/), and
the [sensorhub example API](https://github.com/enkwolf/pwp-course-sensorhub-api-example).

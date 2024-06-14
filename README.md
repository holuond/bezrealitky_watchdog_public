# Bezrealitky Watchdog 🐶
This repository contains a custom watchdog for the Czech real estate marketplace [Bezrealitky.cz](https://www.bezrealitky.cz). 

The watchdog is a simple Python script that tracks relevant offers based on a customizable filter and sends an email notification whenever it encounters any previously unseen offer. The script can be run locally or deployed to Heroku or a similar service. S3 is used for state management (tracking of already seen offers) and SendGrid is used for sending e-mails.

To configure, set up the `.env` file according to `.env_template`. You might also want to adjust the queries and parameters in `graphql_queries.py` and the polygonal location filter in `watchdog.py`.

# Get Started
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m bezrealitky_watchdog
```
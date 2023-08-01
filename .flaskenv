# Public .env file used by the flask command
# Use only during development!
# To override values in here locally use a private .env file
FLASK_APP=qunicorn_core # rename this if you rename the package!
# FLASK_ENV=development # set to production if in production!
FLASK_DEBUG=True # set to False if in production!


# configure default port
FLASK_RUN_PORT=5005
EXECUTE_CELERY_TASK_ASYNCHRONOUS=True

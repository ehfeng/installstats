To run web server:

`FLASK_APP=app.py flask run`

To run celery worker with beat:

`celery -A app.celery worker -B`
To run web server:

`source .env flask run`

To run celery worker with beat:

`celery -A app.celery worker -B`

# TODOs

Cache, with invalidation after base stats are pulled.
release: ./boot.sh
web: gunicorn foxfire:app
worker: rq worker foxfire-tasks

import os
import redis

from rq import Connection
from rq import Queue
from rq import Worker


redis_url = os.getenv('REDIS_URL')
if not redis_url:
    raise RuntimeError('Set up Redis first.')

conn = redis.from_url(redis_url)


if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(Queue('foxfire-tasks'))
        worker.work()

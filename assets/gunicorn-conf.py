import os

bind = os.getenv('GUNICORN_BIND', '0.0.0.0:16824')
reuse_port = True

workers = 2

worker_class = 'uvicorn.workers.UvicornWorker'

keepalive = 30

accesslog = '-'

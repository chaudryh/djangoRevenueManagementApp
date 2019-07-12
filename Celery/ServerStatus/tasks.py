from bowlero_backend.celery import app
from Celery.ServerStatus.ServerStatus import ServerStatus


@app.task
def serverStatus():
    ServerStatus.serverStatus()

    return

from config.celery import app
from celery.schedules import crontab
from celery.task import periodic_task
from config.log import logger


@app.task()
def main_publisher():
    # pub sub celery. scenario : pub and all sub is one code, sharing same redis db for queue
    # the publisher and consumer tasks
    for x in range(0, 100000):
        add_together.delay(x, 2)


@app.task()
def add_together(a, b):
    # pub sub celery. scenario : pub and all sub is one code, sharing same redis db for queue
    # the consumer tasks
    logger.info("{} + {} = {}".format(a, b, a+b))
    return a + b


@periodic_task(
    run_every=(crontab(hour='*/1', minute=0)),
    name="grab_adapter.tasks.status_update",
    ignore_result=True
)
def status_update():
    pass

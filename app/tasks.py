from config.celery import app
from celery.schedules import crontab
from celery.task import periodic_task
from config.log import logger


@periodic_task(
    run_every=(crontab(hour='*/1', minute=0)),
    name="grab_adapter.tasks.status_update",
    ignore_result=True
)
def status_update():
    pass


@app.task(
    name="pub_sub_add"
)
def add(*args, **kwargs):
    logger.info("[consumer 1] {}".format(args[0]))
    return args[0]


@app.task(
    name="pub_sub_main"
)
def main_publisher_distributed():
    for x in range(0, 100000):
        res = add.delay(x)
        logger.info("[publisher 1] {}".format(x))

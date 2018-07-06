from config.celery import app
from celery.schedules import crontab
from celery.task import periodic_task
from config.log import logger
import random


@periodic_task(
    run_every=(crontab(hour='*/1', minute=0)),
    name="grab_adapter.tasks.status_update",
    ignore_result=True
)
def status_update():
    pass


@app.task(
    name="pub_sub_add_main"
)
def add(*args, **kwargs):
    n_data = []
    logger.info("[consumer 1] Generate data training list ke : {}".format(args[0]))
    for n in range(10):
        n_data.append(random.randint(1, 101))
    return n_data


@app.task(
    name="pub_sub_main"
)
def main_publisher_distributed():
    n_data = []
    for x in range(0, 10):
        res = add.delay(x)
        n_data.append(res)
        # logger.info("[publisher 1] {}".format(x))

    logger.info("[publisher 1] Result data : {} ".format(n_data))

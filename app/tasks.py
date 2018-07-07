from config.celery import app
from celery.schedules import crontab
from celery.task import periodic_task
from config.log import logger
from celery.result import allow_join_result
import random


@periodic_task(
    run_every=(crontab(hour='*/1', minute=0)),
    name="grab_adapter.tasks.status_update",
    ignore_result=True
)
def status_update():
    pass


@app.task(
    name="pub_sub_add_main",
    trail=True
)
def add(*args, **kwargs):
    n_data = []
    for n in range(10):
        n_data.append(random.randint(1, 101))

    logger.info("Loop ke : {}. {}".format(args[0], n_data))
    return n_data


@app.task(
    name="pub_sub_main",
    trail=True
)
def main_publisher_distributed():
    n_data = []
    for x in range(0, 100000):
        res = add.delay(x)
        with allow_join_result():
            n_data.append(res.get())

    logger.info("Result data : {} ".format(n_data))

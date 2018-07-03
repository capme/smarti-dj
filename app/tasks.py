from config.celery import app
from celery.schedules import crontab
from celery.task import periodic_task
from config.log import logger
import celery_pubsub


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


@app.task(
    name="pub_sub_add"
)
def add(*args, **kwargs):
    logger.info("[consumer 1] {}".format(args[0]))
    return args[0]


# celery_pubsub.subscribe('some.topic', add)


@app.task(
    name="pub_sub_main"
)
def main_publisher_distributed():
    for x in range(0, 100000):
        # res = celery_pubsub.publish('some.topic', x)
        res = add.delay(x)
        logger.info("[publisher 1] {}".format(x))
        # not working
        # res = celery_pubsub.publish('some.topic', x)
        # logger.info("[publisher] {}".format(res))

from celery.schedules import crontab
from celery.task import periodic_task


@periodic_task(
    run_every=(
        crontab(dict(hour='*/1', minute='*/10'))
    ),
    name="app.tasks.task1",
    ignore_result=True
)
def task1():
    pass


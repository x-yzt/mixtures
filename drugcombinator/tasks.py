from datetime import datetime, timedelta
from urllib.request import HTTPError

from django.apps import apps
from huey.contrib.djhuey import db_task, task

from drugcombinator.business.wayback import WaybackClient, to_datetime


class TaskScheduler:
    def __init__(self, task, cooldown=timedelta(minutes=1)):
        self.task = task
        self.cooldown = cooldown
        self.eta = datetime(1, 1, 1)

    def __call__(self, *args, **kwargs):
        self.eta = max(self.eta + self.cooldown, datetime.now())

        self.task.schedule(args, kwargs, self.eta)


@db_task(retries=5, retry_delay=1, expires=3600)
def get_snapshot(id, uri):
    """Update the snapshot status of a given uri of the model instance
    of given ID."""

    interaction = (
        apps.get_model('drugcombinator.interaction')
        .objects.get(id=id)
    )

    # Ensure the URI is still present in the model instance at the time
    # the task actually runs
    if uri not in interaction.uris:
        return

    meta = interaction.uris[uri]

    snapshot = WaybackClient().get_last_snapshot(uri)

    if snapshot:
        interaction.uris[uri] = {
            'status': 'ARCHIVED',
            'url': snapshot['url'],
            'date': to_datetime(snapshot['timestamp']).timestamp()
        }
        interaction.save(process_uris=False)

    elif meta is None or meta.get('status', None) != 'REQUESTED':
        schedule_capture(id, uri)


@db_task(retries=2, retry_delay=20, expires=3600)
def capture(id, uri):
    """Make a capture request for a given uri of the model instance of
    given ID."""

    interaction = (
        apps.get_model('drugcombinator.interaction')
        .objects.get(id=id)
    )

    # Ensure the URI is still present in the model instance at the time
    # the task actually runs
    if uri not in interaction.uris:
        return

    try:
        request = WaybackClient().capture(uri)

        interaction.uris[uri] = {
            'status': 'REQUESTED',
            'job': request['job_id'],
            'date': datetime.now().timestamp()
        }

    except HTTPError:
        interaction.uris[uri] = {
            'status': 'FAILED',
            'date': datetime.now().timestamp()
        }

    interaction.save(process_uris=False)


@task()
def ping_webarchive(id, uris):
    for uri, meta in uris.items():
        if meta is None or meta['status'] != 'ARCHIVED':
            schedule_get_snapshot(id, uri)


schedule_get_snapshot = TaskScheduler(get_snapshot, timedelta(seconds=1))

schedule_capture = TaskScheduler(capture, timedelta(seconds=20))

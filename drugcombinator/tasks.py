from datetime import datetime, timedelta
from urllib.request import HTTPError

from django.apps import apps
from huey.contrib.djhuey import db_task, task

from drugcombinator.business.wayback import WaybackClient, to_datetime


class TaskScheduler:
    def __init__(self, task, cooldown=timedelta(minutes=1)):
        self.task = task
        self.cooldown = cooldown
        self.run_at = datetime.min

    def __call__(self, *args, **kwargs):
        self.run_at = max(self.run_at + self.cooldown, datetime.now())

        self.task.schedule(args, kwargs, self.run_at)


@db_task(retries=5, retry_delay=1, expires=3600)
def get_snapshot(interaction_id, uri):
    """Update the snapshot status of a given uri for the model instance
    of given ID.

    If a snapshot does not exist, a subsequent query is scheduled to
    make one."""
    interaction = (
        apps.get_model('drugcombinator.interaction')
        .objects.get(id=interaction_id)
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

    elif meta is None or meta['status'] != 'REQUESTED':
        schedule_capture(interaction_id, uri)


@db_task(retries=2, retry_delay=20, expires=3600)
def capture(interaction_id, uri):
    """Make a capture request for a given uri of the model instance of
    given ID."""
    interaction = (
        apps.get_model('drugcombinator.interaction')
        .objects.get(id=interaction_id)
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
def ping_webarchive(interaction_id, uris):
    """Schedule a refresh query for every URI of a given interaction if
    needed."""
    for uri, meta in uris.items():
        if meta is None or meta['status'] != 'ARCHIVED':
            schedule_get_snapshot(interaction_id, uri)


schedule_get_snapshot = TaskScheduler(get_snapshot, timedelta(seconds=1))

schedule_capture = TaskScheduler(capture, timedelta(seconds=20))

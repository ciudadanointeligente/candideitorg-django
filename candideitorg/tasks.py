from celery import task

@task()
def election_updater(election):
    election.update()
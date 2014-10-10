from celery import task

@task()
def election_updater(election):
    election.update()


@task()
def candidate_updater(candidate):
    candidate.update()
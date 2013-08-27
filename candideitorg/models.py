import slumber
from django.db import models
from candideitorg.apikey_auth import ApiKeyAuth
from slumber import url_join, Resource

# Create your models here.
class CandideitorgDocument(models.Model):
    remote_id = models.IntegerField()
    resource_uri = models.CharField(max_length=255)

    class Meta:
	   abstract = True

class Election(CandideitorgDocument):
    information_source = models.TextField()
    description = models.TextField()
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    use_default_media_naranja_option = models.BooleanField()
    slug = models.SlugField(max_length=255)

    @classmethod
    def fetch_all_from_api(cls):
        api = slumber.API("http://127.0.0.1:8000/api/v2/", auth=ApiKeyAuth("admin", "a"))
        elections_from_api = api.election.get()
        for election_dict in elections_from_api["objects"]:
            election = Election.objects.create(
                name=election_dict["name"],
                remote_id=election_dict["id"],
                description=election_dict["description"],
                logo=election_dict["logo"],
                resource_uri=election_dict["resource_uri"],
                slug=election_dict["slug"],
                use_default_media_naranja_option=election_dict["use_default_media_naranja_option"],
                )
            for category_uri in election_dict['categories']:
                kwargs = {}
                for key, value in api._store.iteritems():
                    kwargs[key] = value
                kwargs.update({"base_url": url_join(api._store["base_url"], category_uri)})
                resource = Resource(**kwargs)
                category_dict = resource.get()
                Category.objects.create(
                    name=category_dict['name'],
                    order=category_dict['order'],
                    resource_uri=category_dict['resource_uri'],
                    slug=category_dict['slug'],
                    remote_id=category_dict['id'],
                    election=election
                )
            for candidate_uri in election_dict['candidates']:
                kwargs = {}
                for key, value in api._store.iteritems():
                    kwargs[key] = value
                kwargs.update({"base_url": url_join(api._store["base_url"], candidate_uri)})
                resource = Resource(**kwargs)
                candidate_dict = resource.get()
                Candidate.objects.create(
                    name=candidate_dict['name'],
                    election=election,
                    slug=candidate_dict['slug'],
                    remote_id=candidate_dict['id'],
                    photo=candidate_dict['photo'],
                )
            for background_candidate_uri in election_dict['background_categories']:
                kwargs = {}
                for key, value in api._store.iteritems():
                    kwargs[key] = value
                kwargs.update({"base_url": url_join(api._store["base_url"], background_candidate_uri)})
                resource = Resource(**kwargs)
                background_candidate_dict = resource.get()
                BackgroundCategory.objects.create(
                    name=background_candidate_dict['name'],
                    election=election,
                    remote_id=background_candidate_dict['id']
                    )
            for personal_data_uri in election_dict['personal_data']:
                kwargs = {}
                for key, value in api._store.iteritems():
                    kwargs[key] = value
                kwargs.update({"base_url": url_join(api._store['base_url'], personal_data_uri)})
                resource = Resource(**kwargs)
                personal_data_dict = resource.get()
                PersonalData.objects.create(
                    label=personal_data_dict['label'],
                    remote_id = personal_data_dict['id'],
                    election = election
                    )


class Category(CandideitorgDocument):
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    election = models.ForeignKey(Election)
    slug = models.SlugField(max_length=255)

class Candidate(CandideitorgDocument):
    photo = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    has_answered = models.BooleanField()
    election = models.ForeignKey(Election)

class BackgroundCategory(CandideitorgDocument):
    election = models.ForeignKey(Election)
    name = models.CharField(max_length=255)

class PersonalData(CandideitorgDocument):
    label = models.CharField(max_length=255)
    election = models.ForeignKey(Election)
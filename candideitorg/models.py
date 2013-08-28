import slumber
from django.db import models
from candideitorg.apikey_auth import ApiKeyAuth
from slumber import url_join, Resource

# Create your models here.
class CandideitorgDocument(models.Model):
    remote_id = models.IntegerField()
    resource_uri = models.CharField(max_length=255)

    @classmethod
    def get_api(cls):
        api = slumber.API("http://127.0.0.1:8000/api/v2/", auth=ApiKeyAuth("admin", "a"))
        return api

    class Meta:
	   abstract = True

    @classmethod
    def get_resource_as_dict(cls, uri):
        kwargs = {}
        api = CandideitorgDocument.get_api()
        for key, value in api._store.iteritems():
            kwargs[key] = value
        kwargs.update({"base_url": url_join(api._store["base_url"], uri)})
        resource = Resource(**kwargs)
        dicti = resource.get()
        return dicti

    @classmethod
    def create_new_from_dict(cls, dicti, **kwargs):
        field_names = []

        for field in  iter(cls._meta.fields):
            field_names.append(field.name)

        new_element = {}
        for key in dicti.keys():
            if not isinstance(dicti[key], (list, tuple)):
                if key in field_names and key != "id":
                    new_element[key]= dicti[key]
        new_element["remote_id"] = dicti["id"]
        new_element.update(kwargs)
        return cls.objects.create(**new_element)



class Election(CandideitorgDocument):
    information_source = models.TextField()
    description = models.TextField()
    name = models.CharField(max_length=255)
    logo = models.CharField(max_length=255)
    use_default_media_naranja_option = models.BooleanField()
    slug = models.SlugField(max_length=255)

    @classmethod
    def fetch_all_from_api(cls):
        api = cls.get_api()
        elections_from_api = api.election.get()
        for election_dict in elections_from_api["objects"]:
            election = Election.create_new_from_dict(election_dict)
            for uri in election_dict['categories']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                Category.create_new_from_dict(dictionary, election=election)
            for uri in election_dict['candidates']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                Candidate.create_new_from_dict(dictionary, election=election)
            for uri in election_dict['background_categories']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                backgroundcategory = BackgroundCategory.create_new_from_dict(dictionary, election=election)
                for uri in dictionary['background']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    Background.create_new_from_dict(dictionary, background_category=backgroundcategory)
            for uri in election_dict['personal_data']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                PersonalData.create_new_from_dict(dictionary, election=election)


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

class Background(CandideitorgDocument):
    name = models.CharField(max_length=255)
    background_category = models.ForeignKey(BackgroundCategory)
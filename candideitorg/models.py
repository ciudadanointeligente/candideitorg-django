import slumber
from django.db import models
from candideitorg.apikey_auth import ApiKeyAuth

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
            Election.objects.create(
                name=election_dict["name"],
                remote_id=election_dict["id"],
                description=election_dict["description"],
                logo=election_dict["logo"],
                resource_uri=election_dict["resource_uri"],
                slug=election_dict["slug"],
                use_default_media_naranja_option=election_dict["use_default_media_naranja_option"],
                )

class Category(object):
    pass
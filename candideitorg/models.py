from django.db import models

# Create your models here.
class CandideitorgDocument(models.Model):
    remote_id = models.IntegerField()
    resource_uri = models.CharField(max_length=255)

    class Meta:
	   abstract = True

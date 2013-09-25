import slumber
import re
from django.db import models
from candideitorg.apikey_auth import ApiKeyAuth
from slumber import url_join, Resource
from django.conf import settings
import django.dispatch


twitter_regexp = re.compile(r"^https?://[^/]*(t\.co|twitter\.com)(/.*|/?)")
facebook_regexp = re.compile(r"^https?://[^/]*(facebook\.com|fb\.com|fb\.me)(/.*|/?)")


election_finished = django.dispatch.Signal(providing_args=[])

# Create your models here.
class CandideitorgDocument(models.Model):
    remote_id = models.IntegerField()
    resource_uri = models.CharField(max_length=255)

    @classmethod
    def get_api(cls):
        api = slumber.API(settings.CANDIDEITORG_URL, auth=ApiKeyAuth(settings.CANDIDEITORG_USERNAME, settings.CANDIDEITORG_API_KEY))
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
            for uri in election_dict['personal_data']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                PersonalData.create_new_from_dict(dictionary, election=election)
            for uri in election_dict['background_categories']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                backgroundcategory = BackgroundCategory.create_new_from_dict(dictionary, election=election)
                for uri in dictionary['background']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    Background.create_new_from_dict(dictionary, background_category=backgroundcategory)
            for uri in election_dict['candidates']:
                candidate_dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                candidate = Candidate.create_new_from_dict(candidate_dictionary, election=election)
                for uri in candidate_dictionary['personal_data_candidate']:
                    pdc_dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    personal_data = PersonalData.objects.get(resource_uri=pdc_dictionary["personal_data"])
                    PersonalDataCandidate.create_new_from_dict(pdc_dictionary, 
                        candidate=candidate, 
                        personaldata=personal_data)
                for uri in candidate_dictionary['links']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    Link.create_new_from_dict(dictionary, candidate=candidate)

                for uri in candidate_dictionary['backgrounds_candidate']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    background = Background.objects.get(resource_uri=dictionary["background"])
                    BackgroundCandidate.create_new_from_dict(dictionary, 
                        candidate=candidate, 
                        background=background)
            for uri in election_dict['categories']:
                dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                category = Category.create_new_from_dict(dictionary, election=election)
                for uri in dictionary['questions']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    question = Question.create_new_from_dict(dictionary, category=category)
                    for uri in dictionary['answers']:
                        dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                        answer = Answer.create_new_from_dict(dictionary,question=question)
                        for candidate_uri in dictionary["candidates"]:
                            candidate = Candidate.objects.get(resource_uri=candidate_uri)
                            candidate.answers.add(answer)
                            candidate.save()

            election_finished.send(sender=election)


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
    answers = models.ManyToManyField('Answer')

class BackgroundCategory(CandideitorgDocument):
    election = models.ForeignKey(Election)
    name = models.CharField(max_length=255)

class PersonalData(CandideitorgDocument):
    label = models.CharField(max_length=255)
    election = models.ForeignKey(Election)

class Background(CandideitorgDocument):
    name = models.CharField(max_length=255)
    background_category = models.ForeignKey(BackgroundCategory)

class Answer(CandideitorgDocument):
    caption = models.CharField(max_length=255)
    question = models.ForeignKey('Question')
    # candidate = models.ForeignKey(Candidate)

class Question(CandideitorgDocument):
    question = models.CharField(max_length=255)
    category = models.ForeignKey(Category)

class PersonalDataCandidate(CandideitorgDocument):
    value = models.CharField(max_length=255)
    candidate = models.ForeignKey(Candidate)
    personaldata = models.ForeignKey(PersonalData)

class Link(CandideitorgDocument):
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    candidate = models.ForeignKey(Candidate)

    @property
    def icon_class(self):
        if twitter_regexp.match(self.url):
            return "icon-twitter-sign"
        elif facebook_regexp.match(self.url):
            return "icon-facebook-sign"
        else:
            return "icon-globe"


class BackgroundCandidate(CandideitorgDocument):
    value = models.CharField(max_length=255)
    candidate = models.ForeignKey(Candidate)
    background = models.ForeignKey(Background)

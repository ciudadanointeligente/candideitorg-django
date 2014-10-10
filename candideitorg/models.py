import slumber
import re
from django.db import models
from candideitorg.apikey_auth import ApiKeyAuth
from slumber import url_join, Resource
from django.conf import settings
import django.dispatch
from django.utils.translation import ugettext as _


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
        return cls.get_or_create(dicti, new_element)

    @classmethod
    def get_or_create(cls, dictified_element, new_element):
        existing_objects = cls.objects.filter(remote_id=dictified_element["id"]).count()
        if existing_objects > 0:
            return cls.objects.get(remote_id=dictified_element["id"])
        else:
            return cls.objects.create(**new_element)




class Election(CandideitorgDocument):
    information_source = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    logo = models.CharField(max_length=255, null=True, blank=True)
    use_default_media_naranja_option = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_or_create(cls, dictified_element, new_element):
        existing_objects = cls.objects.filter(remote_id=dictified_element["id"]).count()
        created = True
        if existing_objects > 0:
            election = cls.objects.get(remote_id=dictified_element["id"])
            created = False
        else:
            election = cls.objects.create(**new_element)
        
        return election, created

    def update_answers(self):
        for candidate in self.candidate_set.all():
            candidate_dictionary = CandideitorgDocument.get_resource_as_dict(candidate.resource_uri)
            PersonalDataCandidate.objects.filter(candidate=candidate).delete()
            for uri in candidate_dictionary['personal_data_candidate']:

                pdc_dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                try:
                    personaldata = PersonalData.objects.get(resource_uri=pdc_dictionary["personal_data"])
                    PersonalDataCandidate.create_new_from_dict(pdc_dictionary, 
                                                            candidate=candidate, 
                                                            personaldata=personaldata)
                except:
                    pass




        questions = Question.objects.filter(category__election=self)

        for question in questions:
            question_dictionary = CandideitorgDocument.get_resource_as_dict(question.resource_uri)
            question = Question.objects.get(resource_uri=question_dictionary['resource_uri'])
            for answer_uri in question_dictionary['answers']:
                answer_dictionary = CandideitorgDocument.get_resource_as_dict(answer_uri)

                answer = Answer.create_new_from_dict(answer_dictionary,question=question)


                if answer.candidate_set.all():
                    answer.candidate_set.clear()

                new_candidates = []

                for candidate_uri in answer_dictionary['candidates']:
                    candidate = Candidate.objects.get(resource_uri=candidate_uri)
                    new_candidates.append(candidate)


                answer.candidate_set = new_candidates
            #Getting the information sources
            for information_source_uri in question_dictionary['information_sources']:
                information_dictionary = CandideitorgDocument.get_resource_as_dict(information_source_uri)
                try:
                    information_source = InformationSource.objects.get(resource_uri=information_source_uri)
                    information_source.content = information_dictionary['content']
                    information_source.save()
                except InformationSource.DoesNotExist, error:
                    #I have to create it with something like this 
                    # information_source = InformationSource.create_new_from_dict(dictionary, question=question, candidate=candidate)
                    candidate = Candidate.objects.get(resource_uri=information_dictionary['candidate'])
                    information_source = InformationSource.create_new_from_dict(information_dictionary, question=question, candidate=candidate)






    def cleanup_before_updating(self):
        Question.objects.filter(category__election=self).delete()

    def update(self):
        self.cleanup_before_updating()
        api = self.__class__.get_api()
        election_dict = api.election(self.remote_id).get()
        election, created = Election.create_new_from_dict(election_dict)
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
                #delete previous
                PersonalDataCandidate.objects.filter(candidate=candidate, personaldata=personal_data).delete()
                #delete previous
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

                question_dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                question = Question.create_new_from_dict(question_dictionary, category=category)
                for uri in question_dictionary['answers']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    answer = Answer.create_new_from_dict(dictionary,question=question)
                    answer.candidate_set.clear()
                    for candidate_uri in dictionary["candidates"]:
                        candidate = Candidate.objects.get(resource_uri=candidate_uri)
                        question_of_the_answer = answer.question
                        candidate.answers.add(answer)
                        candidate.save()

                for uri in question_dictionary['information_sources']:
                    dictionary = CandideitorgDocument.get_resource_as_dict(uri)
                    candidate = Candidate.objects.get(resource_uri=dictionary['candidate'])
                    information_source = InformationSource.create_new_from_dict(dictionary, question=question, candidate=candidate)

    @classmethod
    def fetch_all_from_api(cls,offset=0, max_elections=None):
        api = cls.get_api()
        elections_from_api = api.election.get(offset=offset)
        meta = elections_from_api['meta']
        counter = 0
        while True:
            
            for election_dict in elections_from_api["objects"]:
                election, created = Election.create_new_from_dict(election_dict)
                counter += 1
                if max_elections and max_elections == counter:
                    return    
                election.update()
                election_finished.send(sender=Election, instance=election, created=created)
                    
            offset = meta["offset"] + meta["limit"]
            if not meta["next"]:
                break
            elections_from_api = api.election.get(offset=offset, limit=meta["limit"])
            meta = elections_from_api['meta']


class Category(CandideitorgDocument):
    name = models.CharField(max_length=255)
    order = models.IntegerField()
    election = models.ForeignKey(Election)
    slug = models.SlugField(max_length=255)

    def __unicode__(self):
        return _(u'"%(category)s" in election "%(election)s"') % {
        "category": self.name,
        "election": self.election.name
        }

class Candidate(CandideitorgDocument):
    photo = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    has_answered = models.BooleanField()
    election = models.ForeignKey(Election)
    answers = models.ManyToManyField('Answer', null=True, blank=True)

    def update(self):
        candidate_dictionary = CandideitorgDocument.get_resource_as_dict(self.resource_uri)
        PersonalDataCandidate.objects.filter(candidate=self).delete()
        for uri in candidate_dictionary['personal_data_candidate']:

            pdc_dictionary = CandideitorgDocument.get_resource_as_dict(uri)
            try:
                personaldata = PersonalData.objects.get(resource_uri=pdc_dictionary["personal_data"])
                PersonalDataCandidate.create_new_from_dict(pdc_dictionary, 
                                                        candidate=self, 
                                                        personaldata=personaldata)
            except:
                pass

    def __unicode__(self):
        return self.name


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
    caption = models.CharField(max_length=2048)
    question = models.ForeignKey('Question')
    # candidate = models.ForeignKey(Candidate)

    def __unicode__(self):
        return "'%(answer)s' for '%(question)s'"%{
            "answer":self.caption,
            "question":self.question.question,
            }

class Question(CandideitorgDocument):
    question = models.CharField(max_length=255)
    category = models.ForeignKey(Category)

    def __unicode__(self):
        return _(u'"%(question)s" in category "%(category)s", in election "%(election)s"') % {
        'question': self.question,
        'category': self.category.name,
        'election': self.category.election.name
        }
    def _get_number_of_answers_(self):
        answers = self.answer_set.all()
        number_of_answers = 0
        for answer in answers:
            number_of_answers += answer.candidate_set.all().count()
        return number_of_answers
        
    number_of_answers = property(_get_number_of_answers_)




class InformationSource(CandideitorgDocument):
    question = models.ForeignKey(Question)
    candidate = models.ForeignKey(Candidate)
    content = models.TextField()

    def __unicode__(self):
        return _(u'Reference for "%(candidate)s" in question "%(question)s"') % {
        'question':self.question.question,
        'candidate':self.candidate.name

        }
class PersonalDataCandidate(CandideitorgDocument):
    value = models.CharField(max_length=255, null=True)
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

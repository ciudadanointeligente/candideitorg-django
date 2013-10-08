# -*- coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import slumber
from candideitorg.models import CandideitorgDocument, Election, Category, Candidate, BackgroundCategory,\
                                PersonalData, Background, Answer, Question, PersonalDataCandidate, Link,\
                                BackgroundCandidate
from django.core.management import call_command
from django.utils.unittest import skip
from django.template import Template, Context
from django.utils.translation import ugettext as _
import subprocess
import os
from django.core.management import call_command

class CandideitorgTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.install_candidator_yaml()

    @classmethod
    def install_candidator_yaml(cls, yaml_file='candidator_example_data'):
        FNULL = open(os.devnull, 'w')
        subprocess.call(['./candidator_install_yaml.bash', '../' + yaml_file + ".yaml"], stdout=FNULL, stderr=subprocess.STDOUT)


class CandideitorgMoreThanTwentyElections(CandideitorgTestCase):
    @classmethod
    def setUpClass(cls):
        cls.install_candidator_yaml(yaml_file="candidator_example_data_big")

    def test_load_all_elections(self):
        Election.fetch_all_from_api()
        self.assertEquals(Election.objects.count(), 21)


class UpdatingDataCandidator(CandideitorgTestCase):
    def test_upgrade_data(self):
        Election.fetch_all_from_api()
        Election.fetch_all_from_api()
        self.assertEquals(Election.objects.count(), 1)
        self.assertEquals(Category.objects.count(), 2)
        self.assertEquals(Candidate.objects.count(), 3)
        self.assertEquals(BackgroundCategory.objects.count(),2)
        self.assertEquals(PersonalData.objects.count(),4)
        self.assertEquals(Background.objects.count(),4)
        self.assertEquals(BackgroundCategory.objects.count(),2)

    def test_updates_answer(self):
        Election.fetch_all_from_api()

        UpdatingDataCandidator.install_candidator_yaml(yaml_file='candidator_example_data_with_answers2')
        Election.fetch_all_from_api()

        juanito = Candidate.objects.all()[0]


        paros = Question.objects.get(question='Esta de a cuerdo con los paros?')
        marchas = Question.objects.get(question='Le gusta ir a las marchas?')
        carretear = Question.objects.get(question='Quiere gastar su plata carreteando?')
        plata = Question.objects.get(question='Quiere robarse la plata del CEI?')
        
        print juanito.answers
        self.assertEquals(juanito.answers.get(question=paros).caption, u'Si, la llevan')
        self.assertEquals(juanito.answers.get(question=marchas).caption, u'Siempre')
        self.assertEquals(juanito.answers.get(question=carretear).caption, u'A veces')
        self.assertEquals(juanito.answers.get(question=plata).caption, u'No')


    def test_election_update(self):
        Election.fetch_all_from_api()

        UpdatingDataCandidator.install_candidator_yaml(yaml_file='candidator_example_data_with_answers2')

        election = Election.objects.all()[0]
        election.update()

        juanito = Candidate.objects.all()[0]
        
        paros = Question.objects.get(question='Esta de a cuerdo con los paros?')
        self.assertEquals(juanito.answers.get(question=paros).caption, u'Si, la llevan')
        
        marchas = Question.objects.get(question='Le gusta ir a las marchas?')
        self.assertEquals(juanito.answers.get(question=marchas).caption, u'Siempre')
        
        carretear = Question.objects.get(question='Quiere gastar su plata carreteando?')
        self.assertEquals(juanito.answers.get(question=carretear).caption, u'A veces')
        
        plata = Question.objects.get(question='Quiere robarse la plata del CEI?')
        self.assertEquals(juanito.answers.get(question=plata).caption, u'No')



class CandideitorgDocumentTest(TestCase):
    
    def setUp(self):
        super(CandideitorgDocumentTest, self).setUp()

    def test_candideitor_document_is_abstract(self):
        document = CandideitorgDocument()
        
        self.assertTrue(document)
        self.assertTrue(document._meta.abstract)

    def test_candideitorg_document_attribute(self):

        class Element(CandideitorgDocument):
            class Meta:
                app_label = 'candideitorg'
        
        call_command('syncdb', verbosity=0)

        
        element = Element.objects.create(resource_uri="cualquiercosa", remote_id=2)

        self.assertEquals(element.resource_uri,'cualquiercosa')
        self.assertEquals(element.remote_id,2)

    def test_get_api(self):
        class Element(CandideitorgDocument):
            class Meta:
                app_label = 'candideitorg'

        api = Element.get_api()
        self.assertIsInstance(api, slumber.API)


class PossibleNullValues(CandideitorgTestCase):
    def setUp(self):
        super(PossibleNullValues, self).setUp()

    def test_election_null_values(self):
        election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = None,
            logo = None,
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012"
            )

        self.assertTrue(election)
        self.assertIsNone(election.logo)
        self.assertIsNone(election.information_source)
        self.assertFalse(election.use_default_media_naranja_option)


    def test_candidate_null_values(self):
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )        
        candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = None,
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )

        self.assertTrue(candidate)
        self.assertIsNone(candidate.photo)


    def test_personal_data_candidate_null_values(self):
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )
        self.personaldata = PersonalData.objects.create(
            label = 'Nacimiento',
            remote_id = 1,
            election = self.election
            )

        personal_data_candidate = PersonalDataCandidate.objects.create(
            remote_id = 1,
            resource_uri = "/api/v2/personal_data_candidate/1/",
            value = None,
            candidate = self.candidate,
            personaldata = self.personaldata
            )

        self.assertTrue(personal_data_candidate)
        self.assertIsNone(personal_data_candidate.value)



class ElectionTest(CandideitorgTestCase):
    def setUp(self):
        super(ElectionTest, self).setUp()

    def test_is_subclass(self):
        election = Election.objects.create(remote_id=2)
        self.assertIsInstance(election,CandideitorgDocument)

    def test_create_election(self):
        election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

        self.assertTrue(election)
        self.assertEquals(election.description, 'Elecciones CEI 2012')
        self.assertEquals(election.remote_id, 1)
        self.assertEquals(election.information_source, '')
        self.assertEquals(election.logo, '/media/photos/dummy.jpg')
        self.assertEquals(election.name, 'cei 2012')
        self.assertEquals(election.resource_uri, '/api/v2/election/1/')
        self.assertEquals(election.slug, 'cei-2012')
        self.assertTrue(election.use_default_media_naranja_option)

    def test_fetch_all_election(self):
        Election.fetch_all_from_api()
        self.assertEquals(Election.objects.count(), 1)

        election = Election.objects.all()[0]
        self.assertEquals(election.description, 'Elecciones CEI 2012')
        self.assertEquals(election.remote_id, 1)
        self.assertEquals(election.information_source, '')
        self.assertEquals(election.logo, '/media/photos/dummy.jpg')
        self.assertEquals(election.name, 'cei 2012')
        self.assertEquals(election.resource_uri, '/api/v2/election/1/')
        self.assertEquals(election.slug, 'cei-2012')
        self.assertTrue(election.use_default_media_naranja_option)

class CategoryTest(CandideitorgTestCase):

    def setUp(self):
        super(CategoryTest, self).setUp()

    def test_create_category(self):
        election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

        category = Category.objects.create(
            name='category name',
            election=election,
            slug='category-name',
            order=1,
            resource_uri='/api/v2/category/1/',
            remote_id=1
            )

        self.assertTrue(category)
        self.assertIsInstance(category, CandideitorgDocument)
        self.assertEquals(category.name, 'category name')
        self.assertEquals(category.election, election)
        self.assertEquals(category.slug, 'category-name')
        self.assertEquals(category.order, 1)

    def test_fetch_all_categories(self):
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]

        self.assertEquals(Category.objects.count(), 2)

        categorie = Category.objects.all()[0]
        self.assertEqual(categorie.remote_id,1)
        self.assertEqual(categorie.name,'Politicas Publicas')
        self.assertEqual(categorie.order,1)
        self.assertEqual(categorie.resource_uri,'/api/v2/category/1/')
        self.assertEquals(categorie.slug,'politicas-publicas')
        self.assertEquals(categorie.election, election)

class CandidatesTest(CandideitorgTestCase):
    def setUp(self):
        super(CandidatesTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

    def test_create_candidate(self):
        candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )

        self.assertTrue(candidate)
        self.assertIsInstance(candidate, CandideitorgDocument)
        self.assertEquals(candidate.name, 'Juanito Perez')
        self.assertEquals(candidate.photo, '/media/photos/dummy.jpg')
        self.assertEquals(candidate.slug, 'juanito-perez')
        self.assertTrue(candidate.has_answered)
        self.assertEquals(candidate.election, self.election)

    def test_fetch_all_candidates_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]

        self.assertEquals(Candidate.objects.count(), 3)

        candidate = Candidate.objects.all()[0]
        self.assertEquals(candidate.remote_id,1)
        self.assertEquals(candidate.name, 'Juanito Perez')
        self.assertEquals(candidate.slug, 'juanito-perez')
        self.assertEquals(candidate.photo, '/media/photos/dummy.jpg')
        self.assertEquals(candidate.election, election)

class BackgroundCategoriesTest(CandideitorgTestCase):
    def setUp(self):
        super(BackgroundCategoriesTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

    def test_create_background_categorie(self):
        bg_categorie = BackgroundCategory.objects.create(
            name = 'Tendencia Politica',
            resource_uri = "/api/v2/background_category/1/",
            election=self.election,
            remote_id=1,
            )

        self.assertTrue(bg_categorie)
        self.assertIsInstance(bg_categorie, CandideitorgDocument)
        self.assertEquals(bg_categorie.name, 'Tendencia Politica')
        self.assertEquals(bg_categorie.election, self.election)

    def test_fetch_all_background_candidates_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]

        self.assertEquals(BackgroundCategory.objects.count(),2)

        bg_categorie = BackgroundCategory.objects.all()[0]
        self.assertEquals(bg_categorie.remote_id,1)
        self.assertEquals(bg_categorie.name,'Tendencia Politica')
        self.assertEquals(bg_categorie.election,election)

class PersonalDataTest(CandideitorgTestCase):
    def setUp(self):
        super(PersonalDataTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

    def test_create_personaldata(self):

        personaldata = PersonalData.objects.create(
            label = 'Nacimiento',
            remote_id = 1,
            election = self.election
            )

        self.assertTrue(personaldata)
        self.assertIsInstance(personaldata, CandideitorgDocument)
        self.assertEquals(personaldata.label,'Nacimiento')
        self.assertEquals(personaldata.election, self.election)

    def test_fetch_all_personaldata_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]

        self.assertEquals(PersonalData.objects.count(),4)

        personal_data = PersonalData.objects.all()[0]
        self.assertEquals(personal_data.label,'Nacimiento')
        self.assertEquals(personal_data.election, election)

class BackgroundTest(CandideitorgTestCase):
    def setUp(self):
        super(BackgroundTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.background_category = BackgroundCategory.objects.create(
            name = 'Tendencia Politica',
            resource_uri = "/api/v2/background_category/1/",
            election=self.election,
            remote_id=1,
            )

    def test_create_background(self):
        background = Background.objects.create(
            remote_id = 1,
            name = 'Partido politico actual',
            resource_uri = '/api/v2/background/1/',
            background_category = self.background_category
            )

        self.assertTrue(background)
        self.assertIsInstance(background, CandideitorgDocument)
        self.assertEquals(background.name, 'Partido politico actual')
        self.assertEquals(background.resource_uri, '/api/v2/background/1/')
        self.assertEquals(background.background_category, self.background_category)

    def test_fetch_all_background_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]
        background_category = BackgroundCategory.objects.get(remote_id=1)

        self.assertEquals(Background.objects.count(),4)
        background = Background.objects.get(remote_id=1)
        self.assertEquals(background.name,'Partido politico actual')
        self.assertEquals(background.resource_uri,'/api/v2/background/1/')
        self.assertEquals(background.background_category, background_category)

class AnswersTest(CandideitorgTestCase):
    def setUp(self):
        super(AnswersTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.category = Category.objects.create(
            name='category name',
            election=self.election,
            slug='category-name',
            order=1,
            resource_uri='/api/v2/category/1/',
            remote_id=1
            )
        self.question = Question.objects.create(
            remote_id = 1,
            question = 'Esta de a cuerdo con los paros?',
            resource_uri = '/api/v2/question/1/',
            category = self.category,
            )
        self.candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            resource_uri = '/api/v2/candidate/1/',
            remote_id = 1
            )

    def test_unicode(self):
        answer = Answer.objects.create(
            remote_id = 1,
            caption = 'De vez en cuando',
            resource_uri = '/api/v2/answer/8/',
            question = self.question
            )

        self.assertEquals(answer.__unicode__(), "'De vez en cuando' for 'Esta de a cuerdo con los paros?'")

    def test_create_answer(self):
        answer = Answer.objects.create(
            remote_id = 1,
            caption = 'De vez en cuando',
            resource_uri = '/api/v2/answer/8/',
            question = self.question
            )
        self.assertTrue(answer)
        self.assertIsInstance(answer, CandideitorgDocument)
        self.assertEquals(answer.caption, 'De vez en cuando')
        self.assertEquals(answer.resource_uri, '/api/v2/answer/8/')
        self.assertEquals(answer.question, self.question)

    def test_fetch_all_answers_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]
        category = Category.objects.all()[0]
        question = Question.objects.all()[0]

        self.assertEquals(Answer.objects.count(),10)
        answer = Answer.objects.get(remote_id=9)
        self.assertEquals(answer.caption,'Puro perder clases')
        self.assertEquals(answer.resource_uri,'/api/v2/answer/9/')
        self.assertEquals(answer.question, question)

    def test_get_candidates_has_answer(self):
        candidate = self.candidate
        answer = Answer.objects.create(
            remote_id = 1,
            caption = 'De vez en cuando',
            resource_uri = '/api/v2/answer/8/',
            question = self.question
            )
        candidate.answers.add(answer)
        candidate.save()

        self.assertEquals(candidate.answers.all().count(),1)
        self.assertEquals(candidate.answers.all()[0],answer)

    def test_associate_answers(self):
        # Candidate.objects.all().delete()
        Election.fetch_all_from_api()
        candidate1 = Candidate.objects.get(resource_uri="/api/v2/candidate/1/")
        answer8 = Answer.objects.get(resource_uri="/api/v2/answer/8/")

        self.assertIn(answer8, candidate1.answers.all())

class QuestionTest(CandideitorgTestCase):
    def setUp(self):
        super(QuestionTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.category = Category.objects.create(
            name='category name',
            election=self.election,
            slug='category-name',
            order=1,
            resource_uri='/api/v2/category/1/',
            remote_id=1
            )

    def test_create_question(self):
        question = Question.objects.create(
            remote_id = 1,
            question = 'Le gusta ir a las marchas?',
            resource_uri = '/api/v2/question/2/',
            category = self.category,
            )
        self.assertTrue(question)
        self.assertIsInstance(question, CandideitorgDocument)
        self.assertEquals(question.question, 'Le gusta ir a las marchas?')
        self.assertEquals(question.resource_uri, '/api/v2/question/2/')

    def test_get_all_question_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]
        category = Category.objects.all()[0]

        self.assertEquals(Question.objects.count(),4)
        question = Question.objects.all()[0]
        self.assertEquals(question.question, 'Esta de a cuerdo con los paros?')
        self.assertEquals(question.category, category)
        self.assertEquals(question.resource_uri, '/api/v2/question/1/')

class TemplateTagsTest(CandideitorgTestCase):
    def setUp(self):
        super(TemplateTagsTest, self).setUp()
        self.election = Election.fetch_all_from_api()

    def test_templatetag_candidate_answer_value(self):
        question = Question.objects.get(resource_uri="/api/v2/question/2/")
        candidate = Candidate.objects.get(resource_uri="/api/v2/candidate/1/")
        answer = Answer.objects.get(resource_uri="/api/v2/answer/8/")
        expected_html = answer.caption

        template = Template("{% load candideitorg_templetags %}{% answer_for_candidate_and_question candidate question %}")
        context = Context({'candidate':candidate,'question':question})

        self.assertEquals(template.render(context),expected_html)

    def test_template_tag_when_no_answer_is_selected(self):
        candidate = Candidate.objects.get(resource_uri="/api/v2/candidate/1/")
        question = Question.objects.get(resource_uri="/api/v2/question/3/")
        #No one has answered the question 3
        expected_html = _(u"Aún no hay respuesta")
        template = Template("{% load candideitorg_templetags %}{% answer_for_candidate_and_question candidate question %}")
        context = Context({'candidate':candidate,'question':question})


        self.assertEquals(template.render(context),expected_html)

    def test_templatetag_personal_data(self):
        candidate = Candidate.objects.get(resource_uri="/api/v2/candidate/1/")
        personal_data = PersonalData.objects.get(resource_uri="/api/v2/personal_data/1/")
        personal_data_candidate = PersonalDataCandidate.objects.get(resource_uri="/api/v2/personal_data_candidate/1/")
        expected_html = personal_data_candidate.value

        template = Template("{% load candideitorg_templetags %}{% relation_personal_data_candidate candidate personal_data %}")
        context = Context({'candidate':candidate,'personal_data':personal_data})

        self.assertEquals(template.render(context),expected_html)

class PersonalDataCandidateTest(CandideitorgTestCase):
    def setUp(self):
        super(PersonalDataCandidateTest, self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )
        self.personaldata = PersonalData.objects.create(
            label = 'Nacimiento',
            remote_id = 1,
            election = self.election
            )

    def test_create_personal_data_candidate(self):
        personal_data_candidate = PersonalDataCandidate.objects.create(
            remote_id = 1,
            resource_uri = "/api/v2/personal_data_candidate/1/",
            value = "13/13/13",
            candidate = self.candidate,
            personaldata = self.personaldata
            )
        self.assertTrue(personal_data_candidate)
        self.assertIsInstance(personal_data_candidate, CandideitorgDocument)
        self.assertEquals(personal_data_candidate.value,'13/13/13')
        self.assertEquals(personal_data_candidate.resource_uri, '/api/v2/personal_data_candidate/1/')
        self.assertEquals(personal_data_candidate.candidate, self.candidate)
        self.assertEquals(personal_data_candidate.personaldata, self.personaldata)

    def test_get_all_personal_data_candidate_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()

        election = Election.objects.all()[0]
        candidate = Candidate.objects.all()[0]
        personal_data = PersonalData.objects.all()[0]

        self.assertEquals(PersonalDataCandidate.objects.count(),2)
        personal_data_candidate = PersonalDataCandidate.objects.all()[0]
        self.assertEquals(personal_data_candidate.value,'13/13/13')
        self.assertEquals(personal_data_candidate.candidate, candidate)
        self.assertEquals(personal_data_candidate.personaldata, personal_data)

class LinkTest(CandideitorgTestCase):
    def setUp(self):
        super(LinkTest,self).setUp()
        self.election = Election.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        self.candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )

    def test_create_link(self):
        link = Link.objects.create(
            name = 'twitter',
            url = 'http://www.twitter.com',
            candidate = self.candidate,
            remote_id = 1
            )
        self.assertTrue(link)

    def test_get_links_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()

        election = Election.objects.all()[0]
        candidate = Candidate.objects.all()[0]
        link = Link.objects.all()[0]
        
        self.assertEquals(Link.objects.count(),1)
        self.assertEquals(link.url, 'http://www.twitter.com')

    def test_get_links_extra_classes_for_twitter(self):
        link = Link.objects.create(
            name = 'twitter',
            url = 'http://www.twitter.com',
            candidate = self.candidate,
            remote_id = 1
            )

        expected_extra_links = 'icon-twitter-sign'
        self.assertEquals(link.icon_class, expected_extra_links)

    def test_get_links_extra_classes_for_facebook(self):
        link = Link.objects.create(
            name = 'mi_feisBuuK',
            url = 'http://www.facebook.com',
            candidate = self.candidate,
            remote_id = 1
            )

        expected_extra_links = 'icon-facebook-sign'
        self.assertEquals(link.icon_class, expected_extra_links)

class BackgroundCandidateTest(CandideitorgTestCase):
    def setUp(self):
        super(BackgroundCandidateTest, self).setUp()
        Election.fetch_all_from_api()

    def test_create_background_candidate(self):
        background = Background.objects.get(id=1)
        candidate = Candidate.objects.get(id= 1)
        background_candidate = BackgroundCandidate.objects.create(
            value = 'CCC',
            remote_id = 1,
            candidate = candidate,
            background = background
            )
        self.assertTrue(background_candidate)
        self.assertIsInstance(background_candidate, CandideitorgDocument)
        self.assertEquals(background_candidate.value,'CCC')

    def test_get_all_background_candidates_from_api(self):
        candidate = Candidate.objects.get(resource_uri="/api/v2/candidate/1/")
        background = Background.objects.get(resource_uri="/api/v2/background/1/")

        backgrounds_candidates = BackgroundCandidate.objects.filter(
            resource_uri="/api/v2/backgrounds_candidate/1/")
        self.assertEquals(backgrounds_candidates.count(), 1)
        background_candidate = backgrounds_candidates[0]
        self.assertEquals(background_candidate.candidate, candidate)
        self.assertEquals(background_candidate.background, background)

from candideitorg.models import election_finished
from django.dispatch import receiver

# defininig the proxy according to 
# http://stackoverflow.com/questions/3829742/assert-that-a-method-was-called-in-a-python-unit-test

class MethodCallLogger(object):
   def __init__(self, method):
     self.method = method
     self.was_called = False
     self.times = 0

   def __call__(self, sender=None, **kwargs):
     self.times += 1
     self.method(sender, **kwargs)
     self.was_called = True
     

class SignalAfterAllTestCase(CandideitorgTestCase):
    def setUp(self):
        super(SignalAfterAllTestCase, self).setUp()

    def test_a_signal_is_called(self):

        #defining the receiver
        def signal_receiver(sender, instance, created, **kwargs):
            self.assertIsInstance(instance, Election)
            self.assertEquals(sender, Election)
            self.assertTrue(created)


        signal_receiver = MethodCallLogger(signal_receiver)
        #connecting the thing
        election_finished.connect(signal_receiver)

        Election.fetch_all_from_api()

        self.assertTrue(signal_receiver.was_called)
        self.assertEquals(signal_receiver.times, 1)

    def test_it_send_created_parameter_depending_for_updating(self):
        #defining the receiver
        def signal_receiver(sender, instance, created, **kwargs):
            if signal_receiver.times == 1:
                self.assertTrue(created)
            if signal_receiver.times == 2:
                self.assertFalse(created)


        signal_receiver = MethodCallLogger(signal_receiver)
        #connecting the thing
        election_finished.connect(signal_receiver)
        #creating
        Election.fetch_all_from_api()
        #updating
        Election.fetch_all_from_api()


class ManagementCommandTestCase(CandideitorgTestCase):
    def test_call_command(self):
        self.assertEquals(Election.objects.count(), 0)
        call_command('update_from_candidator')
        self.assertEquals(Election.objects.count(), 1)


class ElectionFetchAllFromAPIPagination(CandideitorgTestCase):
    @classmethod
    def setUpClass(cls):
        cls.install_candidator_yaml(yaml_file="candidator_example_data_big")\

    def test_it_gets_only_the_first_5_elections(self):
        Election.fetch_all_from_api(max_elections=5, offset=0)
        self.assertEquals(Election.objects.count(), 5)
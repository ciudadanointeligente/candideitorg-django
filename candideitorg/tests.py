"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import slumber
from candideitorg.models import CandideitorgDocument, Election, Category, Candidate, BackgroundCategory,\
                                PersonalData, Background, Answer, Question
from django.core.management import call_command
from django.utils.unittest import skip

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

class ElectionTest(TestCase):
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

class CategoryTest(TestCase):

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

class CandidatesTest(TestCase):
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

class BackgroundCategoriesTest(TestCase):
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

class PersonalDataTest(TestCase):
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

class BackgroundTest(TestCase):
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

class AnswersTest(TestCase):
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
        self.candidate = Candidate.objects.create(
            name = "Juanito Perez",
            photo = "/media/photos/dummy.jpg",
            slug = "juanito-perez",
            has_answered = True,
            election = self.election,
            remote_id = 1
            )

    @skip('a')
    def test_create_answer(self):
        answers = Answer.objects.create(
            remote_id = 1,
            caption = 'De vez en cuando',
            question = '/api/v2/question/2/',
            resource_uri = '/api/v2/answer/8/',
            candidate = self.candidate,
            )
        self.assertTrue(answers)
        self.assertIsInstance(answers, CandideitorgDocument)
        self.assertEquals(answers.caption, 'De vez en cuando')
        self.assertEquals(answers.question, '/api/v2/question/2/')
        self.assertEquals(answers.resource_uri, '/api/v2/answer/8/')

    @skip('a')
    def test_fetch_all_answers_from_api(self):
        self.election.delete()
        Election.fetch_all_from_api()
        election = Election.objects.all()[0]
        candidate = Candidate.objects.get(remote_id=1)

        self.assertEquals(Answer.objects.count(),1)
        answer = Answer.objects.get(remote_id=8)
        self.assertEquals(answer.caption,'De vez en cuando')
        self.assertEquals(answer.resource_uri,'/api/v2/answer/8/')
        self.assertEquals(answer.candidate, candidate)

class QuestionTest(TestCase):
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

    
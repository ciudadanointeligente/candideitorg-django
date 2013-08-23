"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from candideitorg.models import CandideitorgDocument
from django.core.management import call_command

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

class ElectionTest(TestCase):
	def setUp(self):
    	super(ElectionTest, self).setUp()

    def test_create_election(self):
    	election = Election.objects.create(
    		description: "Elecciones CEI 2012",
    		remote_id: 1,
    		information_source: "",
    		logo: "/media/photos/dummy.jpg",
    		name: "cei 2012",
    		resource_uri: "/api/v2/election/1/",
    		slug: "cei-2012",
    		use_default_media_naranja_option: True
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
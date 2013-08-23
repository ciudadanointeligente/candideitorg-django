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

    	
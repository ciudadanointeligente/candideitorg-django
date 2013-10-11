# -*- coding: utf-8 -*-
from django import template
from django.utils.translation import ugettext as _

register = template.Library()

@register.simple_tag
def answer_for_candidate_and_question(candidate, question):
    '''
    Returns the answer for the given candidate and question pair.

    >> {% answer_for_candidate_and_question candidate question %}
    "answer"
    '''

    try:
        return question.answer_set.get(candidate=candidate).caption
    except:
        pass
    return _(u"Aún no hay respuesta")

@register.inclusion_tag('candideitorg/information_source.html')
def get_information_source(candidate, question):
    '''
    Returns the information source for a candidate referred to a certain question.

    >> {% get_information_source candidate question %}
    "answer"
    '''
    try:
        information_source = question.informationsource_set.get(candidate=candidate)
        return {'information_source':information_source}
    except:
        return {'information_source':None}

@register.simple_tag
def relation_personal_data_candidate(candidate, personaldata):
    try:
        return personaldata.personaldatacandidate_set.get(candidate=candidate).value
    except:
        return _('no message')
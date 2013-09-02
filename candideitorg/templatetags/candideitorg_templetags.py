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
        return '<li>'+question.answer_set.get(candidate=candidate).caption+'</li>'
    except:
        pass
    return '<li>'+_(u"Aún no hay respuesta")+'</li>'
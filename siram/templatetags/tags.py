from django import template
from base.models import *

register = template.Library()

@register.inclusion_tag('navbar.html', takes_context=True)
def setting():
    setting = Setting.objects.get(key='TITLE')
    print(setting)
    return {'setting':setting}
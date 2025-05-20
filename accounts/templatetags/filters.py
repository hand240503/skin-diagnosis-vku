from django import template

register = template.Library()

@register.filter
def equals(value, arg):
    return value == arg

@register.filter
def equals_str(value, arg):
    return str(value) == str(arg)

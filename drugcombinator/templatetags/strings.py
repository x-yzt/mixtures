from django import template
from django.template.defaultfilters import stringfilter
import urllib
import re


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def formatspaces(text):

    replacements = {
        r'^[\t ]+': '', # Remove leading spaces
        r'[\t ]+$': '', # Remove trailing spaces
        r'(\S)\n(\S)': r'\1 \2', # Replace single newlines with spaces
        r'\n{2,}': '\n\n' # Cap sucessive newlines
    }
    text = text.strip()
    for pat, repl in replacements.items():
        text = re.sub(pat, repl, text, re.A, re.M)
    
    return text


@register.filter(is_safe=True)
@stringfilter
def stripspaces(text):

    replacements = {
        r'^[\t ]+': '', # Remove leading spaces
        r'[\t ]+$': '', # Remove trailing spaces
        r'\n': ' ', # Replace newlines with spaces
        r'(\s){2,}': r'\1' # Merge consecutive spaces
    }
    text = text.strip()
    for pat, repl in replacements.items():
        text = re.sub(pat, repl, text, re.A, re.M)
    
    return text


@register.simple_tag
def mailto(recipient, subject=None, body=None):

    args = urllib.parse.urlencode({
        'subject': subject or '',
        'body': body or ''
    }, quote_via=urllib.parse.quote)
    
    return f'mailto:{recipient}?{args}'

import re

from django import template

register = template.Library()


@register.filter(is_safe=False)
def format_links_blank(text):
    return re.sub(
        r"https?://\S+",
        r'<a target="_blank" href="\g<0>">\g<0></a>',
        str(text),
    )

from django import template
register = template.Library()


@register.simple_tag()
def multiply(a, b, *args, **kwargs):
    try:
        return a * b
    except (TypeError, ValueError):
        return str(a)+str(b)

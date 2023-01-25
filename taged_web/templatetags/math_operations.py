from django import template
register = template.Library()


@register.filter(is_safe=False)
def sub(a, b):
    try:
        return a - b
    except Exception:
        return f"{a} - {b}"


@register.filter(is_safe=False)
def mul(a, b):
    try:
        return a * b
    except Exception:
        return f"{a} * {b}"


@register.filter(is_safe=False)
def pow_(a, b):
    try:
        return a ** b
    except Exception:
        return f"{a} ^ {b}"
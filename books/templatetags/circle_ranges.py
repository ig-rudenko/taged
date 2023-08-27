from django import template

register = template.Library()


@register.filter(is_safe=False)
def to_range(value, start_index=0):
    try:
        start_index = int(start_index)
        value = int(value)
        return range(start_index, value+start_index)
    except Exception:
        start_index = 0
        value = len(str(value))
        return range(start_index, value+start_index)

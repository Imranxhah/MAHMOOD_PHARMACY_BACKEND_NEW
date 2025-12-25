from django import template

register = template.Library()

@register.filter
def clean_branch_name(value):
    """Removes 'Mahmood Pharmacy' from the branch name."""
    if isinstance(value, str):
        return value.replace("Mahmood Pharmacy", "").strip()
    return value

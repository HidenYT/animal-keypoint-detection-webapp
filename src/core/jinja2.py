from django.templatetags.static import static
from django.urls import reverse
from crispy_forms.templatetags.crispy_forms_filters import as_crispy_form 
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "crispy": as_crispy_form, 
        }
    )
    return env
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_url(value):
    url_validator = URLValidator()
    if not value.startswith('http'):
        value = 'http://' + value
    url_validator(value)
    return value

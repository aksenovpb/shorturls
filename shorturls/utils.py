from django.test import TestCase
from django.utils.crypto import get_random_string
from django.conf import settings


SHORTCODE_MIN = getattr(settings, 'SHORTCODE_MIN', 6) 
COUNT_ITERATION_MAX = getattr(settings, 'COUNT_ITERATION_MAX', 3)

def create_shortcode(instance, size=SHORTCODE_MIN, iteration=1):
    new_code = get_random_string(length=size)
    qs = instance.__class__.objects.filter(shortcode=new_code)
    if qs.exists():
        if iteration >= COUNT_ITERATION_MAX:
            size += 1
            iteration = 0
        return create_shortcode(size=size, iteration=iteration+1)
    return new_code

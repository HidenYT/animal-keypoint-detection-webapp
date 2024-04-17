from django.core.exceptions import ValidationError


def greater_0(value):
    if value <= 0:
        raise ValidationError(f"Value {value} can't be less than or equal to 0.")
    
def less_1(value):
    if value >= 1:
        raise ValidationError(f"Value {value} can't be greater than or equal to 1.")
import re

from rest_framework.exceptions import ValidationError


def username_validator(value):
    """Валидатор юзернейна на недопустимые символы."""
    cleaned_value = re.sub(r'[^\w.@+-]', '', value)
    if set(value) - set(cleaned_value):
        invalid_characters = set(value) - set(cleaned_value)
        raise ValidationError(
            f'Недопустимые символы {"".join(invalid_characters)}в username. '
            'username может содержать только буквы, цифры и '
            'знаки @/./+/-/_.'
        )
    return value

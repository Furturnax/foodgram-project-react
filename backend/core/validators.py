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


def hex_color_validator(value):
    """Валидатор цвета на недопустимые символы."""
    if not re.match(r'^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{3}$', value):
        invalid_characters = re.sub(r'[0-9a-fA-F#]', '', value)
        raise ValidationError(
            'Недопустимый hex-код. '
            f'Недопустимые символы: {invalid_characters}'
        )
    return value

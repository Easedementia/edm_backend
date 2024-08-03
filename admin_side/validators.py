import os
from django.core.exceptions import ValidationError

def validate_svg(file):
    if not file.name.endswith('.svg'):
        raise ValidationError('File is not an SVG')
    if file.content_type != 'image/svg+xml':
        raise ValidationError('File content is not image/svg+xml')
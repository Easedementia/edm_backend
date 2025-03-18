import os
import imghdr
from django.core.exceptions import ValidationError



def validate_image_format(file):
    """ Validate if the uploaded file is SVG, PNG, or JPG """
    allowed_extensions = ['.svg', '.png', '.jpg', '.jpeg']
    allowed_mime_types = ['image/svg+xml', 'image/png', 'image/jpeg']

    ext = os.path.splitext(file.name)[1].lower()  # Get file extension
    if ext not in allowed_extensions:
        raise ValidationError(f'Only {", ".join(allowed_extensions)} files are allowed.')

    if file.content_type not in allowed_mime_types:
        raise ValidationError(f'Invalid file type. Allowed types: {", ".join(allowed_mime_types)}')

    # If it's not an SVG, double-check using imghdr for PNG/JPG
    if ext != '.svg':
        file_format = imghdr.what(file)
        if file_format not in ['jpeg', 'png']:
            raise ValidationError('Uploaded file is not a valid PNG or JPG image.')
from django.core.exceptions import ValidationError

def validate_image_size(image):
    filesize = image.size
    megabyte_limit = 50.0*1024*1024
    if filesize > megabyte_limit:
        raise ValidationError(f"Max file size is {megabyte_limit}MB")

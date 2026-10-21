import logging

from django import template

register = template.Library()
logger = logging.getLogger(__name__)

@register.filter('image_url')
def image_url(image):
    """
    Returns the URL of an image (or imagekit spec), or an empty string if the image can't be served,
    e.g. because the uploaded file has gone missing. Imagekit generates thumbnails on access and
    raises in that case, which would otherwise break the whole page.
    """
    try:
        return image.url
    except (OSError, ValueError):
        logger.warning("Could not get URL for image %r", getattr(image, 'name', image), exc_info=True)
        return ''

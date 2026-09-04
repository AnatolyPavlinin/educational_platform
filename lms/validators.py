from django.core.exceptions import ValidationError
from urllib.parse import urlparse


def validate_youtube_url(value):
    """Проверяет URL, разрешая только youtube.com и youtu.be."""
    parsed_url = urlparse(value)

    # Проверяем наличие схемы (http/https) и сетевого расположения (домена)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValidationError("Введите полную ссылку, включая http:// или https://")

    domain = parsed_url.netloc.lower()

    allowed_domains = ["youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"]

    if domain not in allowed_domains:
        raise ValidationError(
            f'Разрешены ссылки только на YouTube. Ссылка на "{domain}" недопустима.'
        )

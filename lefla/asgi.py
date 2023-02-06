"""
ASGI config for lefla project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from . import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lefla.settings")

django_asgi_app = get_asgi_application()

application = routing.application

"""
WSGI config for canhemon project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys, site

import mod_wsgi

ROOT_DIR = '/var/www/appname/site/TreeCheckerApp/web/'
APP_DIR = '/var/www/appname/site/TreeCheckerApp/web/canhemon'
VE_DIR = '/var/www/appname/site/venv/lib/python3.6/site-packages'

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, APP_DIR)

sys.path.insert(1,VE_DIR)
site.addsitedir(VE_DIR)


from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "canhemon.settings")

import signal
import time


application = get_wsgi_application()

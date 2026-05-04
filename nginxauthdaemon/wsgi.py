"""WSGI entry point for gunicorn/uWSGI.

Usage: gunicorn nginxauthdaemon.wsgi:app
"""
from nginxauthdaemon import create_app

app = create_app()

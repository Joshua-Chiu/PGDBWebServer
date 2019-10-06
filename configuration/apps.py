from django import apps
from axes.apps import AppConfig


class AxesConfig(AppConfig):
    verbose_name = "Access"


class ConfigurationConfig(apps.AppConfig):
    name = 'configuration'

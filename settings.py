import os
from os import environ
OTREE_PRODUCTION=1
DEBUG = True

SESSION_CONFIGS = [
    dict(
        name='minmax_consent',
        app_sequence=['minmax_consent'],
        num_demo_participants=3,
    ),
    dict(
        name='minmax',
        app_sequence=['minmax'],
        num_demo_participants=3,
    ),
    dict(
        name='lobby',
        app_sequence=['lobby_app'],
        num_demo_participants=30,
    ),
    dict(
        name='pre_R',
        app_sequence=['pre_R'],
        num_demo_participants=2,
    ),
    dict(
        name='post_R',
        app_sequence=['post_R'],
        num_demo_participants=2,
    ),
    dict(
        name='pre_N',
        app_sequence=['pre_N'],
        num_demo_participants=2,
    ),
    dict(
        name='post_N',
        app_sequence=['post_N'],
        num_demo_participants=2,
    ),
    dict(
        name='NL',
        app_sequence=['NL'],
        num_demo_participants=2,
    ),
    dict(
        name='prepost_consent',
        app_sequence=['prepost_consent'],
        num_demo_participants=2,
    ),
]
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []


# rooms
ROOMS = [
    dict(
        name='BEELAB',
        display_name='BEELAB',
    ),
    dict(
        name='signature',
        display_name='signature',
    ),
    dict(
        name='lobby',
        display_name='lobby',
    ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = ''
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 0

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '6929828123368'

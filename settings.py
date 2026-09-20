import os
from os import environ
OTREE_PRODUCTION=1
DEBUG = True

SESSION_CONFIGS = [
    dict(
        name='survey1_pre',
        display_name='설문 1. 사전설문',
        app_sequence=['survey1_pre'],
        num_demo_participants=4,
    ),
    dict(
        name='survey2_1_control',
        display_name='설문 2-1. 사후설문 (control)',
        app_sequence=['survey2_1_control'],
        num_demo_participants=4,
    ),
    dict(
        name='survey2_2_treatment',
        display_name='설문 2-2. 사후설문 (treatment)',
        app_sequence=['survey2_2_treatment'],
        num_demo_participants=4,
    ),
    dict(
        name='survey3_employee',
        display_name='설문 3. 직원 설문',
        app_sequence=['survey3_employee'],
        num_demo_participants=4,
    ),
]



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
LANGUAGE_CODE = 'ko'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = ''
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 0

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '6929828123368'

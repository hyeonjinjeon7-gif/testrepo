import os
from os import environ

# 배포(Heroku)에서는 아래 환경변수를 설정한다.
#   OTREE_PRODUCTION=1        운영 모드 (오류 상세 화면 숨김)
#   OTREE_AUTH_LEVEL=STUDY    관리자 로그인 요구, 참가자는 링크로만 접속
#   OTREE_ADMIN_PASSWORD      관리자 비밀번호
#   OTREE_SECRET_KEY          세션 암호화 키
#   DATABASE_URL              Heroku Postgres 애드온이 자동으로 넣어 준다

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
    # 방 주소는 세션을 새로 만들어도 바뀌지 않는다. QR 코드는 이 주소로 만든다.
    #   https://<앱주소>/room/pre        (사전설문)
    #   https://<앱주소>/room/post_control     (사후설문 control, 파란 목줄)
    #   https://<앱주소>/room/post_treatment   (사후설문 treatment, 빨간 목줄)
    #   https://<앱주소>/room/employee   (직원 설문, 담당 직원에게 메일로 보낼 링크)
    dict(name='pre', display_name='설문 1. 사전설문'),
    dict(name='post_control', display_name='설문 2-1. 사후설문 (control)'),
    dict(name='post_treatment', display_name='설문 2-2. 사후설문 (treatment)'),
    dict(name='employee', display_name='설문 3. 직원 설문'),
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

# 배포에서는 OTREE_SECRET_KEY 환경변수를 쓰고, 내 컴퓨터에서 켤 때만 아래 기본값을 쓴다
SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'local-development-only')

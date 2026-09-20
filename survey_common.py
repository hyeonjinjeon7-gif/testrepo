"""
설문 1-4 공통 도구.

각 앱의 __init__.py 에서 `from survey_common import *` 로 불러 쓴다.
- 필드 만들기: radio, check, text, number, long_text
- 화면 넘기기: matrix, checkboxes (템플릿 _matrix.html, _checkboxes.html 에 넘길 값)
- 블록 순서 무작위: assign_block_order, make_positioned
- 입력 검사: is_valid_phone, is_valid_email, count_checked, clear_other
"""

import random

from otree.api import models, widgets


# ---------------------------------------------------------------------------
# 자주 쓰는 보기 (설문지의 표 순서대로 1, 2, 3 ...)
# ---------------------------------------------------------------------------
AGREE5 = [
    [1, '전혀 동의 안 함'],
    [2, '별로 동의 안 함'],
    [3, '보통'],
    [4, '다소 동의'],
    [5, '매우 동의'],
]

# AGREE5 + "잘 모름" (설문 3의 M6)
AGREE6 = AGREE5 + [[6, '잘 모름']]

KNOW4 = [[1, '잘 알고 있다'], [2, '어느 정도 알고 있다'], [3, '들어본 적 있다'], [4, '모른다']]

YES_NO = [[1, '예'], [2, '아니오']]

# 도입/실행 의향 (설문 2의 E3, E4)
INTENT5_ADOPT = [
    [1, '도입 의향 없음'],
    [2, '검토 가능'],
    [3, '도입 가능성 있음'],
    [4, '적극 도입 예정'],
    [5, '이미 운영 중'],
]
INTENT5_ACT = [
    [1, '의향 없음'],
    [2, '검토 가능'],
    [3, '실행 가능성 있음'],
    [4, '적극 실행 예정'],
    [5, '이미 완료'],
]

# 설문 1 B10 = 설문 2 F1-그룹1 = 설문 4 R1 앞부분
DIFFICULTY_FLEX = [
    'CEO 및 임원의 관심 또는 의지 부족',
    '제도 도입 방법, 절차, 규정을 잘 모름',
    '직원 근태관리 또는 근무평정의 어려움',
    '업무 공백 또는 대체인력 문제',
    '거래기업 또는 고객과의 관계 때문에 어려움',
    '비용 부담',
    '일부 직무에는 적용하기 어려움',
    '직원 간 형평성 문제',
    '직원들이 실제로 사용하기 어려운 조직문화',
    '노동조합 또는 직원의 반대',
    '희망하는(필요한) 직원이 없음',
    '필요성을 느끼지 못함',
    '이미 충분히 운영하고 있음',
    '기타',
]

# 설문 1 C8 = 설문 2 F1-그룹2 = 설문 4 R1 뒷부분
DIFFICULTY_LABOR = [
    '어디까지가 직장 내 괴롭힘인지 판단하기 어려움',
    '신고 접수와 조사 절차를 어떻게 만들지 모름',
    '관리자들이 업무 지적이나 피드백을 꺼리게 됨',
    '젊은 직원과의 소통 방식을 바꾸기 어려움',
    '평가와 보상 기준을 공개하거나 바꾸기 어려움',
    '비용 부담 (노무사 수임료, 교육비 등)',
    '시간과 인력 부족',
    '법이 자주 바뀌어 따라가기 어려움',
    '직원과의 갈등이 생길까 우려됨',
    '필요성을 느끼지 못함',
    '이미 충분히 정비되어 있음',
    '기타',
]

EDUCATION = [[1, '고졸 이하'], [2, '전문대졸'], [3, '대졸'], [4, '대학원졸 이상']]
MARITAL = [[1, '미혼'], [2, '기혼 (사실혼 포함)'], [3, '기타']]
HOUSING = [[1, '자가'], [2, '전세'], [3, '월세 (반전세 포함)'], [4, '기타']]


# ---------------------------------------------------------------------------
# 필드 만들기
# ---------------------------------------------------------------------------
def radio(label, choices):
    """라디오 버튼 (하나만 선택). 응답하지 않고 넘어갈 수 있다."""
    return models.IntegerField(
        label=label, choices=choices, widget=widgets.RadioSelect, blank=True
    )


def dropdown(label, choices):
    return models.IntegerField(label=label, choices=choices, blank=True)


def check(label):
    """체크박스 한 칸 (복수 선택 문항의 보기 하나)"""
    return models.BooleanField(label=label, widget=widgets.CheckboxInput, blank=True)


def text(label=''):
    return models.StringField(label=label, blank=True)


def long_text(label=''):
    return models.LongStringField(label=label, blank=True)


def number(label='', min=0, max=None):
    return models.IntegerField(label=label, min=min, max=max, blank=True)


def field_names(prefix, n, start=1):
    return ['{}{}'.format(prefix, i) for i in range(start, n + start)]


# ---------------------------------------------------------------------------
# 템플릿에 넘길 값
# ---------------------------------------------------------------------------
def scale_labels(choices):
    return [label for value, label in choices]


def matrix(rows, choices):
    """표 문항: _matrix.html 에 넘길 값"""
    return dict(rows=rows, scale=scale_labels(choices))


def checkboxes(rows, max_n=0, exclusive=''):
    """복수 선택 문항: _checkboxes.html 에 넘길 값"""
    return dict(rows=rows, max=max_n, exclusive=exclusive)


# ---------------------------------------------------------------------------
# 블록 순서 무작위 (Qualtrics의 Block Randomizer, Evenly Present)
# ---------------------------------------------------------------------------
def assign_block_order(subsession, orders=('BC', 'CB'), field='block_order'):
    """참가자에게 두 순서를 절반씩 섞어서 배정한다."""
    players = subsession.get_players()
    values = list(orders) * (len(players) // len(orders) + 1)
    values = values[: len(players)]
    random.shuffle(values)
    for p, v in zip(players, values):
        setattr(p, field, v)


def make_positioned(app_name, page_class, position, field='block_order'):
    """
    같은 페이지를 "앞 자리"와 "뒷 자리"에 하나씩 만들어,
    배정된 순서에 맞는 자리에서만 보여 준다.
    page_class 에는 block = 'B' 처럼 어느 블록인지 적어 둔다.
    """
    block = page_class.block
    original_is_displayed = page_class.__dict__.get('is_displayed')

    def is_displayed(player):
        if getattr(player, field)[position - 1] != block:
            return False
        if original_is_displayed is not None:
            return original_is_displayed.__func__(player)
        return True

    return type(
        '{}_{}'.format(page_class.__name__, position),
        (page_class,),
        dict(
            template_name='{}/{}.html'.format(app_name, page_class.__name__),
            is_displayed=staticmethod(is_displayed),
        ),
    )


# ---------------------------------------------------------------------------
# 입력 검사, 정리
# ---------------------------------------------------------------------------
def is_valid_phone(s):
    digits = s.replace('-', '').replace(' ', '')
    return digits.isdigit() and 10 <= len(digits) <= 11 and digits.startswith('01')


def is_valid_email(s):
    s = s.strip()
    return '@' in s and '.' in s.split('@')[-1] and ' ' not in s


def count_checked(values, fields):
    return sum(1 for f in fields if values.get(f))


def clear_other(player, choice_field, other_field, other_value):
    """'기타'를 고르지 않았는데 기타 입력란에 값이 남아 있으면 지운다."""
    if player.field_maybe_none(choice_field) != other_value:
        setattr(player, other_field, None)


def clear_fields(player, fields):
    for f in fields:
        setattr(player, f, None)


def clear_checkboxes(player, fields):
    for f in fields:
        setattr(player, f, False)


def phone_email_errors(values, phone_field=None, email_field=None):
    """연락처 형식 검사. error_message 에서 그대로 반환하면 된다."""
    errors = {}
    if phone_field and values.get(phone_field) and not is_valid_phone(values[phone_field]):
        errors[phone_field] = '휴대전화 번호를 확인해 주십시오. (예: 010-1234-5678)'
    if email_field and values.get(email_field) and not is_valid_email(values[email_field]):
        errors[email_field] = '이메일 주소를 확인해 주십시오.'
    return errors

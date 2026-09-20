from pathlib import Path

from otree.api import *

from survey_common import *


doc = """
설문 3. 직원 설문 (행사 후 2주 이내, 담당 직원이 전달한 공용 링크로 직원이 직접 접속)
Pilot survey draft 20260910.docx 기준.

- 동의(참여, 개인정보, 민감정보, 후속 연구) -> J1(회사 선택) -> K(기본 정보)
  -> L/M 블록(순서 무작위) -> N(직무만족, 이직, 출산 의향) -> O(연락처) -> 종료
- 회사 연결은 J1 하나뿐이다. 목록은 companies.txt 파일에 회사명을 한 줄에 하나씩 적어 두면
  그대로 드롭다운에 나온다 (행사 후 사전설문 A0 회사명으로 채운다).
  목록에 없으면 "목록에 없음"을 고르고 직접 입력할 수 있다.
- 민감정보(임신 여부 K5, 출산 의향 N3-N5)는 민감정보 동의에 동의한 응답자에게만 표시.
- attention check: M5 여섯 번째 행 ("다소 동의" = 4), 실패 여부는 attn_fail_emp
"""


def company_list():
    """companies.txt 의 회사명 목록 (한 줄에 하나). 파일이 없으면 빈 목록."""
    path = Path(__file__).parent / 'companies.txt'
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith('#')]


def company_choices():
    names = company_list()
    choices = [[i + 1, name] for i, name in enumerate(names)]
    choices.append([999, '목록에 없음 (직접 입력)'])
    return choices


class C(BaseConstants):
    NAME_IN_URL = 'survey3_employee'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    COMPANY_NOT_LISTED = 999

    FLEX_ITEMS = [
        '시차출퇴근제',
        '선택근로제',
        '코어타임제 (공통 근무시간대만 고정, 나머지는 자율)',
        '재택/원격근무제',
        '시간단위 휴가 (반차, 반반차)',
        '육아기 근로시간 단축',
        '가족돌봄휴가',
        '배우자 출산휴가',
        '육아휴직',
    ]

    L1_SCALE = [
        [1, '사용할 수 있음'],
        [2, '비공식적으로 가능'],
        [3, '사용할 수 없음'],
        [4, '잘 모름'],
    ]
    FREQ5 = [[1, '전혀 없음'], [2, '드물게'], [3, '가끔'], [4, '자주'], [5, '매우 자주']]
    M1_SCALE = [[1, '예'], [2, '아니오'], [3, '잘 모름']]

    ATTN_CORRECT = 4  # M5 attention check 정답 "다소 동의"

    PREFER_NOT = 9  # 민감 문항의 "응답을 원하지 않음" 보기


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    block_order = models.StringField()  # 'LM' = L 먼저, 'ML' = M 먼저
    attn_fail_emp = models.BooleanField()
    finished = models.BooleanField(initial=False)

    # ----------------------------------------------------------------- 동의
    consent_participate = models.BooleanField(
        label='위 내용을 확인했으며 설문 참여에 동의합니다.',
        widget=widgets.CheckboxInput,
        blank=True,
    )
    consent_privacy = models.IntegerField(
        label='개인정보 수집 및 이용 동의',
        choices=[
            [1, '개인정보 수집 및 이용에 동의합니다'],
            [0, '개인정보 수집 및 이용에 동의하지 않습니다'],
        ],
        widget=widgets.RadioSelect,
    )
    consent_sensitive = models.IntegerField(
        label='민감정보 수집 및 이용 동의',
        choices=[
            [1, '민감정보 수집 및 이용에 동의합니다'],
            [0, '민감정보 수집 및 이용에 동의하지 않습니다 (해당 문항은 표시되지 않습니다)'],
        ],
        widget=widgets.RadioSelect,
    )
    consent_followup = models.IntegerField(
        label='후속 연구 연락에 대한 동의 (선택)',
        choices=[[1, '후속 연구 연락에 동의합니다'], [0, '후속 연구 연락에 동의하지 않습니다']],
        widget=widgets.RadioSelect,
    )

    # ----------------------------------------------------------------- J1. 회사
    j1 = models.IntegerField(label='재직 중인 회사', choices=company_choices())
    j1_other = text('회사명 직접 입력')

    # ----------------------------------------------------------------- K. 기본 정보
    k1 = radio('K1. 성별', [[1, '남성'], [2, '여성']])
    k2 = radio(
        'K2. 연령대',
        [[1, '20대 이하'], [2, '30대'], [3, '40대'], [4, '50대'], [5, '60대 이상']],
    )
    k3 = radio('K3. 혼인 상태', MARITAL)
    k4 = radio('K4. 자녀가 있습니까?', [[1, '없음'], [2, '있음']])
    k4_1 = number('K4-1. 자녀는 모두 몇 명입니까? (명)', max=20)
    k4_2_1 = number('첫째 (세)', max=70)
    k4_2_2 = number('둘째 (세)', max=70)
    k4_2_3 = number('셋째 (세)', max=70)
    k4_2_4 = number('넷째 이상 (여러 명이면 가장 어린 자녀, 세)', max=70)
    k5 = radio('K5. 현재 본인 또는 배우자가 임신 중입니까?', YES_NO)  # 민감정보
    k6 = radio(
        'K6. 직무 유형',
        [
            [1, '사무직'],
            [2, '생산직/현장직'],
            [3, '서비스직'],
            [4, '영업직'],
            [5, '관리직'],
            [6, '기타'],
        ],
    )
    k7 = radio(
        'K7. 고용 형태',
        [[1, '정규직'], [2, '계약직'], [3, '파견/용역'], [4, '기타']],
    )
    k8 = radio(
        'K8. 현재 회사 재직 기간',
        [[1, '1년 미만'], [2, '1-3년'], [3, '4-6년'], [4, '7년 이상']],
    )
    k9 = radio(
        'K9. 주당 평균 근무시간',
        [[1, '40시간 미만'], [2, '40-44시간'], [3, '45-52시간'], [4, '52시간 초과']],
    )
    k10 = radio(
        'K10. 초과근무(야근, 주말근무) 빈도',
        [[1, '거의 없음'], [2, '월 1-2회'], [3, '주 1-2회'], [4, '주 3회 이상']],
    )
    k11 = radio('K11. 최종 학력', EDUCATION)
    k12 = radio(
        'K12. 현재 거주하시는 주택의 형태',
        [[1, '자가'], [2, '전세'], [3, '월세 (반전세 포함)'], [4, '기타 (부모님 집, 기숙사, 무상 거주 등)']],
    )
    k13 = number('K13. 월평균 가구소득 (만원)', max=100000)
    k13_1 = number('K13-1. 월평균 본인 노동소득 (만원)', max=100000)
    k13_2 = number('K13-2. 월평균 배우자 노동소득 (만원, 소득이 없으면 0)', max=100000)

    # ----------------------------------------------------------------- L. 유연근무
    l1_1 = radio(C.FLEX_ITEMS[0], C.L1_SCALE)
    l1_2 = radio(C.FLEX_ITEMS[1], C.L1_SCALE)
    l1_3 = radio(C.FLEX_ITEMS[2], C.L1_SCALE)
    l1_4 = radio(C.FLEX_ITEMS[3], C.L1_SCALE)
    l1_5 = radio(C.FLEX_ITEMS[4], C.L1_SCALE)
    l1_6 = radio(C.FLEX_ITEMS[5], C.L1_SCALE)
    l1_7 = radio(C.FLEX_ITEMS[6], C.L1_SCALE)
    l1_8 = radio(C.FLEX_ITEMS[7], C.L1_SCALE)
    l1_9 = radio(C.FLEX_ITEMS[8], C.L1_SCALE)

    l2 = radio(
        'L2. 지난 12개월 동안 귀하는 위 제도 중 하나 이상을 실제로 사용한 적이 있습니까?',
        [[1, '예'], [2, '아니오'], [3, '해당 없음']],
    )

    l3_1 = check('제도가 없음')
    l3_2 = check('제도가 있는지 몰랐음')
    l3_3 = check('업무상 사용하기 어려움')
    l3_4 = check('상사 눈치가 보임')
    l3_5 = check('동료에게 부담이 갈까 걱정됨')
    l3_6 = check('인사평가나 승진에 불리할까 걱정됨')
    l3_7 = check('소득 감소가 걱정됨')
    l3_8 = check('사용 대상이 아니라고 생각함')
    l3_9 = check('사용할 필요가 없었음')
    l3_10 = check('기타')
    l3_other = text('기타 (직접 입력)')

    l4_1 = radio('우리 회사에서는 유연근무제를 사용해도 불이익이 없을 것 같다', AGREE5)
    l4_2 = radio('우리 회사의 상사는 직원의 일가정 양립을 지지한다', AGREE5)
    l4_3 = radio('우리 회사에서는 육아나 가족돌봄 때문에 근무시간 조정을 요청하기 어렵다', AGREE5)
    l4_4 = radio('유연근무제를 사용하면 동료에게 부담이 갈 것 같다', AGREE5)
    l4_5 = radio('우리 회사에서는 장시간 근무하는 직원이 더 성실하다고 여겨지는 편이다', AGREE5)

    l5_1 = radio('일 때문에 가족 또는 개인 생활에 충분한 시간을 쓰기 어려웠다', C.FREQ5)
    l5_2 = radio('가족 또는 개인 사정 때문에 업무에 집중하기 어려웠다', C.FREQ5)
    l5_3 = radio('근무시간을 예측하기 어려워 개인 일정을 잡기 어려웠다', C.FREQ5)
    l5_4 = radio('육아, 돌봄, 가사와 일을 병행하는 데 부담을 느꼈다', C.FREQ5)

    l6_1 = radio('육아휴직, 육아기 근로시간 단축 등이 필요할 때 우리 회사에서 부담 없이 사용할 수 있다', AGREE5)
    l6_2 = radio('자녀를 한 명 더 낳는다고 해도 회사 생활을 계속할 수 있을 것 같다', AGREE5)

    l7_1 = radio('그때가 되면 육아휴직 등 일가정양립 제도를 사용하고 싶다', AGREE5)
    l7_2 = radio('우리 회사에서 실제로 그런 제도를 사용할 수 있을 것이라고 생각한다', AGREE5)
    l7_3 = radio('출산과 육아 때문에 회사를 그만두게 될까 걱정된다', AGREE5)

    # ----------------------------------------------------------------- M. 노무관리
    m1_1 = radio('회사에 직장 내 괴롭힘이나 고충을 신고할 수 있는 창구(담당자)가 있다', C.M1_SCALE)
    m1_2 = radio('직장 내 괴롭힘을 당했을 때 어디에 어떻게 신고하는지 알고 있다', C.M1_SCALE)
    m1_3 = radio('회사에 고충이나 불만을 제기할 수 있는 공식 절차(고충처리 제도)가 있다', C.M1_SCALE)
    m1_4 = radio('지난 1년간 회사에서 직장 내 괴롭힘 예방교육을 받았다', C.M1_SCALE)

    m2 = radio(
        'M2. 지난 12개월 동안 직장에서 직장 내 괴롭힘을 경험하거나 목격한 적이 있습니까?',
        [
            [1, '본인이 직접 겪은 적이 있다'],
            [2, '다른 직원이 겪는 것을 본 적이 있다'],
            [3, '없다'],
        ],
    )
    m3 = radio(
        'M3. 지난 12개월 동안 회사에 고충이나 불만을 제기한 적이 있습니까?',
        [
            [1, '예, 공식 절차로 제기했다'],
            [2, '예, 상사에게 비공식적으로 말했다'],
            [3, '제기하고 싶었지만 하지 못했다'],
            [4, '제기할 일이 없었다'],
        ],
    )
    m4 = radio(
        'M4. 제기하지 못한 가장 큰 이유는 무엇입니까?',
        [
            [1, '불이익이 걱정되어서'],
            [2, '말해도 바뀌지 않을 것 같아서'],
            [3, '어디에 말해야 할지 몰라서'],
            [4, '기타'],
        ],
    )
    m4_other = text('기타 (직접 입력)')

    m5_1 = radio('부당한 대우를 받으면 회사에 문제를 제기할 수 있다', AGREE5)
    m5_2 = radio('회사는 직원들의 의견을 의사결정에 반영하려고 노력한다', AGREE5)
    m5_3 = radio('나는 회사 경영진을 신뢰한다', AGREE5)
    m5_4 = radio('회사에 문제를 제기하면 불이익을 받을까 걱정된다', AGREE5)
    m5_5 = radio('우리 회사에서는 세대(나이) 차이 때문에 상사나 동료와 소통하기 어렵다', AGREE5)
    m5_attn = radio('이 문항은 응답 확인용입니다. "다소 동의"를 선택해 주십시오', AGREE5)
    m5_6 = radio('우리 회사는 상사의 지시에 반드시 복종해야 하는 분위기가 강하다', AGREE5)

    m6_1 = radio('우리 회사에서는 결혼, 임신, 출산을 이유로 퇴사 압력을 받는 일이 없다', AGREE6)
    m6_2 = radio(
        '우리 회사는 임신 근로자에 대한 법정 의무(태아검진시간, 근로시간 단축, 시간외근로 금지 등)를 지킨다',
        AGREE6,
    )
    m6_3 = radio('출산휴가나 육아휴직 후 복귀한 직원은 이전과 동일하거나 동등한 업무로 복귀한다', AGREE6)
    m6_4 = radio('남성 직원도 배우자 출산휴가나 육아휴직을 부담 없이 사용할 수 있다', AGREE6)

    # ----------------------------------------------------------------- N. 직무만족, 향후 계획
    n1 = radio(
        'N1. 현재 직장에 대한 만족도는 어느 정도입니까?',
        [[1, '매우 불만족'], [2, '다소 불만족'], [3, '보통'], [4, '다소 만족'], [5, '매우 만족']],
    )
    n2_1 = radio('앞으로 2년 이상 이 회사에서 계속 일할 생각이다', AGREE5)
    n2_2 = radio('요즘 다른 직장으로 옮기는 것을 생각해 본 적이 있다', AGREE5)
    n2_3 = radio('조건이 맞는 다른 일자리가 있다면 옮길 의향이 있다', AGREE5)

    n3 = radio(  # 민감정보
        'N3. 앞으로 3년 이내의 가족 계획에 가장 가까운 것은 무엇입니까?',
        [
            [1, '자녀를 가질 계획이 있다'],
            [2, '갖고 싶지만 아직 결정하지 못했다'],
            [3, '계획이 없다'],
            [4, '해당 없음'],
            [C.PREFER_NOT, '응답을 원하지 않음'],
        ],
    )
    n4 = number('N4. 앞으로 3년 이내에 자녀를 가질(또는 더 가질) 가능성', max=100)  # 민감정보
    n4_refuse = check('응답을 원하지 않음')
    n5_1 = check('결혼(또는 동거) 계획이 없어서')  # 민감정보
    n5_2 = check('자녀 계획을 이미 마쳤거나 더 가질 생각이 없어서')
    n5_3 = check('나이 또는 건강상 이유로')
    n5_4 = check('본인 또는 배우자가 현재 임신 중이어서')
    n5_5 = check('기타')
    n5_6 = check('응답을 원하지 않음')
    n5_other = text('기타 (직접 입력)')

    # ----------------------------------------------------------------- O. 연락처
    o1 = text('휴대전화 번호')
    o2 = radio(
        'O2. 첫 화면에서 동의하신 개인정보(휴대전화 번호) 수집 및 이용 동의를 다시 확인해 주십시오.',
        [[1, '동의함'], [0, '동의하지 않음 (상품권 및 후속 설문 안내 불가)']],
    )
    o3 = radio('O3. 6개월, 12개월 후 후속 설문 안내를 받으시겠습니까?', YES_NO)


# ---------------------------------------------------------------------------
# 필드 묶음
# ---------------------------------------------------------------------------
K4_2_FIELDS = field_names('k4_2_', 4)
L1_FIELDS = field_names('l1_', 9)
L3_FIELDS = field_names('l3_', 10)
L4_FIELDS = field_names('l4_', 5)
L5_FIELDS = field_names('l5_', 4)
L6_FIELDS = field_names('l6_', 2)
L7_FIELDS = field_names('l7_', 3)
M1_FIELDS = field_names('m1_', 4)
M5_FIELDS = ['m5_1', 'm5_2', 'm5_3', 'm5_4', 'm5_5', 'm5_attn', 'm5_6']
M6_FIELDS = field_names('m6_', 4)
N2_FIELDS = field_names('n2_', 3)
N5_FIELDS = field_names('n5_', 6)  # 6번은 "응답을 원하지 않음"
SENSITIVE_FIELDS = ['k5', 'n3', 'n4', 'n4_refuse'] + N5_FIELDS + ['n5_other']


def sensitive_ok(player: Player):
    return player.consent_sensitive == 1


def privacy_ok(player: Player):
    return player.consent_privacy == 1


def has_children(player: Player):
    return player.field_maybe_none('k4') == 2


def creating_session(subsession: Subsession):
    assign_block_order(subsession, orders=('LM', 'ML'))


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------
class SurveyPage(Page):
    pass


class Consent(SurveyPage):
    form_model = 'player'
    form_fields = [
        'consent_participate',
        'consent_privacy',
        'consent_sensitive',
        'consent_followup',
    ]

    @staticmethod
    def error_message(player: Player, values):
        if not values['consent_participate']:
            return dict(consent_participate='설문 참여에 동의하셔야 다음으로 넘어갈 수 있습니다. 위 항목에 체크해 주십시오.')


class J1(SurveyPage):
    form_model = 'player'
    form_fields = ['j1', 'j1_other']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(no_company_list=len(company_list()) == 0)

    @staticmethod
    def error_message(player: Player, values):
        if values['j1'] == C.COMPANY_NOT_LISTED and not values.get('j1_other'):
            return dict(j1_other='재직 중인 회사명을 적어 주십시오.')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'j1', 'j1_other', C.COMPANY_NOT_LISTED)


class K1(SurveyPage):
    """K1-K5 (자녀, 임신)"""

    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['k1', 'k2', 'k3', 'k4', 'k4_1'] + K4_2_FIELDS
        if sensitive_ok(player):
            fields.append('k5')
        return fields

    @staticmethod
    def error_message(player: Player, values):
        n = values.get('k4_1')
        if values.get('k4') == 2 and n is not None:
            filled = sum(1 for f in K4_2_FIELDS if values.get(f) is not None)
            if filled > n:
                return dict(k4_1='자녀 수보다 많은 나이를 적으셨습니다. 확인해 주십시오.')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not has_children(player):
            clear_fields(player, ['k4_1'] + K4_2_FIELDS)


class K6(SurveyPage):
    """K6-K12 근무 실태"""

    form_model = 'player'
    form_fields = ['k6', 'k7', 'k8', 'k9', 'k10', 'k11', 'k12']


class K13(SurveyPage):
    """K13, K13-1, K13-2 (한 화면)"""

    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['k13', 'k13_1']
        if player.field_maybe_none('k3') == 2:  # 기혼
            fields.append('k13_2')
        return fields

    @staticmethod
    def error_message(player: Player, values):
        total = values.get('k13')
        if total is None:
            return
        errors = {}
        if values.get('k13_1') is not None and values['k13_1'] > total:
            errors['k13_1'] = '가구소득보다 클 수 없습니다. 확인해 주십시오.'
        if values.get('k13_2') is not None and values['k13_2'] > total:
            errors['k13_2'] = '가구소득보다 클 수 없습니다. 확인해 주십시오.'
        return errors


# ----------------------------- L 블록 -----------------------------
class L1(SurveyPage):
    """L1 + L2 + L3"""

    form_model = 'player'
    form_fields = L1_FIELDS + ['l2'] + L3_FIELDS + ['l3_other']
    block = 'L'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(l1=matrix(L1_FIELDS, C.L1_SCALE), l3=checkboxes(L3_FIELDS, max_n=2))

    @staticmethod
    def error_message(player: Player, values):
        errors = other_text_errors(values, [('l3_10', 'l3_other')])
        if values.get('l2') == 2 and count_checked(values, L3_FIELDS) > 2:
            errors['l3_1'] = '최대 2개까지 선택해 주십시오.'
        return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('l2') != 2:
            clear_checkboxes(player, L3_FIELDS)
            player.l3_other = None
        elif not player.l3_10:
            player.l3_other = None


class L4(SurveyPage):
    """L4 + L5 + (자녀 유무에 따라) L6 또는 L7"""

    form_model = 'player'
    block = 'L'

    @staticmethod
    def get_form_fields(player: Player):
        extra = L6_FIELDS if has_children(player) else L7_FIELDS
        return L4_FIELDS + L5_FIELDS + extra

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            l4=matrix(L4_FIELDS, AGREE5),
            l5=matrix(L5_FIELDS, C.FREQ5),
            l6=matrix(L6_FIELDS, AGREE5),
            l7=matrix(L7_FIELDS, AGREE5),
            has_children=has_children(player),
        )


# ----------------------------- M 블록 -----------------------------
class M1(SurveyPage):
    """M1 + M2 + M3 + M4"""

    form_model = 'player'
    form_fields = M1_FIELDS + ['m2', 'm3', 'm4', 'm4_other']
    block = 'M'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(m1=matrix(M1_FIELDS, C.M1_SCALE))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('m3') != 3:
            player.m4 = None
        clear_other(player, 'm4', 'm4_other', 4)


class M5(SurveyPage):
    """M5 + M6"""

    form_model = 'player'
    form_fields = M5_FIELDS + M6_FIELDS
    block = 'M'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(m5=matrix(M5_FIELDS, AGREE5), m6=matrix(M6_FIELDS, AGREE6))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.attn_fail_emp = player.field_maybe_none('m5_attn') != C.ATTN_CORRECT


# ----------------------------- N, O -----------------------------
class N(SurveyPage):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['n1'] + N2_FIELDS
        if sensitive_ok(player):
            fields += ['n3', 'n4', 'n4_refuse'] + N5_FIELDS + ['n5_other']
        return fields

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            n2=matrix(N2_FIELDS, AGREE5),
            n5=checkboxes(N5_FIELDS, exclusive='n5_6'),
            sensitive=sensitive_ok(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = other_text_errors(values, [('n5_5', 'n5_other')])
        if values.get('n5_6') and count_checked(values, N5_FIELDS[:-1]) > 0:
            errors['n5_1'] = '"응답을 원하지 않음"은 다른 항목과 함께 선택할 수 없습니다.'
        return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not sensitive_ok(player):
            return
        n3 = player.field_maybe_none('n3')
        # N4는 N3에서 ①-③을 고른 경우에만, N5는 "해당 없음"을 고른 경우에만 묻는다
        if n3 != 4:
            clear_checkboxes(player, N5_FIELDS)
            player.n5_other = None
        if n3 not in (1, 2, 3) or player.field_maybe_none('n4_refuse'):
            player.n4 = None
        if not player.field_maybe_none('n5_5'):
            player.n5_other = None


class O(SurveyPage):
    form_model = 'player'

    @staticmethod
    def is_displayed(player: Player):
        return privacy_ok(player)

    @staticmethod
    def get_form_fields(player: Player):
        return ['o1', 'o2', 'o3']

    @staticmethod
    def error_message(player: Player, values):
        return phone_email_errors(values, phone_field='o1')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('o2') == 0:
            player.o1 = None


class End(SurveyPage):
    @staticmethod
    def vars_for_template(player: Player):
        player.finished = True
        # 상품권 안내는 휴대전화 번호를 실제로 남긴 분에게만 보여준다
        # (O2에서 동의를 철회하면 번호가 지워진다)
        return dict(has_phone=bool(player.field_maybe_none('o1')))


L_PAGES = [L1, L4]
M_PAGES = [M1, M5]

page_sequence = (
    [Consent, J1, K1, K6, K13]
    + [make_positioned('survey3_employee', p, 1) for p in L_PAGES + M_PAGES]
    + [make_positioned('survey3_employee', p, 2) for p in L_PAGES + M_PAGES]
    + [N, O, End]
)

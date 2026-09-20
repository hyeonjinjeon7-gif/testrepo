from otree.api import *

from survey_common import *


doc = """
설문 2-1. 사후설문 --- control(대조) 그룹 (그룹 2 --- 노무관리 이슈 특강)
Pilot survey draft 20260910.docx 기준. 강연 직후 대표/인사관리자가 응답.

- 동의 -> A0(회사명, 연락처) -> D(강연 평가) -> E(의향) -> F(이 그룹의 어려움과 필요한 지원)
  -> G(실제 행동) -> H(직원 설문 협조) -> I(추적 동의, 행정자료) -> V(경영 현황) -> W(응답자 정보) -> 종료
- 이 설문은 2 강연장(파란 목줄)에만 비치하는 QR로 접속한다.
  F 블록만 그룹별로 다르고, 나머지 문항은 설문 2-2과 같다.
- E3/E4, E5/E6 의 제시 순서는 응답자마다 무작위 (e34_order, e56_order 에 기록)
- attention check: E4 네 번째 행 ("검토 가능" = 2), 실패 여부는 attn_fail_post
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey2_1_control'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # 이 설문이 담당하는 강연 그룹 (control: 그룹 2 --- 노무관리 이슈 특강)
    GROUP = 2

    # E3 제도 목록
    E3_ITEMS = [
        '시차출퇴근제',
        '선택근로제',
        '코어타임제',
        '재택/원격근무제',
        '시간단위 휴가 (반차, 반반차)',
        '육아기 근로시간 단축',
        '가족돌봄휴가',
        '배우자 출산휴가',
        '육아휴직 사용 장려',
    ]

    # F2-그룹2 (노무관리) 필요한 지원
    F2_LABOR = [
        '취업규칙의 직장 내 괴롭힘 규정 표준 서식',
        '괴롭힘 신고 접수와 조사 절차 매뉴얼',
        '괴롭힘 인정과 불인정 사례집',
        '2026년 노동법 개정 사항 대응 안내',
        '관리자 교육자료 (세대 갈등, 소통 방식)',
        '노무사 또는 전문가 상담',
        '유사 기업 분쟁 사례',
        '필요 없음',
        '기타',
    ]

    SALES_BRACKETS = [
        [1, '5억원 미만'],
        [2, '5억원 이상 10억원 미만'],
        [3, '10억원 이상 30억원 미만'],
        [4, '30억원 이상 50억원 미만'],
        [5, '50억원 이상 100억원 미만'],
        [6, '100억원 이상 300억원 미만'],
        [7, '300억원 이상'],
    ]

    ATTN_CORRECT = 2  # E4 attention check 정답 "검토 가능"


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    lecture_group = models.IntegerField()  # 이 설문은 항상 C.GROUP
    e34_order = models.StringField()  # '34' 또는 '43'
    e56_order = models.StringField()  # '56' 또는 '65'
    attn_fail_post = models.BooleanField()
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
            [0, '개인정보 수집 및 이용에 동의하지 않습니다 (설문 연결과 사례 지급이 불가능합니다)'],
        ],
        widget=widgets.RadioSelect,
    )

    # ----------------------------------------------------------------- A0
    a0 = models.StringField(label='회사명')
    a0_1_phone = text('휴대전화')
    a0_1_email = text('이메일')

    # ----------------------------------------------------------------- D. 강연 평가
    d0 = radio(
        'D0. 오늘 강연에 처음부터 참석하셨습니까?',
        [[1, '처음부터 참석'], [2, '10분 이내 늦게 입장'], [3, '10-30분 늦게 입장'], [4, '30분 이상 늦게 입장']],
    )
    d1 = radio(
        'D1. 오늘 강연 내용을 어느 정도 이해하셨습니까?',
        [[1, '거의 이해하지 못함'], [2, '일부만 이해'], [3, '보통'], [4, '대체로 이해'], [5, '매우 잘 이해']],
    )
    d2 = radio(
        'D2. 오늘 강연에 전반적으로 얼마나 만족하십니까?',
        [[1, '매우 불만족'], [2, '다소 불만족'], [3, '보통'], [4, '다소 만족'], [5, '매우 만족']],
    )
    d3 = radio(
        'D3. 오늘 강연 내용이 귀사(현 소속)의 경영에 얼마나 유용하다고 생각하십니까?',
        [[1, '전혀 유용하지 않음'], [2, '별로 유용하지 않음'], [3, '보통'], [4, '다소 유용함'], [5, '매우 유용함']],
    )
    d4 = long_text('D4. 오늘 강연에서 새로 알게 된 내용이 있다면 한 가지만 적어 주십시오.')
    d5 = radio(
        'D5. 오늘 강연에서 소개된 내용 중 귀사(현 소속)에 실제로 적용해 보고 싶은 것이 있습니까?',
        [[1, '예'], [2, '아직 판단하기 어려움'], [3, '아니오']],
    )
    d5_text = text('어떤 내용입니까?')

    # ----------------------------------------------------------------- E. 의향
    e1 = number(
        'E1. 오늘 강연 이후, 귀사(현 소속)는 향후 6개월 내 유연근무제 또는 일가정양립 제도를 새로 도입하거나 확대할 의향이 얼마나 있습니까?',
        max=100,
    )
    e2 = number(
        'E2. 오늘 강연 이후, 귀사(현 소속)는 향후 6개월 내 노무관리 체계(취업규칙의 괴롭힘 규정, 신고와 조사 절차, 관리자 교육, 노무사 자문 등)를 정비하거나 개선할 의향이 얼마나 있습니까?',
        max=100,
    )

    e3_1 = radio(C.E3_ITEMS[0], INTENT5_ADOPT)
    e3_2 = radio(C.E3_ITEMS[1], INTENT5_ADOPT)
    e3_3 = radio(C.E3_ITEMS[2], INTENT5_ADOPT)
    e3_4 = radio(C.E3_ITEMS[3], INTENT5_ADOPT)
    e3_5 = radio(C.E3_ITEMS[4], INTENT5_ADOPT)
    e3_6 = radio(C.E3_ITEMS[5], INTENT5_ADOPT)
    e3_7 = radio(C.E3_ITEMS[6], INTENT5_ADOPT)
    e3_8 = radio(C.E3_ITEMS[7], INTENT5_ADOPT)
    e3_9 = radio(C.E3_ITEMS[8], INTENT5_ADOPT)

    e4_1 = radio('취업규칙에 직장 내 괴롭힘 예방과 조치 규정 신설 또는 정비', INTENT5_ACT)
    e4_2 = radio('괴롭힘, 고충 신고 창구와 조사 절차 마련', INTENT5_ACT)
    e4_3 = radio('직원 대상 직장 내 괴롭힘 예방교육 실시', INTENT5_ACT)
    e4_attn = radio('이 문항은 응답 확인용입니다. "검토 가능"을 선택해 주십시오', INTENT5_ACT)
    e4_4 = radio('관리자 대상 노동법, 갈등 관리 교육', INTENT5_ACT)
    e4_5 = radio('세대 간 소통을 위한 제도 (정기 면담, 보상 기준 공개, 소통 채널 등)', INTENT5_ACT)
    e4_6 = radio('노무사 자문 계약 또는 상담', INTENT5_ACT)

    # E5 = 설문 1의 B15, E6 = 설문 1의 C4 (반복 측정)
    e5_1 = radio('직원이 눈에 보이지 않으면 일을 제대로 하지 않을 것 같다', AGREE5)
    e5_2 = radio('유연근무는 우리 회사의 업종이나 규모에는 맞지 않는다', AGREE5)
    e5_3 = radio('유연근무를 도입하면 생산성이 떨어질 것이다', AGREE5)
    e5_4 = radio('일부 직원에게 유연근무를 허용하면 특혜로 비쳐 조직 기강이 흐트러질 것이다', AGREE5)
    e5_5 = radio('유연근무를 운영하려면 관리 부담이 너무 크다', AGREE5)

    e6_1 = radio('업무상 필요한 지적이나 질책은 직장 내 괴롭힘이 될 수 없다', AGREE5)
    e6_2 = radio('우리 회사 규모에서는 직장 내 괴롭힘 신고나 분쟁이 생길 가능성이 낮다', AGREE5)
    e6_3 = radio('괴롭힘 신고가 들어오면 회사가 조사하기보다 당사자끼리 해결하도록 하는 것이 낫다', AGREE5)
    e6_4 = radio('젊은 직원들과의 갈등은 세대 차이 문제라서 회사가 제도적으로 대응할 수 있는 것이 아니다', AGREE5)
    e6_5 = radio('노동법 개정 사항은 노무사에게 맡기면 되므로 대표나 관리자가 직접 알 필요는 없다', AGREE5)

    # ----------------------------------------------------------------- F. 남은 어려움 (그룹별)
    # 그룹 2 (노무관리) --- 설문 1 C8과 같은 보기
    f1g2_1 = check(DIFFICULTY_LABOR[0])
    f1g2_2 = check(DIFFICULTY_LABOR[1])
    f1g2_3 = check(DIFFICULTY_LABOR[2])
    f1g2_4 = check(DIFFICULTY_LABOR[3])
    f1g2_5 = check(DIFFICULTY_LABOR[4])
    f1g2_6 = check(DIFFICULTY_LABOR[5])
    f1g2_7 = check(DIFFICULTY_LABOR[6])
    f1g2_8 = check(DIFFICULTY_LABOR[7])
    f1g2_9 = check(DIFFICULTY_LABOR[8])
    f1g2_10 = check(DIFFICULTY_LABOR[9])
    f1g2_11 = check(DIFFICULTY_LABOR[10])
    f1g2_12 = check(DIFFICULTY_LABOR[11])
    f1g2_other = text('기타 (직접 입력)')

    f2g2_1 = check(C.F2_LABOR[0])
    f2g2_2 = check(C.F2_LABOR[1])
    f2g2_3 = check(C.F2_LABOR[2])
    f2g2_4 = check(C.F2_LABOR[3])
    f2g2_5 = check(C.F2_LABOR[4])
    f2g2_6 = check(C.F2_LABOR[5])
    f2g2_7 = check(C.F2_LABOR[6])
    f2g2_8 = check(C.F2_LABOR[7])
    f2g2_9 = check(C.F2_LABOR[8])
    f2g2_other = text('기타 (직접 입력)')

    # ----------------------------------------------------------------- G. 실제 행동
    g1 = radio('G1. 오늘 강연 주제 관련 체크리스트와 표준 서식 자료를 이메일로 받아보시겠습니까?', YES_NO)
    g2 = radio(
        'G2. 무료 후속 컨설팅(노무사 1:1 상담)을 신청하시겠습니까?',
        [[1, '예, 신청하고 싶음'], [2, '나중에 검토하고 싶음'], [3, '아니오']],
    )
    g3 = radio('G3. 귀사(현 소속) 상황에 맞는 도입 및 정비 계획서를 간단히 작성해 보시겠습니까?', YES_NO)
    g3_items = text('검토하고 싶은 제도 또는 조치')
    g3_timing = text('예상 시점')
    g3_owner = text('내부 담당자')
    g3_support = text('추가로 필요한 지원')

    # ----------------------------------------------------------------- H. 직원 설문 협조
    h1 = radio(
        'H1. 직원분들께 설문 안내를 전달해 주실 담당 직원을 지정해 주실 수 있습니까?',
        [[1, '예, 지금 아래에 적겠음'], [2, '예, 돌아오는 월요일에 연구팀 이메일에 회신하겠음'], [3, '아니오']],
    )
    h1_1 = radio(
        'H1-1. 대표님 휴대전화로 직원용 안내 문자를 보내드리면 직접 직원분들께 전달해 주실 수 있습니까?',
        YES_NO,
    )
    h2 = number('H2. 안내를 전달받을 직원은 대략 몇 명입니까?', max=10000)
    h3_name = text('담당 직원 성함')
    h3_title = text('직책')
    h3_email = text('이메일')

    # ----------------------------------------------------------------- I. 추적 동의
    i1 = radio(
        'I1. 본 연구는 6개월, 12개월 후에 짧은 후속 설문(약 5-7분)을 진행합니다. 참여해 주시겠습니까?',
        YES_NO,
    )
    a8_consent = radio(
        'A8. (선택) 고용보험 등 행정자료 연계에 동의하십니까?',
        [[1, '동의함'], [0, '동의하지 않음']],
    )
    a8_biz_no = text('사업자등록번호')
    a8_ei_no = text('고용보험사업장관리번호')

    # ----------------------------------------------------------------- V. 경영 현황
    v1 = number('V1. 직전 회계연도(2025년) 귀사(현 소속)의 총 매출액 (백만원)', max=100000000)
    v1_1 = radio('V1-1. 직전 회계연도 총 매출액에 가장 가까운 구간', C.SALES_BRACKETS)
    v2 = number('V2. 3년 전(2022년) 귀사(현 소속)의 총 매출액 (백만원, 당시 창업 전이면 0)', max=100000000)
    v2_1 = radio('V2-1. 3년 전 총 매출액에 가장 가까운 구간', C.SALES_BRACKETS)
    v3_regular = number('정규직', max=100000)
    v3_nonregular = number('비정규직', max=100000)
    v4 = number('V4. 정규직 직원의 주당 평균 실제 근로시간 (시간)', max=168)
    v5 = number('V5. 직전 회계연도 매출액에서 인건비가 차지하는 비중 (%)', max=100)
    v6 = number('V6. 직전 회계연도 매출액에서 외부 구입 재화와 서비스 비용의 비중 (%)', max=100)
    v7 = number('V7. 직전 회계연도 유형자산 신규 투자액 (백만원, 없으면 0)', max=100000000)
    v8 = number('V8. 귀사(현 소속)의 사업장은 모두 몇 개입니까? (개)', max=10000)

    # ----------------------------------------------------------------- W. 응답자 기본 정보
    w1 = radio('W1. 성별', [[1, '남성'], [2, '여성']])
    w2 = number('W2. 만 나이 (세)', min=15, max=100)
    w3 = radio('W3. 최종 학력', EDUCATION)
    w4 = radio('W4. 혼인 상태', MARITAL)
    w5 = radio('W5. 자녀가 있습니까?', [[1, '없음'], [2, '있음']])
    w5_1 = number('W5-1. 자녀는 모두 몇 명입니까? (명)', max=20)
    w6 = radio('W6. 현재 거주하시는 주택의 형태', HOUSING)


# ---------------------------------------------------------------------------
# 필드 묶음
# ---------------------------------------------------------------------------
E3_FIELDS = field_names('e3_', 9)
E4_FIELDS = ['e4_1', 'e4_2', 'e4_3', 'e4_attn', 'e4_4', 'e4_5', 'e4_6']
E5_FIELDS = field_names('e5_', 5)
E6_FIELDS = field_names('e6_', 5)
F1_FIELDS = field_names('f1g2_', 12)
F2_FIELDS = field_names('f2g2_', 9)
V3_FIELDS = ['v3_regular', 'v3_nonregular']


def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        p.lecture_group = C.GROUP
    assign_block_order(subsession, orders=('34', '43'), field='e34_order')
    assign_block_order(subsession, orders=('56', '65'), field='e56_order')


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------
class SurveyPage(Page):
    pass


class Consent(SurveyPage):
    form_model = 'player'
    form_fields = ['consent_participate', 'consent_privacy']

    @staticmethod
    def error_message(player: Player, values):
        if not values['consent_participate']:
            return dict(consent_participate='설문 참여에 동의하셔야 다음으로 넘어갈 수 있습니다. 위 항목에 체크해 주십시오.')

class A0(SurveyPage):
    form_model = 'player'
    form_fields = ['a0', 'a0_1_phone', 'a0_1_email']

    @staticmethod
    def error_message(player: Player, values):
        return phone_email_errors(values, 'a0_1_phone', 'a0_1_email')


class D(SurveyPage):
    form_model = 'player'
    form_fields = ['d0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd5_text']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'd5', 'd5_text', 1)


class E12(SurveyPage):
    form_model = 'player'
    form_fields = ['e1', 'e2']


class E34(SurveyPage):
    """E3(유연근무 제도별 의향)와 E4(노무관리 조치별 의향), 순서 무작위"""

    form_model = 'player'
    form_fields = E3_FIELDS + E4_FIELDS

    @staticmethod
    def vars_for_template(player: Player):
        e3 = dict(
            matrix(E3_FIELDS, INTENT5_ADOPT),
            title='E3. 귀사(현 소속)는 향후 6개월 내 다음 제도를 도입하거나 확대할 의향이 있습니까?',
        )
        e4 = dict(
            matrix(E4_FIELDS, INTENT5_ACT),
            title='E4. 귀사(현 소속)는 향후 6개월 내 다음 노무관리 조치를 실행할 의향이 있습니까?',
        )
        return dict(tables=[e3, e4] if player.e34_order == '34' else [e4, e3])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.attn_fail_post = player.field_maybe_none('e4_attn') != C.ATTN_CORRECT


class E56(SurveyPage):
    """E5(유연근무 우려)와 E6(노무관리 인식), 순서 무작위 --- 사전설문 B15, C4의 반복 측정"""

    form_model = 'player'
    form_fields = E5_FIELDS + E6_FIELDS

    @staticmethod
    def vars_for_template(player: Player):
        e5 = dict(
            matrix(E5_FIELDS, AGREE5),
            title='E5. 오늘 강연을 듣고 난 지금, 유연근무제에 대한 다음 생각에 얼마나 동의하십니까?',
        )
        e6 = dict(
            matrix(E6_FIELDS, AGREE5),
            title='E6. 오늘 강연을 듣고 난 지금, 노무관리에 대한 다음 생각에 얼마나 동의하십니까?',
        )
        return dict(tables=[e5, e6] if player.e56_order == '56' else [e6, e5])


class F(SurveyPage):
    """이 그룹의 남은 어려움과 필요한 지원"""

    form_model = 'player'
    form_fields = F1_FIELDS + ['f1g2_other'] + F2_FIELDS + ['f2g2_other']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            f1=checkboxes(F1_FIELDS, max_n=3),
            f2=checkboxes(F2_FIELDS, max_n=3, exclusive=F2_FIELDS[-2]),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = other_text_errors(
            values, [('f1g2_12', 'f1g2_other'), ('f2g2_9', 'f2g2_other')]
        )
        for fields in [F1_FIELDS, F2_FIELDS]:
            if count_checked(values, fields) > 3:
                errors[fields[0]] = '최대 3개까지 선택해 주십시오.'
        if values.get(F2_FIELDS[-2]) and count_checked(values, F2_FIELDS[:-2]) > 0:
            errors[F2_FIELDS[0]] = '"필요 없음"은 다른 항목과 함께 선택할 수 없습니다.'
        return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # "기타"를 고르지 않았으면 기타 입력란을 비운다
        if not getattr(player, F1_FIELDS[-1]):
            player.f1g2_other = None
        if not getattr(player, F2_FIELDS[-1]):
            player.f2g2_other = None


class G(SurveyPage):
    form_model = 'player'
    form_fields = ['g1', 'g2', 'g3', 'g3_items', 'g3_timing', 'g3_owner', 'g3_support']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('g3') != 1:
            clear_fields(player, ['g3_items', 'g3_timing', 'g3_owner', 'g3_support'])


class H(SurveyPage):
    form_model = 'player'
    form_fields = ['h1', 'h1_1', 'h2', 'h3_name', 'h3_title', 'h3_email']

    @staticmethod
    def error_message(player: Player, values):
        if values.get('h1') == 1 and values.get('h3_email'):
            return phone_email_errors(values, email_field='h3_email')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        h1 = player.field_maybe_none('h1')
        if h1 != 3:
            player.h1_1 = None
        if not (h1 in (1, 2) or player.field_maybe_none('h1_1') == 1):
            player.h2 = None
        if h1 != 1:
            clear_fields(player, ['h3_name', 'h3_title', 'h3_email'])


class I(SurveyPage):
    form_model = 'player'
    form_fields = ['i1', 'a8_consent', 'a8_biz_no', 'a8_ei_no']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('a8_consent') != 1:
            clear_fields(player, ['a8_biz_no', 'a8_ei_no'])


class V(SurveyPage):
    form_model = 'player'
    form_fields = ['v1', 'v1_1', 'v2', 'v2_1'] + V3_FIELDS + ['v4', 'v5', 'v6', 'v7', 'v8']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 금액을 적었으면 구간 응답은 지운다 (V1-1, V2-1은 미입력 시에만 묻는 문항)
        if player.field_maybe_none('v1') is not None:
            player.v1_1 = None
        if player.field_maybe_none('v2') is not None:
            player.v2_1 = None


class W(SurveyPage):
    form_model = 'player'
    form_fields = ['w1', 'w2', 'w3', 'w4', 'w5', 'w5_1', 'w6']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.field_maybe_none('w5') != 2:
            player.w5_1 = None


class End(SurveyPage):
    @staticmethod
    def vars_for_template(player: Player):
        player.finished = True
        return {}


page_sequence = [Consent, A0, D, E12, E34, E56, F, G, H, I, V, W, End]

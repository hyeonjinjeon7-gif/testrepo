import random

from otree.api import *


doc = """
설문 1. 사전설문 (대표/인사관리자 --- 행사 당일, 강연 전)
Pilot survey draft 20260910.docx 기준.

- 동의(연구 참여, 개인정보, 후속 연구 연락) -> A 블록 -> B/C 블록(순서 무작위) -> 종료
- B 블록과 C 블록 제시 순서는 세션 생성 시 절반씩 배정 (block_order = 'BC' 또는 'CB')
- 필수 응답: 동의 문항, A0 (나머지는 응답하지 않으면 확인 창만 띄움)
- attention check: B9 다섯 번째 행 ("영향 없음" = 3), 실패 여부는 attn_fail_pre
- 보기 코드는 설문지에 적힌 순서대로 1, 2, 3 ... (예: B1 1=잘 알고 있다 ... 4=모른다)
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey1_pre'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # B1, B2, B3 공통 제도 목록 (필드 이름의 번호 1-10과 같은 순서)
    INSTITUTIONS = [
        '출산전후휴가',
        '배우자 출산휴가',
        '임신기 근로시간 단축',
        '육아휴직',
        '육아기 근로시간 단축',
        '가족돌봄휴가',
        '시차출퇴근제',
        '선택근로제',
        '코어타임제 (공통 근무시간대만 고정, 나머지는 자율)',
        '재택/원격근무제',
    ]

    KNOW4 = [[1, '잘 알고 있다'], [2, '어느 정도 알고 있다'], [3, '들어본 적 있다'], [4, '모른다']]
    B2_SCALE = [
        [1, '규정에 명시 (취업규칙, 내규 등)'],
        [2, '규정은 없지만 관례적으로 허용'],
        [3, '없음'],
        [4, '잘 모름'],
    ]
    B3_SCALE = [
        [1, '사용자 있음'],
        [2, '대상자는 있으나 사용자 없음'],
        [3, '대상자 없음'],
        [4, '잘 모름'],
    ]
    AGREE5 = [
        [1, '전혀 동의 안 함'],
        [2, '별로 동의 안 함'],
        [3, '보통'],
        [4, '다소 동의'],
        [5, '매우 동의'],
    ]
    EFFECT5 = [
        [1, '매우 부정적'],
        [2, '다소 부정적'],
        [3, '영향 없음'],
        [4, '다소 긍정적'],
        [5, '매우 긍정적'],
    ]
    C1_SCALE = [[1, '예'], [2, '아니오'], [3, '해당 없음'], [4, '잘 모름']]
    C3_SCALE = [
        [1, '전혀 없다'],
        [2, '별로 없다'],
        [3, '어느 정도 있다'],
        [4, '심하다'],
        [5, '해당 없음'],
    ]

    B1_DONT_KNOW = 4  # B1 "모른다"
    B2_NONE = 3  # B2 "없음"
    B7_DONT_KNOW = 4  # B7 "모른다"
    ATTN_CORRECT = 3  # B9 attention check 정답 "영향 없음"

    B8_CHANNELS = [
        [1, '정부기관 홈페이지 (고용24 등)'],
        [2, '고용센터, 콜센터 상담'],
        [3, '정부/지자체 뉴스레터, 이메일 안내'],
        [4, '노무법인 등 외부 자문기관'],
        [5, '사업주 단체, 동종업계 네트워크'],
        [6, '언론보도'],
        [7, '온라인 검색, SNS'],
        [8, '기타'],
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


# ---------------------------------------------------------------------------
# 필드 만들기 도우미
# ---------------------------------------------------------------------------
def radio(label, choices):
    return models.IntegerField(
        label=label, choices=choices, widget=widgets.RadioSelect, blank=True
    )


def check(label):
    return models.BooleanField(label=label, widget=widgets.CheckboxInput, blank=True)


def text(label=''):
    return models.StringField(label=label, blank=True)


def number(label='', min=0, max=None):
    return models.IntegerField(label=label, min=min, max=max, blank=True)


I = C.INSTITUTIONS


class Player(BasePlayer):
    block_order = models.StringField()  # 'BC' = B 먼저, 'CB' = C 먼저
    attn_fail_pre = models.BooleanField()  # B9 attention check 실패 여부
    finished = models.BooleanField(initial=False)

    # ----------------------------------------------------------------- 동의
    consent_participate = models.BooleanField(
        label='위 내용을 확인했으며 설문 참여에 동의합니다.',
        widget=widgets.CheckboxInput,
        blank=True,
    )
    consent_privacy = models.IntegerField(
        label='개인정보 수집 및 이용 동의',
        choices=[[1, '개인정보 수집 및 이용에 동의합니다'], [0, '개인정보 수집 및 이용에 동의하지 않습니다']],
        widget=widgets.RadioSelect,
    )
    consent_followup = models.IntegerField(
        label='후속 연구 연락 동의 (선택)',
        choices=[[1, '후속 연구 연락에 동의합니다'], [0, '후속 연구 연락에 동의하지 않습니다']],
        widget=widgets.RadioSelect,
    )

    # ----------------------------------------------------------------- A. 기업 기본정보
    a0 = models.StringField(label='회사명')
    a0_1_name = text('성함')
    a0_1_phone = text('휴대전화')
    a0_1_email = text('이메일')

    a1 = radio(
        'A1. 귀하의 직위는 무엇입니까?',
        [[1, '대표이사/CEO'], [2, '임원'], [3, '인사/노무 담당 관리자'], [4, '기타 관리자'], [5, '기타']],
    )
    a1_other = text('기타 (직접 입력)')
    a2 = radio(
        'A2. 귀사(현 소속)의 업종은 무엇입니까?',
        [
            [1, '제조업'],
            [2, '건설업'],
            [3, '도소매업'],
            [4, '운수/물류업'],
            [5, '숙박/음식업'],
            [6, '정보통신업'],
            [7, '전문, 과학 및 기술 서비스업'],
            [8, '기타 서비스업'],
            [9, '기타'],
        ],
    )
    a2_other = text('기타 (직접 입력)')
    a3 = number('A3. 귀사(현 소속)의 설립연도는 언제입니까?', min=1900, max=2026)
    a4_regular = number('정규직', max=100000)
    a4_nonregular = number('비정규직', max=100000)

    # A5 성별 x 연령 인원 (m = 남성, f = 여성)
    a5_m_20s = number(max=100000)
    a5_m_30s = number(max=100000)
    a5_m_40s = number(max=100000)
    a5_m_50s = number(max=100000)
    a5_m_60s = number(max=100000)
    a5_f_20s = number(max=100000)
    a5_f_30s = number(max=100000)
    a5_f_40s = number(max=100000)
    a5_f_50s = number(max=100000)
    a5_f_60s = number(max=100000)
    a5_m_total = models.IntegerField()  # 자동 계산 (응답 페이지에는 표시만)
    a5_f_total = models.IntegerField()

    a6 = radio(
        'A6. 귀사(현 소속)에 인사/노무 업무를 전담하는 직원이 있습니까?',
        [[1, '전담 직원 있음'], [2, '다른 업무와 겸직'], [3, '대표가 직접 담당'], [4, '외부에 위탁']],
    )
    a7 = radio(
        'A7. 귀사(현 소속)는 현재 노무사(공인노무사) 자문 계약을 맺고 있습니까?',
        [[1, '정기 자문 계약 있음'], [2, '필요할 때만 이용'], [3, '이용한 적 없음'], [4, '잘 모름']],
    )

    # ----------------------------------------------------------------- B. 유연근무/일가정양립
    # B1 인지도
    b1_1 = radio(I[0], C.KNOW4)
    b1_2 = radio(I[1], C.KNOW4)
    b1_3 = radio(I[2], C.KNOW4)
    b1_4 = radio(I[3], C.KNOW4)
    b1_5 = radio(I[4], C.KNOW4)
    b1_6 = radio(I[5], C.KNOW4)
    b1_7 = radio(I[6], C.KNOW4)
    b1_8 = radio(I[7], C.KNOW4)
    b1_9 = radio(I[8], C.KNOW4)
    b1_10 = radio(I[9], C.KNOW4)

    # B2 운영 형태 (B1 "모른다"인 제도는 표시 안 함)
    b2_1 = radio(I[0], C.B2_SCALE)
    b2_2 = radio(I[1], C.B2_SCALE)
    b2_3 = radio(I[2], C.B2_SCALE)
    b2_4 = radio(I[3], C.B2_SCALE)
    b2_5 = radio(I[4], C.B2_SCALE)
    b2_6 = radio(I[5], C.B2_SCALE)
    b2_7 = radio(I[6], C.B2_SCALE)
    b2_8 = radio(I[7], C.B2_SCALE)
    b2_9 = radio(I[8], C.B2_SCALE)
    b2_10 = radio(I[9], C.B2_SCALE)

    # B3 사용 실적 (B2 "없음"인 제도, B2가 표시되지 않은 제도는 표시 안 함)
    b3_1 = radio(I[0], C.B3_SCALE)
    b3_2 = radio(I[1], C.B3_SCALE)
    b3_3 = radio(I[2], C.B3_SCALE)
    b3_4 = radio(I[3], C.B3_SCALE)
    b3_5 = radio(I[4], C.B3_SCALE)
    b3_6 = radio(I[5], C.B3_SCALE)
    b3_7 = radio(I[6], C.B3_SCALE)
    b3_8 = radio(I[7], C.B3_SCALE)
    b3_9 = radio(I[8], C.B3_SCALE)
    b3_10 = radio(I[9], C.B3_SCALE)

    # B15 유연근무 인식 (B3 뒤에 배치)
    b15_1 = radio('직원이 눈에 보이지 않으면 일을 제대로 하지 않을 것 같다', C.AGREE5)
    b15_2 = radio('유연근무는 우리 회사의 업종이나 규모에는 맞지 않는다', C.AGREE5)
    b15_3 = radio('유연근무를 도입하면 생산성이 떨어질 것이다', C.AGREE5)
    b15_4 = radio('일부 직원에게 유연근무를 허용하면 특혜로 비쳐 조직 기강이 흐트러질 것이다', C.AGREE5)
    b15_5 = radio('유연근무를 운영하려면 관리 부담이 너무 크다', C.AGREE5)

    b4 = radio(
        'B4. 직원이 출산휴가, 육아휴직, 근로시간 단축을 사용할 때 그 업무 공백을 주로 어떻게 처리하십니까(또는 처리하시겠습니까)?',
        [
            [1, '계약직 대체인력을 추가로 고용'],
            [2, '일용직 인력을 고용하여 해결'],
            [3, '새 정규직 인력을 채용하여 해결'],
            [4, '남은 인력끼리 나눠서 해결'],
            [5, '사례가 없어 잘 모름'],
            [6, '기타'],
        ],
    )
    b4_other = text('기타 (직접 입력)')
    b5 = radio(
        'B5. 대체인력은 주로 어떤 방법으로 충원하십니까?',
        [
            [1, '회사에서 자체적으로 공고, 채용'],
            [2, '고용센터, 대체인력뱅크 등 정부 취업지원기관'],
            [3, '민간 직업소개소 또는 파견업체'],
            [4, '지인 또는 직원의 추천'],
            [5, '기타'],
        ],
    )
    b5_other = text('기타 (직접 입력)')
    b6 = radio(
        'B6. 귀사(현 소속)는 유연근무제 및 일가정양립 제도의 법적 요건과 운영 절차를 어느 정도 알고 있다고 생각하십니까?',
        [[1, '전혀 모른다'], [2, '잘 모르는 편이다'], [3, '보통이다'], [4, '어느 정도 알고 있다'], [5, '매우 잘 알고 있다']],
    )

    # B7 정부 지원제도 인지도
    b7_1 = radio('부모 각각 육아휴직 사용 (자녀 1명당 부모 각 최대 1년)', C.KNOW4)
    b7_2 = radio('6+6 부모육아휴직제 (부모 모두 사용 시 첫 6개월 통상임금 100% 지원)', C.KNOW4)
    b7_3 = radio('육아휴직 지원금 (허용한 사업주에게 지원금 지급)', C.KNOW4)
    b7_4 = radio('육아기 근로시간 단축 지원금 (허용한 사업주에게 지원금 지급)', C.KNOW4)
    b7_5 = radio('대체인력지원금 (휴가/단축 기간 대체인력 채용 사업주 지원)', C.KNOW4)
    b7_6 = radio('유연근무 장려금 (시차출퇴근, 재택 등 활용 사업주 지원)', C.KNOW4)

    # B8 (B7에서 하나라도 "모른다" 외 응답 시)
    b8_rank1 = models.IntegerField(label='1순위', choices=C.B8_CHANNELS, blank=True)
    b8_rank2 = models.IntegerField(label='2순위', choices=C.B8_CHANNELS, blank=True)
    b8_other = text('기타 (직접 입력)')

    # B9 영향 인식 (b9_attn = attention check, 고정 위치 다섯 번째 행)
    b9_1 = radio('직원 만족도', C.EFFECT5)
    b9_2 = radio('직원 이직률 감소', C.EFFECT5)
    b9_3 = radio('채용 경쟁력', C.EFFECT5)
    b9_4 = radio('직원 생산성', C.EFFECT5)
    b9_attn = radio('이 문항은 응답 확인용입니다. "영향 없음"을 선택해 주십시오', C.EFFECT5)
    b9_5 = radio('노무관리 부담', C.EFFECT5)
    b9_6 = radio('인건비 또는 운영비용', C.EFFECT5)

    # B10 어려움 (최대 3개)
    b10_1 = check('CEO 및 임원의 관심 또는 의지 부족')
    b10_2 = check('제도 도입 방법, 절차, 규정을 잘 모름')
    b10_3 = check('직원 근태관리 또는 근무평정의 어려움')
    b10_4 = check('업무 공백 또는 대체인력 문제')
    b10_5 = check('거래기업 또는 고객과의 관계 때문에 어려움')
    b10_6 = check('비용 부담')
    b10_7 = check('일부 직무에는 적용하기 어려움')
    b10_8 = check('직원 간 형평성 문제')
    b10_9 = check('직원들이 실제로 사용하기 어려운 조직문화')
    b10_10 = check('노동조합 또는 직원의 반대')
    b10_11 = check('희망하는(필요한) 직원이 없음')
    b10_12 = check('필요성을 느끼지 못함')
    b10_13 = check('이미 충분히 운영하고 있음')
    b10_14 = check('기타')
    b10_other = text('기타 (직접 입력)')

    # B11 일하는 문화
    b11_1 = radio(
        'B11-1. 일반 직원의 연장근로(야근)는 어느 정도입니까?',
        [[1, '거의 매일'], [2, '1주일에 2-3일'], [3, '1주일에 1일'], [4, '거의 없음 (바쁠 때만 가끔)']],
    )
    b11_2 = radio(
        'B11-2. 휴일근로는 어느 정도입니까?',
        [[1, '거의 매번'], [2, '1달에 2-3회'], [3, '1달에 1회'], [4, '거의 없음']],
    )
    b11_3 = radio(
        'B11-3. 직원들은 개인 형편에 따라 연차를 자유롭게 사용하는 편입니까?',
        [[1, '매우 그렇다'], [2, '그런 편이다'], [3, '그렇지 않은 편이다'], [4, '전혀 그렇지 않다']],
    )
    b11_4 = number('B11-4. 지난해 직원 1인당 연차 평균 부여일수', max=365)
    b11_4_1 = radio(
        'B11-4-1. 지난해 직원 1인당 연차 평균 사용일수는 어느 정도입니까?',
        [[1, '10일 이하'], [2, '11-15일'], [3, '16-20일'], [4, '21-25일'], [5, '26일 이상']],
    )
    b11_5 = radio(
        'B11-5. 귀사(현 소속)에서 사용할 수 있는 가장 작은 단위의 연차는 무엇입니까?',
        [[1, '일(日) 단위만 가능'], [2, '반차 (4시간)'], [3, '반반차 (2시간)'], [4, '1시간 단위'], [5, '기타']],
    )
    b11_5_other = text('기타 (직접 입력)')
    b11_6 = radio(
        'B11-6. 귀사(현 소속)에서는 부여된 연차를 직원이 원하는 시기에 모두 사용할 수 있는 분위기입니까?',
        [[1, '매우 그렇다'], [2, '그런 편이다'], [3, '그렇지 않은 편이다'], [4, '전혀 그렇지 않다']],
    )

    b12 = number(
        'B12. 귀사(현 소속)는 향후 6개월 내 유연근무제 또는 일가정양립 제도를 새로 도입하거나 확대할 가능성이 얼마나 있다고 생각하십니까?',
        max=100,
    )
    b13_1 = radio(
        'B13-1. 정부나 지자체로부터 받은 일과 생활 균형 관련 제도 안내(공문, 이메일, 뉴스레터 등) 수신',
        [[1, '5회 이상'], [2, '3-4회'], [3, '1-2회'], [4, '받아본 적 없음']],
    )
    b13_2 = radio('B13-2. 교육 또는 컨설팅 참여', [[1, '예'], [2, '아니오']])
    b13_2_text = text('내용')
    b14 = models.LongStringField(
        label='B14. (선택) 법에서 정한 제도 외에 귀사(현 소속)가 자체적으로 시행 중인 일과 생활 균형 제도가 있다면 적어 주십시오.',
        blank=True,
    )

    # ----------------------------------------------------------------- C. 노무관리/조직 내 갈등
    c1_1 = radio('취업규칙에 직장 내 괴롭힘 예방과 발생 시 조치 사항이 규정되어 있다', C.C1_SCALE)
    c1_2 = radio('직장 내 괴롭힘이나 고충을 신고할 수 있는 창구(담당자)가 지정되어 있다', C.C1_SCALE)
    c1_3 = radio('직원이 고충이나 불만을 제기할 수 있는 공식 절차(고충처리 제도)가 있다', C.C1_SCALE)
    c1_4 = radio('연령 등을 이유로 한 차별 금지와 공정한 처우 방침이 문서로 정해져 있다', C.C1_SCALE)
    c1_5 = radio('지난 1년간 직원 대상 직장 내 괴롭힘 예방교육을 실시했다', C.C1_SCALE)
    c1_6 = radio('지난 1년간 대표나 관리자가 노동법 또는 노무관리 교육을 받았다', C.C1_SCALE)

    c2 = radio(
        'C2. 지난 1년간 직원들이 제기한 고충 중 가장 많은 유형은 무엇입니까?',
        [
            [1, '임금, 수당'],
            [2, '승진, 배치'],
            [3, '휴가 사용'],
            [4, '산업안전, 근로환경'],
            [5, '업무 방식'],
            [6, '성희롱, 괴롭힘'],
            [7, '상사와의 갈등'],
            [8, '동료와의 갈등'],
            [9, '제기된 고충 없음'],
            [10, '기타'],
        ],
    )
    c2_other = text('기타 (직접 입력)')

    c3_1 = radio('근무시간, 휴가, 유연근무에 대한 요구', C.C3_SCALE)
    c3_2 = radio('업무 지시, 보고, 피드백 등 소통 방식', C.C3_SCALE)
    c3_3 = radio('성과급, 연봉 등 보상의 공정성', C.C3_SCALE)
    c3_4 = radio('업무 분담과 책임 범위', C.C3_SCALE)
    c3_5 = radio('회식, 행사 등 조직문화', C.C3_SCALE)

    c4_1 = radio('업무상 필요한 지적이나 질책은 직장 내 괴롭힘이 될 수 없다', C.AGREE5)
    c4_2 = radio('우리 회사 규모에서는 직장 내 괴롭힘 신고나 분쟁이 생길 가능성이 낮다', C.AGREE5)
    c4_3 = radio('괴롭힘 신고가 들어오면 회사가 조사하기보다 당사자끼리 해결하도록 하는 것이 낫다', C.AGREE5)
    c4_4 = radio('젊은 직원들과의 갈등은 세대 차이 문제라서 회사가 제도적으로 대응할 수 있는 것이 아니다', C.AGREE5)
    c4_5 = radio('노동법 개정 사항은 노무사에게 맡기면 되므로 대표나 관리자가 직접 알 필요는 없다', C.AGREE5)

    c5_1 = check('직장 내 괴롭힘 신고 (사내 신고 또는 고용노동부 진정)')
    c5_2 = check('임금체불, 부당해고 등 진정, 고소, 구제신청')
    c5_3 = check('고용노동부 근로감독, 점검')
    c5_4 = check('상사나 동료와의 갈등을 이유로 한 직원의 퇴사')
    c5_5 = check('기타 노동 관련 분쟁')
    c5_6 = check('없음')
    c5_other = text('기타 노동 관련 분쟁 (직접 입력)')

    c6 = number(
        'C6. 귀사(현 소속)에서 향후 직장 내 괴롭힘 신고, 세대 간 갈등, 노동법 위반 등 노무 문제로 분쟁이 발생할 가능성에 대해 어느 정도 우려하고 계십니까?',
        max=100,
    )
    c7 = number(
        'C7. 귀사(현 소속)는 향후 6개월 내 노무관리 체계(취업규칙의 괴롭힘 규정, 신고와 조사 절차, 관리자 교육, 노무사 자문 등)를 새로 정비하거나 개선할 가능성이 얼마나 있다고 생각하십니까?',
        max=100,
    )

    c8_1 = check('어디까지가 직장 내 괴롭힘인지 판단하기 어려움')
    c8_2 = check('신고 접수와 조사 절차를 어떻게 만들지 모름')
    c8_3 = check('관리자들이 업무 지적이나 피드백을 꺼리게 됨')
    c8_4 = check('젊은 직원과의 소통 방식을 바꾸기 어려움')
    c8_5 = check('평가와 보상 기준을 공개하거나 바꾸기 어려움')
    c8_6 = check('비용 부담 (노무사 수임료, 교육비 등)')
    c8_7 = check('시간과 인력 부족')
    c8_8 = check('법이 자주 바뀌어 따라가기 어려움')
    c8_9 = check('직원과의 갈등이 생길까 우려됨')
    c8_10 = check('필요성을 느끼지 못함')
    c8_11 = check('이미 충분히 정비되어 있음')
    c8_12 = check('기타')
    c8_other = text('기타 (직접 입력)')


# ---------------------------------------------------------------------------
# 세션 생성: B/C 블록 순서 배정 (Qualtrics "Evenly Present"와 같이 절반씩)
# ---------------------------------------------------------------------------
def creating_session(subsession: Subsession):
    players = subsession.get_players()
    orders = ['BC', 'CB'] * (len(players) // 2 + 1)
    orders = orders[: len(players)]
    random.shuffle(orders)
    for p, order in zip(players, orders):
        p.block_order = order


# ---------------------------------------------------------------------------
# 공통 함수
# ---------------------------------------------------------------------------
B1_FIELDS = ['b1_{}'.format(i) for i in range(1, 11)]
B2_FIELDS = ['b2_{}'.format(i) for i in range(1, 11)]
B3_FIELDS = ['b3_{}'.format(i) for i in range(1, 11)]
B7_FIELDS = ['b7_{}'.format(i) for i in range(1, 7)]
B9_FIELDS = ['b9_1', 'b9_2', 'b9_3', 'b9_4', 'b9_attn', 'b9_5', 'b9_6']
B10_FIELDS = ['b10_{}'.format(i) for i in range(1, 15)]
B15_FIELDS = ['b15_{}'.format(i) for i in range(1, 6)]
C1_FIELDS = ['c1_{}'.format(i) for i in range(1, 7)]
C3_FIELDS = ['c3_{}'.format(i) for i in range(1, 6)]
C4_FIELDS = ['c4_{}'.format(i) for i in range(1, 6)]
C5_FIELDS = ['c5_{}'.format(i) for i in range(1, 7)]
C8_FIELDS = ['c8_{}'.format(i) for i in range(1, 13)]
A5_FIELDS = [
    'a5_{}_{}'.format(sex, age)
    for sex in ['m', 'f']
    for age in ['20s', '30s', '40s', '50s', '60s']
]


def scale_labels(choices):
    return [label for value, label in choices]


def matrix(rows, choices):
    return dict(rows=rows, scale=scale_labels(choices))


def checkboxes(rows, max_n=0, exclusive=''):
    return dict(rows=rows, max=max_n, exclusive=exclusive)


def b2_rows(player: Player):
    """B1에서 '모른다'가 아닌 제도 (미응답 포함)"""
    return [
        B2_FIELDS[i]
        for i, f in enumerate(B1_FIELDS)
        if player.field_maybe_none(f) != C.B1_DONT_KNOW
    ]


def b3_rows(player: Player):
    """B2가 표시되었고 B2에서 '없음'이 아닌 제도 (미응답 포함)"""
    shown_b2 = b2_rows(player)
    return [
        B3_FIELDS[i]
        for i, f in enumerate(B2_FIELDS)
        if f in shown_b2 and player.field_maybe_none(f) != C.B2_NONE
    ]


def b8_shown(player: Player):
    """B7에서 하나라도 '모른다' 외 응답"""
    return any(
        player.field_maybe_none(f) not in (None, C.B7_DONT_KNOW) for f in B7_FIELDS
    )


def clear_other(player: Player, choice_field, other_field, other_value):
    """'기타'를 고르지 않았는데 기타 입력란에 값이 남아 있으면 지운다."""
    if player.field_maybe_none(choice_field) != other_value:
        setattr(player, other_field, None)


def count_checked(values, fields):
    return sum(1 for f in fields if values.get(f))


def is_valid_phone(s):
    digits = s.replace('-', '').replace(' ', '')
    return digits.isdigit() and 10 <= len(digits) <= 11 and digits.startswith('01')


def is_valid_email(s):
    s = s.strip()
    return '@' in s and '.' in s.split('@')[-1] and ' ' not in s


def block_displayed(player: Player, block, position):
    """position: 1 = 먼저 제시되는 자리, 2 = 나중 자리"""
    return player.block_order[position - 1] == block


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------
class SurveyPage(Page):
    pass


class Consent(SurveyPage):
    form_model = 'player'
    form_fields = ['consent_participate', 'consent_privacy', 'consent_followup']

    @staticmethod
    def error_message(player: Player, values):
        if not values['consent_participate']:
            return dict(consent_participate='설문 참여에 동의하셔야 설문을 진행할 수 있습니다.')


class A0(SurveyPage):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        # 개인정보 동의 = 동의함일 때만 연락처 문항 표시
        if player.consent_privacy == 1:
            return ['a0', 'a0_1_name', 'a0_1_phone', 'a0_1_email']
        return ['a0']

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values.get('a0_1_phone') and not is_valid_phone(values['a0_1_phone']):
            errors['a0_1_phone'] = '휴대전화 번호를 확인해 주십시오. (예: 010-1234-5678)'
        if values.get('a0_1_email') and not is_valid_email(values['a0_1_email']):
            errors['a0_1_email'] = '이메일 주소를 확인해 주십시오.'
        return errors


class A1(SurveyPage):
    form_model = 'player'
    form_fields = ['a1', 'a1_other', 'a2', 'a2_other', 'a3', 'a4_regular', 'a4_nonregular']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'a1', 'a1_other', 5)
        clear_other(player, 'a2', 'a2_other', 9)


class A5(SurveyPage):
    form_model = 'player'
    form_fields = A5_FIELDS + ['a6', 'a7']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        def total(sex):
            vals = [player.field_maybe_none('a5_{}_{}'.format(sex, a)) for a in ['20s', '30s', '40s', '50s', '60s']]
            vals = [v for v in vals if v is not None]
            return sum(vals) if vals else None

        player.a5_m_total = total('m')
        player.a5_f_total = total('f')


# ----------------------------- B 블록 -----------------------------
class B1(SurveyPage):
    form_model = 'player'
    form_fields = B1_FIELDS
    block = 'B'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(b1=matrix(B1_FIELDS, C.KNOW4))


class B2(SurveyPage):
    form_model = 'player'
    block = 'B'

    @staticmethod
    def is_displayed(player: Player):
        return len(b2_rows(player)) > 0

    @staticmethod
    def get_form_fields(player: Player):
        return b2_rows(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(b2=matrix(B2_FIELDS, C.B2_SCALE))


class B3(SurveyPage):
    """B3 + B15 (B15는 B3 뒤에 배치)"""

    form_model = 'player'
    block = 'B'

    @staticmethod
    def get_form_fields(player: Player):
        return b3_rows(player) + B15_FIELDS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            show_b3=len(b3_rows(player)) > 0,
            b3=matrix(B3_FIELDS, C.B3_SCALE),
            b15=matrix(B15_FIELDS, C.AGREE5),
        )


class B4(SurveyPage):
    form_model = 'player'
    form_fields = ['b4', 'b4_other', 'b5', 'b5_other', 'b6']
    block = 'B'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'b4', 'b4_other', 6)
        if player.field_maybe_none('b4') not in (1, 2, 3):
            player.b5 = None
        clear_other(player, 'b5', 'b5_other', 5)


class B7(SurveyPage):
    form_model = 'player'
    form_fields = B7_FIELDS + ['b8_rank1', 'b8_rank2', 'b8_other']
    block = 'B'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(b7=matrix(B7_FIELDS, C.KNOW4))

    @staticmethod
    def error_message(player: Player, values):
        r1, r2 = values.get('b8_rank1'), values.get('b8_rank2')
        if r1 is not None and r1 == r2:
            return dict(b8_rank2='1순위와 다른 경로를 선택해 주십시오.')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not b8_shown(player):
            player.b8_rank1 = None
            player.b8_rank2 = None
        if 8 not in (player.field_maybe_none('b8_rank1'), player.field_maybe_none('b8_rank2')):
            player.b8_other = None


class B9(SurveyPage):
    """B9 + B10"""

    form_model = 'player'
    form_fields = B9_FIELDS + B10_FIELDS + ['b10_other']
    block = 'B'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            b9=matrix(B9_FIELDS, C.EFFECT5),
            b10=checkboxes(B10_FIELDS, max_n=3),
        )

    @staticmethod
    def error_message(player: Player, values):
        if count_checked(values, B10_FIELDS) > 3:
            return dict(b10_1='최대 3개까지 선택해 주십시오.')

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.attn_fail_pre = player.field_maybe_none('b9_attn') != C.ATTN_CORRECT
        if not player.b10_14:
            player.b10_other = None


class B11(SurveyPage):
    form_model = 'player'
    form_fields = ['b11_1', 'b11_2', 'b11_3', 'b11_4', 'b11_4_1', 'b11_5', 'b11_5_other', 'b11_6']
    block = 'B'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'b11_5', 'b11_5_other', 5)


class B12(SurveyPage):
    """B12 + B13 + B14"""

    form_model = 'player'
    form_fields = ['b12', 'b13_1', 'b13_2', 'b13_2_text', 'b14']
    block = 'B'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'b13_2', 'b13_2_text', 1)


# ----------------------------- C 블록 -----------------------------
class C1(SurveyPage):
    """C1 + C2"""

    form_model = 'player'
    form_fields = C1_FIELDS + ['c2', 'c2_other']
    block = 'C'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(c1=matrix(C1_FIELDS, C.C1_SCALE))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        clear_other(player, 'c2', 'c2_other', 10)


class C3(SurveyPage):
    """C3 + C4"""

    form_model = 'player'
    form_fields = C3_FIELDS + C4_FIELDS
    block = 'C'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            c3=matrix(C3_FIELDS, C.C3_SCALE),
            c4=matrix(C4_FIELDS, C.AGREE5),
        )


class C5(SurveyPage):
    """C5 + C6 + C7 + C8"""

    form_model = 'player'
    form_fields = C5_FIELDS + ['c5_other', 'c6', 'c7'] + C8_FIELDS + ['c8_other']
    block = 'C'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            c5=checkboxes(C5_FIELDS, exclusive='c5_6'),
            c8=checkboxes(C8_FIELDS, max_n=3),
        )

    @staticmethod
    def error_message(player: Player, values):
        errors = {}
        if values.get('c5_6') and count_checked(values, C5_FIELDS[:-1]) > 0:
            errors['c5_1'] = '"없음"은 다른 항목과 함께 선택할 수 없습니다.'
        if count_checked(values, C8_FIELDS) > 3:
            errors['c8_1'] = '최대 3개까지 선택해 주십시오.'
        return errors

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not player.c5_5:
            player.c5_other = None
        if not player.c8_12:
            player.c8_other = None


# ------------------------------------------------------------------
# B/C 블록 순서: 같은 페이지를 "앞 자리"와 "뒷 자리"에 하나씩 만들고
# block_order 에 맞는 자리에서만 표시한다.
# ------------------------------------------------------------------
def make_positioned(page_class, position):
    block = page_class.block
    original_is_displayed = page_class.__dict__.get('is_displayed')

    def is_displayed(player: Player):
        if not block_displayed(player, block, position):
            return False
        if original_is_displayed is not None:
            return original_is_displayed.__func__(player)
        return True

    return type(
        '{}_{}'.format(page_class.__name__, position),
        (page_class,),
        dict(
            template_name='survey1_pre/{}.html'.format(page_class.__name__),
            is_displayed=staticmethod(is_displayed),
        ),
    )


B_PAGES = [B1, B2, B3, B4, B7, B9, B11, B12]
C_PAGES = [C1, C3, C5]


class End(SurveyPage):
    @staticmethod
    def vars_for_template(player: Player):
        player.finished = True
        return {}


page_sequence = (
    [Consent, A0, A1, A5]
    + [make_positioned(p, 1) for p in B_PAGES + C_PAGES]
    + [make_positioned(p, 2) for p in B_PAGES + C_PAGES]
    + [End]
)

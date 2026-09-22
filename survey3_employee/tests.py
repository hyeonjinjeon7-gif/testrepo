from otree.api import Bot, SubmissionMustFail, expect

from . import *

# 실행: otree test survey3_employee
#   case 'parent' : 자녀 있음, 민감정보 동의 -> K5, L6, N3-N5 표시
#   case 'no_kids': 자녀 없음, 민감정보 비동의 -> K5, N3-N5 숨김, L7 표시, 개인정보 비동의 -> O 생략


class PlayerBot(Bot):
    cases = ['parent', 'no_kids']

    def play_round(self):
        parent = self.case == 'parent'
        agree = 1 if parent else 0

        yield SubmissionMustFail(
            Consent, dict(consent_privacy=1, consent_sensitive=1, consent_followup=1)
        )
        yield Consent, dict(
            consent_participate=True,
            consent_privacy=agree,
            consent_sensitive=agree,
            consent_followup=1,
        )

        yield SubmissionMustFail(J1, dict(j1=C.COMPANY_NOT_LISTED))  # 직접 입력 비움
        if parent:
            yield J1, dict(j1=1, j1_other='지워져야 함')
            expect(self.player.field_maybe_none('j1_other'), None)
        else:
            yield J1, dict(j1=C.COMPANY_NOT_LISTED, j1_other='목록에 없는 회사')
            expect(self.player.j1_other, '목록에 없는 회사')

        if parent:
            yield SubmissionMustFail(
                K1, dict(k1=2, k2=2, k3=2, k4=2, k4_1=1, k4_2_1=3, k4_2_2=5, k5=2)
            )  # 자녀 1명인데 나이 2개
            yield K1, dict(k1=2, k2=2, k3=2, k4=2, k4_1=2, k4_2_1=3, k4_2_2=5, k5=1)
            expect(self.player.k5, 1)
        else:
            yield K1, dict(k1=1, k2=1, k3=1, k4=1, k4_1=2, k4_2_1=3)
            expect(self.player.field_maybe_none('k4_1'), None)
            expect(self.player.field_maybe_none('k5'), None)

        yield K6, dict(k6=1, k7=1, k8=2, k9=2, k10=2, k11=3, k12=2)

        if parent:
            yield SubmissionMustFail(K13, dict(k13=400, k13_1=500, k13_2=100))
            yield K13, dict(k13=600, k13_1=350, k13_2=250)
            expect(self.player.k13_2, 250)
        else:
            # "응답하지 않음"을 고르면 입력값은 저장되지 않는다
            yield K13, dict(k13=300, k13_1=300, k13_refuse=True)
            expect(self.player.field_maybe_none('k13'), None)

        def l_block():
            l1 = {f: 1 for f in L1_FIELDS}
            yield SubmissionMustFail(
                L_page('L1'), dict(l1, l2=2, **{f: True for f in L3_FIELDS[:3]})
            )  # 최대 2개
            yield SubmissionMustFail(L_page('L1'), dict(l1, l2=2, l3_10=True))  # "기타"만 고르고 내용 비움
            yield L_page('L1'), dict(l1, l2=2, l3_4=True, l3_10=True, l3_other='기타 이유')
            expect(self.player.l3_other, '기타 이유')

            extra = L6_FIELDS if parent else L7_FIELDS
            yield L_page('L4'), dict(
                {f: 3 for f in L4_FIELDS},
                **{f: 2 for f in L5_FIELDS},
                **{f: 4 for f in extra}
            )

        def m_block():
            yield M_page('M1'), dict(
                {f: 1 for f in M1_FIELDS},
                m2=3 if parent else C.PREFER_NOT,
                m3=3,
                m4=4,
                m4_other='말하기 어려워서',
            )
            expect(self.player.m2, 3 if parent else C.PREFER_NOT)
            expect(self.player.m4_other, '말하기 어려워서')

            m5 = {f: 3 for f in M5_FIELDS}
            m5['m5_attn'] = C.ATTN_CORRECT if parent else 1
            yield M_page('M5'), dict(m5, **{f: 6 for f in M6_FIELDS})
            expect(self.player.attn_fail_emp, not parent)

        def L_page(name):
            return page_by_name(name, 1 if self.player.block_order == 'LM' else 2)

        def M_page(name):
            return page_by_name(name, 1 if self.player.block_order == 'ML' else 2)

        if self.player.block_order == 'LM':
            yield from l_block()
            yield from m_block()
        else:
            yield from m_block()
            yield from l_block()

        if parent:
            yield SubmissionMustFail(
                N, dict({f: 3 for f in N2_FIELDS}, n1=4, n3=4, n5_1=True, n5_6=True)
            )  # "응답을 원하지 않음" + 다른 항목
            yield N, dict({f: 3 for f in N2_FIELDS}, n1=4, n3=4, n4=50, n5_2=True)
            expect(self.player.field_maybe_none('n4'), None)  # n3 = 해당 없음이면 n4는 지워짐
            expect(self.player.n5_2, True)
            yield SubmissionMustFail(O, dict(o1='123', o2=1, o3=1))
            yield O, dict(o1='010-9999-8888', o2=1, o3=1)
            expect(self.player.o1, '010-9999-8888')
        else:
            yield N, dict({f: 3 for f in N2_FIELDS}, n1=2)
            expect(self.player.field_maybe_none('n3'), None)
            # 개인정보에 동의하지 않았으므로 연락처 화면(O)은 나오지 않는다


def page_by_name(name, pos):
    target = '{}_{}'.format(name, pos)
    for p in page_sequence:
        if p.__name__ == target:
            return p
    raise Exception('page not found: ' + target)

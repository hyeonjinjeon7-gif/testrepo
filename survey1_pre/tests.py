from otree.api import Bot, Submission, SubmissionMustFail, expect

from . import *

# 실행: otree test survey1_pre
#   case 'full'      : 모든 문항 응답, attention check 통과
#   case 'dont_know' : B1을 모두 "모른다" -> B2 생략, B3 표 숨김 / 개인정보 비동의 -> 연락처 문항 숨김


class PlayerBot(Bot):
    cases = ['full', 'dont_know']

    def play_round(self):
        case = self.case
        agree = 1 if case == 'full' else 0

        # ---- 동의
        yield SubmissionMustFail(
            Consent,
            dict(consent_privacy=1, consent_followup=1),  # 참여 동의 체크 안 함
        )
        yield Consent, dict(consent_participate=True, consent_privacy=agree, consent_followup=1)

        # ---- A
        if case == 'full':
            yield SubmissionMustFail(A0, dict(a0='테스트회사', a0_1_phone='123', a0_1_email='x'))
            yield A0, dict(
                a0='테스트회사', a0_1_name='홍길동', a0_1_phone='010-1234-5678', a0_1_email='a@b.com'
            )
        else:
            yield A0, dict(a0='테스트회사2')

        yield A1, dict(a1=5, a1_other='팀장', a2=1, a2_other='지워져야 함', a3=2001, a4_regular=30, a4_nonregular=5)
        expect(self.player.field_maybe_none('a2_other'), None)
        expect(self.player.a1_other, '팀장')

        yield A5, dict(a5_m_20s=3, a5_m_30s=4, a5_f_20s=2, a6=1, a7=2)
        expect(self.player.a5_m_total, 7)
        expect(self.player.a5_f_total, 2)

        def b_block():
            b1_value = 1 if case == 'full' else C.B1_DONT_KNOW
            yield B_page('B1'), {f: b1_value for f in B1_FIELDS}
            if case == 'full':
                # B2: 1-5번 "없음", 6-10번 "규정에 명시"
                b2 = {f: (C.B2_NONE if i < 5 else 1) for i, f in enumerate(B2_FIELDS)}
                yield B_page('B2'), b2
                expect(b3_rows(self.player), B3_FIELDS[5:])
                b3 = {f: 1 for f in B3_FIELDS[5:]}
            else:
                expect(b2_rows(self.player), [])
                b3 = {}
            b3.update({f: 3 for f in B15_FIELDS})
            yield B_page('B3'), b3

            yield B_page('B4'), dict(b4=4, b5=2, b6=3)
            expect(self.player.field_maybe_none('b5'), None)

            b7_value = 2 if case == 'full' else C.B7_DONT_KNOW
            b7 = {f: b7_value for f in B7_FIELDS}
            yield SubmissionMustFail(B_page('B7'), dict(b7, b8_rank1=1, b8_rank2=1))
            yield B_page('B7'), dict(b7, b8_rank1=1, b8_rank2=8, b8_other='세미나')
            if case == 'full':
                expect(self.player.b8_rank2, 8)
                expect(self.player.b8_other, '세미나')
            else:
                expect(self.player.field_maybe_none('b8_rank1'), None)

            b9 = {f: 4 for f in B9_FIELDS}
            b9['b9_attn'] = C.ATTN_CORRECT if case == 'full' else 5
            too_many = {f: True for f in B10_FIELDS[:4]}
            yield SubmissionMustFail(B_page('B9'), dict(b9, **too_many))
            yield B_page('B9'), dict(b9, b10_1=True, b10_14=True, b10_other='기타사유')
            expect(self.player.attn_fail_pre, case != 'full')

            yield B_page('B11'), dict(b11_1=1, b11_2=2, b11_3=3, b11_4=15, b11_4_1=2, b11_5=2, b11_6=1)
            yield SubmissionMustFail(B_page('B12'), dict(b12=150))
            yield B_page('B12'), dict(b12=70, b13_1=2, b13_2=1, b13_2_text='컨설팅', b14='주 4일제')

        def c_block():
            yield C_page('C1'), dict({f: 1 for f in C1_FIELDS}, c2=10, c2_other='기타 고충')
            yield C_page('C3'), dict({f: 2 for f in C3_FIELDS}, **{f: 4 for f in C4_FIELDS})
            yield SubmissionMustFail(C_page('C5'), dict(c5_1=True, c5_6=True))
            yield C_page('C5'), dict(c5_6=True, c6=40, c7=60, c8_1=True, c8_2=True)

        def B_page(name):
            return page_by_name(name, 1 if self.player.block_order == 'BC' else 2)

        def C_page(name):
            return page_by_name(name, 1 if self.player.block_order == 'CB' else 2)

        if self.player.block_order == 'BC':
            yield from b_block()
            yield from c_block()
        else:
            yield from c_block()
            yield from b_block()

        expect(self.player.consent_privacy, agree)


def page_by_name(name, pos):
    target = '{}_{}'.format(name, pos)
    for p in page_sequence:
        if p.__name__ == target:
            return p
    raise Exception('page not found: ' + target)

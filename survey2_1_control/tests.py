from otree.api import Bot, SubmissionMustFail, expect

from . import *

# 실행: otree test survey2_1_control
# control 그룹(노무관리 강연) 전용 설문. F 블록만 treatment와 다르다.


class PlayerBot(Bot):
    cases = ['attn_pass', 'attn_fail']

    def play_round(self):
        attn_pass = self.case == 'attn_pass'

        yield SubmissionMustFail(Consent, dict(consent_privacy=1))  # 참여 동의 체크 안 함
        yield Consent, dict(consent_participate=True, consent_privacy=1)
        expect(self.player.lecture_group, C.GROUP)

        yield SubmissionMustFail(A0, dict(a0='테스트회사', a0_1_phone='0101234'))
        yield A0, dict(a0='테스트회사', a0_1_phone='010-1234-5678', a0_1_email='a@b.com')

        yield D, dict(d0=1, d1=4, d2=4, d3=5, d4='괴롭힘 판단 기준', d5=2, d5_text='지워져야 함')
        expect(self.player.field_maybe_none('d5_text'), None)

        yield SubmissionMustFail(E12, dict(e1=120, e2=50))
        yield E12, dict(e1=40, e2=80)

        e34 = {f: 2 for f in E3_FIELDS}
        e34.update({f: 3 for f in E4_FIELDS})
        e34['e4_attn'] = C.ATTN_CORRECT if attn_pass else 5
        yield E34, e34
        expect(self.player.attn_fail_post, not attn_pass)

        yield E56, dict({f: 2 for f in E5_FIELDS}, **{f: 4 for f in E6_FIELDS})

        yield SubmissionMustFail(F, {f: True for f in F1_FIELDS[:4]})  # 최대 3개
        yield SubmissionMustFail(F, dict(f2g2_1=True, f2g2_8=True))  # "필요 없음" + 다른 항목
        yield F, dict(f1g2_1=True, f1g2_12=True, f1g2_other='기타 사유', f2g2_8=True)
        expect(self.player.f1g2_other, '기타 사유')
        expect(self.player.field_maybe_none('f2g2_other'), None)

        yield G, dict(g1=1, g2=2, g3=2, g3_items='지워져야 함')
        expect(self.player.field_maybe_none('g3_items'), None)

        yield SubmissionMustFail(H, dict(h1=1, h3_name='김담당', h3_email='잘못된주소'))
        yield H, dict(h1=1, h2=20, h3_name='김담당', h3_title='총무팀장', h3_email='staff@example.com')
        expect(self.player.field_maybe_none('h1_1'), None)

        yield I, dict(i1=1, a8_consent=0, a8_biz_no='1234567890')
        expect(self.player.field_maybe_none('a8_biz_no'), None)

        yield V, dict(
            v1=1500, v2_1=2, v3_regular=20, v3_nonregular=3, v4=42, v5=30, v6=40, v7=100, v8=2
        )
        expect(self.player.field_maybe_none('v1_1'), None)

        yield W, dict(w1=1, w2=50, w3=3, w4=2, w5=1, w5_1=2, w6=1)
        expect(self.player.field_maybe_none('w5_1'), None)

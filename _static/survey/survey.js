/*
 * 설문 공통 동작 (설문 1-4 공용)
 *
 * HTML에서 쓰는 속성:
 *   data-q                     필수 응답 문항 단위 (표의 한 행, 문항 하나).
 *                              응답하지 않으면 다음 페이지로 넘어갈 수 없다
 *   data-q-optional            건너뛸 수 있는 문항 (설문지에서 '선택' 또는 '건너뛰어도 됨'으로 정한 문항).
 *                              문항 묶음을 감싸는 곳에 붙이면 그 안의 문항이 모두 선택이 된다
 *   data-q-any                 입력칸이 여러 개라도 하나만 채우면 되는 문항 (예: 휴대전화 또는 이메일)
 *   data-must-check="메시지"    안의 체크박스를 체크해야만 다음으로 넘어갈 수 있다 (동의 문항)
 *   data-show-if="a1=5"        a1 값이 5일 때만 표시 (쉼표로 여러 값: "b4=1,2,3",
 *                              | 로 여러 문항: "b8_rank1|b8_rank2=8",
 *                              ; 로 조건 여러 개 중 하나라도 맞으면: "h1=1,2;h1_1=1")
 *   data-show-if-blank="v1"    v1 을 비워 두었을 때만 표시
 *   data-show-if-any="b7_:1,2,3"
 *                              이름이 b7_ 로 시작하는 라디오 중 하나라도 1,2,3이면 표시
 *   data-max-check="3"         (체크박스 묶음) 최대 선택 개수
 *   data-exclusive="c5_6"      (체크박스 묶음) 이 보기를 고르면 나머지 해제
 *   data-sum="a5_m_"           이름이 a5_m_ 로 시작하는 숫자 입력칸의 합계를 표시
 *   data-digits                안의 입력칸에 숫자와 '-' 만 입력되게 한다 (휴대전화, 사업자번호 등)
 *
 * 숨겨지는 문항의 입력값은 지워지고, 서버(__init__.py)에서도 한 번 더 지운다.
 */
/* 화면 맨 위에 뜨는 오류 안내 문구 (oTree 기본 문구를 이 문장으로 바꾼다).
   문구를 바꾸고 싶으면 아래 ERROR_BANNER 한 줄만 고치면 된다. */
var ERROR_BANNER = '아직 완료되지 않은 문항이 있습니다. 아래 표시된 항목을 다시 확인해 주세요.';
var OTREE_DEFAULT_BANNER = '입력 양식의 내용이 잘못되었습니다. 바로잡아주세요.';
/* 응답하지 않은 문항이 있을 때 (N 자리에 개수가 들어간다) */
var UNANSWERED_BANNER = '아직 응답하지 않은 문항이 N개 있습니다. 아래 표시된 문항에 응답해 주셔야 다음으로 넘어갈 수 있습니다.';

(function () {
    'use strict';

    var banner = document.querySelector('.otree-form-errors');
    if (banner && banner.textContent.trim() === OTREE_DEFAULT_BANNER) {
        banner.textContent = ERROR_BANNER;
    }

    var form = document.getElementById('form');
    if (!form) return;

    function isVisible(el) {
        return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
    }

    function currentValues(name) {
        var vals = [];
        var els = form.querySelectorAll('[name="' + name + '"]');
        els.forEach(function (el) {
            if (el.type === 'radio' || el.type === 'checkbox') {
                if (el.checked) vals.push(el.value);
            } else if (el.value !== '') {
                vals.push(el.value);
            }
        });
        return vals;
    }

    function clearInputs(container) {
        container.querySelectorAll('input, select, textarea').forEach(function (el) {
            if (el.type === 'radio' || el.type === 'checkbox') {
                el.checked = false;
            } else {
                el.value = '';
            }
        });
    }

    /* ---------- 조건부 표시 ---------- */
    function updateConditions() {
        form.querySelectorAll('[data-show-if]').forEach(function (el) {
            var show = el.getAttribute('data-show-if').split(';').some(function (cond) {
                var spec = cond.split('=');
                var targets = spec[1].split(',');
                return spec[0].split('|').some(function (name) {
                    return currentValues(name).some(function (v) {
                        return targets.indexOf(v) !== -1;
                    });
                });
            });
            toggle(el, show);
        });
        form.querySelectorAll('[data-show-if-blank]').forEach(function (el) {
            var names = el.getAttribute('data-show-if-blank').split('|');
            var blank = names.every(function (name) {
                return currentValues(name).length === 0;
            });
            toggle(el, blank);
        });
        form.querySelectorAll('[data-show-if-any]').forEach(function (el) {
            var spec = el.getAttribute('data-show-if-any').split(':');
            var prefix = spec[0];
            var targets = spec[1].split(',');
            var show = false;
            form.querySelectorAll('input[type=radio]').forEach(function (r) {
                if (r.name.indexOf(prefix) === 0 && r.checked && targets.indexOf(r.value) !== -1) {
                    show = true;
                }
            });
            toggle(el, show);
        });
    }

    function toggle(el, show) {
        if (show) {
            el.style.display = '';
        } else {
            if (el.style.display !== 'none') clearInputs(el);
            el.style.display = 'none';
        }
    }

    /* ---------- 체크박스 최대 개수, 배타 보기 ---------- */
    function onCheckboxChange(e) {
        var box = e.target;
        if (box.type !== 'checkbox') return;
        var group = box.closest('.cb-group');
        if (!group) return;

        var exclusiveName = group.getAttribute('data-exclusive');
        var boxes = group.querySelectorAll('input[type=checkbox]');
        if (exclusiveName && box.checked) {
            boxes.forEach(function (b) {
                if (box.name === exclusiveName && b !== box) b.checked = false;
                if (box.name !== exclusiveName && b.name === exclusiveName) b.checked = false;
            });
        }

        var max = parseInt(group.getAttribute('data-max-check') || '0', 10);
        if (max > 0 && box.checked) {
            var n = 0;
            boxes.forEach(function (b) { if (b.checked) n++; });
            if (n > max) {
                box.checked = false;
                alert('최대 ' + max + '개까지 선택하실 수 있습니다.');
            }
        }
    }

    /* ---------- 숫자와 '-' 만 입력 (휴대전화, 사업자번호 등) ---------- */
    function setupDigitsOnly() {
        form.querySelectorAll('[data-digits] input').forEach(function (input) {
            input.setAttribute('inputmode', 'numeric');  // 휴대폰에서 숫자 자판이 먼저 열린다

            function strip() {
                var cleaned = input.value.replace(/[^0-9-]/g, '');
                if (cleaned === input.value) return;
                var pos = input.selectionStart - (input.value.length - cleaned.length);
                input.value = cleaned;
                try {
                    input.setSelectionRange(pos, pos);
                } catch (e) { /* 일부 브라우저는 지원하지 않는다 */ }
            }

            input.addEventListener('input', function (e) {
                // 한글 조합 중에는 건드리지 않고, 조합이 끝나면 지운다
                if (e.isComposing) return;
                strip();
            });
            input.addEventListener('compositionend', strip);
            input.addEventListener('blur', strip);
        });
    }

    /* ---------- 합계 표시 ---------- */
    function updateSums() {
        form.querySelectorAll('[data-sum]').forEach(function (out) {
            var prefix = out.getAttribute('data-sum');
            var total = 0;
            var any = false;
            form.querySelectorAll('input[type=number]').forEach(function (inp) {
                if (inp.name.indexOf(prefix) === 0 && inp.value !== '') {
                    total += parseInt(inp.value, 10) || 0;
                    any = true;
                }
            });
            out.textContent = any ? total : '-';
        });
    }

    /* ---------- 필수 응답 확인 (Qualtrics의 Force Response) ---------- */
    function isAnswered(unit) {
        var radios = unit.querySelectorAll('input[type=radio]');
        if (radios.length) {
            var anyChecked = Array.prototype.some.call(radios, function (r) { return r.checked; });
            if (!anyChecked) return false;
        }
        var boxes = unit.querySelectorAll('input[type=checkbox]');
        if (boxes.length) {
            var anyBox = Array.prototype.some.call(boxes, function (b) { return b.checked; });
            if (!anyBox) return false;
        }
        var texts = [];
        unit.querySelectorAll(
            'input[type=text], input[type=number], input[type=email], input[type=tel], select, textarea'
        ).forEach(function (t) {
            if (isVisible(t) && !t.closest('[data-q-optional]')) texts.push(t);
        });
        if (texts.length === 0) return true;

        var filled = texts.filter(function (t) { return t.value.trim() !== ''; });
        if (unit.hasAttribute('data-q-any')) {
            // 입력칸 중 하나만 채우면 된다
            return filled.length > 0;
        }
        return filled.length === texts.length;
    }

    /* ---------- 화면 맨 위 안내 띠 ---------- */
    function showBanner(text) {
        var box = document.querySelector('.otree-form-errors');
        if (!box) {
            box = document.createElement('div');
            box.className = 'otree-form-errors alert alert-danger';
            var body = document.querySelector('.otree-body');
            var title = document.getElementById('_otree-title');
            if (title && title.nextSibling) {
                body.insertBefore(box, title.nextSibling);
            } else {
                body.insertBefore(box, body.firstChild);
            }
        }
        box.textContent = text;
    }

    /* ---------- 반드시 체크해야 하는 동의 문항 ---------- */
    function requiredCheckMissing() {
        var blocked = null;
        form.querySelectorAll('[data-must-check]').forEach(function (unit) {
            if (blocked) return;
            var box = unit.querySelector('input[type=checkbox]');
            if (box && !box.checked) blocked = unit;
        });
        return blocked;
    }

    function showMustCheck(unit) {
        unit.classList.add('must-check-error');
        var msg = unit.querySelector('.must-check-msg');
        if (!msg) {
            msg = document.createElement('div');
            msg.className = 'form-control-errors must-check-msg';
            unit.appendChild(msg);
        }
        msg.textContent = unit.getAttribute('data-must-check');
        unit.scrollIntoView({behavior: 'smooth', block: 'center'});
    }

    form.addEventListener('change', function (e) {
        var unit = e.target.closest && e.target.closest('[data-must-check]');
        if (unit && e.target.checked) {
            unit.classList.remove('must-check-error');
            var msg = unit.querySelector('.must-check-msg');
            if (msg) msg.remove();
        }
    });

    form.addEventListener('submit', function (e) {
        var blocked = requiredCheckMissing();
        if (blocked) {
            e.preventDefault();
            e.stopImmediatePropagation();
            showMustCheck(blocked);
            return;
        }
        form.querySelectorAll('.unanswered').forEach(function (el) {
            el.classList.remove('unanswered');
        });

        var missing = [];
        form.querySelectorAll('[data-q]').forEach(function (unit) {
            if (!isVisible(unit) || unit.closest('[data-q-optional]')) return;
            if (!isAnswered(unit)) missing.push(unit);
        });
        if (missing.length === 0) return;

        missing.forEach(function (u) { u.classList.add('unanswered'); });
        e.preventDefault();
        e.stopImmediatePropagation();
        showBanner(UNANSWERED_BANNER.replace('N', missing.length));
        missing[0].scrollIntoView({behavior: 'smooth', block: 'center'});
    });

    form.addEventListener('change', function (e) {
        onCheckboxChange(e);
        updateConditions();
        var unit = e.target.closest && e.target.closest('.unanswered');
        if (unit && isAnswered(unit)) {
            unit.classList.remove('unanswered');
            // 표시된 문항에 모두 응답했으면 위 안내 띠도 지운다
            if (!form.querySelector('.unanswered')) {
                var box = document.querySelector('.otree-form-errors');
                if (box) box.remove();
            }
        }
    });
    form.addEventListener('input', updateSums);

    setupDigitsOnly();
    updateConditions();
    updateSums();
})();

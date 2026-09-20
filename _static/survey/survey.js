/*
 * 설문 공통 동작 (설문 1-4 공용)
 *
 * HTML에서 쓰는 속성:
 *   data-q                     응답 확인 대상 문항 단위 (표의 한 행, 문항 하나)
 *   data-q-optional            응답 확인에서 제외 (선택 문항)
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
 *
 * 숨겨지는 문항의 입력값은 지워지고, 서버(__init__.py)에서도 한 번 더 지운다.
 */
(function () {
    'use strict';

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

    /* ---------- 응답 확인 (Qualtrics의 Request Response) ---------- */
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
        var texts = unit.querySelectorAll(
            'input[type=text], input[type=number], input[type=email], input[type=tel], select, textarea'
        );
        for (var i = 0; i < texts.length; i++) {
            var t = texts[i];
            if (!isVisible(t) || t.closest('[data-q-optional]')) continue;
            if (t.value.trim() === '') return false;
        }
        return true;
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

    var confirmed = false;
    form.addEventListener('submit', function (e) {
        var blocked = requiredCheckMissing();
        if (blocked) {
            e.preventDefault();
            e.stopImmediatePropagation();
            showMustCheck(blocked);
            return;
        }
        if (confirmed) return;
        form.querySelectorAll('.unanswered').forEach(function (el) {
            el.classList.remove('unanswered');
        });

        var missing = [];
        form.querySelectorAll('[data-q]').forEach(function (unit) {
            if (!isVisible(unit) || unit.hasAttribute('data-q-optional')) return;
            if (!isAnswered(unit)) missing.push(unit);
        });
        if (missing.length === 0) return;

        missing.forEach(function (u) { u.classList.add('unanswered'); });
        var msg = '응답하지 않은 문항이 ' + missing.length + '개 있습니다.\n' +
            '[확인]을 누르면 그대로 다음으로 넘어가고, [취소]를 누르면 표시된 문항으로 돌아갑니다.';
        if (window.confirm(msg)) {
            confirmed = true;
            return; // 그대로 제출
        }
        e.preventDefault();
        e.stopImmediatePropagation();
        missing[0].scrollIntoView({behavior: 'smooth', block: 'center'});
    });

    form.addEventListener('change', function (e) {
        onCheckboxChange(e);
        updateConditions();
        if (e.target.closest('.unanswered')) {
            var unit = e.target.closest('.unanswered');
            if (isAnswered(unit)) unit.classList.remove('unanswered');
        }
    });
    form.addEventListener('input', updateSums);

    updateConditions();
    updateSums();
})();

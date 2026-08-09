#!/usr/bin/env python3
"""**자가 거짓말을 하는지** 잰다 — 참·거짓 예시를 주고 맞히는지 본다.

이 저장소의 셋째 원칙은 "자가 이상하다고 하면 코드보다 자를 먼저 본다" 다.
그 원칙이 왜 있는지는 기록으로 남아 있다 — `docs/개선-200턴.md` 에 여덟 번,
`docs/허브-200턴.md` 에 세 번. 열한 번 다 **자가 틀렸다.**

    esc() 를 제대로 쓴 자리를 잡음 · 문장 뒤쪽의 엉뚱한 .name 을 잡음
    어두운 화면의 흰 글씨를 흰 바탕에 얹어 잼 · 기본 초점 고리를 '없다' 고 함
    "불러오지 못했습니다" 를 못 잡음 · 만들어 넣는 주소를 깨진 링크로 잡음
    한국어 어절로 오탈자를 재어 후보 2,014개 · 화면을 두 번 띄워 창구를 두 배로 셈
    JS 안의 선택자 문자열까지 세어 탭을 13개라고 함
    고장 난 상태에서 창구 수를 재고 '평소' 라고 함
    같은 문서에서 해시만 바꿔 놓고 '주소가 안 읽힌다' 고 함

매번 사람이 손으로 알아냈다. 그때마다 "다음엔 안 그러겠지" 로 넘어갔다.

여기서는 **자마다 맞혀야 할 문제를 붙여 둔다.** 참이라고 해야 할 예시와
거짓이라고 해야 할 예시를 주고, 자가 그대로 답하는지 본다. 자를 고치다가
넓히거나 좁히면 여기서 걸린다.

⚠ 이것은 자를 대신하지 않는다. 자가 **볼 수 있는 것**만 늘어놓은 것이라,
  "화면을 실제로 찍어 봐야 아는 것" 은 여전히 사람 몫이다(넷째 원칙).

    python3 tools/lie_check.py           # 자마다 맞혔는지
    python3 tools/lie_check.py --check   # 하나라도 틀리면 빨간불 (CI용)
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── 자마다: (자 이름, 참이어야 할 것, 거짓이어야 할 것) ─────────────────
# 참 = 자가 '걸려야' 하는 예시, 거짓 = 자가 '넘겨야' 하는 예시.

# ⚠ 규칙을 **베끼지 않는다.** 베껴 두면 자를 고쳤을 때 여기가 옛 규칙을
#   맞히고 앉아, 자가 틀려도 초록불이 된다 — 거짓말을 잡으려다 거짓말을
#   하나 더 두는 셈이다. 진짜 자의 함수를 그대로 부른다.
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import hub_audit                                          # noqa: E402

hub_audit_counts = hub_audit.count_tabs


CASES = [
    # ── hub_audit: 탭 세기 ───────────────────────────────────────────
    # 이 자는 처음에 파일 전체에서 세어 **JS 안의 선택자 문자열**까지 셌다.
    ('hub_audit 탭 세기', hub_audit_counts, [
        ('글에 있는 탭은 센다',
         '<nav><button role="tab">가</button><button role="tab">나</button></nav>', 2),
        ('JS 안의 선택자는 안 센다',
         '<nav><button role="tab">가</button></nav>'
         '<script>document.querySelectorAll(\'[role="tab"]\')</script>', 1),
        ('CSS 안의 것도 안 센다',
         '<nav><button role="tab">가</button></nav>'
         '<style>[role="tab"]{color:red}</style>', 1),
        ('아예 없으면 0',
         '<div>탭 없음</div>', 0),
    ]),
]


def eul(word):
    """받침이 있으면 '을', 없으면 '를'. hub.html 의 같은 규칙을 여기서도 잰다."""
    ch = (word or '').strip()[-1:]
    if not ch:
        return '을(를)'
    c = ord(ch)
    if not (0xAC00 <= c <= 0xD7A3):
        return '을(를)'
    return '을' if (c - 0xAC00) % 28 else '를'


# ── msg_ledger: 가르치는 글과 사람에게 하는 말 ──────────────────────
# 이 자는 처음에 어미(`…입니다`)로만 갈래를 매겨, 해설 문장을 **아이를 평가하는
# 문장**으로 셌다("평가 문장 347개"). 열어 보니 대부분이 화학 설명이었다.
# 같은 어미가 전혀 다른 말을 한다 — 화면의 쓰임으로 먼저 갈라야 한다.
import msg_ledger                                          # noqa: E402


def ledger_kind(pair):
    """(화면 이름, 문장) → 갈래."""
    page, text = pair
    return msg_ledger.kind_of(text, page)


CASES.append(('msg_ledger 갈래', ledger_kind, [
    ('해설의 "…입니다" 는 평가가 아니다',
     ('sol-final-hwol-2024.html', '대칭 구조는 결합 쌍극자가 상쇄돼 무극성입니다'), '가르치는 글'),
    ('강의의 "…하세요" 도 아니다',
     ('lec-072-gibbs-free-energy.html', '단위를 맞춰서 계산해 보세요'), '가르치는 글'),
    ('성적표의 "…습니다" 는 평가다',
     ('report.html', '통과선을 꾸준히 지키고 있습니다'), '평가'),
    ('성적표의 약속은 약속으로 센다',
     ('report.html', '이 영역의 오답을 메우면 도달선을 넘습니다'), '약속'),
    ('못 불러온 것은 실패로 센다',
     ('hub.html', '명단을 불러오지 못했습니다'), '실패'),
]))


CASES.append(('조사 고르기(eul)', eul, [
    ('받침이 있으면 을', 'DT 명단', '을'),
    ('받침이 없으면 를', 'DT 통과', '를'),
    ('받침이 없으면 를 (2)', '재시 대기', '를'),
    ('한글이 아니면 둘 다 적는다', 'sheet', '을(를)'),
    ('비어 있어도 안 죽는다', '', '을(를)'),
]))


# ── audit_pages: 바탕 고르기와 '좁은 단추' ─────────────────────────
# 이 자는 이 문서에서 두 번 더 거짓말했다.
#   ⑥ --bg0 처럼 **번호 붙은 바탕 이름**을 못 알아봐, 어두운 화면의 흰 글씨를
#      흰 종이에 얹어 재고 1.04:1 이라고 했다(세 번째 거짓말과 같은 종류다)
#   ⑦ 작고 여백 좁은 것을 전부 '단추' 로 쳤다 — 실제로는 누를 수 없는 표시용
#      딱지였다. 안 눌리는 것에 손가락 자리를 요구하면 사람이 경고를 무시한다
import importlib.util as _ilu                                # noqa: E402
_spec = _ilu.spec_from_file_location('ap', os.path.join(ROOT, 'tools', 'audit_pages.py'))
audit_pages = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(audit_pages)

_PAGE = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         '<title>ㄱ</title><style>%s</style></head><body><h1>ㄱ</h1><p>가나다</p></body></html>')


def _hits(css, kind):
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, 't.html')
    open(p, 'w', encoding='utf-8').write(_PAGE % css)
    return bool([h for h in audit_pages.audit(p) if kind in h[0]])


def contrast_hit(css):
    return _hits(css, '대비')


def button_hit(css):
    return _hits(css, '좁은 단추')


CASES.append(('audit_pages 바탕 고르기', contrast_hit, [
    ('번호 붙은 어두운 바탕을 알아본다',
     ':root{--bg0:#040612;--bg1:#08162b;--text:#f7fbff}', False),
    ('어느 바탕에서도 안 읽히면 잡는다',
     ':root{--paper:#ffffff;--card:#f7f7f7;--muted:#eeeeee}', True),
    ('상태 띠는 종이가 아니다',
     ':root{--paper:#FAFAF7;--ok-bg:#E7F5EC;--brass-ink:#866A20}', False),
]))

CASES.append(('audit_pages 좁은 단추', button_hit, [
    ('안 눌리는 딱지는 안 센다',
     ':root{--paper:#fff;--ink:#111}'
     '.pill1{padding:2px 7px;font-size:12px}.pill2{padding:2px 7px;font-size:12px}'
     '.pill3{padding:2px 7px;font-size:12px}.pill4{padding:2px 7px;font-size:12px}', False),
    ('누르는 자리는 센다',
     ':root{--paper:#fff;--ink:#111}'
     '.btn1{padding:2px 7px;font-size:12px}.btn2{padding:2px 7px;font-size:12px}'
     '.btn3{padding:2px 7px;font-size:12px}.btn4{padding:2px 7px;font-size:12px}', True),
]))


# ── gen_expl_html: 답 표시와 오개념 한 줄을 가르기 ─────────────────
# 해설 글은 '사고과정 … → ③ <오개념 한 줄>' 꼴이다. 해설지는 오개념을
# 사고과정의 마지막 단계가 아니라 tip 으로 세운다. 그런데 보기를 하나씩 짚는
# 해설은 **글 가운데에도** '④ … → ③' 처럼 동그라미가 나온다(donghyung-1 #23
# 외 여덟). 처음 화살표를 잡으면 답 표시가 문장 한가운데로 가고 뒤가 통째로
# 오개념이 된다. 마지막 화살표를 잡아야 한다.
import importlib.util as _ilu2                                # noqa: E402
_gs = _ilu2.spec_from_file_location('geh', os.path.join(ROOT, 'tools', 'gen_expl_html.py'))
gen_expl_html = _ilu2.module_from_spec(_gs)
_gs.loader.exec_module(gen_expl_html)


def expl_shape(text):
    """글 → (답 표시, tip 이 생겼나)."""
    h = gen_expl_html.build(text)
    m = re.search(r'→ <b>([①-⑤])</b>', h)
    return ((m.group(1) if m else None), '<div class="tip">' in h)


CASES.append(('gen_expl_html 답과 오개념', expl_shape, [
    ('화살표로 끝나면 tip 이 없다',
     '사고과정 하나씩 본다. → ③', ('③', False)),
    ('화살표 뒤의 말은 tip 으로 간다',
     '사고과정 하나씩 본다. → ③ 기체가 나오면 산화환원이라 여김.', ('③', True)),
    ('글 가운데의 동그라미에 안 속는다',
     "사고과정 ④ 셋 모두 LUMO 는 π* 다(옳음). → ③", ('③', False)),
    ('가운데 동그라미가 있어도 뒤의 오개념은 tip 이다',
     '사고과정 ④ 는 옳다. → ② 부호를 뒤바꿔 셈.', ('②', True)),
    ('화살표가 아예 없으면 답 표시도 없다',
     '사고과정 원본 채점표를 그대로 옮겼다.', (None, False)),
]))


# ── rate_check: 정답률이 제자리에 있나 ──────────────────────────────
# 이 자는 여덟 회차의 정답률이 **한 칸씩 밀린 채로** "자료가 성하다" 고 했다.
# 길이도 60, 값도 0~100, 회차도 열 개였으니 재던 셋은 다 통과했다.
# 잴 방법은 있었다 — 폐기된 문항에는 정답률이 인쇄되지 않는다('삭제처리').
# 그러니 빈칸은 폐기 문항 위에 있어야 한다.
import rate_check                                            # noqa: E402


def rate_aligned(given):
    """(회차, 정답률, 폐기 목록) → 자리가 성한가."""
    eid, rate, void = given
    return not rate_check.align_bad(eid, rate, void)


_R = [None if i in (25, 33) else 50 for i in range(1, 61)]    # 25·33번이 빈칸
_OK = [None if i in (26, 34) else 50 for i in range(1, 61)]   # 26·34번이 빈칸

CASES.append(('rate_check 자리', rate_aligned, [
    ('폐기 문항에 빈칸이 있으면 성하다',
     ('hwol-2018', _OK, [26, 34]), True),
    ('한 칸 밀리면 잡는다',
     ('hwol-2018', _R, [26, 34]), False),
    ('폐기 문항에 값이 적혀 있으면 잡는다',
     ('hwol-2018', [50] * 60, [34]), False),
    ('폐기가 없고 빈칸도 없으면 성하다',
     ('hwol-2012', [50] * 60, []), True),
    ('원본에 정답률이 안 적힌 자리는 적어 두었으니 넘긴다',
     ('hwol-2013', [None if i == 31 else 50 for i in range(1, 61)], []), True),
]))


def run_tool(rel, args, text=None):
    """자를 실제로 돌려 종료 코드를 본다."""
    cmd = [sys.executable, os.path.join(ROOT, rel)] + args
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def main():
    check = '--check' in sys.argv
    bad = []
    total = 0

    print('자가 참·거짓 예시를 맞히는가\n')
    for name, fn, cases in CASES:
        ok = 0
        for label, given, want in cases:
            total += 1
            got = fn(given)
            if got == want:
                ok += 1
            else:
                bad.append('%s · %s → %r (맞아야 할 답 %r)' % (name, label, got, want))
        print('  %-24s %d/%d' % (name, ok, len(cases)))

    # ── 진짜로 돌려 보는 자들 ────────────────────────────────────────
    # 지금 저장소가 깨끗하니 --check 는 0 이어야 한다. 1 이 나오면 자가
    # 헛짚는 것이거나 진짜 결함이다 — 어느 쪽이든 사람이 봐야 한다.
    for rel in ('tools/hub_audit.py', 'tools/noindex.py', 'tools/blind_wait.py'):
        total += 1
        code, out = run_tool(rel, ['--check'])
        if code == 0:
            print('  %-24s 깨끗한 저장소에서 조용하다' % os.path.basename(rel))
        else:
            bad.append('%s: 깨끗한 저장소인데 빨간불이다 —\n      %s'
                       % (rel, out.strip().splitlines()[-1] if out.strip() else '(말이 없다)'))

    print('\n예시 %d개' % total)
    if bad:
        print('\n틀린 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n**자를 먼저 본다.** 자가 틀린 것이면 자를 고치고, 예시가 틀린')
        print('것이면 예시를 고친다 — 둘 다 아니면 저장소에 진짜 결함이 있다.')
        return 1 if check else 0

    print('자들이 참·거짓을 그대로 답한다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)

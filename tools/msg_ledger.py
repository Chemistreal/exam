#!/usr/bin/env python3
"""화면이 **사람에게 하는 말**을 한 대장에 모은다.

지금까지의 자들은 글자 크기·대비·뼈대를 봤다. 무엇이 **적혀 있는지**는
아무도 안 봤다. 그런데 학생과 학부모가 실제로 가져가는 것은 그 문장이다.

여기서는 판정하지 않는다. **모아서 줄 세우는 데까지**만 한다
(`docs/내용-400턴.md` 다섯째 원칙 — 사람에게 하는 말은 함부로 안 고친다).

  ① 어디서 뽑나
     ㄱ. 화면에 그대로 박힌 글 (`>…<` 사이)
     ㄴ. 자바스크립트가 만들어 넣는 글 (따옴표 안의 한글)
     둘을 안 가르면 "화면에는 없는데 어떤 경우에만 뜨는 문장" 을 놓친다.

  ② 누가 읽나
     화면 이름으로 가른다. 성적표·해설·강의는 학생, 학부모 리포트는 학부모,
     관리·편집·R&D 는 선생님. 못 가르면 '알 수 없음' 으로 두고 세어 둔다 —
     그 수가 곧 "누구 것인지 안 정한 화면" 의 수다.

  ③ 무엇을 눈여겨보나
     ㄱ. **평가 문장** — 잘한다/부족하다/권한다. 아이가 자기를 보는 방식을 만든다.
     ㄴ. **약속 문장** — "…됩니다/이어집니다". 안 지켜지면 신뢰를 잃는다.
     ㄷ. **실패 문장** — "…못했습니다". 다음에 뭘 하면 되는지가 같이 있어야 한다.

⚠ 이 자는 문장을 **고치지 않는다.** 세고, 갈래를 붙이고, 사람 앞에 놓는다.

    python3 tools/msg_ledger.py              # 요약
    python3 tools/msg_ledger.py --write      # docs/문장대장.md 로 낸다
    python3 tools/msg_ledger.py --check      # 잰 값에서 되돌아가면 빨간불
    python3 tools/msg_ledger.py --repo PATH  # 다른 저장소(DT 등)를 잰다
"""
import argparse
import collections
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, 'tools', 'msg_ledger.json')

# ── 누가 읽는가 ────────────────────────────────────────────────────
# 이름으로 가른다. 이름이 그 화면이 누구 것인지 말하지 못하면 그것도 사실이다.
READER = [
    (r'^(final|final-submit|report|sample_report|integrated-report|batch-report)', '학생'),
    (r'^(sol-|index_haeseol|_haeseol)', '학생'),
    (r'^lec-|^lecture-index|^강의', '학생'),
    (r'^(parent|학부모)', '학부모'),
    (r'^(admin|scan|calibration|response-manager|data-import|qmatrix|prereq-dag-editor)', '선생님'),
    (r'^(hub|dashboard|teaching-brief|system-guide|START_HERE)', '선생님'),
    (r'^(item-|cat|cdm|mirt|knowledge-|learning-|mastery-|spaced-|profile-|ontology-|'
     r'misconception-|multi-|olympiad-|conceptual-|constructed-|content-|test-blueprint|'
     r'longitudinal|diagnosis-|note|cohort)', '선생님'),
    (r'^(paper-|munje|omr)', '학생'),
    # 이름만으로 못 가른 넷은 제목을 열어 보고 정했다(2026-08-09).
    #   grade-j0            조준모의고사 0회 · 자기채점 성적표 → 학생
    #   index               단원평가 정밀 진단 리포트          → 학생
    #   prereq-dag-full     선수 개념 DAG (전체)               → 선생님
    #   prereq-dag-prototype 같은 것의 프로토타입              → 선생님
    (r'^(grade-|index\.html$)', '학생'),
    (r'^prereq-dag', '선생님'),

    # ── DT · study64-report 도 같은 자로 잰다 ──────────────────────
    # 세 저장소를 따로 재면 "우리 성적표는 어떤 말을 하나" 를 세 번 물어야 한다.
    # 이름표는 저장소마다 다르지만 묻는 것은 하나라, 표만 넓힌다.
    (r'^(haeseol_|munje_|omr_)', '학생'),
    (r'^(chemistreal_app|home|exam|retake_entry|challenge)', '학생'),
    (r'^(OX_grader|OMR_|hw_grader|admin_console|roster|pending|letters|pdfs|'
     r'concept_map|dualcoding|diagnosis_app)', '선생님'),
    (r'^(answers|v2|english)', '학생'),
    # ⚠ **한 번 잘못 갈랐던 곳.** `관리자` 를 위 줄에 같이 넣어 두어 '학생' 으로
    #   세고 있었다. 이름이 '관리자' 인 화면을 학생 것으로 센 것이다 — 제목이
    #   '관리자 · 오프라인 수기 입력' 이다. 자가 갈래를 틀리면 "학생이 읽는
    #   평가 문장 몇 개" 라는 수 자체가 틀린다.
    #
    #   KMChC·study64-report 의 세 도구 화면도 이름만으로는 안 갈렸다.
    #   README 가 무엇인지 적고 있어 그것을 보고 정했다(2026-08-10).
    #     리포트_고급_미리보기  내부 미리보기            → 선생님
    #     분석_v2               문항 검증 대시보드        → 선생님
    #     리포트링크생성기       학부모 링크를 만드는 도구  → 선생님
    (r'^(관리자|리포트_고급_미리보기|리포트링크생성기|분석_v2)', '선생님'),
]

# ── 가르치는 글과 사람에게 하는 말을 먼저 가른다 ──────────────────
# ⚠ 이 자는 처음에 이걸 안 갈라서 **거짓말을 했다.** "평가 문장 347개" 라고
#   셌는데 열어 보니 대부분이
#       "결합 차수가 클수록 결합은 짧고 강하다는 대원칙을 …"
#   같은 **해설**이었다. 화학을 설명하는 "…입니다" 와 아이를 두고 하는
#   "…입니다" 는 같은 어미를 쓰지만 전혀 다른 말이다. 어미로만 재면 못 가른다.
#
#   그래서 **화면의 쓰임**으로 먼저 가른다. 해설지·강의·문제지는 가르치는
#   글이고, 성적표·리포트·관리 화면은 사람에게 하는 말이다. 어미는 그다음이다.
TEACHING = re.compile(r'^(sol-|lec-|paper-|munje|_haeseol|index_haeseol|강의|haeseol)')

# ── 갈래 ───────────────────────────────────────────────────────────
# 순서가 뜻을 갖는다. 위에서부터 처음 걸리는 갈래로 센다.
KIND = [
    ('실패', re.compile(r'못했습니다|실패했|오류|불러오지|다시 시도|열 수 없')),
    ('약속', re.compile(r'(로 이어집니다|돌아옵니다|돌아왔습니다|올라갑니다|넘습니다|'
                        r'해결됩니다|보장|회복됩니다|끝납니다)')),
    ('평가', re.compile(r'(입니다|습니다)\.?$')),
    ('시킴', re.compile(r'(하세요|해 보세요|주세요|권합니다|바랍니다|하십시오)')),
]

HANGUL = re.compile(r'[가-힣]')
# 문장으로 볼 만한 것: 한글이 셋 이상이고, 코드 조각이 아닌 것
CODEY = re.compile(r'[{}<>\\]|\$\{|function |return |=>|;;')


def reader_of(name):
    base = os.path.basename(name)
    for pat, who in READER:
        if re.search(pat, base):
            return who
    return '알 수 없음'


def kind_of(text, page):
    """가르치는 글은 갈래를 안 붙인다 — 붙이면 해설이 평가 문장으로 센다."""
    if TEACHING.search(os.path.basename(page)):
        return '가르치는 글'
    t = text.strip()
    for name, pat in KIND:
        if pat.search(t):
            return name
    return '그 밖'


def sentences(src):
    """화면에 박힌 글과, 코드가 만들어 넣는 글을 따로 모은다."""
    body = re.sub(r'<style[\s\S]*?</style>', '', src)
    inline_js = '\n'.join(re.findall(r'<script[^>]*>([\s\S]*?)</script>', body))
    markup = re.sub(r'<script[\s\S]*?</script>', '', body)

    fixed, made = set(), set()
    for m in re.findall(r'>([^<>]{6,200})<', markup):
        t = html.unescape(m).strip()
        if len(HANGUL.findall(t)) >= 3 and not CODEY.search(t):
            fixed.add(re.sub(r'\s+', ' ', t))
    for q in re.findall(r"'((?:[^'\\\n]|\\.){6,200})'|\"((?:[^\"\\\n]|\\.){6,200})\"", inline_js):
        t = (q[0] or q[1]).strip()
        if len(HANGUL.findall(t)) >= 3 and not CODEY.search(t):
            made.add(re.sub(r'\s+', ' ', t))
    return fixed, made


def measure(root):
    pages = sorted(glob.glob(os.path.join(root, '*.html')))
    rows = []
    for p in pages:
        try:
            src = open(p, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        fixed, made = sentences(src)
        who = reader_of(p)
        for t in fixed:
            rows.append((os.path.basename(p), who, '박힌 글', kind_of(t, p), t))
        for t in made:
            rows.append((os.path.basename(p), who, '만들어 넣는 글', kind_of(t, p), t))
    return pages, rows


def summarise(pages, rows):
    by_reader = collections.Counter(r[1] for r in rows)
    by_kind = collections.Counter(r[3] for r in rows)
    by_where = collections.Counter(r[2] for r in rows)
    unknown = sorted({r[0] for r in rows if r[1] == '알 수 없음'})
    return {
        '화면': len(pages),
        '문장': len(rows),
        '독자별': dict(by_reader),
        '갈래별': dict(by_kind),
        '어디에': dict(by_where),
        '독자를 못 가른 화면': len(unknown),
    }


def report(root, rows, pages, verbose=True):
    s = summarise(pages, rows)
    print('화면 %d장 · 사람에게 하는 문장 %d개' % (s['화면'], s['문장']))
    print('\n── 누가 읽나 ──')
    for k, v in sorted(s['독자별'].items(), key=lambda x: -x[1]):
        print('  %-8s %6d' % (k, v))
    print('\n── 어떤 말인가 ──')
    for k, v in sorted(s['갈래별'].items(), key=lambda x: -x[1]):
        print('  %-8s %6d' % (k, v))
    print('\n── 어디에 적혀 있나 ──')
    for k, v in sorted(s['어디에'].items(), key=lambda x: -x[1]):
        print('  %-14s %6d' % (k, v))
    if verbose:
        # 평가·약속은 아이가 가져가는 말이라 실물을 보여 준다.
        for kind in ('약속', '평가'):
            picked = sorted({r[4] for r in rows if r[3] == kind and r[1] in ('학생', '학부모')})
            print('\n── 학생·학부모가 읽는 %s 문장 %d개 (앞 12개) ──' % (kind, len(picked)))
            for t in picked[:12]:
                print('   ', t[:96])
    return s


def write_ledger(rows, pages):
    """훑을 수 있는 꼴로 낸다 — 전부가 아니라 **눈여겨볼 것부터**."""
    s = summarise(pages, rows)
    out = ['# 문장 대장 — 화면이 사람에게 하는 말', '',
           '`python3 tools/msg_ledger.py --write` 가 만든다. 손으로 고치지 않는다.', '',
           '이 대장은 **판정이 아니라 목록**이다. 고칠지는 선생님이 정한다',
           '(`docs/내용-400턴.md` 다섯째 원칙).', '',
           '| | |', '|---|---|',
           '| 화면 | %d장 |' % s['화면'],
           '| 사람에게 하는 문장 | %d개 |' % s['문장'],
           '| 독자를 못 가른 화면 | %d장 |' % s['독자를 못 가른 화면'], '']
    out += ['## 누가 읽나', '', '| 독자 | 문장 |', '|---|---|']
    out += ['| %s | %d |' % (k, v) for k, v in sorted(s['독자별'].items(), key=lambda x: -x[1])]
    out += ['', '## 어떤 말인가', '', '| 갈래 | 문장 | 무엇이 걸리나 |', '|---|---|---|']
    why = {'가르치는 글': '해설·강의·문제지. 화학을 설명하는 말이라 갈래를 안 붙인다',
           '실패': '다음에 뭘 하면 되는지가 같이 있어야 한다',
           '약속': '안 지켜지면 신뢰를 잃는다 — 조건을 같이 적었는가',
           '평가': '아이가 자기를 보는 방식을 만든다',
           '시킴': '한 번에 몇 개를 시키는가',
           '그 밖': '설명·이름표'}
    out += ['| %s | %d | %s |' % (k, v, why.get(k, ''))
            for k, v in sorted(s['갈래별'].items(), key=lambda x: -x[1])]

    for kind in ('약속', '평가', '실패'):
        picked = sorted({(r[1], r[0], r[4]) for r in rows
                         if r[3] == kind and r[1] in ('학생', '학부모')})
        out += ['', '## 학생·학부모가 읽는 %s 문장 (%d개)' % (kind, len(picked)), '',
                '| 독자 | 화면 | 문장 |', '|---|---|---|']
        for who, page, t in picked[:120]:
            out.append('| %s | `%s` | %s |' % (who, page, t.replace('|', '\\|')[:160]))
        if len(picked) > 120:
            out.append('')
            out.append('> 앞 120개만 적는다. 나머지 %d개는 `--check` 가 센다.' % (len(picked) - 120))
    out.append('')
    p = os.path.join(ROOT, 'docs', '문장대장.md')
    open(p, 'w', encoding='utf-8').write('\n'.join(out))
    print('\n적었다 · %s' % os.path.relpath(p, ROOT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=ROOT)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    pages, rows = measure(a.repo)
    s = report(a.repo, rows, pages, verbose=not a.quiet)

    if a.write:
        write_ledger(rows, pages)
        json.dump(s, open(NOTE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('기록했다 · tools/msg_ledger.json')
        return 0

    if a.check and a.repo == ROOT:
        if not os.path.exists(NOTE):
            print('\n기록이 없다 — `--write` 로 먼저 담는다.')
            return 1
        was = json.load(open(NOTE, encoding='utf-8'))
        bad = []
        # 늘어나는 것은 막지 않는다(화면이 늘면 문장도 는다). **줄어드는 것**을 본다 —
        # 문장이 조용히 사라지면 학생이 읽던 말이 없어진 것이다.
        if s['문장'] < was['문장'] * 0.9:
            bad.append('문장이 %d → %d 로 줄었다' % (was['문장'], s['문장']))
        if s['독자를 못 가른 화면'] > was['독자를 못 가른 화면']:
            bad.append('독자를 못 가른 화면이 %d → %d 로 늘었다'
                       % (was['독자를 못 가른 화면'], s['독자를 못 가른 화면']))
        if bad:
            print('\nFAIL')
            for b in bad:
                print('  ' + b)
            return 1
        print('\nPASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)

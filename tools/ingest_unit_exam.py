#!/usr/bin/env python3
"""선생님이 한글(HWPX) 한 파일로 준 **반 시험(문제 + 해설)** 을 파이널 회차로 들인다.

처음 쓴 곳: 화학1 1-3단원 총괄평가(심화반) · 2026-11-16 · 60문항.
읽기는 tools/hwpx_unit_exam.py 가 한다(정답 세 곳 대조 포함).

무엇을 만드는가
---------------
  crops/<id>/<n>.png        문항 크롭 60장 (955px · 오답노트·성적표가 쓴다)
  <id>-problem.pdf          문제지 (표지 + 60문항 · 정답 없음)
  <id>-answer.pdf           해설지 — 선생님 해설 그대로(정답표 · 출제 의도 · 사고 과정 ·
                            선지 분석 · 함정 · 원문항/변형)
  answers/<id>.json         정답 · 영역 · 개념 · 해설 · 선지별 오답 이유
  exams.json                회차 항목 (화학1 단원평가 곁에)

영역 이름
---------
선생님 해설지의 영역 이름 가운데 성적표가 모르는 것은 성적표의 이름으로 옮긴다
(AREA). 원래 이름은 해설지 PDF 에 그대로 남는다. 옮기는 원칙은
tools/ingest_legacy_exam.py 의 ALIAS 와 같다 — 같은 내용이 같은 대영역으로 가야
처방(RXMAP)이 맞는 말을 한다.

쓰기:
    python3 tools/ingest_unit_exam.py <파일.hwpx>            # 재어 보기만
    python3 tools/ingest_unit_exam.py <파일.hwpx> --write    # 심는다
"""
import base64, html, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from hwpx_unit_exam import parse, bins as read_bins, plain, stem_text   # noqa: E402
from hwpx_exam import flat_text, CIRCLED                                # noqa: E402

CROP_W = 955
NODE = '/opt/node22/bin/node' if Path('/opt/node22/bin/node').exists() else 'node'
PW = '/opt/node22/lib/node_modules/playwright' if Path('/opt/node22/lib/node_modules/playwright').exists() else 'playwright'

EXAM = {
    'id': 'kch1to3-s',
    'title': '화학1 1-3단원 총괄평가 (심화반)',
    'range': '몰과 양적관계 ~ 분자의 극성',
    'group': '화학1',
}

# 선생님 영역 → 성적표 영역. 개념(유형) 이름은 선생님 것을 그대로 쓴다.
AREA = {
    '원자의구성': '원자의구조',
    '동위원소': '원자량·동위원소',
    '기초지식': '화학식량',
    'PV=nRT': '몰과부피',
    '오비탈': '양자수',
    'VSEPR': '분자의구조',
    '형식전하': '옥텟규칙',
    '분자의극성': '분자극성',
}
# 「몰=질량/분자량」 은 세 문항이 서로 다른 것을 묻는다 — 개념으로 가른다.
AREA_BY_CONCEPT = {
    '몰과입자수': '몰·아보가드로수',
    '화학량론': '몰과질량',
    '질량백분율과실험식': '양적관계·실험식',
}
# 개념 이름 철자 — 저장소가 이미 쓰는 꼴로 모은다(tools/type_norm.py).
TYPE_SPELL = {'한계반응물과수득률': '한계 반응물과 수득률'}


def concept_of(q):
    return TYPE_SPELL.get(q['concept'], q['concept'])


# 그림·표로 된 선지 — 답지의 choices 는 글이어야 한다(오답 카드가 읽는다).
CHOICE_TEXT = {
    32: ['[↑↓][↑↓][↑↓][↑↓][↑] — 마지막 칸에 홀전자 하나',
         '[↑↓][↑↓][↑][↓][↑↓] — 2p 첫 두 칸에 반대 방향 홀전자',
         '[↑↓][↑↓][↑][↓][↑] — 2p 세 칸에 홀전자 셋(가운데만 아래 방향)',
         '[↑↓][↑↓][↓↓][↑][↑] — 한 칸에 같은 방향 화살표 두 개'],
    52: ['S=S 이중 결합 · S−O 단일 결합 셋', 'S=S 이중 결합 · S=O 하나 · S−O 둘',
         'S−S 단일 결합 · S−O 단일 결합 셋', 'S=S 이중 결합 · S=O 둘 · S−O 하나'],
}


def area_of(q):
    if q['area'] == '몰=질량/분자량':
        return AREA_BY_CONCEPT[q['concept']]
    return AREA.get(q['area'], q['area'])


# ── 글 조각 → html ───────────────────────────────────────────────────────
def frag(s):
    """글 안의 수식 조각(\\x00…\\x01)은 그대로, 나머지는 이스케이프."""
    out, pos = [], 0
    for m in re.finditer('\x00(.*?)\x01', s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        out.append(m.group(1))
        pos = m.end()
    out.append(html.escape(s[pos:], quote=False))
    return ''.join(out)


def img_html(b, bins, maxw=880):
    ext, raw = bins.get(b['ref'], ('png', b''))
    if not raw:
        raise SystemExit('그림 %s 이 파일에 없다' % b['ref'])
    w = b.get('w') or 0
    px = min(maxw, round(w / (7200.0 / 96))) if w else 420     # HWPUNIT → CSS px
    mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/' + ext
    return '<img alt="" style="width:%dpx" src="data:%s;base64,%s">' % (
        px, mime, base64.b64encode(raw).decode())


def is_choice(t):
    return bool(t) and t[0] in CIRCLED


def table_html(b, bins):
    cells = [c for row in b['rows'] for c in row]
    texts = [''.join(x['x'] for x in c['b'] if x['t'] == 'p').strip() for c in cells]
    # 〈보기〉 상자 — 칸 하나에 「<보기>」 와 가·나·다 줄
    if len(cells) == 1 and texts[0].startswith('<보기>'):
        lines = [x for x in cells[0]['b'] if x['t'] == 'p' and x['x'].strip()]
        items = ''.join('<li>%s</li>' % frag(x['x'].strip()) for x in lines[1:])
        return '<div class="bogi"><span class="bogi-h">보 기</span><ul>%s</ul></div>' % items
    if len(cells) == 1:
        inner = blocks_html(cells[0]['b'], bins)
        return '<div class="boxed">%s</div>' % inner
    rows = []
    for row in b['rows']:
        tds = []
        for c in row:
            sp = ''
            if c.get('cs', 1) > 1:
                sp += ' colspan="%d"' % c['cs']
            if c.get('rs', 1) > 1:
                sp += ' rowspan="%d"' % c['rs']
            tds.append('<td%s>%s</td>' % (sp, blocks_html(c['b'], bins, inner=True)))
        rows.append('<tr>%s</tr>' % ''.join(tds))
    return '<table class="grid">%s</table>' % ''.join(rows)


def blocks_html(blocks, bins, inner=False):
    out = []
    for b in blocks:
        if b['t'] == 'p':
            t = b['x'].strip()
            if t:
                out.append('<p>%s</p>' % frag(t) if not inner else frag(t) + '<br>')
        elif b['t'] == 'img':
            out.append('<figure>%s</figure>' % img_html(b, bins) if not inner
                       else img_html(b, bins, maxw=260))
        elif b['t'] == 'tbl':
            out.append(table_html(b, bins))
    h = ''.join(out)
    return h[:-4] if inner and h.endswith('<br>') else h


def choices_html(blocks, bins):
    """선지 — 글 선지는 길이에 따라 네 칸 · 두 칸 · 한 줄. 그림 선지는 번호와 그림을 짝짓는다."""
    has_img = any(b['t'] == 'img' for b in blocks)
    if has_img:
        items, cur = [], None
        for b in blocks:
            if b['t'] == 'p':
                for x in re.split(r'(?=[①-⑤])', b['x']):
                    x = x.strip()
                    if x and x[0] in CIRCLED:
                        cur = [x[0], x[1:].strip(), []]
                        items.append(cur)
            elif b['t'] == 'img' and cur is not None:
                cur[2].append(img_html(b, bins, maxw=200))
        return '<div class="ch ch-img">%s</div>' % ''.join(
            '<div><span class="cn">%s</span>%s%s</div>' % (c, frag(t), ''.join(im)) for c, t, im in items)
    text = ' '.join(b['x'] for b in blocks if b['t'] == 'p')
    items = [x.strip() for x in re.split(r'(?=[①-⑤])', text) if x.strip() and x.strip()[0] in CIRCLED]
    width = max(len(plain(x)) for x in items)
    cols = 4 if width <= 13 else 2 if width <= 30 else 1
    return '<div class="ch c%d">%s</div>' % (cols, ''.join('<div>%s</div>' % frag(x) for x in items))


def question_html(q, bins):
    """지문 블록과 선지 블록을 가른다 — 맨 뒤에 이어진 ① 로 시작하는 문단들이 선지다."""
    body = q['body']
    k = len(body)
    while k > 0 and body[k - 1]['t'] == 'p' and (is_choice(body[k - 1]['x'].strip()) or not body[k - 1]['x'].strip()):
        k -= 1
    # 그림 선지(① 그림 ② 그림 …)는 문단 하나 안에서 글·그림이 번갈아 온다
    j = k
    while j > 0 and body[j - 1]['t'] == 'img' and j - 2 >= 0 and body[j - 2]['t'] == 'p' \
            and is_choice(body[j - 2]['x'].strip()[:1] or ' '):
        j -= 2
    if j < k:
        k = j
    stem, ch = body[:k], body[k:]
    h = blocks_html(stem, bins)
    if ch and any((b['t'] == 'p' and b['x'].strip()) or b['t'] == 'img' for b in ch):
        h += choices_html(ch, bins)
    return h


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;color:#16181d;font-family:'Noto Serif KR','Noto Serif CJK KR',serif;
     font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
.q{width:955px;padding:14px 16px 18px;background:#fff}
.qh{display:flex;align-items:baseline;gap:10px;margin:0 0 9px;
    font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;border-bottom:2px solid #16181d;padding-bottom:5px}
.qn{font-weight:700;font-size:19px;letter-spacing:-.01em}
.q p{margin:.34em 0;text-align:justify;word-break:keep-all}
figure{margin:.55em 0;text-align:center}
figure img{max-width:100%;height:auto}
.ch{margin:.55em 0 0;font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;font-size:16.5px;
    display:grid;gap:.22em 18px}
.ch.c4{grid-template-columns:repeat(4,1fr)}
.ch.c2{grid-template-columns:repeat(2,1fr)}
.ch.c1{grid-template-columns:1fr}
.ch div{padding-left:1.5em;text-indent:-1.5em;word-break:keep-all}
.ch-img{grid-template-columns:repeat(4,1fr);align-items:start}
.ch-img div{padding:0;text-indent:0;text-align:center}
.ch-img .cn{display:block;font-weight:500;margin:0 0 4px}
.ch-img img{max-width:100%;height:auto}
.bogi{position:relative;border:1.3px solid #16181d;padding:16px 16px 9px;margin:.75em 0 .45em;
      font-size:16px}
.bogi-h{position:absolute;top:-.8em;left:50%;transform:translateX(-50%);background:#fff;
        padding:0 10px;font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;font-size:14px;letter-spacing:.2em}
.bogi ul{list-style:none}
.bogi li{margin:.18em 0;padding-left:1.4em;text-indent:-1.4em;word-break:keep-all}
.boxed{border:1.1px solid #9aa0ad;padding:8px 12px;margin:.5em 0;text-align:center}
table.grid{border-collapse:collapse;margin:.6em auto;border:1.4px solid #16181d}
table.grid td{border:1px solid #9aa0ad;padding:4px 10px;font-size:15.5px;text-align:center;vertical-align:middle}
table.grid td img{max-width:240px;height:auto}
.nuc{white-space:nowrap}
.nu{display:inline-block;vertical-align:-.38em;line-height:1.02;font-size:.64em;text-align:right;margin:0 .04em 0 .1em;text-indent:0}
.nu>span{display:block}
.nuc sup,.nuc sub{font-size:.66em;line-height:0}
.nuc .na{margin-left:.1em}
.frac{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;margin:0 .2em}
.frac span:first-child{border-bottom:1px solid #16181d;padding:0 .2em}
.eq{white-space:nowrap}
.cover{page-break-after:always;font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;
       display:flex;flex-direction:column;justify-content:center;min-height:940px;text-align:center}
.cv-brand{font-size:14px;letter-spacing:.32em;color:#8a90a0;margin:0 0 18px}
.cover h1{font-size:34px;letter-spacing:-.02em;margin:0 0 10px;word-break:keep-all}
.cv-meta{font-size:16px;color:#5b6270;margin:0 0 46px}
.cv-id{display:flex;justify-content:center;gap:26px;margin:0 0 52px;font-size:15px}
.cv-id b{font-weight:500;color:#5b6270}
.cv-line{display:inline-block;width:150px;border-bottom:1.5px solid #16181d;vertical-align:-3px;margin-left:8px}
.cv-rules{list-style:none;margin:0 auto;padding:16px 22px;max-width:540px;text-align:left;
          font-size:13.5px;color:#5b6270;border:1px solid #d7dae2;border-radius:8px}
.cv-rules li{margin:.3em 0;padding-left:1.1em;text-indent:-1.1em}
@media print{.q{page-break-inside:avoid}}
"""


def cover_html(title, sub, n, rules):
    return ('<header class="cover"><p class="cv-brand">CHEMISTREAL · 조준모 화학</p>'
            '<h1>%s</h1><p class="cv-meta">%s · %d문항</p>'
            '<div class="cv-id"><span><b>학교</b><span class="cv-line"></span></span>'
            '<span><b>이름</b><span class="cv-line"></span></span></div>'
            '<ul class="cv-rules">%s</ul></header>'
            % (html.escape(title), html.escape(sub), n, ''.join('<li>· %s</li>' % r for r in rules)))


def paper_html(d, bins, cover=True):
    parts = []
    if cover:
        parts.append(cover_html(EXAM['title'], EXAM['range'], d['nQ'], [
            '문항마다 알맞은 답을 하나만 고릅니다.',
            '계산에 필요한 원자량·상수는 문항에 주어진 값을 씁니다.',
            '다 푼 뒤 답안 입력 화면에 답을 넣으면 개인 성적표와 해설을 받습니다.']))
    for q in d['q']:
        parts.append('<section class="q" data-n="%d"><div class="qh"><span class="qn">문제 %d</span></div>%s</section>'
                     % (q['n'], q['n'], question_html(q, bins)))
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>%s</title>'
            '<style>%s</style></head><body>%s</body></html>'
            % (html.escape(EXAM['title']), CSS, ''.join(parts)))


# ── 해설지 ──────────────────────────────────────────────────────────────
SOL_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans KR','Noto Sans CJK KR',sans-serif;color:#1a1a1a;font-size:13.5px;line-height:1.7}
.hd{border-bottom:2px solid #0E5A4C;padding:0 0 10px;margin:0 0 14px}
.hd .b{font-size:11px;letter-spacing:.16em;color:#0E5A4C;font-weight:700}
.hd h1{font-size:22px;margin:4px 0 2px}
.hd p{color:#4a463f;font-size:12.5px}
table.key{border-collapse:collapse;width:100%;font-size:12px;margin:0 0 6px}
table.key th,table.key td{border:1px solid #d9d4ca;padding:3px 6px;text-align:center}
table.key th{background:#f3f0ea;font-weight:600}
table.key td.l{text-align:left}
.q{border:1px solid #e6e2da;border-radius:6px;padding:10px 13px;margin:0 0 10px;page-break-inside:avoid}
.qh{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;border-bottom:1px solid #e6e2da;padding:0 0 5px;margin:0 0 6px}
.qh .n{font-weight:700;font-size:15px}
.qh .a{color:#0E5A4C;font-weight:700}
.qh .m{color:#6b665d;font-size:12px}
h4{font-size:12px;color:#0E5A4C;margin:7px 0 2px;letter-spacing:.04em}
.st{margin:1px 0 1px 1.5em;text-indent:-1.5em}
.st b{color:#0E5A4C;font-weight:600}
.st .sub{display:block;padding-left:1.2em;color:#333}
.trap{margin:7px 0 0;padding:5px 9px;background:#FBF4EE;border-left:3px solid #C0603A}
.org{margin:6px 0 0;font-size:11.5px;color:#6b665d}
"""


def sol_html(d):
    rows = ''.join(
        '<tr><td>%d</td><td>%s</td><td class="l">%s</td><td class="l">%s</td><td>%s</td></tr>'
        % (q['n'], CIRCLED[q['answer'] - 1], html.escape(q['area']), html.escape(q['concept']), q['level'])
        for q in d['q'])
    lv = {k: sum(1 for q in d['q'] if q['level'] == k) for k in '하중상'}
    cards = []
    for q in d['q']:
        s = q['sol']
        steps = ''.join('<p class="st">%s</p>' % (('<b>%s</b> ' % st['k'] + html.escape(st['t'])) if st['k']
                                                   else '<span class="sub">– %s</span>' % html.escape(st['t']))
                        for st in s['steps'])
        opts = ''
        seen = set()
        for k in sorted(s['options']):
            v = s['options'][k]
            if v in seen:
                continue
            seen.add(v)
            lab = v if re.match(r'^[①-⑤]', v) else '%s %s' % (CIRCLED[k - 1], v)
            opts += '<p class="st">%s</p>' % html.escape(lab)
        cards.append(
            '<section class="q"><div class="qh"><span class="n">문제 %d</span><span class="a">정답 %s</span>'
            '<span class="m">%s · %s · 난이도 %s</span></div>'
            '<h4>출제 의도</h4><p>%s</p><h4>사고 과정</h4>%s%s%s%s</section>'
            % (q['n'], CIRCLED[q['answer'] - 1], html.escape(q['area']), html.escape(q['concept']), q['level'],
               html.escape(s['intent']), steps,
               ('<h4>선지 분석</h4>' + opts) if opts else '',
               ('<p class="trap"><b>함정</b> %s</p>' % html.escape(s['trap'])) if s['trap'] else '',
               ('<p class="org">원문항 %s%s</p>' % (html.escape(s['origin']),
                ' · 변형 ' + html.escape(s['variant']) if s['variant'] else '')) if s['origin'] else ''))
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>%s 해설지</title><style>%s</style>'
            '</head><body><div class="hd"><div class="b">CHEMISTREAL · 해설지</div><h1>%s</h1>'
            '<p>%s · 60문항 · 난이도 하 %d · 중 %d · 상 %d · 문항별 정답 · 영역 · 개념 · 사고 과정 · 선지 분석</p></div>'
            '<table class="key"><tr><th>문항</th><th>정답</th><th>영역</th><th>개념(유형)</th><th>난이도</th></tr>%s</table>'
            '<div style="page-break-before:always"></div>%s</body></html>'
            % (html.escape(EXAM['title']), SOL_CSS, html.escape(EXAM['title']), html.escape(EXAM['range']),
               lv['하'], lv['중'], lv['상'], rows, ''.join(cards)))


# ── 답지 ────────────────────────────────────────────────────────────────
def expl_parts(q):
    """해설 조각 — 글(explanation)과 꼴(explanationHtml)을 같은 조각에서 만든다.
    tools/gen_expl_html.py 가 둘이 같은 말인지 본다."""
    s = q['sol']
    sec = [('출제 의도', [s['intent']]),
           ('사고 과정', [('%s %s' % (st['k'], st['t'])) if st['k'] else '– ' + st['t'] for st in s['steps']])]
    opts, seen = [], set()
    for k in sorted(s['options']):
        v = s['options'][k]
        if v in seen:
            continue
        seen.add(v)
        opts.append(v if re.match(r'^[①-⑤]', v) else '%s %s' % (CIRCLED[k - 1], v))
    if opts:
        sec.append(('선지 분석', opts))
    return sec


def expl_text(q):
    out = []
    for h, lines in expl_parts(q):
        out.append(h)
        out.extend(lines)
    out.append('→ %s' % CIRCLED[q['answer'] - 1])
    return '\n'.join(out)


def _sup(s):
    s = html.escape(s, quote=False)
    s = re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+', lambda m: '<sup>%s</sup>' % m.group(0).translate(
        str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻', '0123456789+−')), s)
    s = re.sub('[₀₁₂₃₄₅₆₇₈₉]+', lambda m: '<sub>%s</sub>' % m.group(0).translate(
        str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')), s)
    return s


def expl_html(q):
    """절(출제 의도 · 사고 과정 · 선지 분석)을 살린 꼴. 선지 분석 줄은 class="step opt" 로 둔다 —
    tools/gen_expl_html.py 는 자기 어휘(step·tip·h4·b·첨자)만 쓴 꼴을 «기계가 입힌 옷» 으로 보고
    문장 나누기 꼴로 다시 입히는데, 그러면 절 머리가 사라진다. 사람 해설지의 절은 그대로 둔다."""
    out = []
    for h, lines in expl_parts(q):
        out.append('<h4>%s</h4>' % h)
        cls = {'선지 분석': 'step opt', '출제 의도': 'step aim'}.get(h, 'step')
        out.extend('<p class="%s">%s</p>' % (cls, _sup(x)) for x in lines)
    out.append('<p class="step">→ <b>%s</b></p>' % CIRCLED[q['answer'] - 1])
    return '\n'.join(out)


def answers_json(d):
    qs = {}
    for q in d['q']:
        s = q['sol']
        n = q['n']
        choices = CHOICE_TEXT.get(n) or q['choices']
        if not all(choices):
            # 표로 된 선지(55번) — 표 줄을 글로
            tb = next(b for b in q['body'] if b['t'] == 'tbl')
            rows = [[''.join(x['x'] for x in c['b'] if x['t'] == 'p').strip() for c in r] for r in tb['rows']]
            head = rows[0][1:]
            choices = [', '.join('%s %s' % (h, v) for h, v in zip(head, r[1:])) for r in rows[1:5]]
        wrong = {}
        for k, v in s['options'].items():
            if k != q['answer'] and v:
                wrong[str(k)] = re.sub(r'^[①-⑤,\s]+[:：]?\s*', '', v).strip()
        qs[str(n)] = {
            'answer': q['answer'],
            'acceptableAnswers': [q['answer']],
            'excluded': False,
            'concept': concept_of(q),
            'area': area_of(q),
            'learningPoint': concept_of(q),
            'explanation': expl_text(q),
            'explanationHtml': expl_html(q),
            'misconception': s['trap'],
            'misconceptions': wrong,
            'stem': stem_text([b for b in q['body'] if not (b['t'] == 'p' and is_choice(b['x'].strip()))]),
            'choices': choices,
            'level': q['level'],
            'teacherArea': q['area'],
            'origin': (s['origin'] + (' · 변형 ' + s['variant'] if s['variant'] else '')).strip(),
            'sourceSolution': '선생님 해설지 (%s-answer.pdf)' % EXAM['id'],
            'verificationStatus': 'verified_against_supplied_solution_book',
        }
    return {'schemaVersion': 1, 'examId': EXAM['id'], 'examTitle': EXAM['title'],
            'generatedAt': '2026-11-16',
            'note': 'tools/ingest_unit_exam.py 가 선생님 한글 원본(문제+해설 한 파일)에서 옮겼다. '
                    '정답은 정답표 · 해설 머리 · 선지 분석 세 곳이 같다.',
            'questions': qs}


def entry(d):
    return {
        'id': EXAM['id'], 'title': EXAM['title'], 'group': EXAM['group'], 'nQ': d['nQ'],
        'mode': 'auto', 'cut': [0, 4, 11, 17, 23],
        'key': [q['answer'] for q in d['q']], 'miss': [],
        'area': [area_of(q) for q in d['q']],
        'type': [concept_of(q) for q in d['q']],
        'crops': True, 'sol': 'sol-final-%s.html' % EXAM['id'],
        'pdf': '%s-problem.pdf' % EXAM['id'], 'answerPdf': '%s-answer.pdf' % EXAM['id'],
        'source': {'tool': 'tools/ingest_unit_exam.py', 'kind': '단원별'},
        'solFull': True,
    }


SHOT_JS = r"""
const {chromium} = require(process.argv[2]);
const fs = require('fs'), path = require('path');
(async () => {
  const [_, __, ___, htmlPath, outDir, pdfPath, solHtml, solPdf] = process.argv;
  const b = await chromium.launch({args:['--no-sandbox']});
  const pg = await b.newPage({viewport:{width:1100,height:1400}, deviceScaleFactor:2});
  await pg.goto('file://' + path.resolve(htmlPath), {waitUntil:'load'});
  await pg.evaluate(() => document.fonts.ready);
  if (outDir !== '-') {
    fs.mkdirSync(outDir, {recursive:true});
    for (const n of await pg.$$eval('.q', els => els.map(e => e.dataset.n))) {
      await (await pg.$(`.q[data-n="${n}"]`)).screenshot({path: path.join(outDir, n + '.png')});
    }
  }
  const foot = {displayHeaderFooter:true, headerTemplate:'<span></span>',
    footerTemplate:'<div style="width:100%;text-align:center;font-size:9px;color:#8a90a0;font-family:sans-serif;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'};
  await pg.pdf(Object.assign({path: pdfPath, format:'A4', printBackground:true,
      margin:{top:'12mm', bottom:'15mm', left:'10mm', right:'10mm'}}, foot));
  const sp = await b.newPage();
  await sp.goto('file://' + path.resolve(solHtml), {waitUntil:'load'});
  await sp.evaluate(() => document.fonts.ready);
  await sp.pdf(Object.assign({path: solPdf, format:'A4', printBackground:true,
      margin:{top:'13mm', bottom:'15mm', left:'12mm', right:'12mm'}}, foot));
  await b.close();
})();
"""


def render(d, bins, crops_dir, pdf_path, sol_pdf):
    from PIL import Image
    tmp = Path(tempfile.mkdtemp(prefix='unit-'))
    try:
        (tmp / 'paper.html').write_text(paper_html(d, bins), encoding='utf-8')
        (tmp / 'sol.html').write_text(sol_html(d), encoding='utf-8')
        (tmp / 'shot.js').write_text(SHOT_JS, encoding='utf-8')
        raw = tmp / 'raw'
        r = subprocess.run([NODE, str(tmp / 'shot.js'), PW, str(tmp / 'paper.html'), str(raw),
                            str(pdf_path), str(tmp / 'sol.html'), str(sol_pdf)],
                           capture_output=True, text=True)
        if r.returncode:
            raise SystemExit('조판 실패:\n' + r.stderr[-2000:])
        crops_dir.mkdir(parents=True, exist_ok=True)
        for old in crops_dir.glob('*.png'):
            old.unlink()
        for q in d['q']:
            im = Image.open(raw / ('%d.png' % q['n'])).convert('RGB')
            im = im.resize((CROP_W, round(im.height * CROP_W / im.width)), Image.LANCZOS)
            im.save(crops_dir / ('%d.png' % q['n']), optimize=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def write_exam_entry(ent):
    p = ROOT / 'exams.json'
    E = json.loads(p.read_text(encoding='utf-8'))
    prev = next((e for e in E if e['id'] == ent['id']), None)
    if prev is not None:
        # 다시 들이면 판(rev)을 올린다 — 크롭 주소의 ?v= 로 실려 서비스워커 캐시를 깬다
        ent['rev'] = int(prev.get('rev') or 1) + 1
        E = [ent if e['id'] == ent['id'] else e for e in E]
    else:
        at = max(i for i, e in enumerate(E) if e.get('group') == EXAM['group']) + 1
        E.insert(at, ent)
    # 저장소의 exams.json 은 한 회차 한 줄 꼴이다 — 같은 꼴로 쓴다
    txt = p.read_text(encoding='utf-8')
    one_line = txt.lstrip().startswith('[\n{') or '\n{"id"' in txt
    if one_line:
        p.write_text('[\n' + ',\n'.join(json.dumps(e, ensure_ascii=False) for e in E) + '\n]\n', encoding='utf-8')
    else:
        p.write_text(json.dumps(E, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def write_answers(d):
    # 한글 원본은 온도를 ℃(U+2103, CJK 호환 글자)로 적는다. 저장소는 °C 로
    # 모았고 tools/dh_lint.py 가 지킨다 — 글자 자료로 옮겨 담는 이 문에서 바꾼다.
    # (문제지·크롭은 원본 인쇄 그대로 둔다.)
    text = json.dumps(answers_json(d), ensure_ascii=False, indent=1).replace('\u2103', '°C')
    (ROOT / 'answers' / ('%s.json' % EXAM['id'])).write_text(text + '\n', encoding='utf-8')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    d = parse(args[0])
    ent = entry(d)
    unknown = sorted({a for a in ent['area']} - set(__import__('area_tag').known()[0]))
    if unknown:
        raise SystemExit('성적표가 모르는 영역 이름: %s — AREA 에 옮길 이름을 적는다' % unknown)
    print('%s · %d문항 · 정답 %s… · 영역 %d가지'
          % (EXAM['id'], d['nQ'], ''.join(str(k) for k in ent['key'][:15]), len(set(ent['area']))))
    if '--write' not in sys.argv:
        return 0
    bins = read_bins(args[0])
    render(d, bins, ROOT / 'crops' / EXAM['id'], ROOT / ('%s-problem.pdf' % EXAM['id']),
           ROOT / ('%s-answer.pdf' % EXAM['id']))
    write_answers(d)
    write_exam_entry(ent)
    print('심었다 — 크롭 %d · 문제지 · 해설지 · 답지 · exams.json' % d['nQ'])
    return 0


if __name__ == '__main__':
    sys.exit(main())

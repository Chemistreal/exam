#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단원별 모의고사 여덟 회차를 성적표 시스템에 들인다.

    화학1 1단원 · 1-2단원 · 1-3단원(원본·동형) · 화학2 1단원 · 1-3단원 · 총괄평가

■ 왜 밖에 있었나
  이 여덟 회차는 저장소에 **두 벌**로 흩어져 있었다.

    index.html    회차 등기(제목·범위·응시 수)와 문항 배열 — 정답·정답률·영역·개념·복수정답
    exam_*.json   문항 본문 — 줄기·보기·해설·오개념·출처

  둘 다 온전한데 `exams.json` 에 없어서, final.html 은 이 회차를 아예 모른다.
  그래서 채점도 성적표도 시트 저장도 오답노트도 재도전 10제도 없었다. 학생이
  할 수 있는 것은 문제지(paper-*.html)와 해설(sol-*.html)을 **읽는 것**뿐이었다.

■ 두 벌을 맞대는 까닭
  정답이 두 곳에 따로 적혀 있다. 하나로 합치기 전에 **반드시 대조한다** —
  어긋나는 문항이 하나라도 있으면 멈춘다. 성적표는 정답이 틀리면 조용히
  틀리고, 그 조용함이 가장 나쁘다.

■ 크롭
  오답노트는 `crops/<회차>/<번호>.png` 로 «원문 문제» 를 보여 준다. 이 여덟
  회차는 크롭이 없었으므로 여기서 만든다. 두 갈래다.

    빌린다   출처가 「화학올림피아드 20NN년 M번」 이고 그 회차가 이미 저장소에
             있으면 **진짜 크롭**(그림·표가 살아 있는 원본)을 빌려 쓴다.
             빌리기 전에 정답이 같은지 대조한다 — 다르면 안 빌린다.
    그린다   나머지는 줄기·보기를 글로 그려 크롭을 만든다.

  ⚠ 솔직히 적어 둔다: exam_*.json 은 .hwp 에서 **글만** 캔 것이라 원본의
    그림·표가 들어 있지 않다. 그래서 그려서 만든 크롭에는 그림이 없다.
    줄기가 「그림」·「표」 를 가리키는데 빌리지도 못한 문항은 `--check` 가
    세어서 알려 준다 — 선생님이 나중에 그림을 채워 넣을 자리다.

사용:
    python3 tools/ingest_legacy_exam.py --check
    python3 tools/ingest_legacy_exam.py --write            # 여덟 회차 전부
    python3 tools/ingest_legacy_exam.py --write kch1u1     # 한 회차만
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

CROP_W = 955
NODE = os.environ.get('NODE_BIN', 'node')
PW = os.environ.get('PLAYWRIGHT_MODULE', 'playwright')

# ── 회차 여덟 ────────────────────────────────────────────────────────────
#   id, index.html 의 배열 이름, 본문 파일, 목록에서의 묶음
EXAMS = [
    ('kch1u1',    'Q_KCH1U1',  'exam_kch1u1_full.json',      '화학1'),
    ('kch1to2',   'Q_KCH1TO2', 'exam_kch1to2원본_HWP.json',   '화학1'),
    ('kch1to2-b', 'Q_KCH12B',  'exam_kch1to2동형_HWP.json',   '화학1'),
    ('kch1to3',   'Q_KCH1',    'exam_kch1to3원본_HWP.json',   '화학1'),
    ('kch1to3-b', 'Q_KCH13B',  'exam_kch1to3동형_HWP.json',   '화학1'),
    ('chem2-1',   'Q_CHEM21',  'exam_chem2-1_full.json',     '화학2'),
    ('kch2to3',   'Q_KCH2TO3', 'exam_kch2to3_full.json',     '화학2'),
    ('kch2final', 'Q_KCH2F',   'exam_kch2final_full.json',   '화학2'),
]
GROUP_LABEL = {'화학1': '화학1 단원별', '화학2': '화학2 단원별'}

# ── 영역 이름 옮기기 ─────────────────────────────────────────────────────
# 이 회차들이 쓰는 이름 중 저장소 어휘에 없는 것. 값은 반드시 area_tag.known()
# 안에 있어야 한다(그래야 RXMAP 이 대영역으로 데려간다).
ALIAS = {
    # ── 실제 문항을 읽고 옮긴 것(제안 → 서로 다른 세 눈으로 반박) ──────────
    '우주와 원소': '원소의기원',
    '주기성': '주기율',
    '원자와 원소': '원자의구조',
    '분자 구조·극성': '쌍극자모멘트',
    '몰과 화학량': '몰과개수',
    '분자 구조': '분자의구조',
    '운동속력': '분자운동속도',
    '화학반응식': '계수맞추기',
    '고체심화': '고체의밀도',
    'PV=nRT': '기체',
    '고체·결정': '고체의구조',
    '원자': '원자의구조',
    # ⚠ '화학식량' 으로 보내려다 되돌렸다. 이 회차(kch1u1)는 평균 원자량을
    # **계산하는** 문항을 '원자량' 이라는 별도 영역으로 이미 갈라 두었고,
    # '동위원소' 쪽 여섯은 전부 원자를 이루는 입자와 존재비를 묻는다.
    # 화학식량으로 보내면 대영역이 몰과양적관계가 되어 «한계반응물·연소분석·
    # 계수맞추기» 처방이 나간다 — 동위원소 쌍을 못 고른 학생에게 그건 남의 말이다.
    '동위원소': '원자의구조',
    '고체구조': '고체의구조',
    '산염기평형': '이온화도',
    '기본입자': '원자의구조',
    '원자량': '화학식량',
    '실험식': '원소분석장치',
    '분자간력·액체': '분자간인력',
    '이상기체': '기체',
    '농도': '용액의농도',
    '산염기': '산과염기',
    '용액·농도': '용액의농도',
    # ⚠ '물질의분리' 로 보내려다 되돌렸다. 이 문항(kch1to3·-b 4번)은 입자 모형으로
    # 순물질과 혼합물을 **가려내는** 것이고, 증류·추출·크로마토그래피는 한 글자도
    # 안 나온다. 그런데 물질의분리는 대영역이 「액체,용액」 이라 — 이 회차가
    # 다루지도 않는 단원의 막대와 처방이 생기고, 재도전 풀에도 그 태그는
    # 크로마토그래피 한 문항뿐이라 곧장 대영역으로 흘러내려 몰농도·삼투압으로
    # 재도전하게 된다.
    '물질의 분류': '원자의구조',
    '증기압력': '상평형',
    '실제용액': '용액의총괄성',
    # ── index.html 쪽에만 있는 이름 ──────────────────────────────────────
    '몰': '몰과양적관계',
    '분자의 극성': '쌍극자모멘트',
    '보어모형': '원자모형',
    '빅뱅': '원소의기원',
    '양자역학': '양자수',
    '화학의 기초': '원자의구조',
    '원소분석': '원소분석장치',
    '반지름': '원자반지름',
    '주기적성질': '주기율',
}

# 같은 개념인데 저장소가 이미 다른 철자로 적어 둔 것. 갈려 적히면 재도전이
# 「같은 유형」 을 못 알아본다(tools/type_norm.py 가 이것을 잡는다).
SPELL = {
    '분자의 극성': '분자의극성',
    '헨더슨하셀바흐식': '헨더슨-하셀바흐식',
    'Pv=nRT': 'PV=nRT',          # 대소문자만 다른 오타
    '평균자유핼오': '평균자유행로',   # 오타 — 저장소에 제 철자가 이미 있다
}

_UNKNOWN = set()


def canon(area, typ=''):
    """영역 이름을 저장소가 아는 이름으로. 못 옮기면 기록해 두고 '기타'."""
    import ingest_hwpx_exam as H
    for t in (area, typ):
        if not t:
            continue
        if t in ALIAS:
            return ALIAS[t]
        m = H.map_area(t)
        if m != '기타':
            return m
    _UNKNOWN.add(area or typ)
    return '기타'


# ── index.html 등기 읽기 ─────────────────────────────────────────────────
def index_src():
    return (ROOT / 'index.html').read_text(encoding='utf-8')


def rows_of(src, var):
    m = re.search(r'const %s=(\[.*?\]);' % re.escape(var), src, re.S)
    if not m:
        raise SystemExit('index.html 에 %s 가 없다' % var)
    return json.loads(m.group(1))


def meta_of(src, eid):
    """{id:"...",title:"...",range:"...",N:443,haeseol:"..."} 한 줄."""
    m = re.search(r'\{id:"%s",title:"([^"]*)",range:"([^"]*)",source:"([^"]*)",'
                  r'N:(\d+),haeseol:"([^"]*)"' % re.escape(eid), src)
    if not m:
        raise SystemExit('index.html 에 %s 등기가 없다' % eid)
    return {'title': m.group(1), 'range': m.group(2), 'source': m.group(3),
            'N': int(m.group(4)), 'haeseol': m.group(5)}


# ── 두 벌 맞대기 ─────────────────────────────────────────────────────────
SRC_RE = re.compile(r'화학올림피아드\s*(\d{4})년\s*(\d+)번')
FIG_RE = re.compile(r'그림|도표|아래\s*표|다음\s*표|위\s*표|\(가\)|\(나\)|\(다\)'
                    r'|그래프|모식도|장치|실험\s*결과|추출되지 않')


def load(eid, var, body, group):
    src = index_src()
    meta = meta_of(src, eid)
    rows = rows_of(src, var)
    full = json.loads((ROOT / body).read_text(encoding='utf-8'))
    if len(rows) != 60:
        raise SystemExit('%s: index.html 문항이 %d개다 (60이어야 한다)' % (eid, len(rows)))

    exams = {e['id']: e for e in
             json.loads((ROOT / 'exams.json').read_text(encoding='utf-8'))}
    qs, bad = [], []
    for r in rows:
        n = r[0]
        f = full.get(str(n)) or {}
        ans_i = r[1]                      # index.html 의 정답
        ans_f = f.get('answer')           # 본문 파일의 정답
        try:
            ans_f = int(ans_f)
        except (TypeError, ValueError):
            ans_f = None
        if ans_f is not None and ans_f != ans_i:
            bad.append('%s %d번: index.html 은 %s, %s 는 %s' % (eid, n, ans_i, body, ans_f))
        # 출처가 가리키는 원본에서 크롭을 빌릴 수 있는가
        borrow = None
        m = SRC_RE.search(f.get('source') or '')
        if m:
            sid, sq = 'hwol-%s' % m.group(1), int(m.group(2))
            e = exams.get(sid)
            if (e and sq <= len(e.get('key') or [])
                    and (ROOT / 'crops' / sid / ('%d.png' % sq)).exists()
                    and e['key'][sq - 1] == ans_i):     # 정답까지 같아야 빌린다
                borrow = {'e': sid, 'q': sq}
        stem = (f.get('stem') or '').strip()
        qs.append({
            'n': n, 'ans': ans_i,
            'rate': r[2] if len(r) > 2 and isinstance(r[2], int) else None,
            'area': canon(r[3] if len(r) > 3 else '', r[4] if len(r) > 4 else ''),
            'type': SPELL.get((r[4] if len(r) > 4 else '') or '',
                              (r[4] if len(r) > 4 else '') or ''),
            'accept': r[5] if len(r) > 5 and isinstance(r[5], list) else None,
            'stem': stem, 'choices': f.get('choices') or [],
            'sol': (f.get('solution') or '').strip(),
            'misc': _misc_text(f.get('misc')),
            'src': (f.get('source') or '').strip(),
            'misc_by': f.get('misc') if isinstance(f.get('misc'), dict) else None,
            'borrow': borrow,
            'fig': bool(FIG_RE.search(stem)),
        })
    if bad:
        raise SystemExit('정답이 두 곳에서 어긋난다 — 합치기 전에 사람이 봐야 한다:\n  '
                         + '\n  '.join(bad))
    return {'id': eid, 'group': group, 'meta': meta, 'q': qs}


def _misc_text(m):
    """오개념은 한 줄 글이 원칙인데, 열한 문항은 **보기별로** 적혀 있다.

    성적표는 misconception 을 글로 찍으므로 사전을 그대로 주면 [object Object]
    가 나온다. 그러니 글로 합치되, 보기별 사전은 misconceptions(복수)로 따로
    남겨 둔다 — 동형문제 보기 누르기가 쓰는 자리가 이미 그 이름이다."""
    if isinstance(m, dict):
        if m.get('*'):
            return str(m['*']).strip()
        return ' · '.join('%s %s' % (k, str(v).strip())
                          for k, v in sorted(m.items()) if v)
    return (m or '').strip()


# ── 내보내기 ─────────────────────────────────────────────────────────────
def cut_of(n):
    base = [0, 4, 9, 13, 18]
    return [0] + [max(i, round(v * n / 60)) for i, v in enumerate(base[1:], 1)]


def entry_of(d):
    qs = d['q']
    multi = {str(q['n']): q['accept'] for q in qs if q['accept']}
    e = {
        'id': d['id'], 'title': d['meta']['title'], 'group': d['group'],
        'nQ': 60, 'mode': 'auto', 'cut': cut_of(60),
        'key': [q['ans'] for q in qs], 'miss': [],
        'area': [q['area'] for q in qs], 'type': [q['type'] for q in qs],
        'rate': [q['rate'] for q in qs],
        'crops': True, 'sol': 'sol-final-%s.html' % d['id'],
        'pdf': '%s-problem.pdf' % d['id'],
        'source': {'tool': 'tools/ingest_legacy_exam.py', 'kind': '단원별'},
    }
    if multi:
        e['multi'] = multi
    return e


def answers_of(d):
    out = {}
    for q in d['q']:
        rec = {'answer': q['ans'], 'area': q['area'], 'concept': q['type']}
        if q['sol']:
            rec['explanation'] = q['sol']
        if q['misc']:
            rec['misconception'] = q['misc']
        if q['misc_by']:
            rec['misconceptions'] = {k: v for k, v in q['misc_by'].items() if k != '*'}
        if q['stem']:
            rec['stem'] = q['stem']
        if q['choices']:
            rec['choices'] = q['choices']
        if q['src']:
            rec['sourceSolution'] = q['src']
        # 인정 답안은 **언제나** 적는다. 비워 두면 tools/answer_sync.py 가
        # 「인정 답 [] ≠ 채점 [3]」 으로 잡는다 — 해설 쪽이 채점을 안 따라간
        # 것으로 읽히기 때문이다. 복수정답이면 그 목록, 아니면 정답 하나.
        rec['acceptableAnswers'] = q['accept'] or [q['ans']]
        out[str(q['n'])] = rec
    return {'examId': d['id'], 'title': d['meta']['title'],
            'note': 'tools/ingest_legacy_exam.py 가 index.html + exam_*.json 에서 만든다. '
                    '손으로 고치지 않는다.',
            'questions': out}


# ── 크롭 ─────────────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;color:#16181d;font-family:'Noto Serif KR',serif;
     font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
.q{width:955px;padding:14px 16px 18px;background:#fff}
.qh{display:flex;align-items:baseline;gap:10px;margin:0 0 9px;
    font-family:'Noto Sans KR',sans-serif;border-bottom:2px solid #16181d;
    padding-bottom:5px}
.qn{font-weight:700;font-size:19px;letter-spacing:-.01em}
.qa{font-size:14px;color:#5b6270;font-weight:500}
.ql{margin-left:auto;font-size:12px;color:#8a90a0}
.q p{margin:.34em 0;text-align:justify;word-break:keep-all}
.ch{margin:.5em 0 0;font-family:'Noto Sans KR',sans-serif;font-size:16.5px}
.ch li{list-style:none;margin:.18em 0;padding-left:1.5em;text-indent:-1.5em}
.note{margin:.6em 0 0;padding:7px 10px;background:#FBF6EA;border-left:3px solid #B8912E;
      font-family:'Noto Sans KR',sans-serif;font-size:13.5px;color:#6b5a24;
      word-break:keep-all}
figure{margin:.5em 0}
figure img{max-width:100%;height:auto;display:block}
@media print{.q{page-break-inside:avoid}}
"""

SHOT_JS = """
const {chromium} = require('%s');
const fs = require('fs'), path = require('path');
(async () => {
  const [htmlPath, outDir, pdfPath] = process.argv.slice(2);
  const b = await chromium.launch({args:['--no-sandbox']});
  const pg = await b.newPage({viewport:{width:1100,height:1400}, deviceScaleFactor:2});
  await pg.goto('file://' + path.resolve(htmlPath), {waitUntil:'load'});
  await pg.evaluate(() => document.fonts.ready);
  await pg.evaluate(() => Promise.all([...document.images]
    .filter(i => !i.complete).map(i => new Promise(r => { i.onload = i.onerror = r; }))));
  if (outDir && outDir !== '-') {
    fs.mkdirSync(outDir, {recursive: true});
    const ns = await pg.$$eval('.q', els => els.map(e => e.dataset.n));
    for (const n of ns) {
      const el = await pg.$(`.q[data-n="${n}"]`);
      await el.screenshot({path: path.join(outDir, n + '.png')});
    }
  }
  if (pdfPath) await pg.pdf({path: pdfPath, format: 'A4', printBackground: true,
      margin: {top: '12mm', bottom: '12mm', left: '10mm', right: '10mm'}});
  await b.close();
})();
""" % PW

CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩'


def _esc(s):
    import html as H
    return H.escape(s or '', quote=False)


def page_html(d, need, borrowed_as_img=False):
    body = []
    for q in d['q']:
        if q['n'] not in need:
            continue
        if borrowed_as_img and q['borrow']:
            # 빌려 온 문항은 원본 크롭 그림이 곧 문제다 — 글로 다시 그리지 않는다.
            b = q['borrow']
            src = (ROOT / 'crops' / b['e'] / ('%d.png' % b['q'])).as_uri()
            body.append(
                '<section class="q" data-n="%d">'
                '<div class="qh"><span class="qn">문제 %02d</span>'
                '<span class="qa">%s</span></div>'
                '<figure><img src="%s" alt=""></figure></section>'
                % (q['n'], q['n'], _esc(q['area']), src))
            continue
        ch = ''
        if q['choices']:
            items = []
            for i, c in enumerate(q['choices']):
                c = str(c).strip()
                mark = '' if c[:1] in CIRCLED else (CIRCLED[i] + ' ' if i < 10 else '')
                items.append('<li>%s%s</li>' % (mark, _esc(c)))
            ch = '<ul class="ch">%s</ul>' % ''.join(items)
        note = ''
        if q['fig']:
            note = ('<div class="note">이 문항은 원문에 그림·표가 있습니다. '
                    '문제지에서 %d번을 함께 보세요.</div>' % q['n'])
        body.append(
            '<section class="q" data-n="%d">'
            '<div class="qh"><span class="qn">문제 %02d</span>'
            '<span class="qa">%s</span>%s</div>'
            '<p>%s</p>%s%s</section>'
            % (q['n'], q['n'], _esc(q['area']),
               ('<span class="ql">%s</span>' % _esc(q['src'])) if q['src'] else '',
               _esc(q['stem']) or '(본문이 문제지에 있습니다)', ch, note))
    return ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<title>%s</title><style>%s</style></head><body>%s</body></html>'
            % (_esc(d['meta']['title']), CSS, ''.join(body)))


def render(d):
    """빌리지 못한 문항의 크롭을 그리고, 예순 문항을 담은 문제지 PDF 를 뽑는다.

    PDF 에는 **빌린 문항도 넣는다** — 빌린 자리는 원본 크롭 그림이 곧 문제다.
    학생이 「문제지 PDF ↓」 를 눌렀을 때 스무 문항만 든 종이가 나오면 안 된다.
    """
    from PIL import Image
    need = [q['n'] for q in d['q'] if not q['borrow']]
    cd = ROOT / 'crops' / d['id']
    cd.mkdir(parents=True, exist_ok=True)
    for old in cd.glob('*.png'):
        old.unlink()
    # 빌려 온 문항은 원본 크롭을 **제 폴더로 복사한다.**
    #
    # 처음에는 srcmap 으로 «가리키게» 했는데, 그러면 이 회차만 반쪽 지도를 갖게
    # 되어 크롭 주소를 만드는 자리마다(final·final-submit·weak60·검사) 빈 자리를
    # 따로 다뤄야 한다. 한 자리라도 빠뜨리면 시험지에 구멍이 난다.
    # 복사하면 «회차마다 제 크롭 예순 장» 이라는 규칙이 하나로 지켜진다.
    # 값은 그림 135장어치 디스크뿐이고, 얻는 것은 예외 없는 규칙이다.
    for q in d['q']:
        if q['borrow']:
            b = q['borrow']
            shutil.copyfile(ROOT / 'crops' / b['e'] / ('%d.png' % b['q']),
                            cd / ('%d.png' % q['n']))
    tmp = Path(tempfile.mkdtemp(prefix='legacy-'))
    try:
        shot = tmp / 'shot.js'
        shot.write_text(SHOT_JS, encoding='utf-8')
        # ① 크롭 — 빌리지 못한 문항만
        if need:
            page = tmp / 'crop.html'
            page.write_text(page_html(d, set(need)), encoding='utf-8')
            raw = tmp / 'raw'
            subprocess.run([NODE, str(shot), str(page), str(raw)],
                           check=True, capture_output=True)
            for n in need:
                im = Image.open(raw / ('%d.png' % n)).convert('RGB')
                im = im.resize((CROP_W, round(im.height * CROP_W / im.width)), Image.LANCZOS)
                im.save(cd / ('%d.png' % n), optimize=True)
        # ② 문제지 PDF — 예순 문항 전부
        page2 = tmp / 'paper.html'
        page2.write_text(page_html(d, {q['n'] for q in d['q']}, borrowed_as_img=True),
                         encoding='utf-8')
        subprocess.run([NODE, str(shot), str(page2), '-',
                        str(ROOT / ('%s-problem.pdf' % d['id']))],
                       check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return len(need)


# ── 또래 통계 ────────────────────────────────────────────────────────────
def put_baseline(ds):
    """응시 인원과 문항별 정답자 수만 적는다 — 석차 모집단은 아직 못 만든다.

    `cohort/baseline.json` 은 원래 성적표 엑셀에서 나온다. 담기는 것은 넷이다.

        n     응시 인원                     ← index.html 등기에 있다 (443명 …)
        qc    문항별 정답자 수               ← 정답률 × 인원으로 세울 수 있다
        hist  맞은 문항 수 → 사람 수          ← **엑셀이 있어야 한다**
        q     문항별 선택 분포               ← **엑셀이 있어야 한다**

    앞의 둘만으로도 **또래 정답률**은 제대로 선다(그 회차를 실제로 본 443명이
    모집단이 된다). 뒤의 둘이 없으면 석차·백분위는 예전처럼 «이 브라우저에서
    채점한 사람» 만 모집단으로 삼는다 — 그것은 엑셀을 받아야 고쳐진다.

    없는 것을 있는 척하지 않으려고 hist·q 는 **비워 두지 않고 아예 안 적는다.**
    성적표(final.html:2608)는 hist 가 없으면 석차 칸을 스스로 접는다.
    """
    p = ROOT / 'cohort' / 'baseline.json'
    doc = json.loads(p.read_text(encoding='utf-8'))
    ex = doc.setdefault('exams', {})
    for d in ds:
        n = d['meta']['N']
        qc = []
        for q in d['q']:
            r = q['rate']
            qc.append(round(n * r / 100) if isinstance(r, int) else 0)
        prev = ex.get(d['id']) or {}
        if prev.get('hist'):          # 엑셀에서 나온 진짜 기록이 있으면 안 건드린다
            continue
        # from:'rate' — 이 기록이 **어디서 왔는지**를 밝힌다. 엑셀에서 온 기록은
        # 넷을 다 갖는데 이것은 둘뿐이라, 밝히지 않으면 검사가 «가졌던 것을
        # 잃었다» 고 읽는다(tests/baseline-guard.js). 시트에서 온 기록이
        # from:'sheet' 로 제 사정을 밝히는 것과 같은 자리다.
        # ⚠ 한글을 한 글자도 적지 않는다. 이 파일은 **숫자만** 담기로 되어 있고
        # (tests/rank-baseline.js 가 exams 안의 한글을 0 으로 못 박는다), 그 규칙이
        # 곧 «학생 이름이 흘러들 자리가 없다» 는 보증이다. 설명은 이 도구의
        # 머리말에 적혀 있다 — 데이터에 적을 것이 아니다.
        ex[d['id']] = {'n': n, 'qc': qc, 'from': 'rate'}
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


# ── 심기 ─────────────────────────────────────────────────────────────────
def put_exam(entry):
    p = ROOT / 'exams.json'
    lst = json.loads(p.read_text(encoding='utf-8'))
    prev = next((e for e in lst if e['id'] == entry['id']), None)
    if prev is not None:
        entry['rev'] = int(prev.get('rev') or 1) + 1
        lst[lst.index(prev)] = entry
    else:
        lst.append(entry)
    p.write_text(json.dumps(lst, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def write_one(eid, var, body, group, do_crops=True):
    d = load(eid, var, body, group)
    put_exam(entry_of(d))
    ap = ROOT / 'answers' / ('%s.json' % eid)
    doc = answers_of(d)
    # ⚠ 덮어쓰지 않고 **합친다.** 답지에는 우리가 만드는 것(정답·영역·해설 글)
    # 말고도 **다른 자가 심어 둔 것**이 있다 — tools/gen_expl_html.py 가 짓는
    # explanationHtml 이 그것이다. 통째로 덮으면 그것이 소리 없이 사라지고,
    # 해설지가 «문항 블록이 하나도 없는» 껍데기가 된다(실제로 그랬다).
    # 우리가 쓰는 열쇠만 갈아 끼우고 나머지는 그대로 둔다.
    if ap.exists():
        try:
            prev = json.loads(ap.read_text(encoding='utf-8')).get('questions') or {}
        except Exception:
            prev = {}
        for k, rec in doc['questions'].items():
            old_rec = prev.get(k)
            if isinstance(old_rec, dict):
                merged = dict(old_rec)
                merged.update(rec)
                doc['questions'][k] = merged
    ap.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n',
                  encoding='utf-8')
    made = render(d) if do_crops else 0
    borrowed = sum(1 for q in d['q'] if q['borrow'])
    figless = sum(1 for q in d['q'] if q['fig'] and not q['borrow'])
    print('  %-11s 빌림 %2d · 그림 %2d장 그림   그림이 빠진 문항 %d' %
          (eid, borrowed, made, figless))
    return d


# ── 검사 ─────────────────────────────────────────────────────────────────
def check():
    bad, warn = [], []
    exams = {e['id']: e for e in
             json.loads((ROOT / 'exams.json').read_text(encoding='utf-8'))}
    figless = 0
    for eid, var, body, group in EXAMS:
        d = load(eid, var, body, group)          # 정답 대조는 여기서 터진다
        want = entry_of(d)
        got = exams.get(eid)
        if not got:
            bad.append('%s: exams.json 에 없다 — --write 로 심어라' % eid)
            continue
        for k in ('key', 'area', 'type', 'rate', 'nQ', 'title', 'multi'):
            if want.get(k) != got.get(k):
                bad.append('%s: %s 가 index.html·본문과 어긋난다' % (eid, k))
        ap = ROOT / 'answers' / ('%s.json' % eid)
        if not ap.exists():
            bad.append('%s: 답지가 없다' % eid)
        else:
            a = json.loads(ap.read_text(encoding='utf-8')).get('questions', {})
            keys = [a.get(str(i), {}).get('answer') for i in range(1, 61)]
            if keys != want['key']:
                bad.append('%s: 답지와 회차 정답이 어긋난다' % eid)
        for q in d['q']:
            if not (ROOT / 'crops' / eid / ('%d.png' % q['n'])).exists():
                bad.append('%s %d번: 크롭이 없다' % (eid, q['n']))
            if q['fig'] and not q['borrow']:
                figless += 1
    if _UNKNOWN:
        warn.append('영역 이름을 못 옮긴 것 %d가지: %s'
                    % (len(_UNKNOWN), ' · '.join(sorted(_UNKNOWN))))
    if bad:
        print('FAIL 단원별 회차가 짝이 안 맞는다:')
        for b in bad:
            print('  ' + b)
        return 1
    print('PASS 단원별 %d회차 · 480문항 — 정답이 두 곳에서 같고, 크롭이 다 있다' % len(EXAMS))
    if figless:
        print('  ⓘ 원문에 그림·표가 있었는데 글로만 그린 문항 %d개 — 크롭에 그렇다고 적어 두었다'
              % figless)
    for w in warn:
        print('  ⚠ ' + w)
    return 0


def main():
    argv = sys.argv[1:]
    if '--check' in argv:
        return check()
    if '--write' not in argv:
        print(__doc__)
        return 0
    only = [a for a in argv if not a.startswith('--')]
    nocrop = '--no-crops' in argv
    print('단원별 회차를 심는다%s' % (' (크롭은 건너뛴다)' if nocrop else ''))
    done = []
    for eid, var, body, group in EXAMS:
        if only and eid not in only:
            continue
        done.append(write_one(eid, var, body, group, do_crops=not nocrop))
    if done:
        put_baseline(done)
        print('또래 정답률 %d회차 (응시 %d명) — 석차 모집단은 엑셀을 받아야 선다'
              % (len(done), sum(d['meta']['N'] for d in done)))
    if _UNKNOWN:
        print('\n⚠ 영역 이름을 못 옮긴 것 %d가지 — ALIAS 에 넣어라:' % len(_UNKNOWN))
        print('   ' + ' · '.join(sorted(_UNKNOWN)))
    return 0


if __name__ == '__main__':
    sys.exit(main())

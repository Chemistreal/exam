#!/usr/bin/env python3
"""선생님이 한글(HWPX)로 만든 시험지를 회차로 들인다.

무엇을 만드는가
---------------
  crops/<시험ID>/<번호>.png   문항 크롭 (955px · 오답노트와 성적표가 쓴다)
  <시험ID>-problem.pdf        문제지
  answers/<시험ID>.json       정답·해설
  student-finals.json         회차 항목 (hidden · 곧바른 링크로만 연다)
  sol-final-<시험ID>.html     해설지 (tools/gen_sol_page.py 가 뒤이어 만든다)

왜 크롭을 다시 그리는가
-----------------------
HWPX 안의 문제는 **글자**다. 그림은 몇 자리뿐이고 나머지는 표와 문단이다.
그래서 한글이나 PDF 변환기 없이 읽어서, 화면과 같은 글꼴로 다시 조판해
크롭을 뽑는다 — 원본을 사진 찍는 것보다 또렷하고, 폭도 955px 로 딱 맞는다.

쓰기:
    python3 tools/ingest_hwpx_exam.py <파일.hwpx> [--code CODE] [--write]
    python3 tools/ingest_hwpx_exam.py --check       # 들인 회차가 짝이 맞는지
"""
from __future__ import annotations

import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from hwpx_exam import parse, bindata, flat_text, check as qcheck   # noqa: E402
from hwpx_render import exam_html                                  # noqa: E402

CROP_W = 955
NODE = '/opt/node22/bin/node'
PW = '/opt/node22/lib/node_modules/playwright'
# 해설 안에서 「원본과 달라진 점」 뒤는 오개념 자리로 옮긴다
# 해설 안에서 이 말 뒤는 「짚어둘 점」 자리로 옮긴다
MIS_SPLIT = re.compile(r'(?:■\s*)?(?:원본과 달라진 [곳점]|원문제에서 바뀐 [곳점]|'
                       r'이것만은 기억하자|자주 하는 실수)\s*[―\-·:]?\s*')
# 해설 껍데기 — 정답 칸·번호 칸·「영역 · 난이도 변형」 꼬리표
SHELL = re.compile(r'^(?:■\s*)?(?:정\s*답|풀이|선지\s*분석|알고 가야 할 개념)\s*$')
TAILER = re.compile(r'·\s*난이도\s*(?:변형|[상중하])\s*$')
LEAD = re.compile(r'^(?:■\s*)?(?:풀이|해설)\s*[:：]?\s*')


def tidy(s):
    """저장소가 정한 표기로 모은다.

    한글 원본은 온도를 ℃(U+2103) 한 글자로 쓴다. 그 글자는 CJK 호환용이라
    유니코드가 쓰지 말라 권하고, 「°C」 로 찾으면 안 걸린다 — 저장소는
    °C 로 모아 두었고 tools/dh_lint.py 가 그것을 지킨다.
    """
    return s.replace('\u2103', '°C')


# ── 영역 이름 ────────────────────────────────────────────────────────────
# 성적표는 문항의 `area` 로 영역별 진단과 처방을 만든다. 아는 이름이 아니면
# 그 문항은 **처방 없이 흘러간다** — 화면은 멀쩡하고 점수도 맞아서 아무도
# 모른다(tools/area_tag.py 가 그것을 잰다).
#
# 선생님 시험지는 영역을 두 꼴로 적는다.
#     변형본     「원자모형」            — 이미 아는 이름이다
#     실전세트   「원자와 주기성 · 방사성 붕괴」  — 대단원 · 소단원
# 뒤엣것을 아는 이름으로 옮긴다. 소단원 → 대단원 → 부분일치 차례로 본다.
_UNIT = {'원자와 주기성': '원자의구조', '화학 결합과 분자 구조': '화학결합',
         '기체와 상평형': '기체', '용액과 총괄성': '용액의총괄성',
         '용액과 농도': '용액의농도', '화학 평형과 산·염기': '화학평형',
         '열역학과 전기화학': '열역학', '화학 반응 속도': '반응속도',
         '반응 속도와 메커니즘': '반응속도', '화학량론': '양적관계',
         '유기와 생화학': '탄소화합물'}
# 같은 것을 두 가지로 적지 않는다(tools/type_norm.py). 저장소가 이미 쓰던 꼴로 모은다.
_SPELL = {'헨더슨하셀바흐식': '헨더슨-하셀바흐식', '고체의밀도': '고체의 밀도'}
_KNOWN = None


def _known():
    global _KNOWN
    if _KNOWN is None:
        sys.path.insert(0, str(ROOT / 'tools'))
        import area_tag
        _KNOWN = area_tag.known()[0]
    return _KNOWN


def _squash(s):
    return re.sub(r'[\s·\-,()]', '', s)


def map_area(t):
    """선생님이 적은 영역 이름을 성적표가 아는 이름으로."""
    known = _known()
    if t in known:
        return t
    sq = {_squash(k): k for k in known}
    unit, _, con = t.partition(' · ')
    for c in (con, unit, t):
        if _squash(c) in sq:
            return sq[_squash(c)]
    long_first = sorted(known, key=len, reverse=True)
    for part in (con, unit):
        s = _squash(part)
        for k in long_first:
            if len(k) >= 3 and _squash(k) in s:
                return k
    return _UNIT.get(unit.strip(), '기타')


def type_of(area):
    """유형 이름 — 영역과 같되, 저장소가 쓰던 철자로 모은다."""
    return _SPELL.get(area, area)


def title_of(d):
    return (('파이널 변형본 %d제 · %%s' % d['nQ']) if d['kind'] == '변형본'
            else ('실전 %d제 · %%s' % d['nQ'])) % d['code']


def cut_of(n):
    """수상 판정 칸 — 60제 기준 [0,5,9,14,18] 을 문항 수에 맞춰 줄인다."""
    base = [0, 5, 9, 14, 18]
    return [0] + [max(i, round(v * n / 60)) for i, v in enumerate(base[1:], 1)]


def sol_text(blocks, area=''):
    """해설 덩이를 두 갈래로 나눈다 — 풀이 본문과 짚어둘 점.

    앞에는 정답 칸이 껍데기로 붙어 온다(「정  답」·「①」·「영역 · 난이도 변형」).
    그것을 벗기지 않으면 해설 첫 줄이 정답 번호로 시작한다.
    """
    keep = []
    for k, t in flat_text(blocks):
        if k == 'img' or not t:
            continue
        if SHELL.match(t) or TAILER.search(t) or t == area:
            continue
        if len(t) <= 2 and t[0] in '①②③④⑤':
            continue
        keep.append(LEAD.sub('', t))
    whole = ' '.join(keep).strip()
    m = MIS_SPLIT.search(whole)
    if m:
        return whole[:m.start()].strip(), whole[m.end():].strip()
    return whole, ''


def answers_json(d):
    qs = {}
    for q in d['q']:
        body, tip = sol_text(q['sol'], q['area'])
        area = map_area(tidy(q['area']))
        qs[str(q['n'])] = {
            'answer': q['answer'],
            'acceptableAnswers': [q['answer']],
            'excluded': False,
            'concept': type_of(area),
            'area': area,
            'learningPoint': type_of(area),
            'explanation': tidy(body),
            'explanationHtml': '',
            'misconception': tidy(tip),
            'sourceSolution': '선생님 원본 해설 (%s)' % d['kind'],
            'verificationStatus': 'verified_against_supplied_solution_book',
        }
    return {
        'schemaVersion': 1,
        'examId': d['examId'],
        'examTitle': d['title'],
        'note': 'tools/ingest_hwpx_exam.py 가 선생님 한글 원본에서 옮겼다. '
                '손으로 고치면 --check 가 어긋난다.',
        'questions': qs,
    }


def entry_of(d):
    return {
        'id': d['examId'],
        'title': d['title'],
        'group': '파이널',
        'hidden': True,
        'nQ': d['nQ'],
        'mode': 'auto',
        'cut': cut_of(d['nQ']),
        'key': [q['answer'] for q in d['q']],
        'miss': [],
        'area': [map_area(tidy(q['area'])) for q in d['q']],
        'type': [type_of(map_area(tidy(q['area']))) for q in d['q']],
        'pdf': '%s-problem.pdf' % d['examId'],
        'crops': True,
        'source': {'tool': 'tools/ingest_hwpx_exam.py',
                   'kind': d['kind']},
    }


def render(d, bins, crops_dir, pdf_path):
    """HTML 한 장을 그려 문항 크롭과 문제지 PDF 를 함께 뽑는다."""
    from PIL import Image
    tmp = Path(tempfile.mkdtemp(prefix='hwpx-'))
    try:
        page = tmp / 'exam.html'
        page.write_text(exam_html(d, d['title'], bins), encoding='utf-8')
        shot = tmp / 'shot.js'
        shot.write_text(SHOT_JS, encoding='utf-8')
        raw = tmp / 'raw'
        subprocess.run([NODE, str(shot), str(page), str(raw), str(pdf_path)],
                       check=True, capture_output=True)
        crops_dir.mkdir(parents=True, exist_ok=True)
        for old in crops_dir.glob('*.png'):
            old.unlink()
        for q in d['q']:
            src = raw / ('%d.png' % q['n'])
            im = Image.open(src).convert('RGB')
            im = im.resize((CROP_W, round(im.height * CROP_W / im.width)),
                           Image.LANCZOS)
            im.save(crops_dir / ('%d.png' % q['n']), optimize=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


SHOT_JS = """
const {chromium} = require('%s');
const fs = require('fs'), path = require('path');
(async () => {
  const [htmlPath, outDir, pdfPath] = process.argv.slice(2);
  fs.mkdirSync(outDir, {recursive: true});
  const b = await chromium.launch();
  const pg = await b.newPage({viewport: {width: 1100, height: 1400},
                              deviceScaleFactor: 2});
  await pg.goto('file://' + path.resolve(htmlPath), {waitUntil: 'load'});
  await pg.evaluate(() => document.fonts.ready);
  const ns = await pg.$$eval('.q', els => els.map(e => e.dataset.n));
  for (const n of ns) {
    const el = await pg.$(`.q[data-n="${n}"]`);
    await el.screenshot({path: path.join(outDir, n + '.png')});
  }
  if (pdfPath) await pg.pdf({path: pdfPath, format: 'A4', printBackground: true,
      margin: {top: '12mm', bottom: '12mm', left: '10mm', right: '10mm'}});
  await b.close();
})();
""" % PW


def load_finals():
    p = ROOT / 'student-finals.json'
    return json.loads(p.read_text(encoding='utf-8')), p


def ingest(path, code=None, write=False):
    d = parse(path)
    bad = qcheck(d)
    if bad:
        raise SystemExit('%s: 흠 %s' % (Path(path).name, ' '.join(bad)))
    d['code'] = code or d['code']
    if not d['code']:
        raise SystemExit('%s: 학생 코드를 못 찾았다 — --code 로 준다' % path)
    # 한 학생이 시험지를 둘 받는다 — 변형본 60제(-2) 와 실전세트(-3).
    d['examId'] = d['code'] + ('-2' if d['kind'] == '변형본' else '-3')
    d['title'] = title_of(d)

    ans = answers_json(d)
    ent = entry_of(d)
    if not write:
        print('%s → %s · %d문항 · 정답 %s…'
              % (Path(path).name, d['examId'], d['nQ'],
                 ''.join(str(k) for k in ent['key'][:10])))
        return d

    render(d, bindata(path), ROOT / 'crops' / d['examId'],
           ROOT / ('%s-problem.pdf' % d['examId']))
    (ROOT / 'answers' / ('%s.json' % d['examId'])).write_text(
        json.dumps(ans, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    doc, p = load_finals()
    # 같은 id 를 다시 들이면 판(rev)을 올린다 — 문항 크롭은 서비스워커가
    # 배포를 넘어 cache-first 로 들고 있어서, 주소가 같으면 **옛 그림에
    # 새 정답표**가 붙는다. rev 는 크롭 주소의 ?v= 로 실려 캐시를 깬다.
    prev = next((e for e in doc['exams'] if e['id'] == d['examId']), None)
    if prev is not None:
        ent['rev'] = int(prev.get('rev') or 1) + 1
    doc['exams'] = [e for e in doc['exams'] if e['id'] != d['examId']] + [ent]
    doc['exams'].sort(key=lambda e: e['id'])
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n',
                 encoding='utf-8')
    print('%s 들였다 — 크롭 %d · PDF · 답지 · 회차'
          % (d['examId'], d['nQ']))
    return d


MINE = ('ingest_hwpx_exam.py', 'ingest_pdf_exam.py')


def _mine(e):
    return (e.get('source') or {}).get('tool', '').rsplit('/', 1)[-1] in MINE


def check():
    """선생님이 낸 시험지가 넷 다 같은 것을 가리키는지 — 한글 길·PDF 길 모두."""
    doc, _ = load_finals()
    bad = []
    for e in doc['exams']:
        # 출처에 파일 이름을 적으면 안 된다 — 선생님이 주는 파일 이름에는
        # 학생 실명이 들어 있고, 이 JSON 은 공개 사이트가 서빙한다. 코드 옆에
        # 실명이 서면 가명화가 통째로 풀린다 (2026-08-21 에 실제로 그랬다).
        if 'file' in (e.get('source') or {}):
            bad.append('%s: source.file 이 있다 — 실명이 들어 있을 수 있는 자리다. 지워라' % e['id'])
        if not _mine(e):
            continue
        eid = e['id']
        ap = ROOT / 'answers' / ('%s.json' % eid)
        if not ap.exists():
            bad.append('%s: 답지 없음' % eid)
            continue
        a = json.loads(ap.read_text(encoding='utf-8'))
        keys = [a['questions'][str(i)]['answer'] for i in range(1, e['nQ'] + 1)]
        if keys != e['key']:
            bad.append('%s: 답지와 회차 정답이 어긋난다' % eid)
        cd = ROOT / 'crops' / eid
        got = len(list(cd.glob('*.png'))) if cd.exists() else 0
        if got != e['nQ']:
            bad.append('%s: 크롭 %d/%d' % (eid, got, e['nQ']))
        # PDF 로 들인 회차는 문제지를 안 싣는다 — 원본 PDF 에 해설이 함께
        # 들어 있어서, 그대로 올리면 문제지가 곧 답지가 된다.
        if e.get('pdf') and not (ROOT / e['pdf']).exists():
            bad.append('%s: 문제지 PDF 없음' % eid)
        if not e.get('pdf') and not e.get('crops'):
            bad.append('%s: 문제를 보여 줄 것이 없다 (PDF 도 크롭도 없다)' % eid)
        leak = [i for i in range(1, e['nQ'] + 1)
                if not a['questions'][str(i)]['explanation']]
        if leak:
            bad.append('%s: 해설 빈 문항 %s' % (eid, leak[:5]))
    if bad:
        print('FAIL 선생님 시험지가 짝이 안 맞는다:')
        for b in bad:
            print('  ' + b)
        return 1
    n = sum(1 for e in doc['exams'] if _mine(e))
    print('PASS 선생님 시험지 %d회차 · 크롭·문제지·답지가 모두 짝이 맞는다' % n)
    return 0


def publish():
    """들인 뒤에 따라와야 하는 것들을 한 번에 돌린다.

    답지만 심어 놓고 해설지 꼴(explanationHtml)과 해설지 화면을 안 만들면,
    성적표는 새 글을 보여 주는데 해설지는 텅 비어 나온다 — 파일은 만들어지고
    검사도 지나가므로 아무도 모른다.
    """
    import subprocess
    doc, _ = load_finals()
    ids = [e['id'] for e in doc['exams'] if _mine(e)]
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'gen_expl_html.py'), '--write'],
                   check=True)
    for i in ids:
        subprocess.run([sys.executable, str(ROOT / 'tools' / 'gen_sol_page.py'), i, '--write'],
                       check=True, capture_output=True)
    for t in ('gen_retry_pool.py', 'gen_sw_version.py'):
        subprocess.run([sys.executable, str(ROOT / 'tools' / t), '--write'], check=True)
    print('뒤따르는 것까지 마쳤다 — 해설지 %d장 · 재도전 풀 · 서비스워커' % len(ids))


def main():
    argv = sys.argv[1:]
    if '--check' in argv:
        return check()
    args = [a for a in argv if not a.startswith('--')]
    if not args:
        print(__doc__)
        return 2
    code = None
    if '--code' in argv:
        code = argv[argv.index('--code') + 1]
        args = [a for a in args if a != code]
    for f in args:
        ingest(f, code=code, write='--write' in argv)
    return 0


if __name__ == '__main__':
    sys.exit(main())

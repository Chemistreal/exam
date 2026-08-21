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
        qs[str(q['n'])] = {
            'answer': q['answer'],
            'acceptableAnswers': [q['answer']],
            'excluded': False,
            'concept': q['area'],
            'area': q['area'],
            'learningPoint': q['area'],
            'explanation': body,
            'explanationHtml': '',
            'misconception': tip,
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
        'area': [q['area'] for q in d['q']],
        'type': [q['area'] for q in d['q']],
        'pdf': '%s-problem.pdf' % d['examId'],
        'crops': True,
        'source': {'tool': 'tools/ingest_hwpx_exam.py',
                   'kind': d['kind'], 'file': d['source']},
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

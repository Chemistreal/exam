#!/usr/bin/env python3
"""선생님이 만든 시험지(Word·PDF)를 받아들인다 — 크롭·정답·회차 항목까지.

쓰는 법과 Word 규격은 `docs/선생님-시험지-올리는-법.md` 에 있다. 여기서는
**무엇을 하는 자인지**만 적는다.

    Word ──(LibreOffice)──▶ PDF ──(문항 번호 줄을 찾아)──▶ 크롭 60장
                                                          ├▶ teacher-exams.json
                                                          └▶ answers/<id>.json

■ 왜 그림으로 자르는가

학생이 시험을 보는 화면(final-submit.html)은 문항을 **그림으로** 편다. 기존
회차 마흔넷이 다 그 꼴이고(crops/<회차>/<번호>.png · 가로 955px), 성적표의
오답노트·인쇄물·Word 시험지가 모두 그 그림을 가져다 쓴다. 선생님 Word 를
글로 뜯으면 표·그림·화살표가 다 부서진다 — 보이는 그대로 자르는 것이 맞다.

■ 문항을 어디서 자르는가

문단 **맨 앞**의 번호(`1.` `1)` `[1]` `문제 1` `Q1` `1번`)를 찾는다. 공식
기출은 회색 딱지를 찾지만(build_wrongbook_assets.py) 선생님 Word 에는 그런
것이 없다. 번호가 1부터 빠짐없이 이어지는지 세고, 빠지면 **그 자리에서 멈춘다** —
한 칸 밀린 채로 예순 장을 만들면 오답노트가 통째로 어긋난다.

■ exams.json 에 안 넣는 까닭

이 저장소의 검사들은 「exams.json 의 모든 회차는 문제지 PDF·공식 해설지·기준
기록을 다 갖춘 공개 회차」라는 계약을 강제한다. 선생님이 만든 시험지는 그 밖이라
teacher-exams.json 에 따로 둔다(학생별 파이널과 같은 자리).

    python3 tools/ingest_teacher_exam.py <파일> --exam <id> --for <코드> [--title ...]
    python3 tools/ingest_teacher_exam.py ... --key 3142... --write
    python3 tools/ingest_teacher_exam.py --check          # 심은 것이 온전한가 (CI)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTFILE = os.path.join(ROOT, 'teacher-exams.json')
GROUP = '선생님'
IMG_W = 955                 # 기존 크롭과 같은 가로 폭
RENDER_SCALE = 4            # build_wrongbook_assets.py 와 같은 배율
CIRC = {'①': 1, '②': 2, '③': 3, '④': 4, '⑤': 5}

# 문단 맨 앞의 문항 번호. 「12.5 g」 같은 것을 문항으로 세지 않도록
# 번호 뒤에 반드시 구분자가 오게 한다.
MARKER = re.compile(r'^\s{0,4}(?:문제\s*|Q\s*|\[)?(\d{1,3})\s*(?:[.)\]]|번)\s+')


# ── Word → PDF ────────────────────────────────────────────────────────────
def to_pdf(src, workdir):
    if src.lower().endswith('.pdf'):
        return src
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    if not soffice:
        sys.exit('LibreOffice 가 없다 — Word 를 PDF 로 못 바꾼다. PDF 로 주면 그대로 쓴다.')
    subprocess.run([soffice, '--headless', '--convert-to', 'pdf',
                    '--outdir', workdir, src],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = os.path.join(workdir, os.path.splitext(os.path.basename(src))[0] + '.pdf')
    if not os.path.exists(out):
        sys.exit('PDF 로 바꾸지 못했다: ' + src)
    return out


# ── 문항 자리 찾기 ────────────────────────────────────────────────────────
def find_marks(doc, marker=MARKER):
    """(문항번호, 쪽, y) 목록. 문단 맨 앞 번호만 센다."""
    marks = []
    for pi, page in enumerate(doc):
        d = page.get_text('dict')
        for blk in d.get('blocks', []):
            for line in blk.get('lines', []):
                txt = ''.join(s.get('text', '') for s in line.get('spans', []))
                m = marker.match(txt)
                if not m:
                    continue
                x0 = line['bbox'][0]
                # 왼쪽 여백 가까이에서 시작하는 줄만 — 표 안쪽 숫자를 거른다
                if x0 > page.rect.width * 0.35:
                    continue
                marks.append({'n': int(m.group(1)), 'page': pi,
                              'y': line['bbox'][1], 'x': x0, 'text': txt.strip()[:60]})
    marks.sort(key=lambda m: (m['page'], m['y']))
    return marks


def sequential(marks):
    """1,2,3… 으로 이어지는 것만 남긴다. 되돌아가거나 건너뛰면 거기서 끊는다."""
    out, want = [], 1
    for m in marks:
        if m['n'] == want:
            out.append(m)
            want += 1
    return out


# ── 크롭 ──────────────────────────────────────────────────────────────────
def crop_one(doc, start, end, out_path, fitz):
    """한 문항을 그림으로. 쪽을 넘어가면 이어 붙인다."""
    from PIL import Image
    mat = fitz.Matrix(RENDER_SCALE, RENDER_SCALE)
    pieces = []
    p0, y0 = start['page'], start['y']
    p1, y1 = (end['page'], end['y']) if end else (doc.page_count - 1, None)
    for pi in range(p0, p1 + 1):
        page = doc[pi]
        top = y0 - 4 if pi == p0 else page.rect.y0
        bot = (y1 - 2) if (end and pi == p1) else page.rect.y1
        if bot - top < 6:
            continue
        clip = fitz.Rect(page.rect.x0, top, page.rect.x1, bot)
        pm = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
        pieces.append(Image.frombytes('RGB', (pm.width, pm.height), pm.samples))
    if not pieces:
        return False
    if len(pieces) == 1:
        im = pieces[0]
    else:
        w = max(p.width for p in pieces)
        im = Image.new('RGB', (w, sum(p.height for p in pieces)), 'white')
        y = 0
        for p in pieces:
            im.paste(p, (0, y))
            y += p.height
    im = trim_white(im)
    if im.width != IMG_W:
        im = im.resize((IMG_W, max(1, round(im.height * IMG_W / im.width))), Image.LANCZOS)
    im.convert('P', palette=Image.ADAPTIVE, colors=256).save(
        out_path, 'PNG', optimize=True, compress_level=9)
    return True


def trim_white(im):
    """가장자리 흰 여백을 걷어낸다 — 쪽 여백이 그대로 실리면 그림이 작아 보인다."""
    from PIL import ImageChops, Image
    bg = Image.new('RGB', im.size, 'white')
    bbox = ImageChops.difference(im, bg).getbbox()
    if not bbox:
        return im
    pad = 8
    l, t, r, b = bbox
    return im.crop((max(0, l - pad), max(0, t - pad),
                    min(im.width, r + pad), min(im.height, b + pad)))


# ── 정답·영역 읽기 ────────────────────────────────────────────────────────
def parse_key(text, n):
    """숫자열이든 「1 ③  2 ①」 이든 ①②③④ 든 받아들인다."""
    if not text:
        return None
    t = ''.join(CIRC.get(c, c) and (str(CIRC[c]) if c in CIRC else c) for c in text)
    pairs = re.findall(r'(\d{1,3})\s*[.)]?\s*([1-5])(?![\d])', t)
    if len(pairs) >= n * 0.9:
        key = [0] * n
        for a, b in pairs:
            i = int(a)
            if 1 <= i <= n:
                key[i - 1] = int(b)
        if all(key):
            return key
    digits = re.sub(r'[^1-5]', '', t)
    if len(digits) == n:
        return [int(c) for c in digits]
    return None


def key_from_pdf(doc, n):
    tail = ''
    for pi in range(max(0, doc.page_count - 3), doc.page_count):
        tail += doc[pi].get_text()
    m = re.search(r'정\s*답', tail)
    return parse_key(tail[m.end():], n) if m else None


# 학생이 보는 종이에 정답이 실리면 안 된다. 마지막 문항 크롭은 그 아래를 다
# 끌고 오므로, 시험지 끝에 붙인 「정답」 구역이 그대로 딸려 들어간다 —
# 실제로 그랬다(60번 크롭에 예순 문항 정답표가 통째로 박혔다).
# 그래서 정답 구역이 **어디서 시작하는지** 찾아 거기서 끊는다.
ANSWER_HEAD = re.compile(r'^\s*(?:정\s*답|해\s*설|정답표|answer\s*key)\b', re.I)


def answer_zone(doc):
    """「정답」·「해설」이 시작하는 자리 (쪽, y). 없으면 None."""
    for pi in range(doc.page_count):
        d = doc[pi].get_text('dict')
        for blk in d.get('blocks', []):
            for line in blk.get('lines', []):
                txt = ''.join(s.get('text', '') for s in line.get('spans', []))
                if ANSWER_HEAD.match(txt):
                    return {'page': pi, 'y': line['bbox'][1]}
    return None


def areas_from_marks(marks):
    """번호 줄 끝의 [영역 / 유형] 을 읽는다."""
    area, typ = [], []
    for m in marks:
        g = re.search(r'\[([^\]/]+?)(?:\s*/\s*([^\]]+?))?\]\s*$', m['text'])
        area.append(g.group(1).strip() if g else '')
        typ.append((g.group(2) or g.group(1)).strip() if g else '')
    return area, typ


def load_teacher():
    if not os.path.exists(OUTFILE):
        return {'schemaVersion': 1,
                'note': ('tools/ingest_teacher_exam.py 가 선생님 Word 에서 받아들인 회차. '
                         'exams.json 과 따로 사는 까닭은 그 도구의 머리에 적혀 있다.'),
                'exams': []}
    return json.load(open(OUTFILE, encoding='utf-8'))


def save_teacher(data):
    with open(OUTFILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def scaled_cut(n):
    cut, prev = [0], 0
    for f in (0.07, 0.15, 0.22, 0.30):
        import math
        v = max(prev, math.ceil(n * f))
        cut.append(v)
        prev = v
    return cut


# ── 검사 ──────────────────────────────────────────────────────────────────
def check():
    data = load_teacher()
    exams = data.get('exams', [])
    if not exams:
        print('· teacher-exams.json 에 아직 아무것도 없다 — 잴 것이 없다')
        return 0
    bad = []
    for e in exams:
        eid = e['id']
        n = e['nQ']
        if len(e.get('key') or []) != n:
            bad.append('%s: 정답키가 %d개인데 nQ 는 %d' % (eid, len(e.get('key') or []), n))
        cut = e.get('cut') or []
        if not (len(cut) == 5 and cut[0] == 0 and all(a <= b for a, b in zip(cut, cut[1:]))):
            bad.append('%s: cut 이 다섯 칸 단조증가가 아니다 — 성적표가 죽는다' % eid)
        src = e.get('cropsFrom') or eid
        for q in range(1, n + 1):
            if not os.path.exists(os.path.join(ROOT, 'crops', src, '%d.png' % q)):
                bad.append('%s: 크롭이 없다 — crops/%s/%d.png' % (eid, src, q))
                break
        ap = os.path.join(ROOT, 'answers', eid + '.json')
        if not os.path.exists(ap):
            bad.append('%s: 답지가 없다 — answers/%s.json' % (eid, eid))
            continue
        qs = json.load(open(ap, encoding='utf-8')).get('questions', {})
        if len(qs) != n:
            bad.append('%s: 답지 문항이 %d개인데 nQ 는 %d' % (eid, len(qs), n))
        for q in range(1, n + 1):
            it = qs.get(str(q))
            if it and it.get('answer') and it['answer'] != e['key'][q - 1]:
                bad.append('%s %d번: 답지와 정답키가 다르다' % (eid, q))
                break
    if bad:
        print('✗ 선생님 시험지 %d벌 — 어긋난 곳 %d' % (len(exams), len(bad)))
        for b in bad[:30]:
            print('  ' + b)
        return 1
    print('✓ 선생님 시험지 %d벌 — 크롭·정답키·답지가 다 맞는다' % len(exams))
    return 0


# ── 본체 ──────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('src', nargs='?', help='선생님이 만든 시험지 (.docx 또는 .pdf)')
    ap.add_argument('--exam', help='시험 id (영문·숫자·붙임표). 크롭 폴더 이름이 된다')
    ap.add_argument('--for', dest='who', default='', help='학생 코드. 쉼표로 여럿')
    ap.add_argument('--title', default='', help='화면에 뜰 이름')
    ap.add_argument('--key', default='', help='정답 60자 또는 「1 ③ 2 ①」 꼴')
    ap.add_argument('--key-file', default='')
    ap.add_argument('--areas', default='', help='번호<탭>영역<탭>유형 파일')
    ap.add_argument('--multi', default='', help='복수 정답  예: "7=1,3 23=2,4"')
    ap.add_argument('--void', default='', help='전원정답 번호  예: 34,41')
    ap.add_argument('--marker', default='', help='문항 번호 정규식을 손수 줄 때')
    ap.add_argument('--nq', type=int, default=0, help='문항 수를 못 세면 손으로')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    if a.check:
        return check()
    if not a.src or not a.exam:
        ap.print_help()
        print('\n규격: docs/선생님-시험지-올리는-법.md')
        return 2
    if not os.path.exists(a.src):
        sys.exit('그런 파일이 없다: ' + a.src)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*', a.exam):
        sys.exit('시험 id 는 영문·숫자·붙임표만: ' + a.exam)

    import fitz
    work = tempfile.mkdtemp(prefix='ingest-')
    try:
        pdf = to_pdf(a.src, work)
        doc = fitz.open(pdf)
        marker = re.compile(a.marker) if a.marker else MARKER
        stop = answer_zone(doc)
        raw = find_marks(doc, marker)
        if stop:
            # 정답 구역 안의 「1 ③ 2 ①」 을 문항 번호로 세면 안 된다
            raw = [m for m in raw
                   if (m['page'], m['y']) < (stop['page'], stop['y'])]
        marks = sequential(raw)
        n = a.nq or len(marks)

        print('%s · %d쪽' % (os.path.basename(a.src), doc.page_count))
        print('  번호처럼 보이는 줄 %d개 · 1부터 이어지는 것 %d개' % (len(raw), len(marks)))
        if len(marks) < 5:
            print('\n✗ 문항을 거의 못 찾았다. 번호가 문단 맨 앞에 있는지 보아라.')
            print('  찾은 것 몇 개:')
            for m in raw[:8]:
                print('    %d쪽  %s' % (m['page'] + 1, m['text']))
            return 1
        if len(marks) != len(raw):
            missing = sorted({m['n'] for m in raw} - {m['n'] for m in marks})
            print('  ⚠ 이어지지 않아 뺀 번호: %s' % (missing[:12] or '없음'))

        key = parse_key(a.key, n)
        if not key and a.key_file:
            key = parse_key(open(a.key_file, encoding='utf-8').read(), n)
        if not key:
            key = key_from_pdf(doc, n)
        area, typ = areas_from_marks(marks)
        if a.areas:
            area, typ = [''] * n, [''] * n
            for line in open(a.areas, encoding='utf-8'):
                p = [x.strip() for x in re.split(r'\t|,', line) if x.strip()]
                if len(p) >= 2 and p[0].isdigit() and 1 <= int(p[0]) <= n:
                    area[int(p[0]) - 1] = p[1]
                    typ[int(p[0]) - 1] = p[2] if len(p) > 2 else p[1]

        multi = {}
        for tok in re.findall(r'(\d+)\s*=\s*([\d,]+)', a.multi or ''):
            multi[tok[0]] = [int(x) for x in tok[1].split(',') if x.strip()]
        void = [int(x) for x in re.findall(r'\d+', a.void or '')]

        print('  문항 %d개 · 정답키 %s · 영역 %d개 · 복수정답 %d · 전원정답 %d'
              % (n, ('있음' if key else '**없음**'),
                 sum(1 for x in area if x), len(multi), len(void)))
        if stop:
            print('  정답·해설 구역이 %d쪽에서 시작한다 — 마지막 문항 크롭을 그 앞에서 끊는다'
                  % (stop['page'] + 1))
        else:
            print('  ⚠ 「정답」 구역을 못 찾았다. 시험지 끝에 정답을 적었다면 마지막 문항 '
                  '크롭에 딸려 들어간다 — 정답은 --key 로 주고 시험지에서는 빼는 것이 안전하다.')
        if not key:
            print('    → --key 로 주거나 Word 끝에 「정답」 줄을 넣어라')
        for i, m in enumerate(marks[:3], 1):
            print('    %d번 ← %d쪽  %s' % (i, m['page'] + 1, m['text']))

        if not a.write:
            print('\n(미리 보기다. 심으려면 --write)')
            return 0
        if not key:
            sys.exit('정답 없이는 안 심는다 — 채점을 못 한다')

        cdir = os.path.join(ROOT, 'crops', a.exam)
        os.makedirs(cdir, exist_ok=True)
        made = 0
        for i in range(n):
            nxt = marks[i + 1] if i + 1 < len(marks) else stop
            if crop_one(doc, marks[i], nxt, os.path.join(cdir, '%d.png' % (i + 1)), fitz):
                made += 1
        print('  크롭 %d/%d 장' % (made, n))
        if made != n:
            sys.exit('크롭이 모자라다 — 심지 않는다')

        codes = [c.strip() for c in (a.who or '').split(',') if c.strip()]
        data = load_teacher()
        entries = [e for e in data['exams'] if e['id'] != a.exam
                   and not e['id'].startswith(a.exam + '-')]
        base = {'group': GROUP, 'hidden': True, 'nQ': n, 'mode': 'auto',
                'cut': scaled_cut(n), 'key': key, 'miss': [],
                'area': area, 'type': typ, 'authored': True}
        if multi:
            base['multi'] = multi
        if void:
            base['voided'] = void
        targets = codes or ['']
        for c in targets:
            eid = (a.exam + '-' + c) if c else a.exam
            e = dict(base)
            e['id'] = eid
            e['title'] = a.title or ('선생님 시험지 · ' + eid)
            if eid != a.exam:
                e['cropsFrom'] = a.exam      # 크롭은 한 벌만 둔다
                e['srcmap'] = [{'e': a.exam, 'q': q} for q in range(1, n + 1)]
            else:
                e['srcmap'] = [{'e': a.exam, 'q': q} for q in range(1, n + 1)]
            if c:
                e['forStudent'] = c
            entries.append(e)
        data['exams'] = entries
        save_teacher(data)

        for c in targets:
            eid = (a.exam + '-' + c) if c else a.exam
            qs = {}
            for q in range(1, n + 1):
                qs[str(q)] = {'answer': key[q - 1],
                              'acceptableAnswers': multi.get(str(q)) or [key[q - 1]],
                              'excluded': q in void,
                              'concept': typ[q - 1] or '', 'area': area[q - 1] or '',
                              'learningPoint': typ[q - 1] or '',
                              'explanation': '', 'misconception': '',
                              'sourceSolution': '선생님이 만든 시험지'}
            with open(os.path.join(ROOT, 'answers', eid + '.json'), 'w', encoding='utf-8') as f:
                json.dump({'schemaVersion': 1, 'examId': eid,
                           'examTitle': a.title or eid,
                           'note': 'tools/ingest_teacher_exam.py 가 받아들인 것. 해설은 뒤에 붙일 수 있다.',
                           'questions': qs}, f, ensure_ascii=False, indent=1)
                f.write('\n')

        print('\n심었다:')
        print('  crops/%s/1.png … %d.png' % (a.exam, n))
        for c in targets:
            eid = (a.exam + '-' + c) if c else a.exam
            print('  answers/%s.json' % eid)
            print('  → final-submit.html?exam=%s' % eid)
        print('  teacher-exams.json (회차 %d벌)' % len(entries))
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())

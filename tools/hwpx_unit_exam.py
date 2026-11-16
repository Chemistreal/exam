#!/usr/bin/env python3
"""선생님이 한글(HWPX)로 만든 **반 단위 시험지 + 해설지 한 파일**을 읽는다.

화학1 1-3단원 총괄평가(심화반, 2026-11) 꼴이다. ingest_hwpx_exam.py 가 읽는
학생별 파이널(「문제 NN」 머리표가 표 첫 칸)과 생김새가 달라서 따로 둔다.

한 파일에 세 덩이
  section0   표지 — 「화학 총괄평가 (몰과 양적관계 ~ 분자의 극성) …」
  section1   문제 — 「문제 N」 문단(번호 문단 꼴) 뒤로 지문 · 표 · 그림 · 수식 · 선지
  section2   해설 — 정답·영역·개념·난이도 표 60줄 + 문항마다 해설 표 하나
               (출제 의도 · 사고 과정 n단계 · 선지 분석 · 함정 · 원문항/변형)

정답은 세 곳이 말한다 — 정답표 · 해설 머리(「정답 ③」) · 선지 분석의 「정답.」 줄.
셋이 하나라도 어긋나면 멈춘다. 정답이 틀리면 성적표가 조용히 틀린다.

쓰기:
    python3 tools/hwpx_unit_exam.py <파일.hwpx>          # 재어 보고 흠을 말한다
    python3 tools/hwpx_unit_exam.py <파일.hwpx> --json   # 구조를 그대로 찍는다
"""
import json, re, sys, zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwpx_exam import _tbl, flat_text, CIRCLED   # noqa: E402  표 읽기는 같은 것을 쓴다

HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
HEAD = re.compile(r'^문제\s*(\d{1,3})\s*$')
SOL_HEAD = re.compile(r'^문제\s*(\d{1,3})\s+(\S+)\s+난이도\s*([상중하])\s*정답\s*([①-⑤])')
STEP = re.compile(r'^(\d+)단계\s*')


# ── 수식 ────────────────────────────────────────────────────────────────
# 한글 수식 스크립트는 일곱 개뿐이다(핵종 기호 여섯 · 발머 식 하나). 수식기를
# 두는 대신 **알아보는 꼴만** 옮기고, 모르는 꼴이 오면 멈춘다 — 조용히 글자로
# 흘리면 시험지에 «{}_{26}^{53} Fe» 가 그대로 찍힌다.
_SUP = str.maketrans('0123456789+-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻')
_SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def eq_html(script):
    s = re.sub(r'[`~]', ' ', script).strip()
    s = re.sub(r'\s+', ' ', s)
    # 핵종: {}_{Z}^{A} X ^{q}  ·  {} ^{A} X   ·  _{y}^{x} beta
    nuc = re.compile(r'(?:\{\}\s*)?(?:_\{\s*([^}]*)\}\s*)?\^\{\s*([^}]*)\}\s*(?:_\{\s*([^}]*)\}\s*)?'
                     r'([A-Za-z]+)(?:\s*\^\{\s*([^}]*)\})?')
    if s.startswith('lambda'):
        m = re.match(r'lambda\s*=\s*\{\s*hm\s*\^\{2\}\s*\}\s*over\s*\{\s*m\s*\^\{2\}\s*-\s*n\s*\^\{2\}\s*\}$', s)
        if not m:
            raise ValueError('모르는 수식: %r' % script)
        return ('<span class="eq">λ = <span class="frac"><span>hm<sup>2</sup></span>'
                '<span>m<sup>2</sup> − n<sup>2</sup></span></span></span>')
    parts, pos = [], 0
    for m in nuc.finditer(s):
        gap = s[pos:m.start()].strip()
        if gap:
            parts.append(gap.replace('->', '→').replace('+', ' + '))
        z = (m.group(1) or m.group(3) or '').strip()
        a = (m.group(2) or '').strip()
        sym = 'β' if m.group(4) == 'beta' else m.group(4)
        q = (m.group(5) or '').strip()
        if a and z:
            left = '<span class="nu"><span>%s</span><span>%s</span></span>' % (a, z)
        elif a:
            left = '<sup class="na">%s</sup>' % a
        else:
            left = '<sub class="nz">%s</sub>' % z
        parts.append('<span class="nuc">%s%s%s</span>' % (left, sym, ('<sup>%s</sup>' % q) if q else ''))
        pos = m.end()
    rest = s[pos:].strip()
    if rest:
        parts.append(rest)
    if not parts or '{' in ''.join(parts).replace('<', ''):
        raise ValueError('모르는 수식: %r' % script)
    return ' '.join(parts)


# ── 읽기 ────────────────────────────────────────────────────────────────
def _runs(p):
    """문단 하나 — 글 · 그림 · 수식 차례대로. 수식은 html 조각으로 싣는다."""
    out, buf = [], []

    def flush():
        if buf:
            out.append({'t': 'p', 'x': ''.join(buf)})
            buf.clear()

    def walk(node):
        for ch in node:
            if ch.tag == HP + 'tbl':
                continue
            if ch.tag == HP + 't':
                buf.append(''.join(ch.itertext()))
            elif ch.tag == HP + 'equation':
                sc = ch.find(HP + 'script')
                buf.append('\x00%s\x01' % eq_html(sc.text or ''))
            elif ch.tag == HP + 'pic':
                ref = next((im.get('binaryItemIDRef') for im in ch.iter()
                            if im.tag.endswith('}img') and im.get('binaryItemIDRef')), None)
                sz = ch.find(HP + 'sz')
                if ref:
                    flush()
                    out.append({'t': 'img', 'ref': ref,
                                'w': int(sz.get('width', 0)) if sz is not None else 0,
                                'h': int(sz.get('height', 0)) if sz is not None else 0})
            else:
                walk(ch)

    walk(p)
    flush()
    return out


def _para_blocks(p):
    out = list(_runs(p))
    for tbl in p.iter(HP + 'tbl'):
        out.append(_eqtbl(tbl))
    return out


def _eqtbl(tbl):
    """표 안 칸도 수식·그림을 살린다 — hwpx_exam._tbl 의 칸 읽기만 바꿔 끼운다."""
    t = _tbl(tbl)
    # _tbl 은 칸 안을 hwpx_exam._body 로 읽어 수식을 버린다. 칸을 다시 읽는다.
    cells = {}
    for tr in tbl.findall(HP + 'tr'):
        for tc in tr.findall(HP + 'tc'):
            ad = tc.find(HP + 'cellAddr')
            key = (int(ad.get('rowAddr')), int(ad.get('colAddr'))) if ad is not None else None
            body = []
            for sub in tc.findall(HP + 'subList'):
                for p in sub.findall(HP + 'p'):
                    body.extend(_para_blocks(p))
            cells[key] = body
    keys = sorted(k for k in cells if k is not None)
    i = 0
    for row in t['rows']:
        for c in row:
            if i < len(keys):
                c['b'] = cells[keys[i]]
            i += 1
    return t


def bins(path):
    """그림 — 머리(header.xml)의 binItem id 와 BinData 파일을 잇는다."""
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        m = re.match(r'BinData/([^/]+)\.(\w+)$', n)
        if m:
            out[m.group(1)] = (m.group(2).lower(), z.read(n))
    return out


def _ptext(p):
    return ''.join(''.join(t.itertext()) for t in p.iter(HP + 't')).strip()


def parse(path):
    z = zipfile.ZipFile(path)
    cover = ET.fromstring(z.read('Contents/section0.xml'))
    title_bits = [t for t in (_ptext(p) for p in cover.iter(HP + 'p')) if t]

    # ── 문제 ──
    sec1 = ET.fromstring(z.read('Contents/section1.xml'))
    qs, cur = [], None
    for p in [x for x in sec1 if x.tag == HP + 'p']:
        m = HEAD.match(_ptext(p))
        if m:
            cur = {'n': int(m.group(1)), 'body': []}
            qs.append(cur)
            continue
        if cur is not None:
            cur['body'].extend(_para_blocks(p))
    for i, q in enumerate(qs, 1):
        if q['n'] != i:
            raise ValueError('문제 번호가 %d 다음에 %d 이다' % (i - 1, q['n']))

    # ── 해설 ──
    sec2 = ET.fromstring(z.read('Contents/section2.xml'))
    tbls = list(sec2.iter(HP + 'tbl'))
    key_tbl, sol_tbls = tbls[0], tbls[1:]
    table = {}
    for tr in key_tbl.findall(HP + 'tr'):
        cells = [_ptext(tc) for tc in tr.findall(HP + 'tc')]
        if cells and cells[0].isdigit():
            n = int(cells[0])
            table[n] = {'answer': CIRCLED.index(cells[1]) + 1, 'area': cells[2],
                        'concept': cells[3], 'level': cells[4]}
    sols = {}
    for t in sol_tbls:
        paras = [_ptext(p) for p in t.iter(HP + 'p')]
        paras = [x for x in paras if x]
        m = SOL_HEAD.match(paras[0]) if paras else None
        if not m:
            continue
        n = int(m.group(1))
        s = {'concept': m.group(2), 'level': m.group(3), 'answer': CIRCLED.index(m.group(4)) + 1,
             'intent': '', 'steps': [], 'options': {}, 'trap': '', 'origin': '', 'variant': ''}
        mode = None
        for x in paras[1:]:
            if x.startswith('출제 의도'):
                s['intent'] = x[len('출제 의도'):].strip()
            elif x == '사고 과정':
                mode = 'steps'
            elif x == '선지 분석':
                mode = 'opts'
            elif x.startswith('함정'):
                s['trap'] = x[len('함정'):].strip()
                mode = None
            elif x.startswith('원문항'):
                body = x[len('원문항'):].strip()
                o, _, v = body.partition('변형')
                s['origin'], s['variant'] = o.strip(), v.strip()
            elif mode == 'steps':
                # 「N단계」 로 시작하는 줄이 단계, 아닌 줄은 앞 단계의 세부 줄이다(원본 그대로)
                m2 = STEP.match(x)
                s['steps'].append({'k': (m2.group(1) + '단계') if m2 else '',
                                   't': STEP.sub('', x).strip() if m2 else x.strip()})
            elif mode == 'opts' and x[:1] in CIRCLED:
                # 「①, ②, ③ …」 처럼 여럿을 한 줄로 묶은 것도 있다
                heads = re.match(r'^((?:[①-⑤]\s*,?\s*)+)', x)
                nums = [CIRCLED.index(c) + 1 for c in heads.group(1) if c in CIRCLED]
                txt = x[heads.end():].strip()
                for k in nums:
                    s['options'][k] = x if len(nums) > 1 else txt
            elif mode == 'opts' and s['options']:
                last = max(s['options'])
                s['options'][last] += ' ' + x
        sols[n] = s

    nq = len(qs)
    for q in qs:
        n = q['n']
        if n not in table or n not in sols:
            raise ValueError('%d번 해설·정답표가 없다' % n)
        a, b = table[n], sols[n]
        if a['answer'] != b['answer'] or a['concept'] != b['concept'] or a['level'] != b['level']:
            raise ValueError('%d번 정답표와 해설 머리가 다르다: %r vs %r' % (n, a, b))
        # 선지 분석이 정답을 말하는 꼴 — 「…: 정답.」 「… 정답.」 「정답은 ④이다」
        marked = set()
        for k, v in b['options'].items():
            if re.search(r'정답\.?\s*$', v) and not re.search(r'정답은', v):
                marked.add(k)
            for c in re.findall(r'정답은\s*([①-⑤])', v):
                marked.add(CIRCLED.index(c) + 1)
        marked = sorted(marked)
        if marked and marked != [a['answer']]:
            raise ValueError('%d번 선지 분석의 「정답」 이 %s 인데 정답표는 %d' % (n, marked, a['answer']))
        q.update(answer=a['answer'], area=a['area'], concept=a['concept'], level=a['level'],
                 sol=b, answerMarked=bool(marked))
        q['choices'] = _choices(q['body'])
    return {'title_bits': title_bits, 'nQ': nq, 'q': qs, 'table_n': len(table)}


def _choices(blocks):
    """선지 글 — 글 선지는 ①~④ 로 쪼개고, 그림·표 선지는 빈칸으로 둔다."""
    out = {}
    for k, t in flat_text(blocks):
        if k == 'img' or not t or t[0] not in CIRCLED:
            continue
        for x in re.split(r'(?=[①-⑤])', t):
            x = x.strip()
            if x and x[0] in CIRCLED:
                out.setdefault(CIRCLED.index(x[0]) + 1, plain(x[1:].strip()))
    return [out.get(i, '') for i in range(1, 5)]


def plain(s):
    """html 조각(수식)을 글로 — 답지의 stem·choices 는 글이어야 한다."""
    def one(m):
        h = m.group(1)
        # 핵종 — 숫자면 ²³⁸₉₂U 꼴, 글자(x·y·z)면 말로 푼다(글자 첨자는 유니코드에 다 있지 않다)
        def nu(k, a, z, x):
            if (a + z).isdigit() or (a.isdigit() and not z) or (z.isdigit() and not a):
                return a.translate(_SUP) + z.translate(_SUB) + x
            bits = []
            if a:
                bits.append('질량수 ' + a)
            if z:
                bits.append('원자 번호 ' + z)
            return '%s(%s)' % (x, ', '.join(bits))
        h = re.sub(r'<span class="nuc"><span class="nu"><span>([^<]*)</span><span>([^<]*)</span></span>([^<]*)',
                   lambda k: nu(k, k.group(1), k.group(2), k.group(3)), h)
        h = re.sub(r'<span class="nuc"><sup class="na">([^<]*)</sup>([^<]*)',
                   lambda k: nu(k, k.group(1), '', k.group(2)), h)
        h = re.sub(r'<span class="nuc"><sub class="nz">([^<]*)</sub>([^<]*)',
                   lambda k: nu(k, '', k.group(1), k.group(2)), h)
        h = re.sub(r'<sup>([^<]*)</sup>', lambda k: k.group(1).translate(_SUP), h)
        h = re.sub(r'<span class="frac"><span>(.*?)</span><span>(.*?)</span></span>', r'(\1)/(\2)', h)
        return re.sub(r'<[^>]+>', '', h)
    return re.sub(r' {2,}', ' ', re.sub('\x00(.*?)\x01', one, s))


def stem_text(blocks):
    out = []
    for k, t in flat_text(blocks):
        if k == 'img' or (t and t[0] in CIRCLED):
            continue
        out.append(plain(t))
    return ' '.join(out).strip()


def main():
    ap = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not ap:
        print(__doc__)
        return 2
    d = parse(ap[0])
    if '--json' in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0
    bad = []
    for q in d['q']:
        if sum(1 for c in q['choices'] if c) < 4 and not any(k == 'img' for k, _ in flat_text(q['body'])) \
                and not any(b['t'] == 'tbl' for b in q['body']):
            bad.append('%d(선지 %d)' % (q['n'], sum(1 for c in q['choices'] if c)))
        if not q['sol']['steps']:
            bad.append('%d(풀이 없음)' % q['n'])
    print('%d문항 · 정답표 %d줄 · 「정답」 표시로 다시 맞춘 문항 %d · 흠 %s'
          % (d['nQ'], d['table_n'], sum(q['answerMarked'] for q in d['q']), ' '.join(bad) or '없음'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())

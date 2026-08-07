#!/usr/bin/env python3
"""강의 125장을 전수로 훑는다 — **처음 보는 학생이 알아들을 수 있는가.**

강의는 순서대로 읽히지 않는다. 학생은 자기 오답이 가리키는 **한 강만** 열어
본다. 그런데 강의를 쓸 때는 앞뒤를 다 아는 사람이 쓰므로, "앞에서 배운
Ka·Kb(087)" 같은 문장이 자연스럽게 나온다. 087을 안 본 학생에게 그 문장은
모르는 말을 이미 아는 것처럼 다루는 말이다 — 거기서 막힌다.

여기서 기계가 볼 수 있는 것만 본다. 화학 내용이 옳은지는 사람이 본다.

  ① 머리글이 맞는가        번호가 파일 이름과 · 제목이 시험 쪽 목록과 같은가
  ② 보강 문구가 맞는가     "이번 진단에서 <b>X</b>가 보강" 의 X 가 그 강의인가
  ③ **앞뒤가 맞는가**      다른 강을 부르는 자리마다, 이미 배운 것처럼 말하는
                          강이 실제로 **더 앞**인가. 뒤엣것을 배운 것처럼 말하면
                          처음 보는 학생은 못 알아듣는다.
  ④ 없는 강을 부르는가     001~125 밖이거나 파일이 없는 번호
  ⑤ 오답 → 강의가 맞는가   final.html 의 영역·유형 → 강의 지도가 실제로 그
                          내용을 다루는 강의를 가리키는가(영역이 같은가)

실행:
    python3 tools/lec_audit.py            # 전체 보고
    python3 tools/lec_audit.py --check    # 하나라도 걸리면 빨간불
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = os.path.join(ROOT, 'final.html')
# 선생님이 이미 보고 남겨 둔 것. 여기 적힌 것은 빨간불을 안 켠다 —
# 대신 **새로 생기는 것**은 그 자리에서 막는다(tools/dupe_pages.py 와 같은 방침).
NOTE = os.path.join(ROOT, 'tools', 'lec_audit.json')


def known_gaps():
    try:
        with open(NOTE, encoding='utf-8') as fh:
            return set(json.load(fh).get('오답→강의', []))
    except (OSError, ValueError):
        return set()

# 이미 배운 것처럼 말하는 말투. 이 말이 붙은 번호는 **더 앞**이라야 한다.
# 넓게 잡으면 잡음이 쏟아진다 — '본 ', '나온' 같은 흔한 말은 뺀다.
BACK = ['앞에서', '앞 강', '앞의', '이미', '배운', '배웠', '지난 강', '했던', '봤',
        '정리한', '다뤘']
# 뒤에서 다룬다고 알리는 말투. 이 말이 붙은 번호는 **더 뒤**라야 한다.
# '곧', '가서' 는 '즉'·'내려가서' 로도 쓰여 못 쓴다.
# '예고' 는 활용에 따라 앞뒤가 뒤집힌다 — '예고하고'(이 강이 알린다)와
# '117에서 예고한'(앞 강이 알렸다)이 같은 낱말이다. 그래서 안 쓴다.
FWD = ['다음 강', '이어서', '뒤에서', '나중에', '에서 다룰', '에서 볼',
       '에서 배울', '다음 영역']


def shares(a, b):
    """두 이름이 같은 것을 가리키는가. 표기가 달라도 **겹치는 토막**이 있으면
    같은 것으로 본다 — 두 글자 이상 이어서 겹치면 우연이 아니다."""
    x = re.sub(r'[^0-9A-Za-z가-힣]', '', a)
    y = re.sub(r'[^0-9A-Za-z가-힣]', '', b)
    if not x or not y:
        return True                        # 잴 것이 없으면 시비 걸지 않는다
    if x.lower() in y.lower() or y.lower() in x.lower():
        return True
    for i in range(len(x) - 1):
        if x[i:i + 2] in y:
            return True
    return False


def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', s)


def load_pages():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'lec-*.html'))):
        rel = os.path.basename(p)
        with open(p, encoding='utf-8') as fh:
            src = fh.read()
        m = re.match(r'lec-(\d{3})-', rel)
        num = m.group(1) if m else None
        h = re.search(r'<h1 class="serif">(.*?)</h1>\s*<div class="sub">(\d{3})\s*·\s*(.*?)</div>', src)
        hw = re.search(r'<div class="hw">(.*?)</div>', src, re.S)
        out.append({
            'file': rel, 'num': num, 'src': src,
            'title': strip_tags(h.group(1)).strip() if h else None,
            'hnum': h.group(2) if h else None,
            'area': strip_tags(h.group(3)).strip() if h else None,
            'hw': strip_tags(hw.group(1)) if hw else '',
            'text': strip_tags(src),
        })
    return out


def lec_map():
    """final.html 의 영역/유형 → 강의 지도. 오답이 어느 강으로 가는지."""
    with open(FINAL, encoding='utf-8') as fh:
        s = fh.read()
    m = re.search(r'const AREALEC\s*=\s*\{(.*?)\n\};', s, re.S)
    out = {}
    if m:
        for k, v in re.findall(r"'([^']+)'\s*:\s*'(lec-[\w-]+\.html)'", m.group(1)):
            out[k] = v
    return out


def lec_list():
    """LECLIST — 강의 파일과 시험 쪽이 부르는 이름."""
    with open(FINAL, encoding='utf-8') as fh:
        s = fh.read()
    m = re.search(r'const LECLIST\s*=\s*(\[.*?\]);', s, re.S)
    return dict(json.loads(m.group(1))) if m else {}


def refs(page, known):
    """다른 강을 부르는 자리를 모두 찾아 앞뒤를 견준다.

    ⚠ 강의 글에는 세 자리 숫자가 널려 있다 — 273K · 180° · 394kJ · 760mmHg.
      그것을 강의 번호로 읽으면 보고가 잡음으로 덮인다. 그래서 **001~125 안**
      이면서 강의를 부르는 말투가 붙은 것만 본다.
    """
    bad = []
    self_n = int(page['num'])
    t = page['text']
    for m in re.finditer(r'(?<![0-9])(\d{3})(?![0-9])', t):
        n = m.group(1)
        if not (1 <= int(n) <= 125):
            continue                       # 화학 값이다(273 · 394 · 760 …)
        # 뒤에 단위가 붙으면 강의가 아니다.
        if re.match(r'\s*(°|K|kJ|kcal|nm|mmHg|atm|g|mL|L|℃|%|배|개|년)', t[m.end():m.end() + 4]):
            continue
        # 말투는 **숫자 바로 옆**에서만 읽는다. 넓게 보면 한 문장 안의 다른
        # 구절이 딸려 온다 — "다음 강(100…)에서는 098에서 배운 산화수를" 에서
        # 098 의 말투는 뒤에 붙은 '배운' 이지 앞의 '다음 강' 이 아니다.
        pre = t[max(0, m.start() - 16):m.start()]
        post = t[m.end():m.end() + 16]
        near = pre + ' ' + post
        looks_lec = ('강' in pre[-12:] or re.match(r'\s*강', post) or
                     re.match(r'\s*에서', post) or
                     ('(' in pre[-2:] and ')' in post[:2]))
        if not looks_lec:
            continue
        if n not in known:
            bad.append(('없는 강', n, (pre + '[' + n + ']' + post).strip()))
            continue
        k = int(n)
        if k == self_n:
            continue
        back = any(w in near for w in BACK)
        fwd = any(w in near for w in FWD)
        if back and not fwd and k > self_n:
            bad.append(('아직 안 본 강을 배운 것처럼', n,
                        (pre + '[' + n + ']' + post).strip()))
        elif fwd and not back and k < self_n:
            bad.append(('앞 강을 뒤엣것처럼', n, (pre + '[' + n + ']' + post).strip()))
    return bad


def main():
    check = '--check' in sys.argv[1:]
    pages = load_pages()
    known = {p['num'] for p in pages if p['num']}
    names = lec_list()
    amap = lec_map()
    bad = {'머리글': [], '보강 문구': [], '앞뒤': [], '오답→강의': []}

    for p in pages:
        f = p['file']
        if not p['title']:
            bad['머리글'].append(f + ' — 머리글을 못 읽었습니다')
            continue
        if p['hnum'] != p['num']:
            bad['머리글'].append(f + ' — 머리글 번호 ' + str(p['hnum']) +
                                ' 가 파일 이름(' + p['num'] + ')과 다릅니다')
        # ② 보강 문구의 개념이 이 강의인가.
        #    말이 똑같기를 바라면 안 된다 — 문구는 **진단이 부르는 이름**이고
        #    제목은 강의 이름이라 원래 다르게 적는다('원자모형 · 원자의 구조'
        #    ↔ '원자의 구조와 동위원소'). 겹치는 데가 **한 군데도 없을 때**만
        #    딴 개념을 데려온 것이다.
        m = re.match(r'이번 진단에서 (.+?)\s*(?:가|이) 보강', p['hw'])
        if m:
            said = m.group(1)
            want = p['title'] + ' ' + (p['area'] or '')
            if not shares(said, want):
                bad['보강 문구'].append(f + ' — "' + said + '" 인데 제목은 "' +
                                      p['title'] + '"(' + (p['area'] or '') + ')')
        for why, n, ctx in refs(p, known):
            bad['앞뒤'].append(f + ' [' + why + ' → ' + n + '] …' + ctx + '…')

    # ⑤ 오답이 가리키는 강의가 그 내용을 실제로 다루는가.
    #    영역 이름끼리 견주면 안 된다 — 지도의 열쇠는 진단이 붙인 **개념 이름**
    #    (pH · 몰농도 · 헤스법칙)이고 강의 영역은 큰 묶음(산과 염기)이라 원래
    #    다르다. 그 개념이 강의 **어디에도 안 나오면** 엉뚱한 강의로 보낸 것이다.
    byfile = {p['file']: p for p in pages}
    for area, target in sorted(amap.items()):
        if target not in byfile:
            bad['오답→강의'].append(area + ' → ' + target + ' (그런 강의가 없습니다)')
            continue
        g = byfile[target]
        hay = (g['title'] or '') + ' ' + (g['area'] or '') + ' ' + g['hw']
        if shares(area, hay):
            continue
        # 제목·영역·보강문구에 없으면 본문까지 본다. 본문에도 없으면 엉뚱하다.
        # ⚠ 사이의 부호까지 지우고 견준다 — 지도는 '헨더슨하셀바흐식' 으로
        #   적고 강의는 '헨더슨-하셀바흐 식' 으로 쓴다. 같은 말이다.
        flat = lambda z: re.sub(r'[^0-9A-Za-z가-힣]', '', z).lower()
        if flat(area) in flat(g['text']):
            continue
        bad['오답→강의'].append('\'' + area + '\' → ' + target + ' (' +
                              (g['title'] or '?') + ') · 그 강의에 그 말이 없습니다')

    print('강의 ' + str(len(pages)) + '장 · 이름표 ' + str(len(names)) +
          '개 · 오답 지도 ' + str(len(amap)) + '갈래')
    total = 0
    for k in ['머리글', '보강 문구', '앞뒤', '오답→강의']:
        v = bad[k]
        total += len(v)
        print('\n── ' + k + ' · ' + (str(len(v)) + '건' if v else '이상 없음') + ' ──')
        for line in v[:40]:
            print('  ✗ ' + line)
        if len(v) > 40:
            print('  … ' + str(len(v) - 40) + '건 더')

    if check:
        seen = known_gaps()
        fresh = [x for x in bad['오답→강의'] if x not in seen]
        hard = len(bad['머리글']) + len(bad['보강 문구']) + len(bad['앞뒤']) + len(fresh)
        if bad['오답→강의'] and not fresh:
            print('\n(오답→강의 ' + str(len(bad['오답→강의'])) +
                  '건은 선생님이 보고 남겨 둔 것입니다 — tools/lec_audit.json)')
        if hard:
            print('\nFAIL ' + str(hard) + '건 (새로 생긴 것)')
            return 1
    if '--write' in sys.argv[1:]:
        with open(NOTE, 'w', encoding='utf-8') as fh:
            json.dump({'설명': '오답이 가리키는 강의에 그 말이 없는 자리. 강의를 고칠지 '
                              '지도를 옮길지는 선생님이 정한다. 여기 적힌 것은 빨간불을 '
                              '안 켜고, 새로 생기는 것만 막는다.',
                       '오답→강의': bad['오답→강의']}, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        print('\n기록했습니다: ' + str(len(bad['오답→강의'])) + '건')
        return 0
    print('\n' + ('PASS' if check else '합계 ' + str(total) + '건'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

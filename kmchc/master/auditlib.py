# -*- coding: utf-8 -*-
"""auditlib — 감사37~39 가 세운 기계 검사 A~S 를 한 자리에 모은다

  ★왜 모으는가★ — 감사37·38·39 는 같은 검사를 세 벌 베껴 적었다. T14 마감이 R·S 를
  세울 때 세 파일 가운데 ★맨 마지막 것만★ 고쳐졌고, 앞의 둘은 옛 꼴로 남았다.
  검사가 늘 때마다 베끼는 자리가 늘면 어느 감사가 무엇을 걸었는지 알 수 없게 된다.
  그래서 A~S 는 여기에 두고, 테마마다 새로 세우는 검사만 감사 파일에 적는다.

  쓰임
      import auditlib
      F = []
      auditlib.core(items, lambda it, cls, msg: F.append((it['id'], cls, msg)))
      # 그 뒤 테마별 검사를 더 걸고 auditlib.CLS 를 늘려 쓴다

  ★검사를 넓히기 전에 오탐부터 센다★ — 감사38 의 N(낱말 집합 포함관계)과 감사39 의
  R 첫 판이 모두 이 규약을 어겨 버려졌다. 여기 남은 것은 오탐을 세고 좁힌 뒤의 꼴이다.
"""
import json, os, re
from collections import Counter

MK = ['①', '②', '③', '④']


def load(lo, hi, bank=None):
    """은행에서 범위를 잘라 온다 — 감사 파일마다 같은 여덟 줄을 적지 않게."""
    here = os.path.dirname(os.path.abspath(__file__))
    b = bank or json.load(open(os.path.join(here, 'master_bank.json'), encoding='utf-8'))
    items = [i for i in b if lo <= i['id'] <= hi]
    assert items, '범위에 문항이 없다'
    return items


def core(items, rep):
    """감사37~39 의 A~S 를 그대로 건다 — rep(it, cls, msg) 로 알린다."""
    NUM = re.compile(r'^\s*[-−]?\d')
    SYM = re.compile(r'[A-Za-z()\[\]<>=+ₗ₁₂]')

    for it in items:
        cs, a, sol = it['choices'], it['answer'], it['solution']

        if not it.get('objective'):
            rep(it, 'A', 'objective 결손')
        elif it['objective'].strip() == it.get('skill', '').strip():
            rep(it, 'A', f"objective 가 skill 의 되풀이 — {it['objective']}")

        for fld in ('stem', 'solution'):
            if '★' in it[fld]:
                rep(it, 'B', f'{fld} 에 ★ 유출')

        for k in range(4):
            if MK[k] + ' ' + cs[k] not in sol:
                rep(it, 'C', f'해설의 {MK[k]} 인용이 선지 문면과 다르다 — 선지 「{cs[k]}」')
        #   ▸ ★확정 어구는 꼴이 여럿이다★ — '①이 옳아' 말고도 '①이 답이야' · '②가
        #     바닥상태야' 처럼 물음에 맞춘 말로 닫는다. 감사37 의 좁은 꼴을 넓혔다.
        if not (any(t in sol for t in ('가 옳아', '이 옳아', f'답이 {MK[a]}'))
                or re.search(re.escape(MK[a]) + r'[이가]\s*[^.]{0,12}(답|옳|맞|이야|야)', sol)):
            rep(it, 'D', '해설에 정답 확정 어구가 없다')

        ds = it.get('distractors', [])
        if sorted(d['opt'] for d in ds) != sorted(set(range(4)) - {a}):
            rep(it, 'E', f"distractor 자리가 어긋난다 — {[d['opt'] for d in ds]}, 정답 {a}")
        for d in ds:
            if not d.get('error') or not d.get('type'):
                rep(it, 'E', f"distractor opt{d['opt']} 의 error/type 결손")

        if len(set(cs)) != 4:
            rep(it, 'G', f'선지 중복 — {cs}')
        if len(sol) < 300:
            rep(it, 'G', f'해설 {len(sol)}자 (하한 300)')
        L = sorted(len(c) for c in cs)
        la = len(cs[a])
        if la == L[3] and L[2] < L[3]:
            rep(it, 'F', f'G3 정답이 단독 최장 — {[len(c) for c in cs]}')
        if la == L[0] and L[0] < L[1]:
            rep(it, 'F', f'G3 정답이 단독 최단 — {[len(c) for c in cs]}')
        mid = (L[1] + L[2]) / 2
        if mid >= 8 and (L[3] - L[0]) / mid > 0.25:
            rep(it, 'F', f'G3b 산포 {(L[3]-L[0])/mid:.3f} — {[len(c) for c in cs]}')

        if all(NUM.match(c) for c in cs):
            head = [int(re.match(r'\s*[-−]?(\d+)', c).group(1)) for c in cs]
            if head != sorted(head):
                rep(it, 'H', f'G6 앞자리 숫자가 오름차순이 아니다 — {head}')
            par = [h % 2 for h in head]
            if Counter(par)[par[a]] == 1:
                rep(it, 'H', f'패리티로 정답만 남는다 — 앞자리 {head}')

        parts = [c.split(' ') for c in cs]
        if all(len(p) == 2 for p in parts) and len({p[0] for p in parts}) < 4 \
                                           and len({p[1] for p in parts}) < 4:
            x = [p[0] for p in parts]; y = [p[1] for p in parts]
            tx = Counter(x).most_common(1)[0]; ty = Counter(y).most_common(1)[0]
            if tx[1] > 1 and ty[1] > 1 and [i for i in range(4)
                                            if x[i] == tx[0] and y[i] == ty[0]] == [a]:
                rep(it, 'I', f'축별 최빈값 교차가 정답을 가리킨다 — {tx[0]} × {ty[0]}')

        for fld in ('answer_proof', 'calc_check', 'device', 'scenario'):
            if not it.get(fld):
                rep(it, 'J', f'{fld} 결손')

        def inste(c):
            m = NUM.match(c) and re.match(r'\s*[-−]?(\d+)', c)
            return bool(m) and bool(re.search(r'(?<!\d)' + m.group(1) + r'(?!\d)', it['stem']))
        if NUM.match(cs[a]) and inste(cs[a]) and not any(inste(c) for i, c in enumerate(cs) if i != a):
            rep(it, 'K', f'정답값 「{cs[a]}」 만 발문에 그대로 있다')

        neg = [i for i, c in enumerate(cs) if any(t in c for t in ('않', '없', '아니', '못'))]
        if neg == [a]:
            rep(it, 'L', f'정답만 부정형 — 극성으로 홀로 선다 「{cs[a]}」')

        # ── M ★G3g 칸별 최빈값 조합★ ────────────────────────────────────────
        toks = [c.split() for c in cs]
        if len(toks[0]) >= 2 and all(len(t) == len(toks[0]) for t in toks):
            picks = []
            for col in zip(*toks):
                cc = Counter(col).most_common()
                win = [v for v, k in cc if k == cc[0][1]]
                picks.append(win[0] if len(win) == 1 else None)
            if any(p is not None for p in picks):
                surv = [i for i, t in enumerate(toks)
                        if all(p is None or t[k] == p for k, p in enumerate(picks))]
                if surv == [a]:
                    rep(it, 'M', f'칸별 최빈값 조합이 정답만 남긴다 — {" ".join(p or "·" for p in picks)}')

        # ── N ★선지 사이 포함관계★ ─────────────────────────────────────────
        #   낱말 집합으로 본다. 정답의 낱말이 다른 선지의 낱말에 모두 들어 있으면,
        #   그 선지가 참일 때 정답도 참이 되기 쉬워 소거의 실마리가 된다.
        #   ▸ ★낱말 집합으로 보면 오탐만 나온다★ — '황(원자 번호 16)' 과 '염소(원자 번호 17)'
        #     처럼 한 글자 낱말이 빠져 서로를 품는 것으로 보인다(감사38 초판이 5건 모두 오탐).
        #     문자열이 통째로 들어 있을 때만 짚는다 — 뜻의 포함관계는 손으로 볼 일이다.
        for i, c in enumerate(cs):
            if i == a:
                continue
            if len(cs[a]) >= 6 and cs[a] in c:
                rep(it, 'N', f'정답이 {MK[i]} 안에 통째로 들어 있다 — 「{cs[a]}」 ⊂ 「{c}」')
            elif len(c) >= 6 and c in cs[a]:
                rep(it, 'N', f'{MK[i]} 가 정답 안에 통째로 들어 있다 — 「{c}」 ⊂ 「{cs[a]}」')

        # ── O ★형태 홀로서기 3 : 1★ ────────────────────────────────────────
        has = [bool(SYM.search(c)) for c in cs]
        if Counter(has)[has[a]] == 1:
            rep(it, 'O', f'기호 유무로 정답만 홀로 선다 — {["기호" if h else "순우리말" for h in has]}')

        # ── P ★발문 어미의 형식 기대★ ──────────────────────────────────────
        #   ▸ ★'짝지은 것은?' 은 빼야 한다★ — 두 마디('X — Y')로 된 선지의 표준 어미이고
        #     〈보기〉를 예고하지 않는다(감사38 초판이 4건 모두 이 꼴로 오탐).
        if re.search(r'(묶은|고른)\s*것은', it['stem']) and '—' not in ''.join(cs) and \
                not any(t in ''.join(cs) for t in ('ㄱ', 'ㄴ', 'ㄷ')):
            rep(it, 'P', '발문이 〈보기〉 조합형을 예고하는데 선지에 ㄱ·ㄴ·ㄷ 이 없다')

        # ── Q ★어미 반향★ ──────────────────────────────────────────────────
        tails = [c.strip()[-3:] for c in cs]
        if len(tails[a]) == 3 and tails[a] in it['stem'] and \
                not any(t in it['stem'] for i, t in enumerate(tails) if i != a):
            rep(it, 'Q', f'정답의 꼬리말 「{tails[a]}」 만 발문에 있다')

        # ── R ★★잰 값을 기제의 산물로 못 박은 자리★★ (T14 마감 · 첫 판은 11/11 오탐으로 버렸다)
        #   ▸ '적힌 값 …이 그 결과' 꼴 — 발문의 수치를 기제의 결과로 귀속하는 주장.
        #     서로 다른 기준으로 잰 값이 섞여 있으면 그 귀속이 과잉이 된다.
        for _f in ('answer_proof', 'calc_check', 'solution'):
            _t = it.get(_f) or ''
            for _m in re.finditer(r'(적힌|주어진) 값[^.\n]{0,40}', _t):
                if re.search(r'\d', _m.group(0)) and '결과' in _m.group(0):
                    rep(it, 'R', f'{_f} 가 잰 값을 기제의 산물로 못 박는다 — {_m.group(0)[:34]}')

        # ── S ★★어휘 반향 — 정답만 발문의 낱말을 되받는다★★ (T14 마감) ────────
        #   ▸ 두 자 이상 한글 낱말만 센다. 조사·어미가 붙는 자리를 피해 어간 2자로 자른다.
        def _w(s):
            return {t[:2] for t in re.findall(r'[가-힣]{2,}', s)}

        stw = _w(it['stem'])
        echo = [len(_w(c) & stw) for c in cs]
        if echo[a] >= 2 and all(echo[i] == 0 for i in range(4) if i != a):
            shared = sorted(_w(cs[a]) & stw)[:4]
            rep(it, 'S', f"정답만 발문의 낱말을 되받는다 — {'·'.join(shared)}")

CLS = {'A': 'objective', 'B': '★ 유출', 'C': '해설 인용 불일치(STALE)',
       'D': '정답 확정 어구', 'E': 'distractor', 'F': '길이 단서(G3/G3b)',
       'G': '선지·해설 형식', 'H': '수치 선지 3단', 'I': '축별 최빈값 교차',
       'J': '근거 필드', 'K': '발문 메아리', 'L': '극성 홀로서기',
       'M': '★G3g 칸별 최빈값 조합★', 'N': '★선지 포함관계★',
       'O': '★형태 홀로서기 3:1★', 'P': '★발문 어미 형식 기대★', 'Q': '★어미 반향★',
       'R': '★잰 값을 기제의 산물로★', 'S': '★어휘 반향(정답만)★'}

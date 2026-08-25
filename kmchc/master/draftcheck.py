# -*- coding: utf-8 -*-
"""draftcheck — 에이전트 초안(JSON)을 ★빌더로 옮겨 적기 전에★ 기계로 잰다

  쓰임:  python3 draftcheck.py <초안.json> [자리표.json]

  ★왜 옮겨 적기 전에 재는가★ — render_batch 로 옮겨 적은 뒤에 local_checks 가 울면
  고칠 자리가 ★두 곳(초안 JSON 과 빌더 .py)★ 으로 갈린다. 초안에서 고치면 한 곳이다.
  local_checks 와 ★같은 규약★ 을 걸되, 초안에만 있는 것(정답 자리·길이순위 지정)을 더 본다.

  거는 것
    ① 정답 자리가 자리표와 같은가 · ② 정답 길이순위가 자리표와 같은가
    ③ 선지 길이 산포 (최장−최단)÷평균 ≤ 0.22 · ④ 선지 길이 동률
    ⑤ 오답 유형 셋이 서로 다른가 · ⑥ 오답끼리 자카드 < 0.60
    ⑦ 정답만 부정형 · ⑧ 정답이 발문과 낱말을 혼자 가장 많이 겹침
    ⑨ 해설이 오답 셋을 문면 그대로 인용 · ⑩ 정답 확정 어구
    ⑪ wmap 의 문면이 선지와 같은가 · ⑫ 조사 앞 빈칸 · ⑬ ★ 기호
    ⑭ 트랙 하한(일반 ≥ 7) · ⑮ 쉬움 ≤ 3 · ⑯ 수치 선지 오름차순(G6)
    ⑰ 선지 글자 수 16~24 · ⑱ 선지가 온점으로 끝나지 않는가
    ⑲ ★G3g 칸별 최빈값 조합이 정답만 남기지 않는가★ (M02968 이 이 자리에서 울었다)
"""
import json
import re
import sys
from collections import Counter

MK = '①②③④'
NEG = ('않', '없', '아니', '못', '안 ')
#   ★'이' 는 조사이기도 하고 '이 표는' 의 매김말이기도 하다★ — 매김말까지 울려 열세 건이
#   오탐이었다. 그래서 '이' 는 ★숫자·로마자 뒤★ 에서만 조사로 본다(349 이 → 어긋남).
JOSA = re.compile(r'\s(을|를|가|은|는|에|의|와|과|로|으로|만|도|부터|까지)\b')
JOSA_I = re.compile(r'[0-9A-Za-z]\s이\b')
NUM = re.compile(r'^\s*[-−]?\d')


def toks(s):
    return {w for w in re.findall(r'[0-9A-Za-z가-힣]{2,}', s)}


def jac(a, b):
    A, B = toks(a), toks(b)
    return len(A & B) / len(A | B) if A and B else 0.0


def rank_of(cs, a):
    L = sorted((len(c) for c in cs), reverse=True)
    return L.index(len(cs[a])) + 1


def main():
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    items = d['items'] if isinstance(d, dict) else d
    plan = {}
    if len(sys.argv) > 2:
        pj = json.load(open(sys.argv[2], encoding='utf-8'))
        rows = pj['items'] if isinstance(pj, dict) and 'items' in pj else pj
        plan = {r['id']: r for r in rows}
    bad, warn = [], []
    for x in items:
        cs, a, i = x['choices'], x['answer'], x['id']
        p = plan.get(i)
        if p is not None:
            if a != p['answer']:
                bad.append('%s 정답 자리 %d — 자리표는 %d' % (i, a + 1, p['answer'] + 1))
            r = rank_of(cs, a)
            if r != p['rank']:
                bad.append('%s 정답 길이순위 %d위 — 자리표는 %d위 (%s)'
                           % (i, r, p['rank'], [len(c) for c in cs]))
        L = [len(c) for c in cs]
        sp = (max(L) - min(L)) / (sum(L) / 4)
        if sp > 0.22:
            bad.append('%s 길이 산포 %.3f — %s' % (i, sp, L))
        if len(set(L)) < 4:
            warn.append('%s 선지 길이 동률 — %s' % (i, L))
        if any(not (16 <= n <= 24) for n in L):
            warn.append('%s 선지 글자 수가 16~24 를 벗어남 — %s' % (i, L))
        ts = [w['type'] for w in x['wrongs']]
        if len(set(ts)) < 3:
            bad.append('%s 오답 유형이 겹침 — %s' % (i, ts))
        wt = [w['text'] for w in x['wrongs']]
        for k in range(3):
            for m in range(k + 1, 3):
                s = jac(wt[k], wt[m])
                if s >= 0.60:
                    bad.append('%s 오답 자카드 %.2f — 「%s」 ↔ 「%s」' % (i, s, wt[k][:18], wt[m][:18]))
        neg = [k for k, c in enumerate(cs) if any(t in c for t in NEG)]
        if neg == [a]:
            bad.append('%s 정답만 부정형 — 「%s」' % (i, cs[a]))
        st = toks(x['stem'])
        ov = [len(toks(c) & st) for c in cs]
        if ov[a] == max(ov) and ov.count(max(ov)) == 1:
            bad.append('%s 정답이 발문과의 낱말 겹침 최다(유일) — %s' % (i, ov))
        for w in x['wrongs']:
            if w['text'] not in x['prose']:
                bad.append('%s 해설이 오답을 그대로 인용하지 않았다 — 「%s」' % (i, w['text'][:22]))
        if not re.search(re.escape(MK[a]) + r'[이가]?\s*[^.]{0,10}(옳아|답이야|맞아)', x['prose']):
            bad.append('%s 해설에 정답 확정 어구가 없다' % i)
        for w in x['wmap']:
            if w['text'] not in cs:
                bad.append('%s wmap 의 문면이 선지와 다르다 — 「%s」' % (i, w['text'][:22]))
        for fld in ('stem', 'prose', 'proof', 'calc'):
            m = JOSA.search(x[fld]) or JOSA_I.search(x[fld])
            if m:
                warn.append('%s %s 에 조사 앞 빈칸 — %s' % (i, fld, m.group(0).strip()))
            if '★' in x[fld]:
                bad.append('%s %s 에 ★ 기호' % (i, fld))
        for c in cs:
            if JOSA.search(c) or JOSA_I.search(c):
                warn.append('%s 선지에 조사 앞 빈칸 — 「%s」' % (i, c))
        #   ★선지는 온점으로 끝나지 않는다★ — 은행 11,816 선지 가운데 온점으로 끝난 것이
        #   하나도 없다. T18P1 초안이 마흔 선지 모두에 온점을 붙여 왔고, 해설의 인용은
        #   온점 없이 적혀 ★인용 불일치가 서른 건★ 울렸다. 길이도 한 자씩 늘어난다.
        for k, c in enumerate(cs):
            if c.rstrip().endswith('.'):
                bad.append('%s 선지 %s 가 온점으로 끝난다 — 「%s」' % (i, MK[k], c))
        #   ⑲ ★G3g★ — 선지를 빈칸으로 갈라 칸마다 최빈값을 고르고, 그 조합에 남는 것이
        #   정답 하나뿐이면 뜻을 몰라도 정답이 짚힌다. T18P2 M02968 이 이 자리에서 울었다
        #   (칸1 '결합각은' × 칸4 '107도이다' → ④만 남았다). 한 칸을 동률로 만들면 풀린다.
        tk = [c.split() for c in cs]
        if len(tk[0]) >= 2 and all(len(t) == len(tk[0]) for t in tk):
            picks = []
            for col in zip(*tk):
                cc = Counter(col).most_common()
                win = [v for v, n in cc if n == cc[0][1]]
                picks.append(win[0] if len(win) == 1 else None)
            if any(q is not None for q in picks):
                surv = [k for k, t in enumerate(tk)
                        if all(q is None or t[j] == q for j, q in enumerate(picks))]
                if surv == [a]:
                    bad.append('%s G3g 칸별 최빈값 조합이 정답만 남긴다 — %s'
                               % (i, ' '.join(q or '·' for q in picks)))
        if all(NUM.match(c) for c in cs):
            head = [int(re.match(r'\s*[-−]?(\d+)', c).group(1)) for c in cs]
            if head != sorted(head):
                bad.append('%s G6 수치가 오름차순이 아니다 — %s' % (i, head))
    tr = Counter(x['track'] for x in items)
    df = Counter(x['difficulty'] for x in items)
    if tr.get('일반', 0) < 7:
        bad.append('일반 트랙 %d제 — 하한 7' % tr.get('일반', 0))
    if df.get('쉬움', 0) > 3:
        bad.append('쉬움 %d제 — 상한 3' % df.get('쉬움', 0))
    print('초안 %d제 · 트랙 %s · 난이도 %s' % (len(items), dict(tr), dict(df)))
    print('  정답 자리 %s' % Counter(x['answer'] + 1 for x in items))
    print('  길이순위 %s' % Counter(rank_of(x['choices'], x['answer']) for x in items))
    if warn:
        print('\n  △ 눈여겨볼 자리 %d' % len(warn))
        for w in warn:
            print('     ·', w)
    if bad:
        print('\n  ❌ 어긋난 자리 %d' % len(bad))
        for b in bad:
            print('     ·', b)
        raise SystemExit(1)
    print('\n  ✅ 초안 점검 통과')


if __name__ == '__main__':
    main()

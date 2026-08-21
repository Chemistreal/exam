#!/usr/bin/env python3
"""수업 한 벌에 필요한 것을 학생마다 미리 셈해 둔다 — student-packets.json.

시험 직전 회차(4시간)에 학생 손에 쥐여 줄 것이 넷이다.

    워밍업 6제      예열. **맞힐 수 있는 것**으로만. 시험이 아니다.
    내 함정 한 장    그 학생이 실제로 틀린 문항의 오개념 스무 줄
    진단표          무엇이 새고 있는가 — 시간인가 빈칸인가 개념인가
    시험장 지시 한 줄  진단에서 나온다. 학생마다 다르다.

이것을 화면(weak60.html)에서 그때그때 세면 60문항 × 스물몇 회차를 브라우저가
매번 훑어야 한다. 그래서 여기서 한 번 셈해 파일로 둔다. 화면은 그 파일을 읽어
Word 로 옮기기만 한다.

**이름은 안 싣는다.** 열쇠는 학생 코드다(시트가 소금 쳐 만든 것). 이름을 붙여
보는 표는 선생님 브라우저에만 있다(weak60.html 의 이름↔코드 표).

    python3 tools/gen_student_packets.py            # 무엇이 담기는지 보여만 준다
    python3 tools/gen_student_packets.py --write    # 심는다
    python3 tools/gen_student_packets.py --check    # 심은 것이 지금 자료와 맞는가 (CI)
"""
import json
import os
import re
import sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import gen_student_final as G          # 채점 규칙·강의 잇기를 그대로 쓴다

OUTFILE = os.path.join(ROOT, 'student-packets.json')
N_TRAP = 20        # 함정 카드 줄 수
N_WARM = 6         # 워밍업 문항 수
AREA_CAP = 2       # 한 영역이 워밍업을 다 먹지 못하게


def load(pin=None):
    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    by_title = {e['title']: e for e in exams}
    by_id = {e['id']: e for e in exams}
    gp = os.path.join(ROOT, 'student-final-groups.json')
    groups = json.load(open(gp, encoding='utf-8'))['groups'] if os.path.exists(gp) else []
    canon = {c: g['id'] for g in groups for c in g['codes']}
    if pin:
        bfile = os.path.join(ROOT, 'backup', pin)
        bk = json.load(open(bfile, encoding='utf-8'))
    else:
        bfile, bk = G.latest_backup()
    sf = os.path.join(ROOT, 'student-finals.json')
    finals = {e['id']: e for e in json.load(open(sf, encoding='utf-8'))['exams']} \
        if os.path.exists(sf) else {}
    return exams, by_title, by_id, canon, bk['rows'], os.path.basename(bfile), finals


_ANS = {}
def answers_of(eid):
    if eid not in _ANS:
        p = os.path.join(ROOT, 'answers', eid + '.json')
        _ANS[eid] = (json.load(open(p, encoding='utf-8')).get('questions')
                     if os.path.exists(p) else None) or {}
    return _ANS[eid]


def scan(by_title, by_id, canon, rows):
    """학생 → 문항 하나하나의 이력. 회차마다 가장 최근 제출 하나만 본다."""
    latest = {}
    for r in rows:
        e = by_title.get(r.get('exam'))
        who = canon.get(r['code'])
        if not e or not who:
            continue
        if len(r.get('answers') or '') != e['nQ']:
            continue
        k = (who, e['id'])
        if k not in latest or r.get('saved', '') > latest[k].get('saved', ''):
            latest[k] = r

    S = defaultdict(lambda: {'items': [], 'types': defaultdict(
        lambda: {'c': 0, 'w': 0, 'b': 0, 'exw': set()}),
        'seg': [[0, 0, 0] for _ in range(5)], 'att': 0})
    for (who, eid), r in sorted(latest.items(), key=lambda x: (x[1].get('saved', ''), x[0])):
        e = by_id[eid]
        astr = r['answers']
        n = e['nQ']
        aq = answers_of(eid)
        S[who]['att'] += 1
        for q in range(1, n + 1):
            if G._allc(e, q):
                continue
            a = int(astr[q - 1]) if astr[q - 1].isdigit() else 0
            area = (e.get('area') or [None] * n)[q - 1] or '기타'
            typ = (e.get('type') or [None] * n)[q - 1] or area
            ok = a != 0 and a in G._acc(e, q)
            seg = min(4, (q - 1) * 5 // n)
            d = S[who]['types'][typ]
            S[who]['seg'][seg][0] += 1
            if a == 0:
                d['b'] += 1
                S[who]['seg'][seg][1] += 1
            elif ok:
                d['c'] += 1
            else:
                d['w'] += 1
                S[who]['seg'][seg][2] += 1
            it = aq.get(str(q)) or {}
            S[who]['items'].append({
                'e': eid, 'q': q, 'ok': ok, 'blank': a == 0, 'area': area, 'typ': typ,
                'concept': it.get('concept', ''), 'mis': (it.get('misconception') or '').strip(),
                'saved': r.get('saved', ''),
            })
            if not ok:
                d['exw'].add(eid)
    return S


def verdict(st):
    seg = st['seg']
    br = [(s[1] / s[0] * 100 if s[0] else 0) for s in seg]
    tot = sum(s[0] for s in seg)
    blanks = sum(s[1] for s in seg)
    wrongs = sum(s[2] for s in seg)
    bp = blanks / tot * 100 if tot else 0
    wp = wrongs / tot * 100 if tot else 0
    tail, head = br[3] + br[4], br[0] + br[1]
    if tail > head * 2.5 and tail > 8:
        return ('시간 부족',
                '앞은 멀쩡한데 뒤에서 무너집니다. 뒤 문항이 어려워서가 아니라 도달을 못 했습니다.',
                '「90분에 45번」 — 구간 시각을 답안지 맨 위에 쓰고 시작합니다.', bp, wp, br)
    if bp >= 8:
        return ('빈칸 습관',
                '무응답이 %.1f%%입니다. 빈칸은 수상 판정에서 오답과 똑같이 셉니다 — 순손실입니다.' % bp,
                '「빈칸 0개」 — 마지막 15분은 빈칸 채우기에 씁니다.', bp, wp, br)
    if bp < 1 and wp >= 45:
        return ('무작정 찍기',
                '무응답 %.1f%%인데 오답률 %.1f%%입니다. 모르는 문항도 다 찍고 있습니다.' % (bp, wp),
                '「찍기 전에 한 선지는 지운다」 — 한 개만 지워도 기댓값이 이득으로 바뀝니다.', bp, wp, br)
    return ('고르게 분포',
            '시간·빈칸에 뚜렷하게 새는 자리는 없습니다. 개념 회수가 주 전선입니다.',
            '「△ 표시한 건 반드시 되돌아온다」', bp, wp, br)


def buckets(st):
    shaky, always, stable = [], [], []
    for t, d in st['types'].items():
        bad = d['w'] + d['b']
        row = {'type': t, 'c': d['c'], 'bad': bad, 'rounds': len(d['exw'])}
        if d['c'] > 0 and bad > 0:
            shaky.append(row)
        elif bad > 0:
            always.append(row)
        else:
            stable.append(row)
    shaky.sort(key=lambda x: (-x['rounds'], -x['bad']))
    always.sort(key=lambda x: (-x['rounds'], -x['bad']))
    return shaky, always, stable


def trap_lines(st, final_entry=None):
    """함정 카드 — 한 영역이 카드를 다 먹으면 「내 약점 지도」가 아니라
       그 단원 이야기가 된다. 영역을 돌아가며 담는다.

       ⚠ **곧 풀 시험지에 실린 문항은 뺀다.** 파이널도 오답에서 고르고 함정
       카드도 오답에서 뽑으므로 두 집합은 구조적으로 겹친다. 재어 보니 스무
       줄 가운데 평균 열두 줄이 그 학생이 그날 풀 문항의 오개념이었다 —
       시험 직전 15분에 읽으라고 주는 종이가 답을 미리 알려 주고 있었다."""
    used = {(m['e'], int(m['q'])) for m in (final_entry.get('srcmap') or [])} \
        if final_entry else set()
    rep = {t: len(d['exw']) for t, d in st['types'].items()}
    seen, by_area = set(), defaultdict(list)
    for it in sorted((x for x in st['items'] if not x['ok'] and x['mis']
                      and (x['e'], x['q']) not in used),
                     key=lambda x: -rep.get(x['typ'], 1)):
        k = re.sub(r'\s+', '', it['mis'])[:28]
        if k in seen:
            continue
        seen.add(k)
        by_area[it['area']].append(it)
    order = sorted(by_area, key=lambda a: -max(rep.get(x['typ'], 1) for x in by_area[a]))
    out = []
    for rnd in range(4):
        for a in order:
            if len(by_area[a]) > rnd and len(out) < N_TRAP:
                x = by_area[a][rnd]
                lab = x['concept'] or x['typ']
                same = re.sub(r'\s', '', lab) == re.sub(r'\s', '', x['area'])
                out.append({'area': x['area'], 'label': '' if same else lab, 'line': x['mis']})
        if len(out) >= N_TRAP:
            break
    return out


def warmup(st, shaky, stable, final_entry, by_id):
    """예열용 여섯. **맞힐 수 있는 것**으로만 고른다 — 시험이 아니다.
       셋은 늘 맞히는 유형(자신감), 셋은 흔들리는 유형 중 최근에 맞힌 것
       (회수 가능분을 깨워 둔다). 파이널 60제와 겹치는 것은 뺀다."""
    stable_t = {r['type'] for r in stable}
    shaky_t = {r['type'] for r in shaky}
    used = {(m['e'], int(m['q'])) for m in (final_entry.get('srcmap') or [])} \
        if final_entry else set()
    pool_s, pool_k = [], []
    for it in sorted((x for x in st['items'] if x['ok']),
                     key=lambda x: x['saved'], reverse=True):
        if (it['e'], it['q']) in used:
            continue
        if it['typ'] in stable_t:
            pool_s.append(it)
        elif it['typ'] in shaky_t:
            pool_k.append(it)

    def spread(pool, n, taken):
        got, per = [], Counter()
        for c in pool:
            k = (c['e'], c['q'])
            if k in taken or per[c['area']] >= AREA_CAP:
                continue
            taken.add(k)
            per[c['area']] += 1
            got.append(c)
            if len(got) >= n:
                break
        return got

    taken = set()
    picks = spread(pool_s, 3, taken) + spread(pool_k, 3, taken)
    if len(picks) < N_WARM:
        picks += spread(pool_s + pool_k, N_WARM - len(picks), taken)
    out = []
    for c in picks[:N_WARM]:
        e = by_id[c['e']]
        # 정답은 안 싣는다. 이 파일은 **학생용 종이를 짓는 원천**이고 정적으로
        # 배포된다 — 아무도 안 쓰는 정답키를 두면 언젠가 한 줄로 새어 나간다.
        out.append({'e': c['e'], 'q': c['q'], 'title': e['title'], 'area': c['area'],
                    'concept': c['concept']})
    return out


def build(pin=None):
    exams, by_title, by_id, canon, rows, bname, finals = load(pin)
    S = scan(by_title, by_id, canon, rows)
    packets = {}
    for code in sorted(S):
        st = S[code]
        v, why, card, bp, wp, br = verdict(st)
        shaky, always, stable = buckets(st)
        tot = sum(s[0] for s in st['seg'])
        corr = sum(1 for x in st['items'] if x['ok'])
        packets[code] = {
            'attempts': st['att'], 'graded': tot, 'correct': corr,
            'acc': round(corr / tot * 100, 1) if tot else 0,
            'blankPct': round(bp, 1), 'wrongPct': round(wp, 1),
            'blankBySeg': [round(x, 1) for x in br],
            'verdict': v, 'why': why, 'card': card,
            'shaky': shaky[:20], 'always': always[:15],
            'nShaky': len(shaky), 'nAlways': len(always), 'nStable': len(stable),
            'trap': trap_lines(st, finals.get(code)),
            'warmup': warmup(st, shaky, stable, finals.get(code), by_id),
        }
    return packets, bname


def dump(packets, bname):
    return json.dumps({
        'schemaVersion': 1,
        'source': bname,
        'note': ('tools/gen_student_packets.py 가 누적 응시에서 셈한 파생물. 손으로 안 고친다. '
                 '이름은 안 실린다 — 열쇠는 학생 코드다.'),
        'packets': packets,
    }, ensure_ascii=False, indent=1) + '\n'


def main():
    if '--check' in sys.argv:
        # ⚠ **지금 백업이 아니라 심을 때 쓴 백업으로 잰다.**
        #   백업은 봇이 하루 한 번 커밋하는데 그 커밋은 backup/*.json 하나만
        #   바꾼다(파생물을 다시 안 심는다). 지금 백업으로 재면 사람이 아무것도
        #   안 했는데 다음 날 아침 CI 가 빨개진다 — 매일.
        #   이 자가 막는 것은 「심어 둔 것이 그때 그 자료와 어긋나는 것」이다.
        #   백업이 새로 왔다는 것은 빨간불이 아니라 알림으로 적는다.
        if not os.path.exists(OUTFILE):
            print('✗ student-packets.json 이 없다 — --write 로 심는다')
            return 1
        now = open(OUTFILE, encoding='utf-8').read()
        try:
            pin = json.loads(now).get('source')
        except Exception:
            pin = None
        if not pin or not os.path.exists(os.path.join(ROOT, 'backup', pin)):
            print('✗ 심어 둔 자료가 어느 백업에서 나왔는지 알 수 없다 — --write 로 다시 심는다')
            return 1
        packets, bname = build(pin)
        if now != dump(packets, bname):
            print('✗ student-packets.json 이 %s 에서 다시 셈한 것과 어긋난다 — --write 로 다시 심는다' % pin)
            return 1
        newest = os.path.basename(G.latest_backup()[0])
        print('✓ 수업 자료 %d명 — %s 와 맞는다' % (len(packets), pin))
        if newest != pin:
            print('· 백업이 새로 왔다(%s). 수업 전에 --write 로 다시 심으면 그날 응시까지 든다.' % newest)
        return 0

    packets, bname = build()
    print('백업 %s · 학생 %d명' % (bname, len(packets)))
    print('%-14s%6s%7s%8s   %-9s %s' % ('코드', '회차', '문항', '정답률', '판정', '함정/워밍업'))
    for c, p in packets.items():
        print('%-14s%6d%7d%7.1f%%   %-9s %d줄 / %d제'
              % (c, p['attempts'], p['graded'], p['acc'], p['verdict'],
                 len(p['trap']), len(p['warmup'])))
    if '--write' in sys.argv:
        open(OUTFILE, 'w', encoding='utf-8').write(dump(packets, bname))
        print('심었다: student-packets.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

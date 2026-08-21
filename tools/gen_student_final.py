#!/usr/bin/env python3
"""학생별 파이널 시험을 짓는다 — 한 사람이 곧 한 회차다.

    final-submit.html?exam=<학생코드>

backup/*.json(가장 최근 한 장)의 누적 응시에서 학생(12자 코드)마다 오답을
모으고, weak60.html 의 배정 규칙(영역 몫 최대잔여법 · 되풀이 유형 가중 ·
교과 차례 정렬)을 그대로 옮겨 60제를 고른 뒤, 그 60제를 **진짜 회차처럼**
심는다:

    student-finals.json      id=학생코드 · group '파이널' · srcmap
    answers/<코드>.json      원본 회차 답지에서 그대로 조립 (출처 명기)

**exams.json 에는 넣지 않는다.** 이 저장소의 검사들은 「exams.json 의 모든
회차는 문제지 PDF·크롭·해설지·기준기록을 다 갖춘 공개 회차」라는 계약을
수십 곳에서 강제한다(exam-assets · wrongbook-assets 총량 자물쇠 · crop_align
· gen_sol_page · cohort_cover …). 학생별 파이널은 원본 회차의 재료를 빌려
쓰는 파생 회차라 그 계약 밖이다 — 그래서 딴 파일에 두고, 화면 셋
(final.html · final-submit.html · weak60.html)이 목록과 따로 읽어
**직링크로만** 연다. 목록·예비본·계수 검사는 exams.json 만 세므로 흔들리지
않는다.

크롭은 복사하지 않는다 — srcmap[n-1]={e,q} 가 원본 회차의 크롭
(crops/<e>/<q>.png)을 가리키고, final.html·final-submit.html 의 크롭 URL
헬퍼가 이것을 따라간다. 이름은 여기 없다 — 코드는 시트 쪽에서 소금 친
해시로 만든 것이고, 이름↔코드 표는 시트 `_이름코드` 탭에만 있다.

weak60.html 과 다른 곳 (의도한 갈림):
  · 자료원이 브라우저 명단(final:roster:*)이 아니라 backup/*.json 이다.
    선생님 브라우저가 없는 자리(CI·배포)에서도 지을 수 있어야 하기 때문.
  · 발행 기록(w60Served)을 못 보므로 전 문항이 첫 출제(원문)다.
  · 오답풀이 60 미만이면 그만큼만 싣는다 — 같은 크롭을 두 번 싣지 않는다
    (weak60 은 마지막에 원문+동형 두 갈래로 채우지만, 여기는 갈래가 하나다).

    python3 tools/gen_student_final.py            # 무엇이 달라지는지 보여만 준다
    python3 tools/gen_student_final.py --write    # 심는다
    python3 tools/gen_student_final.py --check    # 심은 것이 원본과 맞는지 잰다 (CI)
"""
import glob
import json
import math
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP = '파이널'
N_TARGET = 60
MIN_POOL = 5          # 오답이 이보다 적으면 시험지가 못 된다 — 짓지 않는다

# ── 채점 규칙 · final.html 공유 블록의 okq/allc 를 그대로 옮긴 것 ──────────
def _allc(e, q):
    if e.get('miss') and q in e['miss']:
        return True
    if e.get('voided') and q in e['voided']:
        return True
    m = (e.get('multi') or {}).get(str(q))
    if m and len(m) >= 4:
        return True
    key = e.get('key') or []
    if not key or q < 1 or q > len(key):
        return False
    k = key[q - 1]
    return k in (0, '', 'X', 'x', None)

def _acc(e, q):
    m = (e.get('multi') or {}).get(str(q))
    return m if m else [e['key'][q - 1]]

def _okq(e, q, a):
    return _allc(e, q) or a in _acc(e, q)

# ── 개념 강의 차례 · weak60.html loadLecs/LEC_ALIAS/lecFind/w60Curric 이식 ──
class _LecParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self._href = None
        self._in_t = False
        self._buf = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and 'lec' in (a.get('class') or '').split():
            self._href = a.get('href') or ''
        elif self._href is not None and tag == 'span' and 't' in (a.get('class') or '').split():
            self._in_t = True
            self._buf = ''

    def handle_data(self, data):
        if self._in_t:
            self._buf += data

    def handle_endtag(self, tag):
        if tag == 'span' and self._in_t:
            self._in_t = False
            m = re.match(r'^lec-(\d{3})', self._href or '')
            tt = self._buf.strip()
            if m and tt:
                self.out.append({'no': int(m.group(1)), 'title': tt,
                                 'key': re.sub(r'[^가-힣A-Za-z0-9]', '', tt)})
        elif tag == 'a':
            self._href = None

def load_lecs():
    p = os.path.join(ROOT, 'lecture-index.html')
    if not os.path.exists(p):
        return []
    par = _LecParser()
    par.feed(open(p, encoding='utf-8').read())
    return par.out

# weak60.html LEC_ALIAS 를 그대로 — 'pH':46+38 은 84다.
LEC_ALIAS = {
    'pH': 84,
    '반응의자발성': 72,
    'PV=nRT': 46, '이상기체': 46,
    '압력': 44,
    '분출속도': 48, '확산': 48,
    '반데르발스식': 49,
    '용해도곱상수': 74, '공통이온효과': 74,
    'ICE식': 75, '평형농도': 75,
    '초기속도법': 110, '반응차수': 110, '메커니즘': 110,
    '극성': 25, '쌍극자모멘트': 25,
    '농도환산': 54,
    '가열곡선': 70,
    '반응열': 65, '연소열': 65,
    '염의가수분해': 89,
    '원자모형': 1, '러더퍼드': 1, '수소원자': 1,
    '실험식구하기': 36, '질량백분율': 36, '원소분석장치': 36,
}

def _lcs(a, b):
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]:
                k += 1
            if k > best:
                best = k
    return best

def lec_find(lecs, *names):
    by_no = {L['no']: L for L in lecs}
    for raw in names:
        raw = str(raw or '').strip()
        no = LEC_ALIAS.get(raw) or LEC_ALIAS.get(re.sub(r'\s+', '', raw))
        if no and no in by_no:
            return by_no[no]
    words, seen = [], set()
    for raw in names:
        w = re.sub(r'[^가-힣A-Za-z0-9]', '', str(raw or ''))
        if len(w) >= 2 and w not in seen:
            seen.add(w)
            words.append(w)
    for w in words:
        best, bs = None, 0
        for L in lecs:
            sc = _lcs(w, L['key'])
            if sc > bs:
                bs, best = sc, L
        if best and bs >= 3 and bs >= 0.55 * min(len(w), len(best['key'])):
            return best
    return None

# ── 오답 모으기 · weak60.html histOf/weakScan 이식 (자료원만 backup) ────────
def latest_backup():
    fs = sorted(glob.glob(os.path.join(ROOT, 'backup', '????-??-??.json')))
    if not fs:
        raise SystemExit('backup/*.json 이 없다')
    return fs[-1], json.load(open(fs[-1], encoding='utf-8'))

def weak_scan(rows, by_title, groups=None):
    """학생 → 오답 행 목록. 회차마다 가장 최근 제출 하나만 본다.

    groups 가 있으면(student-final-groups.json) 같은 학생의 코드 여럿을
    한 사람으로 합친다 — 같은 학생이 학교 칸을 다르게 적으면 시트가 다른
    코드를 만들기 때문이다. 합칠 때도 「회차마다 가장 최근 하나」는 코드가
    아니라 **사람 기준**으로 지킨다(final.html histOf 가 이름 기준인 것과 같다)."""
    canon = {}
    if groups:
        for g in groups:
            for c in g['codes']:
                canon[c] = g['id']
    latest = {}
    for r in rows:
        e = by_title.get(r.get('exam'))
        if not e:
            continue
        a = r.get('answers') or ''
        if len(a) != e['nQ']:
            continue
        who = canon.get(r['code']) if groups else r['code']
        if groups and who is None:
            continue
        k = (who, e['id'])
        if k not in latest or r.get('saved', '') > latest[k].get('saved', ''):
            latest[k] = r
    pools = {}
    for (code, eid), r in sorted(latest.items()):
        e = by_title[r['exam']]
        astr = r.get('answers') or ''
        ts = r.get('saved') or ''
        for q in range(1, e['nQ'] + 1):
            a = int(astr[q - 1]) if astr[q - 1].isdigit() else 0
            if _okq(e, q, a):
                continue
            area = (e.get('area') or [None] * e['nQ'])[q - 1] or '기타'
            typ = (e.get('type') or [None] * e['nQ'])[q - 1] or area
            pools.setdefault(code, []).append(
                {'id': e['id'], 'q': q, 'chosen': a, 'blank': a == 0,
                 'ts': ts, 'area': area, 'type': typ})
    return pools

# ── 배정 · weak60.html w60Rep/weakAreas/w60Quota/weak60Plan 이식 ────────────
def weak_areas(rows):
    by_type = {}
    for w in rows:
        by_type.setdefault(w['type'], set()).add(w['id'])
    rep = {t: len(ids) for t, ids in by_type.items()}
    by = {}
    for w in rows:
        w = dict(w)
        w['rep'] = rep.get(w['type'], 1)
        w['wt'] = 1 + min(max(w['rep'], 1) - 1, 2)
        g = by.setdefault(w['area'], {'area': w['area'], 'n': 0, 'weight': 0, 'items': []})
        g['n'] += 1
        g['weight'] += w['wt']
        g['items'].append(w)
    out = list(by.values())
    # weak60 과 같은 차례: 되풀이 잦은 것 → 최근 것 → id → 번호.
    # 파이썬의 안정 정렬을 뒤에서부터 쌓아 같은 차례를 만든다.
    for g in out:
        g['items'].sort(key=lambda w: (w['id'], w['q']))
        g['items'].sort(key=lambda w: w['ts'], reverse=True)
        g['items'].sort(key=lambda w: -w['rep'])
    out.sort(key=lambda g: (-g['weight'], -g['n'], g['area']))
    return out

def quota_of(areas, n):
    cap = max(3, math.ceil(n / 3))
    tot = sum(g['weight'] for g in areas) or 1
    q, used, rem = {}, 0, []
    for g in areas:
        raw = n * g['weight'] / tot
        f = math.floor(raw)
        q[g['area']] = f
        used += f
        rem.append((g['area'], raw - f))
    rem.sort(key=lambda x: -x[1])
    i = 0
    while used < n and rem:
        q[rem[i % len(rem)][0]] += 1
        used += 1
        i += 1
    for g in areas:
        q[g['area']] = min(max(q[g['area']], 1), cap)
    return q

def plan(areas, n):
    """첫 출제 전제(served 없음): 몫대로 담고, 모자라면 몫을 풀고 마저 담는다."""
    quota = quota_of(areas, n)
    picks, taken, seen = [], {}, set()

    def one_pass(use_quota):
        moved = True
        while len(picks) < n and moved:
            moved = False
            for g in areas:
                if len(picks) >= n:
                    break
                if use_quota and taken.get(g['area'], 0) >= quota.get(g['area'], 0):
                    continue
                for w in g['items']:
                    k = (w['id'], w['q'])
                    if k in seen:
                        continue
                    picks.append((w, g['area']))
                    taken[g['area']] = taken.get(g['area'], 0) + 1
                    seen.add(k)
                    moved = True
                    break
    one_pass(True)
    one_pass(False)
    return picks[:n]

def curric_sort(picks, lecs, ans_all):
    out = []
    for i, (w, area) in enumerate(picks):
        a = (ans_all.get(w['id']) or {}).get(str(w['q'])) or {}
        L = lec_find(lecs, a.get('concept'), w['type'], w['area'])
        out.append((L['no'] if L else 999, i, w, L))
    out.sort(key=lambda x: (x[0], x[1]))
    return [(w, L) for _, _, w, L in out]

# ── 조립 ────────────────────────────────────────────────────────────────────
def scaled_cut(n):
    cut, prev = [0], 0
    for f in (0.07, 0.15, 0.22, 0.30):
        v = max(prev, math.ceil(n * f))
        cut.append(v)
        prev = v
    return cut

def build(write=False):
    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    by_title = {e['title']: e for e in exams}
    by_id = {e['id']: e for e in exams}
    bfile, bk = latest_backup()
    gp = os.path.join(ROOT, 'student-final-groups.json')
    groups = (json.load(open(gp, encoding='utf-8')).get('groups')
              if os.path.exists(gp) else None)
    pools = weak_scan(bk['rows'], by_title, groups)
    lecs = load_lecs()
    if not lecs:
        print('⚠ lecture-index.html 을 못 읽어 교과 차례 없이 (영역 차례로) 싣는다')

    src_ids = sorted({w['id'] for rows in pools.values() for w in rows})
    ans_all = {}
    for sid in src_ids:
        p = os.path.join(ROOT, 'answers', sid + '.json')
        ans_all[sid] = (json.load(open(p, encoding='utf-8')).get('questions')
                        if os.path.exists(p) else None) or {}

    made, skipped = [], []
    for code in sorted(pools):
        rows = pools[code]
        if len(rows) < MIN_POOL:
            skipped.append((code, len(rows)))
            continue
        areas = weak_areas(rows)
        picks = plan(areas, N_TARGET)
        ordered = curric_sort(picks, lecs, ans_all)
        nq = len(ordered)

        key, area, typ, srcmap, multi = [], [], [], [], {}
        qs = {}
        for n, (w, L) in enumerate(ordered, 1):
            e = by_id[w['id']]
            acc = _acc(e, w['q'])
            key.append(e['key'][w['q'] - 1])
            if len(acc) > 1:
                multi[str(n)] = acc
            area.append(w['area'])
            typ.append(w['type'])
            srcmap.append({'e': w['id'], 'q': w['q']})
            src_item = (ans_all.get(w['id']) or {}).get(str(w['q']))
            if src_item:
                item = dict(src_item)
                # verificationStatus 는 빼고 옮긴다 — 복사본이 검증 셈
                # (tools/verify_status.py 의 봉인)을 부풀리면 안 된다.
                item.pop('verificationStatus', None)
                item['origin'] = {'exam': w['id'], 'q': w['q']}
                item['sourceSolution'] = ((item.get('sourceSolution') or '').strip()
                                          + (' · ' if item.get('sourceSolution') else '')
                                          + f'원문 {w["id"]} {w["q"]}번')
                qs[str(n)] = item

        entry = {
            'id': code,
            'title': f'파이널 {nq}제 · {code}',
            'group': GROUP,
            'hidden': True,
            'nQ': nq,
            'mode': 'auto',
            'cut': scaled_cut(nq),
            'key': key,
            'miss': [],
            'area': area,
            'type': typ,
            'srcmap': srcmap,
        }
        if multi:
            entry['multi'] = multi
        made.append((code, entry, qs, len(rows)))

    print(f'백업 {os.path.basename(bfile)} · 학생 {len(pools)}명 · 지은 시험 {len(made)}벌'
          f' · 오답 {MIN_POOL}개 미만이라 건너뛴 학생 {len(skipped)}명')
    for code, entry, qs, pool in made:
        print(f"  {code}  오답풀 {pool:4d} → {entry['nQ']:2d}문항 · 해설 {len(qs)}")

    if not write:
        return made

    with open(os.path.join(ROOT, 'student-finals.json'), 'w', encoding='utf-8') as f:
        json.dump({'schemaVersion': 1,
                   'note': 'tools/gen_student_final.py 가 backup 응시 기록으로 지은 학생별 파이널. 손으로 고치지 않는다. exams.json 과 따로 사는 까닭은 이 파일 머리의 도구 설명에 있다.',
                   'exams': [e for _, e, _, _ in made]}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    for code, entry, qs, _ in made:
        with open(os.path.join(ROOT, 'answers', code + '.json'), 'w', encoding='utf-8') as f:
            json.dump({'schemaVersion': 1, 'examId': code, 'examTitle': entry['title'],
                       'note': 'tools/gen_student_final.py 가 원본 회차 답지에서 조립한 파생물. 손으로 고치지 않는다.',
                       'questions': qs}, f, ensure_ascii=False, indent=1)
            f.write('\n')
    print('심었다: student-finals.json · answers/<코드>.json')
    return made

# ── 검사 ────────────────────────────────────────────────────────────────────
def check():
    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    by_id = {e['id']: e for e in exams}
    sf = os.path.join(ROOT, 'student-finals.json')
    if not os.path.exists(sf):
        print('· student-finals.json 이 없다 — 지은 것이 없으니 잴 것도 없다')
        return 0
    finals = json.load(open(sf, encoding='utf-8')).get('exams', [])
    bad = []
    for e in finals:
        sid = e['id']
        sm = e.get('srcmap') or []
        if not e.get('hidden'):
            bad.append(f'{sid}: hidden 이 아니다 — 학생 목록에 노출된다')
        if len(sm) != e['nQ'] or len(e['key']) != e['nQ']:
            bad.append(f'{sid}: nQ({e["nQ"]}) 와 srcmap({len(sm)})·key({len(e["key"])}) 길이가 다르다')
            continue
        if not (isinstance(e.get('cut'), list) and len(e['cut']) == 5
                and e['cut'][0] == 0 and all(a <= b for a, b in zip(e['cut'], e['cut'][1:]))):
            bad.append(f'{sid}: cut 이 다섯 칸 단조증가가 아니다 — 성적표가 죽는다')
        ansp = os.path.join(ROOT, 'answers', sid + '.json')
        qs = json.load(open(ansp, encoding='utf-8')).get('questions', {}) if os.path.exists(ansp) else {}
        for n, m in enumerate(sm, 1):
            src = by_id.get(m['e'])
            if not src:
                bad.append(f'{sid} {n}번: 원본 회차 {m["e"]} 가 exams.json 에 없다')
                continue
            crop = os.path.join(ROOT, 'crops', m['e'], f'{m["q"]}.png')
            if not os.path.exists(crop):
                bad.append(f'{sid} {n}번: 크롭이 없다 — crops/{m["e"]}/{m["q"]}.png')
            if e['key'][n - 1] != src['key'][m['q'] - 1]:
                bad.append(f'{sid} {n}번: 정답키가 원본 {m["e"]} {m["q"]}번과 다르다')
            sacc = _acc(src, m['q'])
            eacc = (e.get('multi') or {}).get(str(n)) or [e['key'][n - 1]]
            if sorted(sacc) != sorted(eacc):
                bad.append(f'{sid} {n}번: 인정 답안이 원본과 다르다 {eacc} != {sacc}')
            it = qs.get(str(n))
            if it and it.get('origin') != {'exam': m['e'], 'q': m['q']}:
                bad.append(f'{sid} {n}번: 답지 출처 표기가 srcmap 과 다르다')
    if bad:
        print(f'✗ 학생별 파이널 {len(finals)}벌 — 어긋난 곳 {len(bad)}')
        for b in bad[:40]:
            print('  ' + b)
        return 1
    print(f'✓ 학생별 파이널 {len(finals)}벌 — srcmap·정답키·크롭·출처 전부 원본과 맞다')
    return 0

if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(check())
    build(write='--write' in sys.argv)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ledger.py — 개념 대장

왜 필요한가
-----------
지금까지 "이 테마에서 무엇을 아직 안 냈는가"를 **기억과 감사 기록에 의존**해 왔다.
164제를 한 테마에 배분하면서 소재가 겹치는지를 사람이 훑어 판단했고,
그래서 판례 ⑤(단일 지식 프레임 변주)·⑥(계산 숫자만 바꾼 복제) 같은 부채가 쌓였다.
소급 감사에서 R1 13쌍·R2 6쌍·R3 66쌍·R5 26쌍이 뒤늦게 드러난 것이 그 결과다.

대장은 그 판단을 **자료로 바꾼다.** 교재에서 뽑은 개념 하나하나에 ID를 붙이고,
어떤 문항이 그 개념을 썼는지 역으로 건다. 그러면 세 가지를 기계가 답한다.
  · 아직 안 쓴 개념이 무엇인가          → 다음 배치의 소재
  · 한 개념에 문항이 몇 개나 몰렸는가   → 판례 ⑤ 사전 차단
  · 교재의 어느 쪽이 비어 있는가        → 범위 누락 검출

개념 하나 = 문항 하나가 아니다. 한 개념에서 서로 다른 **각도**(angles)로 여러 문항이
나올 수 있고, 그것이 정당한 경우가 판례 ④(거울이나 정답 상반)다.
그래서 개념마다 각도를 미리 적어 두고, 각도 단위로 소진 여부를 본다.

스키마 (master/concepts.json)
-----------------------------
{ "T12": [ {
    "id":     "C12-001",
    "stmt":   "한 줄 진술",
    "page":   73,                     교재 쪽
    "kind":   "실험과 그 결론",        정의 / 실험과 그 결론 / 수식 / 표·그림 자료 / 한계·경계
    "prereq": ["..."],
    "values": "교재가 명시한 수치·상수 (없으면 빈 문자열)",
    "angles": [ {"a": "물음의 각도", "by": ["M01807"]}, ... ],
    "note":   ""
} ] }

사용
----
  python3 master/ledger.py import T12 <파일.json>   개념 목록 등록 (기존과 병합, id 충돌 시 갱신)
  python3 master/ledger.py list T12 [--open]        전체 / 미소진 각도만
  python3 master/ledger.py use C12-003 0 M01817     개념·각도번호에 문항 연결
  python3 master/ledger.py stats T12                소진율·쪽 커버리지·개념당 문항 쏠림
  python3 master/ledger.py check                    은행과 대장의 정합성 (유령 ID·미등록 문항)
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
LEDGER = os.path.join(HERE, 'concepts.json')

KINDS = ('정의', '실험과 그 결론', '수식', '표·그림 자료', '한계·경계')


def load():
    if not os.path.exists(LEDGER):
        return {}
    return json.load(open(LEDGER, encoding='utf-8'))


def save(d):
    json.dump(d, open(LEDGER, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def cmd_import(theme_key, path):
    d = load()
    new = json.load(open(path, encoding='utf-8'))
    cur = {c['id']: c for c in d.get(theme_key, [])}
    added = updated = 0
    for c in new:
        for f in ('id', 'stmt', 'page', 'kind', 'angles'):
            assert f in c, f"{c.get('id','?')}: 필수 항목 {f} 없음"
        assert c['kind'] in KINDS, f"{c['id']}: 유형 '{c['kind']}' 이 허용 집합 밖 {KINDS}"
        c.setdefault('prereq', []); c.setdefault('values', ''); c.setdefault('note', '')
        c['angles'] = [a if isinstance(a, dict) else {'a': a, 'by': []} for a in c['angles']]
        for a in c['angles']:
            a.setdefault('by', [])
        if c['id'] in cur:
            # 이미 연결된 문항은 보존한다 — 재판독으로 진술이 다듬어져도 이력은 남긴다
            old = {a['a']: a['by'] for a in cur[c['id']]['angles']}
            for a in c['angles']:
                a['by'] = a['by'] or old.get(a['a'], [])
            updated += 1
        else:
            added += 1
        cur[c['id']] = c
    d[theme_key] = sorted(cur.values(), key=lambda x: (x['page'], x['id']))
    save(d)
    print(f"✅ {theme_key}: 신규 {added} · 갱신 {updated} · 누적 {len(d[theme_key])}개념")


def cmd_list(theme_key, only_open=False):
    d = load().get(theme_key, [])
    if not d:
        print(f"⛔ {theme_key} 개념 없음"); return
    page = None
    for c in d:
        rows = [(i, a) for i, a in enumerate(c['angles']) if not (only_open and a['by'])]
        if only_open and not rows:
            continue
        if c['page'] != page:
            page = c['page']; print(f"\n── {page}쪽 ──")
        print(f"{c['id']} [{c['kind']}] {c['stmt']}")
        if c['values']:
            print(f"    수치: {c['values']}")
        for i, a in c['angles']:
            mark = '·'.join(a['by']) if a['by'] else '○ 미소진'
            print(f"    ({i}) {a['a']}   {mark}")


def cmd_use(cid, ai, *items):
    d = load()
    for key, lst in d.items():
        for c in lst:
            if c['id'] == cid:
                ai = int(ai)
                assert 0 <= ai < len(c['angles']), f"{cid}: 각도 번호 {ai} 없음 (0~{len(c['angles'])-1})"
                a = c['angles'][ai]
                for it in items:
                    if it not in a['by']:
                        a['by'].append(it)
                save(d)
                print(f"✅ {cid}({ai}) ← {'·'.join(a['by'])}  «{a['a']}»")
                return
    print(f"⛔ 개념 {cid} 없음")


def cmd_stats(theme_key):
    d = load().get(theme_key, [])
    if not d:
        print(f"⛔ {theme_key} 개념 없음"); return
    ang = [(c, a) for c in d for a in c['angles']]
    done = [x for x in ang if x[1]['by']]
    print(f"═══ 개념 대장 · {theme_key} ═══")
    print(f"개념 {len(d)}개 · 각도 {len(ang)}개 · 소진 {len(done)}개 ({len(done)/len(ang):.0%})")
    kc = Counter(c['kind'] for c in d)
    print("유형 " + " · ".join(f"{k} {kc.get(k,0)}" for k in KINDS))
    pc = Counter(c['page'] for c in d)
    print("쪽별 개념 " + " · ".join(f"{p}쪽:{n}" for p, n in sorted(pc.items())))
    load_per = Counter()
    for c in d:
        load_per[c['id']] = sum(len(a['by']) for a in c['angles'])
    hot = [(k, v) for k, v in load_per.most_common() if v >= 3]
    if hot:
        print("\n★ 문항이 몰린 개념 (판례 ⑤ 점검 대상)")
        for k, v in hot:
            c = [x for x in d if x['id'] == k][0]
            print(f"   {k} {v}제  {c['stmt'][:40]}")
    empty = [c['id'] for c in d if load_per[c['id']] == 0]
    print(f"\n미착수 개념 {len(empty)}개" + (f": {' '.join(empty[:12])}" if empty else ""))


def cmd_check():
    d = load()
    bank = json.load(open(BANK, encoding='utf-8'))
    ids = {x['id'] for x in bank}
    linked = set()
    ghost = []
    for key, lst in d.items():
        for c in lst:
            for a in c['angles']:
                for it in a['by']:
                    linked.add(it)
                    if it not in ids:
                        ghost.append((c['id'], it))
    print(f"대장에 연결된 문항 {len(linked)}제")
    if ghost:
        print(f"⛔ 은행에 없는 문항 ID {len(ghost)}건: {ghost[:10]}")
    # 대장 상위 키 = 은행의 theme 이름. 그 테마 문항 중 대장에 안 걸린 것을 찾는다
    for key in d:
        pool = [x for x in bank if x.get('theme') == key]
        if not pool:
            print(f"⚠ 대장 키 '{key}' 에 해당하는 은행 테마가 없음 — 이름 불일치 확인")
            continue
        miss = [x['id'] for x in pool if x['id'] not in linked]
        if miss:
            print(f"⚠ {key}: 대장에 연결되지 않은 문항 {len(miss)}/{len(pool)}제 — {' '.join(miss[:12])}")
        else:
            print(f"✅ {key}: {len(pool)}제 전부 대장에 연결됨")
    if not ghost:
        print("✅ 유령 ID 없음")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    c = sys.argv[1]
    if c == 'import':
        cmd_import(sys.argv[2], sys.argv[3])
    elif c == 'list':
        cmd_list(sys.argv[2], '--open' in sys.argv)
    elif c == 'use':
        cmd_use(sys.argv[2], sys.argv[3], *sys.argv[4:])
    elif c == 'stats':
        cmd_stats(sys.argv[2])
    elif c == 'check':
        cmd_check()
    else:
        print(__doc__)

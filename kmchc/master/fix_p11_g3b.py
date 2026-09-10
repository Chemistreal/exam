#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_p11_g3b.py — P11(M01743~M01752)을 새 규칙 G3b/G3c 에 맞춘다.

배경: G3(정답 유일최장 금지)를 '오답 하나만 정답보다 길게' 늘려 해소해 온 관행이
      정답을 길이 2위로 몰아 왔다(최근 100제 46%, T11 45%). P11 도 7/10 이 2위였다.
      규칙을 새로 만든 이상 내 배치부터 맞춘다.

방침: 패딩을 더 얹지 않고 **보기 길이를 나란히** 맞춘다(짧은 보기를 올리고 늘려 둔 것을 줄임).
      뜻·정오답 관계는 그대로 두고 표현만 다듬는다. 교체 문자열은 choices 와 solution 에
      함께 반영해 해설 라벨이 어긋나지 않게 한다.
사용: python3 master/fix_p11_g3b.py          (검증만)
      python3 master/fix_p11_g3b.py --apply  (반영)
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from batch_template import spread, g3b_applies, len_rank

BANK = os.path.join(HERE, 'master_bank.json')

# (문항ID, 기존 보기, 새 보기) — 뜻은 유지, 길이만 나란히
EDITS = [
    # ── M01748 정답 48자 · 나머지를 44~48자로(정답은 동률 최장이라 G3 통과) ──
    ("M01748",
     "β선은 전기장에서 어느 쪽으로도 휘지 않는 전자기파이다",
     "β선은 전하를 띠지 않아 전기장 속에서 어느 쪽으로도 휘지 않는 전자기파이다"),
    ("M01748",
     "γ선은 (−)전하를 띤 전자의 흐름이며 세 방사선 가운데 투과력이 가장 약해 종이 한 장에도 막힌다",
     "γ선은 (−)전하를 띤 전자의 흐름으로 세 방사선 가운데 투과력이 가장 약해 잘 막힌다"),
    ("M01748",
     "세 방사선 가운데 질량이 가장 큰 것은 γ선이다",
     "세 방사선 가운데 질량이 가장 큰 것은 γ선이고 α선은 질량을 가지지 않는다"),

    # ── M01746 정답 33자 · 오답 하나를 올려 길이순위를 3위로(순위 편중 해소) ──
    ("M01746",
     "양성자 수가 20을 넘는 원자핵은 안정하게 존재할 수 없다",
     "양성자 수가 20을 넘는 원자핵은 무거워서 안정하게 존재할 수 없다"),

    # ── M01749 정답 39자에 맞춰 34~42자로 ──
    ("M01749",
     "전리 작용은 α선이 가장 강하고 γ선이 가장 약하다",
     "전리 작용은 α선이 가장 강하고 γ선이 가장 약해 투과력과 반대이다"),
    ("M01749",
     "전기장 속에서 γ선은 전하를 띠지 않으므로 어느 쪽으로도 휘지 않고 곧게 나아간다",
     "전기장 속에서 γ선은 전하가 없어 어느 쪽으로도 휘지 않고 곧게 나아간다"),
    ("M01749",
     "β선은 (−)전하를 띠고, α선은 (+)전하를 띤다",
     "β선은 (−)전하를 띠고 α선은 (+)전하를 띠어 서로 반대쪽으로 휜다"),

    # ── M01750 정답을 조금 줄이고 나머지를 올려 44~52자로 ──
    ("M01750",
     "어느 원자가 언제 붕괴할지는 알 수 없지만, 아주 많은 원자를 모으면 반감기마다 절반씩 줄어든다",
     "어느 원자가 언제 붕괴할지는 알 수 없지만, 많은 원자를 모으면 반감기마다 절반씩 줄어든다"),
    ("M01750",
     "원자 하나만 따로 지켜보아도 반감기가 지나는 바로 그 순간에 그 원자가 어김없이 붕괴하는 것을 볼 수 있다",
     "원자 하나만 따로 지켜보아도 반감기가 지나는 바로 그 순간에 그 원자가 어김없이 붕괴하게 된다"),
    ("M01750",
     "붕괴할 원자를 하나씩 순서대로 골라 차례차례 붕괴시킨다",
     "붕괴할 원자를 하나씩 순서대로 골라 차례차례 붕괴시키는 정해진 규칙이 따로 있다"),
    ("M01750",
     "원자의 개수가 많을수록 반감기가 점점 길어진다",
     "모아 둔 원자의 개수가 많을수록 반감기가 점점 길어져 붕괴가 더 느리게 진행된다"),

    # ── M01751 정답 27자에 맞춰 24~28자로 ──
    ("M01751",
     "감마 붕괴로 남는 에너지만 내보낸다",
     "감마 붕괴로 남아 있는 에너지만 밖으로 내보낸다"),

    # ── M01752 정답 31자 · 동률 최단으로 두어 길이순위를 4위로(순위 편중 해소) ──
    ("M01752",
     "감마선의 강한 전리 작용 — 두꺼운 종양을 몸 밖에서 치료",
     "감마선의 강한 전리 작용 — 두꺼운 종양을 밖에서 치료"),
    ("M01752",
     "알파선의 큰 투과력 — 연기 감지기 속 공기를 이온화",
     "알파선의 큰 투과력 — 연기 감지기 속의 공기를 이온화하여 검출"),
    ("M01752",
     "베타선의 무거운 질량 — 유물의 나이를 재는 연대 측정",
     "베타선의 무거운 질량 — 오래된 유물의 나이를 재는 연대 측정"),
]


def apply_edits(bank):
    idx = {x['id']: x for x in bank}
    for fid, old, new in EDITS:
        it = idx[fid]
        assert old in it['choices'], f"{fid}: 기존 보기를 찾지 못함 → {old!r}"
        assert new not in it['choices'], f"{fid}: 새 보기가 이미 존재 → {new!r}"
        it['choices'][it['choices'].index(old)] = new
        assert old in it['solution'], f"{fid}: 해설에서 기존 보기를 찾지 못함"
        it['solution'] = it['solution'].replace(old, new)
    return bank


def report(bank):
    p11 = [x for x in bank if 'M01743' <= x['id'] <= 'M01752']
    bad = []
    for x in p11:
        sp = spread(x['choices'])
        viol = g3b_applies(x['choices']) and sp > 0.25
        if viol:
            bad.append(x['id'])
        print(f"  {x['id']} 순위{len_rank(x)} 산포{sp:.2f}{' ✗G3b' if viol else ''} "
              f"길이{[len(c) for c in x['choices']]}")
    rr = Counter(len_rank(x) for x in p11)
    print(f"  길이순위 분포 {dict(sorted(rr.items()))} · 최빈 {max(rr.values())}/10 "
          f"{'✗G3c' if max(rr.values()) > 4 else '✓'}")
    print(f"  G3b 위반 {len(bad)}건 {bad}")
    return not bad and max(rr.values()) <= 4


if __name__ == '__main__':
    bank = json.load(open(BANK, encoding='utf-8'))
    print("── 수정 전 ──"); report(bank)
    bank = apply_edits(bank)
    print("── 수정 후 ──"); ok = report(bank)
    if '--apply' in sys.argv:
        assert ok, "⛔ 아직 규칙 미충족 — 문구를 더 다듬을 것"
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만 수행. 반영하려면 --apply")

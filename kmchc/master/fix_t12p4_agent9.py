# -*- coding: utf-8 -*-
"""T12 P4 · 에이전트 9차 순회 조치 — ★정지 조건에 처음 닿은 회차★

  · solver      정답 10/10 '확실' · 자족성 10/10 '충분' · 세트 누출 0건.
                "심각한 것은 없고 사소한 것만 있습니다."
  · defender    정답 키 10/10 참 · 독립 진술로 참인 오답 0 · ★조치 불필요★ (7·8·9차 3연속 0건)
  · factchecker ★✗ 0건★ (P4 에서 처음) · △ 4건, 전부 '감점 사안 아님'으로 스스로 분류

★정지 조건 충족★ — 착수 문서에 적어 둔 대로 solver·defender·factchecker 셋이 모두 조치 0건이다.
  student-sim 은 정지 조건에 넣지 않는다(3차에 목표치 달성 후 제안이 끝없이 이어졌다).

이 스크립트가 하는 일은 결함 조치가 아니라 ★마감 다듬기★다.
남은 △ 가운데 '되풀이 지적된 것'과 '위험이 0 인 것'만 반영하고, 나머지는 기록만 한다.

【반영】
  (1) M01837 자가진단 "톰슨이 세운 그 대목"
      본문은 중성을 톰슨이 *세운* 것이 아니라 *받아들인* 사실로 서술한다
      ("정작 원자 덩어리는 전기를 띠지 않아. 그러니 … (+)가 어딘가 있어야 했고").
      ★8차의 ✗ 두 건이 모두 '자가진단이 본문과 어긋남'이었다★ — 같은 자리를 다시 맞춘다.
  (2) M01838 발문에 '상댓값' 명시 — 7·8·9차 세 회차 연속 같은 방향 지적.
      ★한 방향으로 두 번 이상 눌리면 회차 간 반전이 아니라 미조치 결함이다★(8차에 세운 규칙).
  (3) M01840 "수소 방전관을 프리즘에 통과시키면" — 통과시키는 것은 관이 아니라 빛이다.
      뜻에 영향이 없고 위험이 0 인 표현 교정.
  (4) M01844 K=0 오해 서술에 한 마디 — 그 오해를 끝까지 밀면 도착 준위도 밀려
      선지에 없는 조합이 된다. 지금 문면은 '출발 껍질'로 좁혀 두었으나
      학생이 '이 오해는 출발 쪽에만 영향을 준다'로 일반화할 여지가 있다.

【기록만 — 조치하지 않음】
  · M01837 발문 범위 : factchecker 가 "발문이 '줄곧 유지된 것'을 묻는 형태라면 톰슨~러더퍼드로
    좁혀야 한다"고 조건부로 적었다. 실제 발문은 "앞선 모형이 말한 것 **가운데**"라 '어느 하나'로
    읽힌다(defender 7차가 같은 판단). 그리고 좁히는 것은 ★6차에 넓힌 것을 되돌리는 일★이라
    ④(불가분성)가 다시 판정 대상 밖으로 나간다. 조건이 성립하지 않으므로 손대지 않는다.
  · M01841 "원자들이 모두 같은 파장을 내놓는다" : 실제 방출선은 유한한 폭을 갖는다.
    factchecker 스스로 '감점 사안 아님'. 이 자리는 ②의 뜻을 떠받치는 문장이고
    3·5·7차에 걸쳐 문면이 오간 반전 구역이라, 첫 지적만으로는 건드리지 않는다.
  · M01842 ① 이 죽은 선지가 됨 : 8차에 발문에서 '0'을 뺀 결과 유인력을 잃었다.
    defender 가 "타당도가 아닌 선지 효율 문제이므로 F2 관점에서 개입할 이유가 없다"고 닫았다.
    ★중재 원칙(거짓+죽은 선지 > 참+매력적)에 따라 설계 부채로 적고 넘어간다.★
"""
import json, sys, os

BANK = os.path.join(os.path.dirname(__file__), 'master_bank.json')

STEM_SET = {
    'M01838': ("같은 전기장에 대전 입자를 통과시키면 진로가 휘어진다. "
               "휘는 정도는 전하량에 비례하고 질량에 반비례한다. "
               "전하량과 질량을 상댓값으로 나타내면 갑은 전하량 1·질량 1, "
               "을은 전하량 3·질량 2, 병은 전하량 2·질량 4 이다. "
               "휘는 정도가 큰 것부터 늘어놓은 것은?"),
}

SOL_REPL = [
    ('M01837',
     "자가진단: 넷 가운데 살아남은 것은 원자의 중성 — 톰슨이 세운 그 대목을 러더퍼드가 그대로 두었다.",
     "자가진단: 넷 가운데 살아남은 것은 원자의 중성 — 톰슨 모형이 전제로 받아들인 그 대목을 러더퍼드가 그대로 두었다."),
    ('M01840',
     "그런데 실제로 수소 방전관을 프리즘에 통과시키면",
     "그런데 실제로 수소 방전관에서 나온 빛을 프리즘에 통과시키면"),
    ('M01844',
     "셋째 걸음에서 K 를 n=0 으로 세어 출발 껍질이 한 칸 밀려(그러면 ③ 쪽으로 가지).",
     "셋째 걸음에서 K 를 n=0 으로 세어 출발 껍질이 한 칸 밀려(그러면 ③ 쪽으로 가지). "
     "그 오해를 도착 쪽까지 밀면 L 이 아니라 M 이 되어 아예 선지에 없는 짝이 나오지."),
]

WATCH_ADD = {
    'M01837': ("◇마감 기록(9차)◇ 자가진단을 '톰슨이 세운 그 대목'으로 되돌리지 말 것 — "
               "본문은 중성을 톰슨이 세운 것이 아니라 받아들인 사실로 서술한다. / "
               "◇발문 범위 확인(9차)◇ 발문을 '톰슨 모형에서 러더퍼드 모형으로'로 좁히라는 조건부 제안이 있었으나, "
               "실제 발문은 '앞선 모형이 말한 것 가운데'라 '어느 하나'로 읽히므로 조건이 성립하지 않는다. "
               "좁히면 6차에 넓힌 것을 되돌리는 일이 되어 ④가 다시 판정 대상 밖으로 나간다."),
    'M01841': ("◇기록만(9차)◇ ② 반박의 '원자들이 모두 같은 파장을 내놓는다'는 실제로는 선폭이 유한하다는 점에서 "
               "엄밀하지 않다(factchecker 스스로 '감점 사안 아님'). 이 자리는 3·5·7차에 문면이 오간 반전 구역이라 "
               "첫 지적만으로는 건드리지 않는다. 다시 지적되면 '거의 같은 파장'으로 고칠 것."),
    'M01842': ("◇설계 부채(9차)◇ 8차에 발문에서 '0'을 빼면서 ①('0 은 표에 적을 수 없는 값')이 유인력을 잃어 "
               "사실상 죽은 선지가 됐다. defender 는 '타당도가 아닌 선지 효율 문제이므로 F2 관점에서 개입할 이유가 없다'고 닫았다. "
               "★중재 원칙 — 거짓+죽은 선지는 참+매력적보다 낫다.★ 되살리려고 발문에 '0'을 되돌리지 말 것."),
    'M01838': ("◇마감 기록(9차)◇ 발문에서 '상댓값'을 빼지 말 것 — 7·8·9차에 세 회차 연속 지적됐다. "
               "★한 방향으로 두 번 이상 눌린 것은 회차 간 반전이 아니라 미조치 결함이다.★"),
}

STALE = [
    ('M01837', '톰슨이 세운 그 대목'),
    ('M01840', '수소 방전관을 프리즘에'),
]


def spread(ch):
    L = sorted(len(str(x)) for x in ch)
    return (L[3] - L[0]) / ((L[1] + L[2]) / 2) if L[1] + L[2] else 0.0


def len_rank(it):
    L = [len(str(x)) for x in it['choices']]
    order = sorted(range(4), key=lambda i: (-L[i], i))
    return order.index(it['answer']) + 1


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    items = bank if isinstance(bank, list) else bank['items']
    idx = {x['id']: x for x in items}
    n = 0

    for fid, st in STEM_SET.items():
        assert idx[fid]['stem'] != st
        idx[fid]['stem'] = st; n += 1
    for fid, old, new in SOL_REPL:
        s = idx[fid]['solution']
        assert old in s, f"{fid} 원문 없음: {old[:44]}"
        idx[fid]['solution'] = s.replace(old, new); n += 1
    for fid, add in WATCH_ADD.items():
        v = idx[fid].setdefault('verified', {})
        v['watch'] = (v.get('watch', '') + ' / ' + add).strip(' /'); n += 1

    print(f"조치 {n}곳\n")

    bad = []
    for fid, phrase in STALE:
        if phrase in idx[fid]['solution']:
            print(f"⛔ STALE {fid} 해설에 옛 문구가 남았다: '{phrase}'"); bad.append('STALE')

    ranks = {}
    for i in range(1837, 1847):
        fid = f'M0{i}'
        it = idx[fid]
        L = [len(str(x)) for x in it['choices']]
        r = len_rank(it); sp = spread(it['choices']); sol = it['solution']
        ranks[r] = ranks.get(r, 0) + 1
        print(f"{fid} {it['track']} 답{'①②③④'[it['answer']]} 길이{L} 순위{r} 산포{sp:.2f} 해설{len(sol)}자")
        if sp > 0.25 and sorted(L)[1] >= 8:
            print(f"  ⛔ G3b 산포 {sp:.2f}"); bad.append('G3b')
        if L[it['answer']] == max(L) and L.count(max(L)) == 1:
            print("  ⛔ G3 정답=유일 최장"); bad.append('G3')
        if L[it['answer']] == min(L) and L.count(min(L)) == 1:
            print("  ⛔ G3 정답=유일 최단"); bad.append('G3')
        if len(sol) < 300:
            print("  ⛔ G9 해설 300자 미만"); bad.append('G9')
        if '**' in sol or '**' in it['stem']:
            print("  ⛔ G10 마크다운 강조"); bad.append('G10')
        for d in it['distractors']:
            mark = '①②③④'[d['opt']]
            if mark not in sol:
                print(f"  ⛔ G9 오답 {mark} 미언급"); bad.append('G9')

    pos = {}
    for i in range(1837, 1847):
        a = idx[f'M0{i}']['answer']; pos[a] = pos.get(a, 0) + 1
    print("\n위치 " + ' '.join(f"{'①②③④'[k]}{pos.get(k,0)}" for k in range(4)) +
          f" · 길이순위 {dict(sorted(ranks.items()))}")
    for r, c in ranks.items():
        if c > 4:
            print(f"  ⛔ G3c 순위 {r} 가 {c}/10"); bad.append('G3c')

    if bad:
        print("\n⛔ 위반 " + ', '.join(sorted(set(bad)))); sys.exit(1)
    print("✅ 규칙 위반 없음")

    if '--apply' in sys.argv:
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만. 반영하려면 --apply")


if __name__ == '__main__':
    main()

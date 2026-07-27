#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_t12p3_agent5.py — T12 P3 층5 에이전트 **5차(마감) 패스**

★★★수렴했다★★★ 다섯 회차 만에 처음으로 세 검증자 모두 **조치 필요 0건**을 냈다.
  solver      정답 10/10 확실 · **세트 누출 0건**(전수 대조) · 답을 흔드는 새 결함 없음
  defender    정답 키 10/10 정확 · **F2 차단이 필요한 오답 없음** · 제2정답 없음
  factchecker **✗ 0건** · 자가진단↔본문 10편 전수 대조 모순 없음
남은 것은 전부 문구 △ 뿐이라, 구조는 건드리지 않고 표현만 다듬어 마감한다.

★수렴의 근거를 남긴다★ 회차별 '조치가 필요한 지적'의 수:
  1차 45 → 2차 35 → 3차 35 → 4차 15 → **5차 0(문구 △ 5건만)**
그리고 상위 변별(심화 7제 C=D): 7/7 → 7/7 → 5/7 → 2/7.
★언제 멈추는가★ — **세 기술 검증자(solver·defender·factchecker)가 모두 조치 0건을 낼 때.**
student-sim 의 매력도 제안은 끝없이 나올 수 있으므로 정지 조건에 넣지 않는다.
그것을 정지 조건에 넣으면 죽은 선지를 쫓다 F2 를 새로 만든다(2·3차에서 실제로 그랬다).

────────────────────────────────────────────────────────────────────────────
[A] 문구 △ — factchecker
  A1 M01829 ③ 반박 "그만큼 큰 에너지라 몸을 뚫고 지나가지" — 투과력을 에너지로 환원했다.
     투과는 에너지가 아니라 물질과의 상호작용(흡수)이 작기 때문이고, 반례가 바로 옆 단원에
     있다 — **알파 입자는 X선 광자보다 에너지가 훨씬 커도 종이 한 장에 막힌다.**
     학생이 '에너지가 크다 = 잘 뚫는다'로 일반화하기 쉽다.
  A2 M01833 본문 "알갱이 하나가 전자 하나를 때려 내보내니" — 광자 1개 ↔ 전자 1개를 단정했다.
     실제 양자 수율은 1보다 훨씬 작고, 결론(정비례해 두 배)은 '수율이 일정하다'에서 나온다.
     결론은 옳으므로 오류는 아니지만 단정만 덜어 낸다.
  A3 단위 표기(M01832·M01834 공통) — "빛 알갱이 하나의 에너지"와 kJ/mol 이 한 문장에 섞였다.
     이 단원에서 광자 1개(J)와 광자 1 mol(kJ/mol)을 구분 못 하는 학생이 많다. 한 번 못 박는다.
     ※ 4차에서 M01832 **stem** 의 같은 혼동을 고쳤는데, 해설 쪽에 같은 표현이 남아 있었다.
  A4 M01836 "가시광선의 파장이 수백 나노미터라 그보다 작은 것은 분간하지 못하거든" —
     회절 한계는 대략 λ/2 수준이라 '파장보다 작은 것은 전부 못 본다'는 단정이 과하다.

[S] 문체·정합 — solver
  S1 M01833 정답 ① 은 "전자 하나의 에너지"인데 오답 ③ 만 "**가장 빠른** 전자의 속력"으로
     한정어가 붙어 있었다. 4차 수정이 만든 **문체 비대칭**이고, 꼼꼼한 학생이 정답 쪽을
     의심할 여지를 준다. → ③ 도 "전자 하나의 속력"으로 맞춘다.
     (교재 C12-040 의 표현이 '평균 운동에너지'이므로 낱개 기준 서술이 이 단원의 어법이다.)
  S2 M01833 ④ "전자 수는 두 배가 되고 **안 나오던 금속에서도** 나온다" — 한 문장 안에서
     대상 금속이 바뀐다(0 의 두 배는 0). → 주어를 바꾸지 않는 "세기만 올려도 문턱을 넘는다"로.

  ★비채택 기록★
   · M01836 ③ 이 정답과 앞절을 공유한다(defender 경미) — 뒷절이 "**빛의** 파장"이라 명백히
     거짓이고, defender 스스로 "결정적 변호는 못 된다"로 닫았다. 유지.
   · M01827 ④ 가 정답과 뒷절을 공유한다(defender 경미) — defender 가 "유지. 변별도는 양(+)일
     것"으로 닫았다. 유지.
   · M01831 stem '오르내린다'를 '전이한다'로(defender 경미) — 발문이 "서로 다른 것이"로
     이미 막고 있고, '오르내린다'는 이 은행의 구어체 어법이다. 유지.
   · M01829 ② 가 외부 자기장을 전제한다(defender) — "라디오파–핵스핀"은 교재 대응표
     C12-030 의 표준 짝이고 defender 자신이 "거의 무시 가능"으로 닫았다. 유지.

★후속 배치 금지 사항(solver 5차)★
  M01829 에 "마이크로파–분자 회전" 선지를 넣는 순간 M01832 가 계산 없이 풀린다.
  이 배치가 은행에 남아 있는 한 그 방향의 손질은 금지다. watch 에 박아 둔다.

사용: python3 master/fix_t12p3_agent5.py [--apply]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
CIR = '①②③④'

CH_REPL = [
 ('M01833', 2, "튀어나오는 전자 수는 두 배가 되고 가장 빠른 전자의 속력도 두 배가 된다",
              "튀어나오는 전자 수는 두 배가 되고 전자 하나의 속력도 두 배가 된다"),
 ('M01833', 3, "튀어나오는 전자 수는 두 배가 되고 안 나오던 금속에서도 나온다",
              "튀어나오는 전자 수는 두 배가 되고 세기만 올려도 문턱을 넘는다"),
]

SOL_REPL = [
 # [A1]
 ('M01829',
  "③ X선은 원자에서 안쪽 전자를 떼어낸다: 바르게 짝지어졌어 — 그만큼 큰 에너지라 몸을 뚫고 지나가지.",
  "③ X선은 원자에서 안쪽 전자를 떼어낸다: 바르게 짝지어졌어 — 안쪽 껍질의 전자까지 떼어낼 만큼 큰 에너지야."),
 # [A3] M01832
 ('M01832',
  "빛 알갱이 하나의 에너지는 파장에 반비례해.",
  "빛 알갱이의 에너지는 파장에 반비례해(여기서는 모두 1 mol 기준으로 견준다)."),
 # [A2][S1][S2] M01833
 ('M01833',
  "알갱이 하나가 전자 하나를 때려 내보내니, 날아드는 알갱이가 두 배면 튀어나오는 전자의 수도 "
  "두 배가 돼.",
  "알갱이 하나가 전자 하나를 때려 내보낼 수 있으니, 날아드는 알갱이가 두 배면 튀어나오는 "
  "전자의 수도 두 배가 돼."),
 ('M01833',
  "③ 튀어나오는 전자 수는 두 배가 되고 가장 빠른 전자의 속력도 두 배가 된다: 세게 쬐면 더 세게 "
  "튀어나올 것 같지만, 전자 하나가 받아 가는 에너지가 그대로니 속력도 그대로야. ②와 견주어 "
  "보면 재미있어 — 에너지가 두 배라도 속력은 두 배가 아니라 √2 배거든. 둘 다 틀린 말이지.\n"
  "④ 튀어나오는 전자 수는 두 배가 되고 안 나오던 금속에서도 나온다: 광전효과에서 가장 흔한 "
  "오해가 이거야. 문턱을 넘지 못하는 색이면 아무리 세게 쬐어도 전자는 하나도 안 나와. "
  "알갱이를 더 많이 보낸다고 알갱이 하나가 커지지는 않으니까.",
  "③ 튀어나오는 전자 수는 두 배가 되고 전자 하나의 속력도 두 배가 된다: 세게 쬐면 더 세게 "
  "튀어나올 것 같지만, 전자 하나가 받아 가는 에너지가 그대로니 속력도 그대로야. ②와 견주어 "
  "보면 재미있어 — 에너지가 두 배라도 속력은 두 배가 아니라 √2 배거든. 둘 다 틀린 말이지.\n"
  "④ 튀어나오는 전자 수는 두 배가 되고 세기만 올려도 문턱을 넘는다: 광전효과에서 가장 흔한 "
  "오해가 이거야. 문턱을 넘지 못하는 색이면 아무리 세게 쬐어도 전자는 하나도 안 나와. "
  "알갱이를 더 많이 보낸다고 알갱이 하나가 커지지는 않으니까."),
 # [A3] M01834
 ('M01834',
  "빛 알갱이 하나의 에너지는 파장에 반비례해.",
  "빛 알갱이의 에너지는 파장에 반비례해 — 낱개끼리 견줄 때도, 1 mol 씩 견줄 때도 마찬가지야."),
 # [A4] M01836
 ('M01836',
  "가시광선의 파장이 수백 나노미터라 그보다 작은 것은 분간하지 못하거든.",
  "가시광선의 파장이 수백 나노미터라 그 절반쯤보다 작은 것은 분간하지 못하거든."),
]

DIST_SET = [
 ('M01833', 2, '세기를 올리면 더 세게 튀어나온다고 여김 — 최대 운동에너지는 불변', 'causal'),
 ('M01833', 3, '세기를 올리면 문턱을 넘을 수 있다고 여김 — 문턱은 색이 정함', 'causal'),
]

WATCH_ADD = {
 'M01829': " / ★후속 배치 금지(5차 solver)★ 이 문항에 '마이크로파–분자 회전' 선지를 넣으면 "
           "그 순간 M01832 가 계산 없이 풀린다. M01832 가 은행에 있는 한 금지",
 'M01833': " / ★문체 대칭★ 네 선지의 한정어를 맞출 것. ③만 '가장 빠른 전자'로 쓰면 정답 ①의 "
           "'전자 하나'가 덜 정밀해 보여 꼼꼼한 학생이 정답을 의심한다(4차가 만든 비대칭)",
}
VERIFIED = {"layer5": "F1~F7 통과 · 에이전트 5차 순회에서 수렴(세 기술 검증자 조치 0건)",
            "at": "T12 P3",
            "by": "독립 에이전트 4종 5회(solver·defender·factchecker·student-sim)"}


def apply(bank):
    idx = {x['id']: x for x in bank}
    n = 0
    for fid, i, old, new in CH_REPL:
        x = idx[fid]
        assert x['choices'][i] == old, f"{fid} {CIR[i]} 불일치: {x['choices'][i]}"
        x['choices'][i] = new
        for d in x['distractors']:
            if d['opt'] == i and 'text' in d:
                d['text'] = new
        n += 1
    for fid, old, new in SOL_REPL:
        x = idx[fid]
        assert old in x['solution'], f"{fid} 해설 불일치: {old[:44]}"
        x['solution'] = x['solution'].replace(old, new, 1); n += 1
    for fid, opt, err, typ in DIST_SET:
        hit = [d for d in idx[fid]['distractors'] if d['opt'] == opt]
        assert hit, f"{fid} opt{opt} 없음"
        hit[0]['error'] = err; hit[0]['type'] = typ; n += 1
    for fid in [f"M0{i}" for i in range(1827, 1837)]:
        prev = idx[fid].get('verified', {}).get('watch', '')
        idx[fid]['verified'] = dict(VERIFIED)
        w = prev + WATCH_ADD.get(fid, '')
        if w:
            idx[fid]['verified']['watch'] = w
    return bank, n


if __name__ == '__main__':
    bank = json.load(open(BANK, encoding='utf-8'))
    bank, n = apply(bank)
    sys.path.insert(0, HERE)
    from batch_template import len_rank, spread, g3b_applies
    idx = {x['id']: x for x in bank}
    print(f"조치 {n}곳\n")
    ranks, bad, pos, trk = {}, [], {}, {}
    for fid in [f"M0{i}" for i in range(1827, 1837)]:
        x = idx[fid]
        L = [len(c) for c in x['choices']]
        r = len_rank(x); sp = spread(x['choices'])
        ranks[r] = ranks.get(r, 0) + 1
        pos[x['answer']] = pos.get(x['answer'], 0) + 1
        trk[x['track']] = trk.get(x['track'], 0) + 1
        flag = ''
        if g3b_applies(x['choices']) and sp > 0.25: flag += ' ⛔G3b'; bad.append(fid)
        if L[x['answer']] == max(L) and L.count(max(L)) == 1: flag += ' ⛔G3최장'; bad.append(fid)
        if L[x['answer']] == min(L) and L.count(min(L)) == 1: flag += ' ⛔G3최단'; bad.append(fid)
        if len(x['solution']) < 300: flag += ' ⛔해설<300'; bad.append(fid)
        if '**' in x['solution'] or '**' in x['stem']: flag += ' ⛔마크다운'; bad.append(fid)
        for d in x['distractors']:
            if d.get('text') and d['text'] != x['choices'][d['opt']]:
                flag += f" ⛔메타불일치{CIR[d['opt']]}"; bad.append(fid)
            if d['opt'] == x['answer']:
                flag += ' ⛔정답에오답메타'; bad.append(fid)
        for j, c in enumerate(x['choices']):
            if j != x['answer'] and f"{CIR[j]} {c}:" not in x['solution']:
                flag += f" ⛔풀이누락{CIR[j]}"; bad.append(fid)
        if f"{CIR[x['answer']]} {x['choices'][x['answer']]}" not in x['solution']:
            flag += ' ⛔정답문구불일치'; bad.append(fid)
        print(f"{fid} {x['track']} 답{CIR[x['answer']]} 길이{L} 순위{r} 산포{sp:.2f} 해설{len(x['solution'])}자{flag}")
    # ── 누적 7건의 누출·F2 경로 재발 방지 (전 회차 누적) ──
    checks = [
      ('마이크로파' in ''.join(idx['M01829']['choices']), "L1 M01829 에 마이크로파가 되살아나 M01832 를 지워 준다"),
      ('촘촘' in idx['M01830']['stem'], "L2 M01830 stem 의 '촘촘'이 M01828 의 방향 판단을 공짜로 만든다"),
      ('n=4, 5, 6' in idx['M01830']['stem'], "L0 M01830 stem 의 준위 열거가 M01831 을 답해 준다"),
      ('짧다' in idx['M01830']['choices'][3], "L3 M01830 ④ 가 방향형이면 M01828 이 지워 준다"),
      (any('시간' in c for c in idx['M01833']['choices']), "F2 M01833 의 시간축은 어떻게 써도 참으로 읽힌다"),
      ('빛 알갱이 하나' in idx['M01832']['stem'], "F1 M01832 stem 이 몰 에너지를 광자 하나로 적었다"),
      ('1초에 10 J' in idx['M01834']['stem'], "지침(d) M01834 두 램프 출력이 같아졌다"),
      ('가장 빠른' in ''.join(idx['M01833']['choices']), "S1 M01833 선지 한정어가 다시 어긋났다"),
    ]
    for hit, msg in checks:
        if hit:
            print(f"⛔ {msg}"); bad.append(msg.split()[0])
    print(f"\n위치 {' '.join(f'{CIR[k]}{v}' for k, v in sorted(pos.items()))} · "
          f"길이순위 {dict(sorted(ranks.items()))} · 트랙 {trk}")
    over = [k for k, v in ranks.items() if v > 4]
    if bad or over:
        print(f"⛔ 위반 {sorted(set(bad))} · 순위초과 {over}"); sys.exit(1)
    print("✅ 규칙 위반 없음 — T12 P3 마감")
    if '--apply' in sys.argv:
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만. 반영하려면 --apply")

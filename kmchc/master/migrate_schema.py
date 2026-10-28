#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_schema.py — 품질 최우선 로드맵 1기: 스키마 확장

지금 기록하지 않으면 나중에 소급이 불가능한 다섯 가지에 자리를 만든다.

  source_page   교재 쪽수      → 커버리지 추적(어느 개념을 덮었는지)
  objective     출제 의도      → 무엇을 재는 문항인가
  prereq        선수 개념      → 저장소의 prereq-dag 와 연결
  verified      검증 이력      → 감사 층5(F1~F6)를 언제 누가 통과시켰나
  observed_p    실제 정답률    → 응시 데이터가 들어오면 채움
  observed_disc 실제 변별도    → 〃

기존 문항은 값을 알 수 없으므로 null/빈값으로 자리만 만든다.
단 T12 P1(M01807~M01816)은 교재 쪽을 보고 집필했으므로 source_page 를 채운다.

★비파괴★ — 기존 22필드는 건드리지 않는다.
사용: python3 master/migrate_schema.py [--apply]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')

NEW_FIELDS = {
    'source_page': None,
    'objective': '',
    'prereq': [],
    'verified': None,
    'observed_p': None,
    'observed_disc': None,
}

# 집필 근거가 분명한 것만 소급 기록한다 (T12 P1 — 교재 70~72쪽 판독분)
KNOWN_PAGE = {
    'M01807': 70,   # 원자 모형의 변천 — 돌턴/톰슨
    'M01808': 71, 'M01809': 71, 'M01810': 71, 'M01811': 71,   # 음극선 실험·비전하
    'M01812': 70,   # 톰슨 푸딩 모형
    'M01813': 72, 'M01814': 72, 'M01815': 72, 'M01816': 72,   # α 산란·러더퍼드 한계
}


def migrate(bank):
    added = 0
    for it in bank:
        for k, v in NEW_FIELDS.items():
            if k not in it:
                it[k] = [] if isinstance(v, list) else v
                added += 1
        if it['id'] in KNOWN_PAGE:
            it['source_page'] = KNOWN_PAGE[it['id']]
    return added


if __name__ == '__main__':
    bank = json.load(open(BANK, encoding='utf-8'))
    before = set(k for x in bank for k in x)
    added = migrate(bank)
    after = set(k for x in bank for k in x)
    print(f"필드 추가: {sorted(after - before)}")
    print(f"채운 슬롯 {added}개 / 문항 {len(bank)}제")
    print(f"source_page 소급 기록: {sum(1 for x in bank if x.get('source_page'))}제")
    if '--apply' in sys.argv:
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만 수행. 반영하려면 --apply")

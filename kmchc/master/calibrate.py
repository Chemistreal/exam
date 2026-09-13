#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calibrate.py — 실측 코호트로 문항 은행의 난이도 추정치를 보정한다.

문제의식
--------
은행의 `expected_solve_rate` 는 전량 저작 시점 추정치다. 감사 33회는 모두 은행
'내부 정합성'만 봤고, 바깥의 실측과 대조된 적이 한 번도 없다. 그런데 같은
저장소의 `cohort_data_authoritative.json` 에는 8개 시험지 480문항을 연 1,523명이
실제로 푼 기록(문항별 정답률·변별도·선택지별 반응률)이 들어 있다.

방법
----
1. 실측 문항의 주제 라벨 157종을 교재 61테마에 대응시킨다(LABEL_TO_THEME).
2. 테마별 실측 앵커(정답률 평균·변별도 평균·문항 수)를 만든다.
3. 은행 문항의 보정값을 낸다 — 테마 안의 상대 난이도는 저작자 판단을 존중하고,
   테마의 '수준'만 실측 평균에 맞춰 옮긴다.

       esr_cal = esr_item × (앵커 정답률 / 그 테마 은행 추정 평균)

   앵커가 없는 테마는 전체 비(global ratio)를 쓴다. [0.05, 0.95] 로 자른다.
4. 결과는 **비파괴**로 기록한다 — 원래 값(`expected_solve_rate`)은 건드리지 않고
   `esr_cohort_ref`·`esr_ref_basis` 필드를 새로 붙인다.

한계 (리포트에도 명시)
---------------------
· 실측 문항과 은행 문항은 **다른 문항**이다. 테마 수준의 앵커일 뿐, 문항별 진짜
  p값이 아니다. 문항별 보정은 실제 응시를 받아야 가능하다.
· 응시 집단이 시험지마다 다르다(17명~443명). 표본이 작은 시험지는 가중치가 낮다.
· 매핑되지 않은 라벨은 앵커에서 제외되며 리포트에 남는다.

사용: python3 master/calibrate.py            리포트만
      python3 master/calibrate.py --apply    esr_cohort_ref 필드 부여
"""
import json, os, sys
from collections import defaultdict
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
COHORT = os.path.abspath(os.path.join(HERE, '..', '..', 'cohort_data_authoritative.json'))
OUT = os.path.join(HERE, 'calibration.json')

# 실측 주제 라벨 → 교재 테마 번호
LABEL_TO_THEME = {
    # T1 양성자·중성자·전자수
    '원자의구성입자': 1, '중성자수': 1, '원자': 1, '이온': 1, '표기법': 1,
    '등전자이온': 1, '입자수': 1,
    # T2 원자의 크기
    '원자의크기': 2, '반지름': 2, '원자핵의크기': 2, '보어반지름': 2,
    # T3 열과 에너지
    '열화학': 3, 'Q=CmT': 3, '비열': 3, '온도': 3, '몰열용량': 3,
    # T4 동위원소
    '동위원소': 4, '평균원자량': 4, '질량분석': 4, '원자량': 4,
    # T5 몰
    '몰': 5, '몰=질량/분자량': 5, '아보가드로수': 5, '원자수': 5,
    '몰과개수': 5, '몰해석': 5, '분자량': 5, '화학식': 5,
    # T6 PV=nRT
    'PV=nRT': 6, 'Pv=nRT': 6, '기체': 6,
    # T7 물질의 조성
    '실험식': 7, '원소분석': 7, '리비히원소분석장치': 7, '질량비': 7, '비율': 7,
    # T8 계수 맞추기①
    '계수맞추기': 8, '알짜이온반응식': 8,
    # T9 양적관계
    '양적관계': 9, '몰과양적관계': 9, 'ICE식': 9, '한계반응물': 9, '밀도': 9,
    # T10 원소의 기원
    '빅뱅': 10, '별에서의핵융합': 10, '인체의구성원소': 10,
    '우주의원소분포': 10, '원소': 10,
    # T11 방사성붕괴
    '방사성붕괴': 11, '투과력': 11, '납': 11,
    # T12 원자 모형
    '돌턴': 12, '톰슨': 12, '러더퍼드': 12, '돌턴의원자설': 12, '보어모형계열': 12,
    '수소원자': 12, '수소원자스펙트럼': 12, '발머계열': 12, '전자기파': 12,
    '가시광선': 12, '에너지준위': 12, '광전효과': 12, '물질파': 12,
    '파동성': 12, '양자화학': 12, '에너지': 12,
    # T13 양자수·전자배치
    '양자수': 13, '전자배치': 13, '전자스핀': 13, '홀전자수': 13, '옥텟규칙': 13,
    # T14 원자반지름
    '원자반지름': 14, '이온반지름': 14,
    # T15 이온화에너지
    '이온화에너지': 15, '순차적이온화에너지': 15,
    # T16 전자친화도·전기음성도
    '전자친화도': 16, '전기음성도': 16, '주기적성질': 16,
    # T17 화학결합
    '화학결합': 17, '결합에너지': 17, '결합해리엔탈피': 17, '본하버순환': 17,
    # T18 분자의 구조
    '분자의모양': 18, '분자의 모양': 18,
    # T19 혼성오비탈
    '혼성오비탈': 19,
    # T20 분자의 극성
    '분자의극성': 20, '분자의 극성': 20, '극성': 20, '결합의극성': 20,
    '쌍극자모멘트': 20,
    # T30 분자 사이의 힘
    '수소결합': 30, '분자간인력': 30, '분자간인력세기': 30, 'HF': 30, '얼음': 30,
    '수소결합크기': 30, '점도': 30, '모세관현상': 30, '끓는점': 30,
    # T31 기체 분자 운동 속도
    '분자운동속도': 31, '볼츠만분포': 31, '충돌수': 31, '충돌빈도': 31,
    '평균자유핼오': 31,
    # T32 이상기체·실제기체
    '이상기체': 32, '실제용액': 32, '압축인자': 32, '반데르발스식': 32,
    # T33 기체의 압력
    '압력': 33, '부분압력계산': 33,
    # T35~37 고체
    '고체의구조': 35, '면심입방': 35, '단위세포길이': 35,
    '공간점유율': 36, '면적': 36, '사면체자리': 37,
    # T38 용액의 농도
    '몰농도': 38, '몰분율': 38, '%농도': 38, '해리도': 38,
    # T39 용액의 총괄성
    '삼투압': 39, '삼투현상': 39, '어는점내림': 39, '증기압력내림': 39,
    '용액의총괄성': 39, '바느호프인자': 39, '증기압력': 39,
    # T40~42 열역학
    '흡열반응': 40, '반응열계산': 40, '표준생성엔탈피': 40,
    '헤스법칙': 41, '엔트로피비교': 42, '열역학3법칙': 42,
    # T43~46 평형
    '평형상수계산': 43, '평형농도계산': 43, '반응지수': 43,
    '평형이동': 44, '상평형': 45, '물질의상태': 45, '상태': 45, '용해평형': 46,
    # T47~50 산·염기
    '산의해리': 47, '양쪽성물질': 47, '중화점pH': 48, '다양성자산의적정': 48,
    '염의가수분해': 49, '완충용액': 50, '헨더슨하셀바흐식': 50,
    # T51~55 전기화학·속도론
    '전지': 51, '전기분해': 52, '속도식': 53, '반응속도': 53, '반응차수': 54,
    # T61 기타
    '물질의분류': 61, '순물질': 61, '그래프해석': 61,
}


def load_measured():
    """실측 문항을 (테마, 정답률, 변별도, 응시자수, 라벨) 리스트로 편다."""
    d = json.load(open(COHORT, encoding='utf-8'))
    rows, unmapped = [], defaultdict(int)
    for paper, v in d.items():
        n = v.get('nSeed') or v.get('nFull') or 0
        for lab, rate, disc in zip(v['type'], v['rate'], v['disc']):
            th = LABEL_TO_THEME.get(lab)
            if th is None:
                unmapped[lab] += 1
                continue
            rows.append({'paper': paper, 'theme': th, 'rate': rate / 100.0,
                         'disc': disc, 'n': n, 'label': lab})
    return rows, unmapped


def anchors(rows):
    """테마별 실측 앵커. 응시자 수로 가중평균한다(표본 17명짜리 시험지 보호)."""
    by = defaultdict(list)
    for r in rows:
        by[r['theme']].append(r)
    out = {}
    for th, rs in by.items():
        W = sum(r['n'] for r in rs) or len(rs)
        out[th] = {
            'measured_rate': round(sum(r['rate'] * r['n'] for r in rs) / W, 4),
            'measured_disc': round(sum(r['disc'] * r['n'] for r in rs) / W, 4),
            'n_items': len(rs),
            'n_responses': W,
            'labels': sorted({r['label'] for r in rs}),
        }
    return out


def build():
    bank = json.load(open(BANK, encoding='utf-8'))
    rows, unmapped = load_measured()
    anc = anchors(rows)

    bank_by_theme = defaultdict(list)
    for it in bank:
        bank_by_theme[it['textbook_theme']].append(it)

    g_meas = mean(r['rate'] for r in rows)
    g_bank = mean(it['expected_solve_rate'] for it in bank)
    g_ratio = g_meas / g_bank

    table = []
    for th in sorted(set(list(anc) + list(bank_by_theme))):
        items = bank_by_theme.get(th, [])
        a = anc.get(th)
        row = {'theme': th, 'n_bank': len(items),
               'bank_esr': round(mean(it['expected_solve_rate'] for it in items), 4) if items else None,
               'measured_rate': a['measured_rate'] if a else None,
               'measured_disc': a['measured_disc'] if a else None,
               'n_measured': a['n_items'] if a else 0}
        if a and items and row['bank_esr']:
            row['ratio'] = round(a['measured_rate'] / row['bank_esr'], 3)
        table.append(row)
    return bank, table, anc, unmapped, g_meas, g_bank, g_ratio


def calibrate(bank, anc, g_ratio):
    """비파괴 기준값 부여.

    ★이름을 'calibrated'가 아니라 'cohort_ref'로 둔 이유★
    전체 비 1.73 은 테마를 가리지 않고 일정하다(1.37~2.16, 대부분 1.6~2.0).
    이 일관성은 '은행이 난이도를 틀리게 적었다'보다 **응시 집단과 문항 의도가
    다르다**는 쪽을 가리킨다 — 은행은 심화(82%)·올림피아드 지향이고, 실측은
    학교 시험지다. 그래서 원래 값을 덮어쓰지 않고, '일반 학교 코호트라면
    이 정도 맞힐 것'이라는 **참조 눈금**을 따로 붙인다.

    저작 추정치(expected_solve_rate)는 그대로 둔다.
    """
    by = defaultdict(list)
    for it in bank:
        by[it['textbook_theme']].append(it)
    n_anchored = 0
    for th, items in by.items():
        bm = mean(it['expected_solve_rate'] for it in items)
        if th in anc and bm > 0:
            ratio, basis = anc[th]['measured_rate'] / bm, f"theme{th}-anchor"
            n_anchored += len(items)
        else:
            ratio, basis = g_ratio, "global-ratio"
        for it in items:
            v = it['expected_solve_rate'] * ratio
            it['esr_cohort_ref'] = round(min(0.95, max(0.05, v)), 3)
            it['esr_ref_basis'] = basis
    return n_anchored


if __name__ == '__main__':
    bank, table, anc, unmapped, g_meas, g_bank, g_ratio = build()
    print(f"실측 480문항 중 매핑 성공 {sum(r['n_items'] for r in anc.values())}건 · "
          f"미매핑 라벨 {len(unmapped)}종({sum(unmapped.values())}건)")
    print(f"전체 실측 평균 정답률 {g_meas:.1%} · 은행 추정 평균 {g_bank:.1%} "
          f"→ 비 {g_ratio:.2f}\n")
    print(f"{'테마':>4} {'은행':>5} {'추정':>7} {'실측':>7} {'비':>6} {'잔차':>7} {'변별도':>7} {'실측':>5}")
    for r in table:
        if r['measured_rate'] is None or r['bank_esr'] is None:
            continue
        resid = r['ratio'] / g_ratio
        r['residual'] = round(resid, 3)
        mark = '  ←상대적으로 어려움' if resid < 0.85 else ('  ←상대적으로 쉬움' if resid > 1.15 else '')
        print(f"T{r['theme']:<3} {r['n_bank']:5d} {r['bank_esr']:7.1%} "
              f"{r['measured_rate']:7.1%} {r['ratio']:6.2f} {resid:7.2f} "
              f"{r['measured_disc']:7.3f} {r['n_measured']:5d}{mark}")
    only_meas = [r for r in table if r['measured_rate'] is not None and r['bank_esr'] is None]
    if only_meas:
        print(f"\n  아직 은행에 없는 테마의 실측 앵커(착수 시 활용): "
              + " · ".join(f"T{r['theme']} {r['measured_rate']:.0%}({r['n_measured']}문항)"
                           for r in sorted(only_meas, key=lambda x: x['theme'])[:14]))
    if '--apply' in sys.argv:
        n = calibrate(bank, anc, g_ratio)
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump({'anchors': anc, 'table': table, 'global_ratio': round(g_ratio, 4),
                   'unmapped': dict(unmapped)},
                  open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f"\n✅ esr_cohort_ref 부여 — 앵커 기반 {n}제 / 전체 {len(bank)}제")
        print(f"✅ {OUT}")
    else:
        print("\n※ 리포트만 수행. 반영하려면 --apply")

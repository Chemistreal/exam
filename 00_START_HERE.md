# 00 · 먼저 읽으세요 — Chemistreal 진단 리포트 프로젝트 인수인계

> 이 문서 하나로 새 채팅의 Claude가 지금까지의 모든 맥락을 이어받아 **새 시험지를 추가하고 시스템을 수정·개선**할 수 있도록 작성했습니다. 대화 기록 없이도 자립적으로 동작하도록 구성했습니다.

---

## 0. 작업자(Eric) 선호 — 반드시 준수

- **언어**: 한국어. 간결·고밀도·직설. 아부·과한 칭찬 금지, 솔직한 비판 우선.
- **표기**: em-dash `—` 쓰지 말 것(가운뎃점 `·`, 쉼표, 괄호로 대체). 한글은 리터럴 UTF-8(절대 `\uXXXX` 금지). 불릿·볼드 최소화.
- **단, "가장 자세히"처럼 명시적으로 깊이를 요구하면 장문 환영.**
- Eric = 서울대 화학교육 석사, 대치동 영재(올림피아드) 화학 강사, 올림피아드 교재 저술. 전문 용어를 정확히 쓰면 신뢰가 올라가는 독자층(대치동 학부모/강사) 대상.

## 0-1. 작업 환경(컨테이너) 관례

- 작업 폴더 `/home/claude/work/`에서 작업. 업로드는 `/mnt/user-data/uploads/`(읽기전용, 목록이 가끔 불안정하니 직접 경로 사용).
- 도구: `node v22`, `pdftotext`, `pdftoppm`, `python3`(PIL 사용 가능).
- **업로드 PDF는 이미지 기반이라 `pdftotext`가 빈 결과를 냄 → 반드시 `pdftoppm`으로 래스터화 후 `view`/`zoom`으로 판독.**
- 산출물은 `/mnt/user-data/outputs/`로 복사 후 `present_files`. **규칙: 그 턴에 바뀐 파일만 출력(안 바뀐 파일 재출력 금지).**
- HTML 수정은 "패치 스크립트"(파이썬에서 정확한 앵커 문자열을 `count==1`로 검증 후 치환)로 진행. 매 패치 후 `node --check`로 가장 큰 `<script>` 블록 문법 검사.

---

## 1. 시스템 개요 — 3개 산출물

대치동 화학 시험을 학생 답안으로 진단하는 **정적 단일 파일** 웹앱(GitHub Pages, `Chemistreal` 레포 추정).

| 파일 | 역할 |
|---|---|
| `index.html` (~236KB) | **리포트 엔진** + 모든 시험 데이터 인라인. 학생이 답 입력 → 채점 → 추정 백분위/시드 코호트 → 학부모용 다구역 진단 리포트 렌더 |
| `관리자.html` (~52KB) | **채점 콘솔**(강사용). 시험 선택 + 답안 입력/검증, 데모 등 |
| `해설-{id}.html` | 시험별 **해설 페이지**(원본 해설지 이미지 + 정답/정답률/개념 요약표). `gen_haeseol.py`로 생성. 현재 `해설-chem2-1.html`(3.5MB)만 존재 |

데이터 흐름: 학생 답안 → `analyze()` → (estP면 추정 백분위, 코호트면 시드 기반 실측 석차) → 리포트 섹션들.

---

## 2. 현재 등록된 7개 시험

| id | 제목 | 영역수 | 정답률 | 코호트 | 해설 | 비고 |
|---|---|---|---|---|---|---|
| `kch1to3` | 화학1 1-3단원 모의고사 | 13 | 실측계열 | **SEED_KCH1(422명) 잠금** | 없음 | 코호트 영역 배정 **절대 변경 금지** |
| `kch1to2` | 화학1 1-2단원 모의고사 | 9 | 〃 | 〃 | 없음 | |
| `kch1u1` | 화학1 1단원 모의고사 | 5 | 〃 | 〃 | 없음 | 5축(오각형) — 8축 미만, 백로그 |
| `kch2final` | 화학2 총괄평가 | 8 | 〃 | 〃 | 없음 | |
| `chem2-1` | 화학2 1단원 모의고사 | **8(하위영역)** | 추정(estP) | 없음 | **해설-chem2-1.html** | 4상태→8 하위영역 재분석, #32 복수정답 |
| `kch1to3-b` | 화학1 1-3단원 모의고사 (동형) | 11 | 추정(estP) | 없음 | 미생성 | 분류 검수 대상 |
| `kch1to2-b` | 화학1 1-2단원 모의고사 (동형) | 9 | 추정(estP) | 없음 | 미생성 | 원자모형 22문항 집중, 검수 대상 |

`관리자.html`에는 7개 모두 등록됨.

---

## 3. index.html 엔진 아키텍처 (영역-불가지론적)

### 3-1. 시험 객체 구조 (`EXAMS` 배열)

```js
{
  id:"chem2-1", title:"...", range:"... · ...", source:"...",
  N:0,                       // 0이면 questions.length로 자동
  estP:true,                 // true면 추정 정답률(별표 표기), 백분위 점프 억제
  haeseol:"해설-chem2-1.html",// 빈 문자열이면 '전체 해설 보기' 버튼 미표시
  areaOrder:[...],           // 영역(=레이더 축) 순서. 표/레이더/바둑판이 이 순서를 따름
  areaGroup:{영역:단원, ...}, // 영역 → 상위 단원(group). 표 그룹 헤더·바둑판 색의 기준
  questions: Q_XXX.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],
                            page:0, accept:r[5], misc:...}))
}
```

문항 객체 `{n, ans, p, area, type, page, accept?, misc?}`:
- `ans` 1~4(정답 보기), `p` 정답률(%), `area` 영역, `type` 세부 유형.
- `accept`: **복수 정답** 배열(예 `[2,3]`). 있으면 그 중 하나면 정답.
- `misc`: 오개념(misconception) 배열 `[{type, why}, ...]`. 큐레이션하거나 `omFor(type)`로 자동 생성.

### 3-2. 영역(area) vs 단원(group) — 2계층

- `area` = 레이더 축·표 행·바둑판 셀의 단위.
- `group` = `areaGroup[area]`로 매핑되는 상위 단원. 표는 group이 바뀔 때 그룹 헤더(grp-row) 출력. **바둑판은 group색으로 칠함(4색 등 깔끔).**
- 헬퍼: `areaOrderFor(exam)`, `areaGroupFor(exam)`, `groupOrderFor(exam)`, `orderedAreasOf(r)`.

### 3-3. 추정(estP) vs 코호트

- **estP:true** → `analyze()`가 `Phi(z)`(정규분포, `erf()` 사용)로 추정 정답률·추정 백점·추정 표준편차 산출. 백분위는 **구조적으로 좁아 과대평가되므로 점수(+N점)만 강조하고 백분위 점프는 억제**(정직성 가드).
- **코호트(예 kch1to3=SEED_KCH1, 422명)** → 실제 백분위·석차. **시드가 자기 영역에 잠겨 있어 kch1to3 계열 영역 배정은 절대 바꾸지 말 것.**

### 3-4. 멀티 정답 채점

`accAns(q)`(허용 정답 배열), `isHit(choice,q)`(허용 중 하나면 정답), `ansLabel(q)`(표기). 채점 전 경로에 `isHit` 사용.

### 3-5. 오개념 자동화 — OMLIB / omFor

`OMLIB`(개념 키워드 → 오개념 배열) + `omFor(type)`가 문항의 `type` 문자열을 키워드 매칭해 오개념 카드를 자동 생성. **새 시험은 `misc:omFor(r[4])`만 줘도 개념 수준 오답 카드가 나옴.** → 그래서 `type` 문자열에 OMLIB이 아는 키워드(중성자·동위원소·아보가드로·이온화에너지·전기음성도·옥텟·VSEPR·혼성·수소결합·끓는점 등)를 넣는 게 유리.

### 3-6. analyze() 반환값(요지)

`{total, maxTotal, my100, estPct/estMu/estSd, totalStat(코호트), quad{miss,strength,base,task}, areaList[], groupList[], conceptList[], misc[], graded[], ...}`
- `quad`: 난이도×정오 신호등 사분면. `miss`=쉬운데 틀림(습관), `task`=어려운데 틀림(실력 공백), `strength`=어려운데 맞음, `base`=쉽고 맞음.
- `areaList[A]`: `{name,group,nQ,correct,pts,maxPts,myAcc,popAcc,cohMean100,diff100,...}`.

### 3-7. 렌더 함수(모두 메인 `<script>` 안)

`renderReport`가 총괄. 섹션별:
- **헤더 KPI**: 백점환산 / 백분위·tier(추정이면 별표) / 즉시 회복 +N점(`kUpside`) / 보강 영역(`kFocus`).
- `buildLens` (학부모님께): 정량 판정 리드(이름·백분위·tier·회복·강점/보강).
- **`.method`(진단 설계)**: 3계층 진단 모형 명시(① 오개념 역추적 ② 난이도×정오 신호등 ③ 백분위·변별도) + 개념 변화(conceptual change) 정초. `buildLens` 직후.
- `buildNarrative`(상세 진단), `scatterSVG`(신호등 사분면), `distSVG`/`distSVGEst`(분포: 코호트 히스토그램+곡선 / 추정 곡선), `trendSVG`(재응시 추이).
- **영역별 성취**: `radarBlock`→`radarSVG`(레이더) + 영역표. `badukHTML`(정오 바둑판, group색).
- `conceptList`(개념 숙련도 지도), 오답 카드(misc), `buildRx`(처방), `buildFAQ`, `buildNote`(총평/소견), 푸터 `.note__meta`(도구 식별 라인).
- 아이콘: `secIco(title)`는 **섹션 제목 문자열로 키잉**(제목 바꾸면 아이콘 매칭 깨짐, 주의). `aIco(area)`는 미지 영역이면 'flask'로 폴백.

### 3-8. 레이더 핵심 파라미터 (자주 건드림)

- `radarData(r)`: present 영역 수 ≤13이면 영역을 축으로, >13이면 group으로 축소. **즉 8~13축은 영역 그대로.**
- `radarSVG(r)` 가드: `if(n<3||n>16) return ''`. **상한이 16이라 9~13축도 렌더됨.** (과거 상한 8이라 9~13축이 빈 채로 안 나오는 회귀가 있었음 → 16으로 수정 완료.)
- 라벨 폰트: 축 많으면 자동 축소(`lf=n>10?9:(n>8?10:11)`).
- **"예쁜 레이더"의 최적 축수 ≈ 8. 4축(다이아몬드)은 빈약. chem2-1은 60문항을 8 하위영역으로 분할해 해결(아래 9-1 참고).**

---

## 4. 관리자.html 구조

- 동일한 `EXAMS` 배열(단, 엔트리는 `{id,title,range,questions:Q.map(r=>({n,ans,p,area,type,accept?}))}`로 단순 — OM/misc 없음).
- `SHEET_ENDPOINT`(Google Apps Script)로 결과 저장. `PT=3`, `CHO=["①","②","③","④"]`.
- 데모 버튼은 관리자.html에 위치(공개 앱에는 없음).

---

## 5. ★ 새 시험 추가 워크플로 (가장 중요)

새 시험지 PDF(문제 + 답/해설)를 받으면 아래 순서로 진행.

**Step 1. 래스터화 & 정답표 판독(정확도 최우선)**
```bash
pdftoppm -f 1 -l 1 -r 200 -png "답.pdf" ans   # 정답표는 보통 답 PDF p1 좌상단
# PIL로 좌상단 크롭 후 view/zoom해서 ①②③④ 60문항 정확히 판독
```
- 정답은 채점의 근간이라 **고해상도(200dpi)로 두 번 확인**. 이미지 인라인 판독만으로는 오독 가능(실제로 동형 1-3단원 19번/57번을 처음에 오독 후 고해상도로 교정한 전례).

**Step 2. 문제 PDF로 영역·유형 분류**
```bash
pdftoppm -r 130 -png "문제.pdf" q
```
- 각 문항을 **기존 시험과 같은 영역 체계**로 분류(아래 영역 셋 참고). 그래야 레이더가 8~13축으로 풍부하고 `areaGroupFor`/`aIco`가 동작.
- 화학1 영역 셋(13): 화학의 기초/화학식량/몰/기체/양적관계/원소의 기원/원자모형/전자배치/주기율/분자의 구조/분자의 모양/분자의 극성(+기타).
- 화학2 1단원은 chem2-1처럼 8 하위영역 권장(9-1 참고).
- **분류는 "Claude의 판독"이며 출제자 검수 대상임을 항상 플래그.**

**Step 3. 데이터 모듈 작성** (`chem1_data.py` 패턴 그대로)
- `ANS`(정답 60), `AT[n]=(영역, 유형)`, `AREA_P`(영역별 추정 정답률), `AREA_GROUP`(영역→단원).
- 행 생성기 `rows() -> [[n,ans,p,area,type], ...]`(복수정답 있으면 6번째에 accept 배열).
- 검증: 정답 60개·1~4 범위, AT 1~60 완전 커버, 영역수 8~13 확인.

**Step 4. index.html 패치** (`patch_addexams.py`가 작동 예시)
- `Q_XXX` 배열 정의를 `mkExam` 앞에 삽입.
- `EXAMS` 배열의 마지막 엔트리 뒤·`];` 앞에 새 엔트리 삽입:
  ```js
  {id:"...",title:"...",range:"...",source:"...",N:0,estP:true,haeseol:"",
   areaOrder:[...], areaGroup:{...},
   questions:Q_XXX.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4],page:0,misc:omFor(r[4])}))}
  ```
- 패치는 앵커 `count==1` 검증 후 치환. 매번 `node --check`.

**Step 5. 관리자.html 패치**
- `Q_XXX` 배열을 `const EXAMS=[` 앞에 삽입.
- 단순 엔트리 추가: `{id,title,range,questions:Q_XXX.map(r=>({n:r[0],ans:r[1],p:r[2],area:r[3],type:r[4]}))}`.

**Step 6. 검증**(아래 11장 체크리스트) → outputs 복사 → present_files.

**Step 7.(선택) 해설 페이지 생성** (6장).

---

## 6. 해설 생성 toolchain

`gen_haeseol.py config.json` → `해설-{id}.html`(원본 해설지 이미지 임베드 + 요약표). 답 PDF가 곧 해설지.
- config: `{id,title,range,sub,sol_pdf,dpi,quality,questions:[[n,ans,p,area,type],...], qpage?}`.
- 문항→PDF페이지 매핑: 1페이지=정답표 가정, 단독 동그라미(①②③④) 줄로 문항 경계 탐지(`qpage`로 수동 지정 가능).
- 파일: `gen_haeseol.py`, `_haeseol_template.html`, 예시 `cfg_chem21.json`.
- 동형 2종은 해설 미생성 — 원하면 같은 방식으로 `해설-kch1to3-b.html`/`해설-kch1to2-b.html` 생성 후 해당 EXAMS 엔트리의 `haeseol`에 파일명 채우면 '전체 해설 보기' 버튼이 켜짐.
- 주의: 해설 페이지의 영역 pill은 chem2-1의 경우 **상태(4상태) 레벨**로 둠(index의 8 하위영역과 별개). 그래서 chem2-1 하위영역 변경 시 해설 재생성 불필요.

---

## 7. 데이터 모듈 파일

- `chem21_data.py`: chem2-1의 ANS/AT/AREA_P/ACCEPT + **8 하위영역 분할**(`_SUB_ASSIGN`, `SUB_OF`, `SUB_GROUP`, `rows_sub()`). #32는 `ACCEPT[32]=[2,3]`.
- `chem1_data.py`: 동형 2종(kch1to3-b, kch1to2-b)의 ANS/AT/AREA_P/AREA_GROUP + `rows_k13b()`/`rows_k12b()`/`present_area_order()`/`area_group_map()`.

---

## 8. 설계 결정·관례 (이미 반영됨)

- **학부모 단일 리포트**(학생/토글 제거). 설득 최적화: 회복 +N점 전환 타일, 정량 판정 리드. estP는 백분위 점프 억제(정직성).
- **전문성 설계**: `.method` 진단 설계 블록(개념 변화 정초) + 헤더/푸터 도구 식별 라인 수미상관. 총평은 임상 소견 톤(건드리지 말 것 — 이미 정밀).
- **시각화**: 영역 레이더(틸 본인 폴리곤 + 점선 평균), 정오 바둑판(group색, 복수정답 '복' 마커, '전체 해설 보기' 버튼은 haeseol 있을 때만), 분포 곡선 오버레이.
- **레이더 8축화**: chem2-1을 4상태→8 하위영역으로 재분석(상태는 상위 group). 레이더 임계 13, 가드 16.
- **바둑판 group색 통일**: 영역색(최대 13색 반복) 대신 단원색으로(chem2-1 4색, kch1to3 3색).

## 9. gotchas (실수 주의)

1. **kch1to3 계열 영역 배정 변경 금지**(SEED 코호트 잠김).
2. **섹션 제목 문자열 바꾸면 `secIco` 아이콘 매칭 깨짐.**
3. 한글 리터럴(절대 `\uXXXX` 아님), em-dash 금지.
4. 업로드 PDF는 이미지 → `pdftotext` 무용, 래스터화 필수.
5. 패치는 앵커 `count==1` 검증 후. 매 패치 `node --check`.
6. **그 턴에 바뀐 파일만 outputs로 출력**(안 바뀐 파일 재출력 금지).
7. estP 시험은 백분위 과대평가 → 점수 강조, 백분위 점프 억제 유지.
8. 새 영역 이름이 `AREA_ICO`에 없으면 flask 폴백(정상). OM은 `type` 키워드로 자동.

### 9-1. chem2-1 8 하위영역(레이더 축) 분할표
기체운동·속도(8) / 충돌·실제기체(7) / 부분압·증기압(4) → **기체**; 분자간력·끓는점(11) / 계면·상태변화(6) → **액체**; 결정구조·조성(8) / 결정밀도·계산(8) → **고체**; 용액·총괄성(8) → **용액**. (상세 매핑은 `chem21_data.py`의 `_SUB_ASSIGN`.)

---

## 10. 미완 · 다음 단계(백로그)

1. **동형 2종 해설 페이지 미생성** — 답 PDF로 `gen_haeseol` 생성 후 `haeseol` 채우면 됨.
2. **동형 2종 실측 정답률 미반영** — PDF에 일부 문제만 실측 정답률(19~79%) 인쇄됨. 현재 영역 추정(estP)으로 통일. 원하면 인쇄값 추출해 반영하면 난이도 신호등·변별도 정확도↑.
3. **동형 2종 영역·유형 분류 검수** — Claude 판독이라 검수 필요. 경계 예: kch1to2-b #3(황동 비열→'기타', 화학1 범위 밖 성격), 등전자종/종합 문항(38·59·60 등), kch1to2-b 원자모형 22문항 집중.
4. **kch1u1 5축** — 문제 PDF가 있으면 chem2-1처럼 8 하위영역 분할 가능(현재 오각형).
5. **시각적 프리미엄 광택** — Claude가 렌더를 못 봐 눈대중 불가. Eric이 "이 부분 싸구려" 식으로 짚어주면 그 지점만 정밀 수정.
6. **강사 자격 표기** — 대치동 최대 전문성 레버. 헤더/ID카드에 "출제·분석 조준모 · 서울대 화학교육 석사" 한 줄. 개인 정보라 임의 하드코딩 안 함 → Eric의 정확한 문구 확인 후 삽입.

---

## 11. 검증 체크리스트 (시험 추가/수정 후 매번)

```bash
# 1) 문법
node -e "const fs=require('fs');const h=fs.readFileSync('index.html','utf8');const b=[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).sort((a,b)=>b.length-a.length)[0];fs.writeFileSync('_cp.js',b);" && node --check _cp.js
# 관리자.html도 동일
```
- 정답 라운드트립: 추출한 `Q_XXX`의 ans가 데이터 모듈 ANS와 일치(True).
- 영역 배선: 행영역 ⊆ areaOrder ⊆ areaGroup keys(모두 True), 고아 영역 없음.
- 레이더 축수: 의도한 값(예 11/9), `radarData` 반환 = 영역수, `radarSVG` 비어있지 않음.
- 채점 새너티: 만점 60/60, 1오답 59/60.
- 관리자에 신규 id 등장.

---

## 12. 이 패키지의 파일 목록

| 파일 | 용도 | 새 채팅에서 |
|---|---|---|
| `00_START_HERE.md` | **이 문서**(마스터 맥락) | 가장 먼저 업로드·정독 |
| `index.html` | 현재 리포트 엔진(7시험) | 업로드(수정 대상) |
| `관리자.html` | 현재 채점 콘솔(7시험) | 업로드(수정 대상) |
| `chem21_data.py` | chem2-1 데이터+8하위영역 | 업로드(데이터 포맷 레퍼런스) |
| `chem1_data.py` | 동형 2종 데이터 | 업로드(추가 워크플로 레퍼런스) |
| `gen_haeseol.py` | 해설 생성기 | 업로드(해설 만들 때) |
| `_haeseol_template.html` | 해설 템플릿 | 업로드(해설 만들 때) |
| `cfg_chem21.json` | 해설 config 예시 | 업로드(해설 만들 때) |
| `patch_addexams.py` | **시험 추가 작동 예시** | 업로드(워크플로 코드 패턴) |

> `해설-chem2-1.html`(3.5MB)은 용량이 커 미포함. GitHub Pages에 이미 배포돼 있고, 시스템 수정에는 불필요. 필요 시 `gen_haeseol.py`로 재생성.

---

## 13. 새 채팅 시작 멘트(예시)

> "Chemistreal 진단 리포트 프로젝트를 이어서 작업한다. 첨부한 `00_START_HERE.md`에 전체 맥락·아키텍처·워크플로가 있다. `index.html`/`관리자.html`이 현재 배포본이다. 새 시험지 PDF(문제+답)를 줄 테니 5장 워크플로대로 추가해라. 먼저 문서를 읽고 현재 등록 시험과 추가 절차를 요약해서 확인해라."

이 멘트 + 위 파일들 + 새 시험지 PDF를 올리면 됩니다.

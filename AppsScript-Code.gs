/**
 * Chemistreal 성적 자동 저장 - Google Apps Script (단일 시트 · '시험' 열로 구분)
 *
 * 설치
 * 1) 저장할 스프레드시트 > 확장 프로그램 > Apps Script
 * 2) 이 코드를 전부 붙여넣고 저장
 * 3) 배포 > 새 배포(또는 기존 배포 수정) > 유형: 웹 앱 (실행 대상: 나 / 액세스: 모든 사용자)
 * 4) .../exec URL을 index.html 의 SHEET_ENDPOINT 에 넣는다.
 *    - 기존 배포를 "수정"해 새 버전으로 올리면 URL이 그대로라 index.html 손댈 필요 없음.
 *    - "새 배포"를 하면 URL이 새로 생기므로 SHEET_ENDPOINT 를 교체해야 함.
 *
 * 모든 시험을 한 시트('성적기록')에 모으고, 맨 앞 '시험' 열로 구분한다.
 * 열 순서:  시험 | 학생이름 | 공유링크 | 저장시각 | 수험번호 | 응시일 | 학교 | 학년 |
 *           원점수 | 만점 | 백점환산 | 백분위 | 석차 | 전체누적인원 | 맞은개수 | 영역별 득점 | 답안(60)
 *
 * [중요] 열 순서를 바꿨다. 기존 '성적기록' 탭이 있으면 한 번 비우거나 삭제한 뒤
 *        새로 저장해야 새 머리글이 적용된다(안 그러면 옛 순서와 섞임).
 *
 * [접근] 열쇠(동기화 키)는 두지 않는다. 선생님 요청으로 없앴다.
 *        **이 웹앱 URL 을 아는 사람은 누구나** 학생 이름·학교·점수를 읽고,
 *        행을 고치거나 지울 수 있다. 아는 것이 곧 권한이다.
 *
 *        그래도 남는 울타리:
 *          - URL 은 배포마다 달라지는 긴 무작위 문자열이고, 공개된 곳에 적혀 있지
 *            않다. 이것 하나가 유일한 장벽이다.
 *          - 고치기·지우기는 시험 + 이름 + 답안이 **다 맞는 행**만 건드린다.
 *            지나가다 누른다고 통째로 날아가지는 않는다.
 *          - 배포 URL 이 새 나갔다고 판단되면 Apps Script 편집기에서 **새로 배포**해
 *            URL 을 바꾸고, 앱의 SHEET_ENDPOINT 를 그 값으로 고치면 된다.
 */

/* 동기화 시 '시험' 열로 거르기 위한 시험 id → 제목 매핑.
 * 저장(doPost)은 시험 제목을, 동기화(doGet)는 시험 id를 보내므로 이 표가 필요하다.
 * [중요] index.html 의 EXAMS 제목을 바꾸면 아래 값도 똑같이 맞춰야 한다. */
var EXAM_TITLES = {
  'kch1to3':             ['화학1 1-3단원 모의고사'],
  'kch1to2':             ['화학1 1-2단원 모의고사'],
  'kch1u1':              ['화학1 1단원 모의고사'],
  'kch2final':           ['화학2 총괄평가'],
  'chem2-1':             ['화학2 1단원 모의고사'],
  'kch1to3-b':           ['화학1 1-3단원 모의고사 (동형)'],
  'kch1to2-b':           ['화학1 1-2단원 모의고사 (동형)'],
  'kch2to3':             ['화학2 1-3단원 모의고사'],
  'j0':                  ['조준모의고사 0회'],
  'jmchc-1':             ['JMChC 모의고사 1회'],
  'jmchc-2':             ['JMChC 모의고사 2회'],
  'jmchc-3':             ['JMChC 모의고사 3회'],
  'jmchc-4':             ['JMChC 모의고사 4회'],
  'jmchc-5':             ['JMChC 모의고사 5회'],
  'jmchc-6':             ['JMChC 모의고사 6회'],
  'jmchc-7':             ['JMChC 모의고사 7회'],
  'jmchc-8':             ['JMChC 모의고사 8회'],
  'jmchc-9':             ['JMChC 모의고사 9회'],
  'jmchc-10':            ['JMChC 모의고사 10회'],
  'jmchc-11':            ['JMChC 모의고사 11회'],
  'jmchc-11-1':          ['JMChC 모의고사 11-1회'],
  'sanyeom-60':          ['산과염기 60제'],
  'jmchc-12':            ['JMChC 모의고사 12회'],
  'jmchc-13':            ['JMChC 모의고사 13회'],
  'jmchc-14':            ['JMChC 모의고사 14회'],
  'donghyung-1':         ['기출동형 1회'],
  'donghyung-2':         ['기출동형 2회'],
  'donghyung-3':         ['기출동형 3회'],
  'donghyung-4':         ['기출동형 4회'],
  'kmchc-2026-1-simhwa': ['KMChC 2026 제1차 · 심화'],
  'kmchc-2025-2-simhwa': ['KMChC 2025 제2차 · 심화'],
  'kmchc-2025-1-ilban':  ['KMChC 2025 제1차 · 일반'],
  'kmchc-2025-1-simhwa': ['KMChC 2025 제1차 · 심화'],
  'kmchc-2024-2':        ['KMChC 2024 제2차'],
  'hwol-2024':           ['KMChC 2024 제1차', '화올 2024', 'KMChC 2024 제1차 · 동형 2세트'],
  'hwol-2023':           ['KMChC 2023', '화올 2023'],
  'hwol-2022':           ['KMChC 2022', '화올 2022'],
  'hwol-2021':           ['KMChC 2021', '화올 2021'],
  'hwol-2019':           ['KMChC 2019', '화올 2019', 'KMChC 2019 · 동형 2세트'],
  'hwol-2018':           ['KMChC 2018', '화올 2018', 'KMChC 2018 · 동형 2세트'],
  'hwol-2017':           ['KMChC 2017', '화올 2017'],
  'hwol-2016':           ['KMChC 2016', '화올 2016'],
  'hwol-2015':           ['KMChC 2015', '화올 2015'],
  'hwol-2014':           ['KMChC 2014', '화올 2014'],
  'hwol-2013':           ['KMChC 2013', '화올 2013'],
  'hwol-2012':           ['KMChC 2012'],
  'hwol-2011':           ['KMChC 2011'],
  'hwol-2010':           ['KMChC 2010'],
  'hwol-2009':           ['KMChC 2009'],
  'kmchc-2018':          ['KMChC 2018', '화올 2018', 'KMChC 2018 · 동형 2세트'],
  'kmchc-2019':          ['KMChC 2019', '화올 2019', 'KMChC 2019 · 동형 2세트'],
  'kmchc-2024-1':        ['KMChC 2024 제1차', '화올 2024', 'KMChC 2024 제1차 · 동형 2세트'],
};

var HEADER = [
  '시험', '학생이름', '공유링크', '저장시각', '수험번호', '응시일', '학교', '학년',
  '원점수', '만점', '백점환산', '백분위', '석차', '전체누적인원',
  '맞은개수', '영역별 득점', '답안(60)'
];

function doPost(e) {
  var lock = null, scheduled = false;
  try {
    /* 잠금은 **덧붙이는 그 순간**만 쥔다. 아래에서 재계산을 예약만 하므로
       한 사람이 쥐고 있는 시간이 1초 안쪽이다 — 열 명이 몰려도 줄이 안 선다. */
    try { lock = LockService.getScriptLock(); lock.waitLock(45000); } catch (eL) { lock = null; }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('성적기록') || ss.insertSheet('성적기록');

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADER);
      sheet.getRange(1, 1, 1, HEADER.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    var d = JSON.parse(e.postData.contents);
    // 9열(d.total)은 맞은 문항 수 — 석차의 기준이라 그대로 둔다.
    // 감점을 반영한 진짜 원점수는 맨 뒤 열에 따로 받는다(옛 행은 비어 있다).
    var row = [
      d.exam, d.name, d.link || '', new Date(), d.examno, d.date, d.school, d.grade,
      d.total, d.max, d.pct100, d.percentile, d.rank, d.n,
      d.correct, d.areas, "'" + d.answers, '',
      (d.raw === 0 || d.raw) ? d.raw : ''
    ];

    /* ── 같은 응시는 **덧붙이지 않고 그 줄을 고친다** (2026-08-12) ─────────
       선생님이 물으셨다 — *"이런애들 지금 시험 안봤는데 왜 올라가있어?"*
       7월에 본 회차의 학생 넷이 오늘 날짜로 시트에 올라가 있었다. 그날 채점한
       것은 다른 회차뿐이었다.

       고리는 이랬다.

         ① 앱은 `no-cors` 로 쏘므로 **갔는지 알 수가 없다**
         ② 그래서 «아직 확인 못 함(up:0)» 을 달고, 열 때마다 **다시 보낸다**
            (망이 끊긴 채 채점한 기록을 살리는 유일한 장치다)
         ③ 여기서 무조건 appendRow 했다 → 다시 보낼 때마다 **새 줄**,
            저장시각은 `new Date()` = 오늘
         ④ 30초 뒤 재계산이 «이름+답안 같으면 최신 1건만 남김» 으로 정리하면서
            **오늘 것을 남기고 원본을 지웠다**
         ⑤ 그래서 7월 기록의 날짜가 오늘로 바뀌어, 오늘 본 것처럼 보였다

       ②는 옳은 설계다. 다만 그 설계는 **다시 보내는 것이 무해하다**는 전제
       위에 서 있는데, ③이 그 전제를 깨고 있었다. 전제를 지키게 고친다 —
       같은 응시(같은 시험 + 같은 이름 + 같은 답안)면 그 줄을 고쳐 쓴다.

       ⚠ **저장시각·응시일은 안 건드린다.** 그것이 이 병의 증상이었다.
       ⚠ **빈 값으로는 안 덮는다.** 다시 보내는 기록에는 학교·학년이 비어 있을
         수 있다(링크로 열린 성적표에는 그 칸이 없다). 덮으면 있던 것이 지워진다.

       열쇠는 앱의 `subSig`(이름+답안)와 같다. 두 자가 같은 것을 같다고 해야
       «시트에 있으니 그만 보내라» 가 통한다. */
    var hit = _findSameAttempt_(sheet, d);
    if (hit > 0) {
      var old = sheet.getRange(hit, 1, 1, HEADER.length).getValues()[0];
      row[3] = old[3];                       // 저장시각 — 처음 들어온 때 그대로
      row[5] = old[5] || row[5];             // 응시일 — 처음 것 그대로
      if (!row[6]) row[6] = old[6];          // 학교 — 빈 값으로 안 덮는다
      if (!row[7]) row[7] = old[7];          // 학년 — 〃
      if (!row[4]) row[4] = old[4];          // 수험번호 — 〃
      if (!row[2]) row[2] = old[2];          // 링크 — 〃
      sheet.getRange(hit, 1, 1, HEADER.length).setValues([row]);
    } else {
      sheet.appendRow(row);
    }

    /* [자동 재계산] 시트에 쌓인 **모든 회차**의 석차·백분위·인원·성적표 문자를
       최종 코호트로 다시 맞춘다. 방금 저장한 회차만 맞추면 다른 회차의 옛 행은
       굳은 채 남아, 선생님은 그게 언제 풀릴지 알 수 없다.

       ⚠ 재계산을 여기서 끝까지 돌리지 않는다.
       재계산은 시트를 통째로 읽고 다시 쓰는 일이라 몇 초가 걸린다. 그동안 이
       잠금을 쥐고 있으면 **뒤에 온 저장이 줄줄이 기다린다.** 열 명을 이어
       채점하면 마지막 사람은 최대 45초를 기다리다 잠금 없이 밀고 들어간다 —
       화면은 '보냈다' 고 하는데 시트에는 한참 안 보이니, 앱이 못 갔다고 보고
       다시 보낸다. 같은 줄이 쌓이고, 그중 똑같은 것은 중복 지우기에 지워진다.
       **줄이 생겼다 지워졌다 하는 것**이 그것이었다(2026-08-06).

       그래서 저장은 **덧붙이는 것까지만** 한다. 재계산은 예약해 두고 잠금을
       놓는다 — 열 명을 이어 채점해도 재계산은 한 번만 돈다. */
    try { SpreadsheetApp.flush(); } catch (eF) {}
    scheduled = _bookRecompute_(30 * 1000);
    /* 예약을 못 걸었으면(트리거 한도 등) 예전처럼 여기서 돌린다. 느려도
       안 맞는 것보다 낫다. 이미 걸려 있는 경우('have')는 그냥 둔다. */
    if (scheduled === false) {
      try { recomputeAllExams(); }
      catch (eR) {
        Logger.log('자동 재계산 실패(저장은 완료): ' + eR);
        try { fillReportMessages(); } catch (eM) { Logger.log('자동 문자 생성 실패: ' + eM); }
      }
    }

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    if (lock) try { lock.releaseLock(); } catch (eU) {}
  }
}

/* 시험 제목 → 자동 재계산 설정.
 * 예전에는 '조준모의고사 0회' 하나만 돌려주고 나머지는 null 이었다. 그래서 다른
 * 회차는 재계산이 아예 돌지 않았고, 먼저 채점한 학생은 43명 중 몇 등, 나중 학생은
 * 44명 중 몇 등으로 저장 순간의 인원이 행에 굳은 채 남았다 — 그 숫자 그대로
 * 성적표 문자가 나갔다. 이제 EXAM_COHORT 에 있는 모든 회차가 재계산된다.
 * 표에 없는 제목(옛 kch* 시험 등)은 여전히 저장만 하고 넘어간다. */
function _recomputeConfigFor(title) {
  if (String(title) === '조준모의고사 0회') return { base: J0_BASE_TOTALS, qCount: 60 };
  var c = EXAM_COHORT[String(title)];
  if (!c) return null;
  return { base: c.base || [], qCount: c.q || 60 };
}

/**
 * doGet: 앱의 "시트 동기화" 버튼(JSONP)이 호출.
 *   ?action=list&exam=<시험ID>&callback=<함수명>  →  callback({students:[...]})
 *   ?action=history&name=<이름>&callback=<함수명>  →  callback({rows:[...]})
 *     한 학생의 전 회차. 어느 기기에서 채점했든 시트에 다 있다.
 *   ?action=all&callback=<함수명>                 →  callback({rows:[...],n:N})
 *     시트 전체를 한 번에. 회차마다 묻던 것을 대신한다.
 * 요청 시험 id를 제목으로 바꿔, '시험' 열이 일치하는 행만 돌려준다(시험 섞임 방지).
 * 매핑에 없는 id면 거르지 않고 전체를 돌려준다(하위호환). 브라우저로 열면 상태만 표시.
 */
/* ── 한 학생의 전 회차 이력 ────────────────────────────────────────────
   ?action=history&name=<이름>&callback=<함수명>

   성적표의 '성장 대시보드·성장 추적' 은 그동안 **그 브라우저에 채점해 둔
   기록**만 세었다. 그래서 학부모 휴대폰에서 공유 링크를 열면 그 폰이 우연히
   열어 본 회차만 잡혀 "지금까지 2회 응시" 가 됐다 — 실제로는 여섯 번을 봤는데.
   선생님이 학원 PC 를 바꿔도 마찬가지였다.

   시트에는 어느 기기에서 채점했든 다 들어 있다. 학생 하나를 이름으로 물으면
   전 회차를 한 번에 돌려준다(회차마다 부르면 서른여덟 번이 된다).

   이름은 **공백을 지우고** 견준다. '박하람' 과 '박 하람' 은 한 사람이다 —
   시트에도 그렇게 갈려 들어가 있다. */
function _histKey_(s) { return String(s == null ? '' : s).replace(/\s+/g, ''); }
/* 시트에는 **그때 쓰던 제목**이 적혀 있다('화올 2018' → 'KMChC 2018').
   앱은 id 로 회차를 찾으므로 제목을 id 로 되돌려 준다 — 안 그러면 이름이
   바뀐 회차의 옛 기록이 통째로 빠진다. EXAM_TITLES 는 id 하나에 제목을
   여러 개 달고 있으니 그걸 뒤집으면 된다. */
var _TITLE2ID_ = null;
function _idOfTitle_(title) {
  if (!_TITLE2ID_) {
    _TITLE2ID_ = {};
    for (var id in EXAM_TITLES) {
      var ts = EXAM_TITLES[id];
      if (!(ts instanceof Array)) ts = [ts];
      for (var i = 0; i < ts.length; i++) _TITLE2ID_[String(ts[i])] = id;
    }
  }
  return _TITLE2ID_[String(title || '')] || '';
}
/* ── 시트의 응시 기록을 앱이 쓰는 모양으로 ─────────────────────────────
   한 학생만 뽑을 때(history)와 전부 뽑을 때(all)가 같은 자리를 읽는다.
   두 벌로 두면 한쪽만 고쳐져 어긋난다 — 실제로 '학교·학년을 안 돌려준다' 는
   버그가 list 쪽에만 있었다.

   key 를 주면 그 학생만, 안 주면 전부. */
function _recordRows_(key) {
  var out = [];
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('성적기록');
    if (!sh || sh.getLastRow() <= 1) return out;
    var rows = sh.getRange(2, 1, sh.getLastRow() - 1, HEADER.length).getValues();
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (key && _histKey_(r[1]) !== key) continue;
      var ans = String(r[16] || '').replace(/^'/, '').replace(/[^0-4]/g, '');
      if (!ans) continue;
      var eid = _idOfTitle_(r[0]);
      if (!eid) continue;                    // 표에 없는 제목은 앱이 못 찾는다
      out.push({
        examId: eid,
        exam: String(r[0] || ''),
        name: String(r[1] || ''),
        school: String(r[6] || ''),
        grade: String(r[7] || ''),
        answers: ans,
        ts: (r[3] instanceof Date) ? r[3].getTime() : 0
      });
    }
  } catch (err) {}
  return out;
}
function _jsonOut_(body, cb) {
  return cb
    ? ContentService.createTextOutput(cb + '(' + body + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
    : ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}
function historyFor_(name, cb) {
  var key = _histKey_(name);
  return _jsonOut_(JSON.stringify({ ok: true, rows: key ? _recordRows_(key) : [] }), cb);
}
/* ── 시트 전체를 한 번에 ────────────────────────────────────────────────
   ?action=all&callback=<함수명>  →  callback({ok:true, rows:[...]})

   예전에는 회차마다 한 번씩 물었다. 서른여덟 번이다. 한 번에 12초를 기다리니
   최악이면 7분 반이 걸렸고, 그래서 '시트에서 불러오기' 는 아무도 안 누르는
   버튼이 됐다 — 결국 화면에 뜨는 것은 늘 이 브라우저에 남은 것뿐이었다.

   한 번에 다 준다. 회차 수와 무관하게 한 번이라, 페이지를 열 때마다 조용히
   맞출 수 있다. 그래야 어느 기기에서 열어도 같은 것이 보인다. */
function allRows_(cb) {
  var rows = _recordRows_('');
  return _jsonOut_(JSON.stringify({ ok: true, rows: rows, n: rows.length }), cb);
}

/* ── 한 회차의 **익명** 점수 분포 ──────────────────────────────────────
   공유 링크로 열린 성적표는 **만든 시점의 인원**이 박혀 있었다. 받는 쪽
   브라우저에는 채점 기록이 없어서, 링크를 지을 때 세어 둔 숫자를 그대로
   싣는 수밖에 없었다. 그래서 뒤에 채점한 학생이 아무리 늘어도 학부모 화면의
   분모는 그대로였다("연도누적 총석차 1/5" 가 다섯 명인 채로 굳는다).

   여기서 **지금** 시트를 세어 준다. 나가는 것은 맞은 문항 수별 사람 수뿐이다 —
   이름도 학교도 답안도 안 나간다. `all` 은 이름이 들어 있어 학부모 브라우저에
   줄 수 없다. 이 창구는 줄 수 있다.

   ⚠ 링크가 localhost 인 줄은 안 센다. 그건 학생이 낸 것이 아니라 **검사가**
   낸 것이다(홍길동 60/60 · 예비본 57/60 …). 시트에서 지우기 전에도 여기
   숫자는 바로 맞는다. */
function cohortOf_(examId, cb) {
  var hist = {}, yhist = {}, n = 0, yn = 0, skipped = 0;
  /* 시간대에 안 기댄다 — _seoulYear_ 주석 참고. */
  var year = _seoulYear_(new Date());
  try {
    var want = EXAM_TITLES[examId] || null;
    if (want && !(want instanceof Array)) want = [want];
    /* ⚠ 표에 없는 회차면 **아무것도 안 센다.** 다른 창구는 못 찾으면 필터를
       걸지 않고 다 주는데(하위호환), 여기서 그러면 **모든 회차 사람을 한
       회차 모집단으로** 세게 된다 — 분모가 열 배로 부풀고 등수가 통째로
       틀린다. 빈 대답이면 성적표는 링크에 실린 값을 그대로 쓴다. */
    if (!want) return _jsonOut_(JSON.stringify(
      { ok: true, exam: examId, hist: {}, n: 0, unknown: true }), cb);
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('성적기록');
    if (sh && sh.getLastRow() > 1) {
      var rows = sh.getRange(2, 1, sh.getLastRow() - 1, HEADER.length).getValues();
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        if (want.indexOf(String(r[0])) < 0) continue;
        if (/localhost/i.test(String(r[2] || ''))) { skipped++; continue; }
        var c = Number(r[14]);                    // [14] 맞은개수
        if (!isFinite(c) || c < 0) continue;
        c = Math.round(c);
        hist[c] = (hist[c] || 0) + 1;
        n++;
        /* 올해 채점한 것만 따로 센다 — 반석차가 쓰는 모집단이다.
           가르는 잣대는 **채점해 넣은 시각**([3] 저장시각)이다. 응시일은
           비어 있는 줄이 많다. 시각을 모르는 줄은 올해로 치지 않는다 —
           모르는 것을 올해로 세면 반석차가 소리 없이 부풀어 오른다. */
        var t = (r[3] instanceof Date) ? _seoulYear_(r[3]) : 0;
        if (t === year) { yhist[c] = (yhist[c] || 0) + 1; yn++; }
      }
    }
  } catch (err) {}
  return _jsonOut_(JSON.stringify({ ok: true, exam: examId, hist: hist, n: n,
                                    yhist: yhist, yn: yn, year: year, skipped: skipped }), cb);
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  var cb = p.callback;
  if (p.action === 'history') return historyFor_(p.name, cb);
  if (p.action === 'all') return allRows_(cb);
  if (p.action === 'cohort') return cohortOf_(String(p.exam || ''), cb);
  if (p.action === 'list') {
    var students = [];
    try {
      // 제목은 바뀐다('화올 2018' → 'KMChC 2018'). 시트에 이미 쌓인 옛 이름을
      // 잃지 않도록 id 하나에 제목을 여러 개 달고, 그중 아무거나 맞으면 통과시킨다.
      // 표에 없는 id 면 필터하지 않는다(하위호환).
      var want = EXAM_TITLES[p.exam] || null;
      if (want && !(want instanceof Array)) want = [want];   // 옛 형식(문자열 하나)도 받는다
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var sheet = ss.getSheetByName('성적기록');
      if (sheet && sheet.getLastRow() > 1) {
        var rows = sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADER.length).getValues();
        // 새 열 순서: [0시험,1이름,2링크,3저장시각,4수험번호,5응시일,6학교,7학년,...,16답안]
        for (var i = 0; i < rows.length; i++) {
          var r = rows[i];
          if (want && want.indexOf(String(r[0])) < 0) continue;   // '시험' 열로 필터
          var ans = String(r[16] || '').replace(/^'/, '').replace(/[^0-4]/g, '');
          if (!ans) continue;
          var dd = r[5];   // 응시일
          var date = (dd instanceof Date)
            ? Utilities.formatDate(dd, Session.getScriptTimeZone(), 'yyyy-MM-dd')
            : String(dd || '');
          students.push({
            examno: r[4] || '',
            date: date,
            name: String(r[1] || ''),
            // 학교·학년을 안 돌려주고 있었다. 그래서 시트에서 받아온 기록은
            // 명단에서 학교·학년이 비어 '-' 로 뜨고, 같은 학생인데 다른 사람처럼
            // 보였다. 시트에는 처음부터 들어 있던 값이다.
            school: String(r[6] || ''),
            grade: String(r[7] || ''),
            answers: ans,
            ts: (r[3] instanceof Date) ? r[3].getTime() : 0   // 저장시각
          });
        }
      }
    } catch (err) {}
    var out = JSON.stringify({ ok: true, students: students });
    return cb
      ? ContentService.createTextOutput(cb + '(' + out + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
  }
  /* ── 시트 고치기 (앱의 '명단 관리'가 부른다) ──────────────────────────
     이름을 잘못 입력했을 때 앱에서 고쳐도 시트에는 옛 이름 행이 그대로
     남았다. 그러면 '시트에서 불러오기'가 그 행을 **다른 사람**으로 보고
     다시 넣는다(중복 판정이 이름+답안이라서). 앱 쪽에도 막는 장치를 뒀지만,
     시트가 계속 틀린 채로 있으면 성적문자도 옛 이름으로 나간다.

     그래서 시트를 직접 고칠 창구를 연다.
       ?action=rename&from=..&to=..[&school=..&grade=..]   이름 일괄(전 시험)
       ?action=deleteName&name=..[&school=..&grade=..]     그 학생의 전 회차 삭제
       ?action=dedupe                                      겹친 줄 정리

     school·grade 를 함께 주면 그 학교·학년인 행만 고른다. 동명이인이 있을 때
     한쪽만 건드리기 위한 것이다(이름·학교·학년이 모두 같아야 같은 학생이다).
     주지 않으면 이름만 보고 고른다.
       ?action=editRow&exam=..&name=..&answers=..&setName=..&setSchool=..&setGrade=..
       ?action=deleteRow&exam=..&name=..&answers=..

     행을 고르는 열쇠는 앱이 쓰는 것과 같다 — 시험 + 이름 + 답안.
     저장시각은 기기마다 달라 쓸 수 없다.

     열쇠는 두지 않는다(선생님 요청). URL 을 아는 사람은 누구나 부를 수 있다.
     대신 행을 **정확히 지목**해야만 바뀐다 — 시험·이름·답안이 하나라도 어긋나면
     0건이다. 통째로 비우는 동작은 아예 만들지 않았다. */
  /* ── 석차·백분위를 지금 다시 맞춘다 ────────────────────────────────
     평상시에는 저장할 때마다 저절로 맞춰지고, 매일 05시 트리거가 안전망이다.
     그런데 채점이 몰려 재계산이 겹치면 그때 물러난다(그래야 방금 넣은 줄이
     안 덮인다). 그러면 그 회차는 **저장 순간의 인원**이 굳은 채 남는다 —
     먼저 채점한 학생은 1명 중 1등, 나중 학생은 10명 중 3등 같은 식이다.
     2026-08-05 JMChC 12회가 그랬다. 밤까지 기다리지 않고 지금 맞춘다.

     ⚠ 지우는 동작이 아니다. 다시 계산해 적을 뿐이고, 겹친 저장이 있으면
       _flushRows 가 물러난다(그때는 changed=false 로 알려 준다). */
  if (p.action === 'recompute') {
    var rOut, rLock = null;
    try {
      /* 저장과 같은 잠금을 쥐고 돈다 — 사람이 누른 재계산이 저장과 겹쳐
         헛돌면 "눌러도 안 맞는다" 가 된다. */
      try { rLock = LockService.getScriptLock(); rLock.waitLock(60000); } catch (eRL) { rLock = null; }
      var rr = recomputeAllExams();
      /* false 면 세 번 다시 읽어도 계속 겹쳤다는 뜻이다 — 지금 누가 채점 중이다.
         그 경우 30초 뒤에 혼자 다시 도는 예약이 걸려 있으니 기다리기만 하면 된다. */
      rOut = (rr === false)
        ? { ok: true, retry: true, msg: '지금 채점이 몰려 있습니다 — 잠시 뒤 저절로 맞춰집니다' }
        : { ok: true, done: (rr && rr.done) || 0, of: (rr && rr.of) || 0,
            dropped: (rr && rr.dropped) || 0 };
    }
    catch (eRc) { rOut = { ok: false, error: String(eRc) }; }
    finally { if (rLock) { try { rLock.releaseLock(); } catch (eRU) {} } }
    var rBody = JSON.stringify(rOut);
    return cb
      ? ContentService.createTextOutput(cb + '(' + rBody + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(rBody).setMimeType(ContentService.MimeType.JSON);
  }
  if (p.action === 'rename' || p.action === 'editRow' || p.action === 'deleteRow' || p.action === 'deleteName' || p.action === 'dedupe') {
    var body = JSON.stringify(_sheetEdit(p));
    return cb
      ? ContentService.createTextOutput(cb + '(' + body + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
  }
  /* ── 검사가 남긴 줄만 지운다 ────────────────────────────────────────
     CI 의 브라우저 검사가 진짜 앱스크립트로 제출해서, 학생이 아닌 줄이
     시트에 쌓였다(홍길동 60/60 · 예비본 57/60 · 오프라인테스트 …).
     그 줄들이 석차·백분위·또래 정답률 모집단에 그대로 들어가 **진짜
     학생들의 등수를 밀어냈다.**

     손으로 지우면 빠뜨린다 — 이름만으로는 못 가른다. '이도현' 은 진짜 줄과
     검사 줄이 둘 다 있다. 가르는 것은 **링크**다: 검사는 localhost 에서
     돌고, 학생 화면은 언제나 chemistreal.github.io 다.

     ⚠ 지우는 조건을 밖에서 못 정한다. 링크가 localhost 인 줄, 그것뿐이다.
     통째로 비우는 길은 여기에도 없다.

       ?action=purgeTest            몇 줄이 걸리는지만 본다(안 지운다)
       ?action=purgeTest&go=1       지운다 */
  if (p.action === 'purgeTest') {
    var body2 = JSON.stringify(_purgeTestRows(String(p.go || '') === '1'));
    return cb
      ? ContentService.createTextOutput(cb + '(' + body2 + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(body2).setMimeType(ContentService.MimeType.JSON);
  }
  var status = JSON.stringify({ ok: true, msg: 'Chemistreal endpoint live' });
  return cb
    ? ContentService.createTextOutput(cb + '(' + status + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
    : ContentService.createTextOutput(status).setMimeType(ContentService.MimeType.JSON);
}

/* 검사가 남긴 줄(링크가 localhost)만 지운다.
   go 가 아니면 세기만 한다 — 지우는 것은 되돌릴 수 없으므로 먼저 보여 준다.
   아래에서 지우는 조건은 이 한 줄뿐이고, 밖에서 바꿀 수 없다. */
function _purgeTestRows(go) {
  var lock = null;
  try {
    try { lock = LockService.getScriptLock(); lock.waitLock(20000); } catch (eL) { lock = null; }
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('성적기록');
    if (!sheet || sheet.getLastRow() < 2) return { ok: true, found: 0, removed: 0, rows: [] };
    var n = sheet.getLastRow() - 1;
    var all = sheet.getRange(2, 1, n, HEADER.length).getValues();
    var kill = [], rows = [];
    for (var i = 0; i < n; i++) {
      var link = String(all[i][2] || '');
      if (!/localhost|127\.0\.0\.1/i.test(link)) continue;
      kill.push(i + 2);
      rows.push({ exam: String(all[i][0] || ''), name: String(all[i][1] || '') });
    }
    if (!go) return { ok: true, found: kill.length, removed: 0, rows: rows, dryRun: true };
    // 아래에서부터 지운다 — 위에서부터 지우면 남은 행 번호가 밀린다.
    kill.sort(function (a, b) { return b - a; });
    for (var k = 0; k < kill.length; k++) sheet.deleteRow(kill[k]);
    /* 지우고 나면 모집단이 달라진다. 석차·백분위·성적표 문자를 다시 계산해
       두지 않으면, 시트에는 옛 등수가 남아 문자로 그대로 나간다. */
    var redone = [];
    try {
      var seen = {};
      for (var r2 = 0; r2 < rows.length; r2++) {
        // recomputeExam 은 **시험 제목**을 받는다(id 가 아니다).
        var t = rows[r2].exam;
        if (!t || seen[t]) continue;
        seen[t] = 1;
        var cfg = _recomputeConfigFor(t);
        if (!cfg) continue;                     // 기준 코호트가 없는 회차는 안 건드린다
        try { recomputeExam(t, cfg.base, cfg.qCount); redone.push(t); } catch (e2) {}
      }
    } catch (e3) {}
    return { ok: true, found: kill.length, removed: kill.length, rows: rows, recomputed: redone };
  } catch (err) {
    return { ok: false, error: String(err) };
  } finally {
    if (lock) { try { lock.releaseLock(); } catch (e) {} }
  }
}

/* 성적기록 시트의 행을 고치거나 지운다. doGet 의 rename·editRow·deleteRow 가 부른다.
   열 순서: 1시험 2이름 3링크 4저장시각 5수험번호 6응시일 7학교 8학년 … 17답안 */
function _sheetEdit(p) {
  var lock = null;
  try {
    try { lock = LockService.getScriptLock(); lock.waitLock(20000); } catch (eL) { lock = null; }
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('성적기록');
    if (!sheet || sheet.getLastRow() < 2) return { ok: true, changed: 0 };
    var n = sheet.getLastRow() - 1, changed = 0;

    /* 학생 한 명을 통째로 지운다. 전학·중복 등록처럼 그 사람의 기록 자체를
       없애야 할 때 쓴다. 이름만으로 고르므로 **동명이인이 있으면 함께 지워진다** —
       앱 쪽에서 몇 건이 지워지는지 미리 보여 주고, 이름을 다시 받아 확인한다. */
    /* 같은 사람인지 가리는 자리. school·grade 를 주면 함께 본다. */
    var wantS = p.school == null ? null : String(p.school).trim();
    var wantG = p.grade == null ? null : String(p.grade).trim();
    var sameWho = function (row, nm) {
      if (String(row[1] || '').trim() !== nm) return false;
      if (wantS !== null && String(row[6] || '').trim() !== wantS) return false;
      if (wantG !== null && String(row[7] || '').trim() !== wantG) return false;
      return true;
    };

    /* 같은 응시가 여러 줄로 쌓인 것을 한 줄로 줄인다. 열쇠는 시험+이름+답안.
       학교·학년이 적힌 줄을 살린다 — 그 줄이 누구인지 말해 주기 때문이다. */
    if (p.action === 'dedupe') {
      var all = sheet.getRange(2, 1, n, HEADER.length).getValues();
      var seen = {}, drop = [];
      var sig = function (r) {
        return String(r[0]) + '\u0001' + String(r[1] || '').trim() + '\u0001' +
               String(r[16] == null ? '' : r[16]).replace(/^'/, '').replace(/[^0-4]/g, '');
      };
      var score = function (r) { return ((r[6] ? 1 : 0) + (r[7] ? 1 : 0)); };
      for (var d = 0; d < n; d++) {
        var key = sig(all[d]);
        if (seen[key] === undefined) { seen[key] = d; continue; }
        // 더 잘 채워진 쪽을 남기고 나머지를 버린다
        if (score(all[d]) > score(all[seen[key]])) { drop.push(seen[key] + 2); seen[key] = d; }
        else drop.push(d + 2);
        changed++;
      }
      drop.sort(function (x, y) { return x - y; });
      for (var dd = drop.length - 1; dd >= 0; dd--) sheet.deleteRow(drop[dd]);
    } else if (p.action === 'deleteName') {
      var who = String(p.name || '').trim();
      if (!who) return { ok: false, error: 'bad-args' };
      var rowsD = sheet.getRange(2, 1, n, HEADER.length).getValues(), gone = [];
      for (var g = 0; g < n; g++) if (sameWho(rowsD[g], who)) { gone.push(g + 2); changed++; }
      // 뒤에서부터. 앞에서 지우면 남은 행 번호가 밀린다.
      for (var gg = gone.length - 1; gg >= 0; gg--) sheet.deleteRow(gone[gg]);
    } else if (p.action === 'rename') {
      var from = String(p.from || '').trim(), to = String(p.to || '').trim();
      if (!from || !to || from === to) return { ok: false, error: 'bad-args' };
      var rowsR = sheet.getRange(2, 1, n, HEADER.length).getValues();
      var col = sheet.getRange(2, 2, n, 1).getValues();
      for (var i = 0; i < n; i++) if (sameWho(rowsR[i], from)) { col[i][0] = to; changed++; }
      if (changed) sheet.getRange(2, 2, n, 1).setValues(col);
    } else {
      var want = EXAM_TITLES[p.exam] || null;
      if (want && !(want instanceof Array)) want = [want];
      var norm = function (v) { return String(v == null ? '' : v).replace(/^'/, '').replace(/[^0-4]/g, ''); };
      var name = String(p.name || '').trim(), ans = norm(p.answers);
      if (!name || !ans) return { ok: false, error: 'bad-args' };
      var rows = sheet.getRange(2, 1, n, HEADER.length).getValues(), kill = [];
      for (var j = 0; j < n; j++) {
        var r = rows[j];
        if (want && want.indexOf(String(r[0])) < 0) continue;
        if (String(r[1] || '').trim() !== name) continue;
        if (norm(r[16]) !== ans) continue;
        if (p.action === 'deleteRow') { kill.push(j + 2); changed++; continue; }
        if (p.setName)             sheet.getRange(j + 2, 2).setValue(String(p.setName).trim());
        if (p.setSchool != null)   sheet.getRange(j + 2, 7).setValue(String(p.setSchool));
        if (p.setGrade  != null)   sheet.getRange(j + 2, 8).setValue(String(p.setGrade));
        changed++;
      }
      // 뒤에서부터 지운다. 앞에서 지우면 남은 행 번호가 밀린다.
      for (var k = kill.length - 1; k >= 0; k--) sheet.deleteRow(kill[k]);
    }

    // 성적문자 탭은 성적기록을 그대로 옮겨 적은 것이라 같이 다시 만든다.
    if (changed) { try { SpreadsheetApp.flush(); fillReportMessages(); } catch (eM) { Logger.log('문자 재생성 실패: ' + eM); } }
    return { ok: true, changed: changed };
  } catch (err) {
    return { ok: false, error: String(err) };
  } finally {
    if (lock) try { lock.releaseLock(); } catch (eU) {}
  }
}

/* ============================================================
   성적 재계산 · 정리 (관리자가 수동 실행)
   ------------------------------------------------------------
   왜 필요한가:
   백분위·석차·전체누적인원은 "저장하는 그 순간"의 인원으로 한 번만 계산되어
   행에 박제된다. 그래서 학생이 며칠에 걸쳐 응시하면, 같은 점수인데도
   먼저 본 학생과 나중에 본 학생의 석차·인원이 제각각(40, 44, 48 …)이 된다.
   이 함수는 모든 행을 "하나의 최종 코호트"에 대해 다시 계산해 일관되게 맞춘다.

   무엇을 하나:
   1) 완전 중복 행(이름+답안 동일) 제거 — 저장시각이 가장 최신인 1건만 남김
   2) 학교명 오타 교정(_SCHOOL_FIX)
   3) 코호트 = 기준분포(EXAM_COHORT) + 학생별 최신 1건(이름·학교·학년 기준)
   4) 각 행의 백분위·석차·전체누적인원을 이 코호트로 재계산
   5) 성적표 문자(18열)도 새 수치로 다시 채움

   실행:
   - 평상시에는 실행할 필요 없음 — 학생이 제출할 때마다 doPost가 자동으로 재계산한다.
   - 시트를 손으로 고쳤거나 상태가 의심될 때만: 편집기에서 recomputeAllExams 선택 → 실행 (수동 복구용)
   - setupAllTriggers()를 1회 실행하면 매일 새벽 5시 백업 재계산 트리거도 설치된다.
   ============================================================ */

/* 조준모의고사 0회 기준 코호트 총점 분포(익명 40명) — index.html의 BASE_TOTALS['j0']와 동일 */
var J0_BASE_TOTALS = [12,21,32,37,40,44,54,54,54,59,59,60,60,63,69,69,71,75,78,82,86,87,87,93,93,96,99,100,102,105,108,111,112,117,126,129,129,141,144,171];

/* 시험 제목 → { q: 문항 수, base: 기준 코호트 원점수 }.
 * 여기에 없는 제목은 재계산이 통째로 건너뛰어, 먼저 채점한 학생은 43명 기준·
 * 나중 학생은 44명 기준으로 굳은 채 남는다. 그래서 기준 기록이 없는 회차도
 * base: [] 로 넣어 둔다(문항 수는 회차마다 다르다 — 60문항 32개, 50문항 6개).
 * base 는 final.html 이 화면에서 쓰는 cohort/baseline.json 과 같은 기록이다.
 * 앱은 맞은 문항 수로, 시트는 원점수로 세므로 3을 곱해 둔 값이다.
 * [중요] 손으로 고치지 말 것 — `python3 tools/gen_gas_cohort.py --write` 가 만든다. */
var EXAM_COHORT = {
  'JMChC 모의고사 1회': { q: 60, base: [11,12,13,16,16,17,18,19,19,19,19,20,21,22,22,23,23,24,24,25,25,26,26,27,28,28,29,29,29,31,33,37,37,38,38,38,38,38,39,41,42,43,44,44,46,47] },
  'JMChC 모의고사 2회': { q: 60, base: [22,28,29,29,31,31,36,36,44,45,46,48] },
  'JMChC 모의고사 3회': { q: 60, base: [9,10,15,15,16,17,19,19,19,19,20,20,21,21,22,23,23,24,24,24,24,26,27,28,28,28,28,28,29,30,34,34,36,37,38,40,41,41,41,42,42,45,46,47,47,48,49] },
  'JMChC 모의고사 4회': { q: 60, base: [19,21,23,27,28,39,39,45,48,48,52] },
  'JMChC 모의고사 5회': { q: 60, base: [8,11,12,13,13,14,15,17,17,18,18,19,19,20,20,21,22,22,23,23,23,23,24,24,26,26,27,28,29,29,33,34,35,36,37,37,38,39,41,41,42,42,43,44] },
  'JMChC 모의고사 6회': { q: 60, base: [23,25,32,34,35,39,39,40,42,43,46] },
  'JMChC 모의고사 7회': { q: 60, base: [9,12,14,15,16,18,19,19,20,21,23,23,24,24,26,27,27,30,30,30,31,32,33,33,33,33,34,35,36,37,37,39,40,40,40,41,41,42,44,44,48,49] },
  'JMChC 모의고사 8회': { q: 60, base: [16,21,27,28,29,32,38,38,39,39,42,48,52] },
  'JMChC 모의고사 9회': { q: 60, base: [7,9,12,13,14,14,15,15,15,17,18,18,18,18,19,20,21,22,24,26,26,27,28,28,29,29,29,30,30,30,30,31,31,32,32,32,34,34,34,36,40,44] },
  'JMChC 모의고사 10회': { q: 60, base: [14,21,23,23,26,29,32,33,40,47,49] },
  'JMChC 모의고사 11회': { q: 60, base: [14,14,15,17,17,20,23,26,26,29,30,30,31,32,33,39] },
  'JMChC 모의고사 11-1회': { q: 60, base: [19,20,20,20,25,26,31,38,38,40,45] },
  '산과염기 60제': { q: 60, base: [12,12,16,16,18,19,19,19,20,20,22,22,25,25,27,28,29,30,31,32,33,49] },
  'JMChC 모의고사 12회': { q: 60, base: [18,22,26,27,32,33,40,41,48] },
  'JMChC 모의고사 13회': { q: 60, base: [5,8,9,11,12,14,15,15,16,16,17,18,19,19,20,20,21,21,22,23,23,24,24,25,26,26,26,27,28,29,29,29,33,35,37,37,37,38,42,47] },
  'JMChC 모의고사 14회': { q: 60, base: [16,16,23,24,25,27,27,34,40,44] },
  '기출동형 1회': { q: 60, base: [8,12,12,12,12,12,12,13,15,16,17,18,18,19,19,19,20,20,20,21,21,21,21,21,22,22,22,22,23,23,23,23,24,24,24,24,24,24,25,25,25,25,26,26,26,26,27,27,27,27,28,28,28,28,28,28,29,30,30,30,30,30,30,31,31,31,31,31,32,33,33,33,33,34,34,34,34,34,34,35,35,35,36,36,36,36,36,36,37,37,38,38,39,39,39,40,41,41,43,44,44,44,44,47,48,48,50,51,52,52,53,53,54,55] },
  '기출동형 2회': { q: 60, base: [9,9,10,11,12,13,13,15,16,17,17,17,17,17,18,19,19,19,20,20,21,21,21,21,22,23,24,24,24,25,25,25,26,27,27,27,27,28,28,28,29,30,30,31,31,31,32,32,33,33,33,33,33,33,33,34,34,34,35,35,36,36,36,36,36,36,36,37,37,37,37,38,39,39,39,39,40,40,40,40,40,41,42,43,43,43,43,44,45,46,47,47,48,48,48,49,49,50,52,52,53,54,54,56,57] },
  '기출동형 3회': { q: 60, base: [6,10,12,12,12,13,13,13,14,14,14,15,16,16,16,17,18,18,19,21,21,22,22,22,23,23,23,24,25,25,26,26,27,27,28,28,29,29,30,30,30,30,30,30,30,31,31,31,31,31,31,31,31,32,32,32,32,32,33,33,33,34,34,34,34,34,34,34,34,35,36,36,36,36,37,37,37,37,37,37,38,38,38,38,38,40,40,42,42,42,43,43,43,43,44,44,44,44,44,44,45,45,47,49,50,51,51,51,52] },
  '기출동형 4회': { q: 60, base: [7,8,10,11,12,13,14,14,14,14,16,16,16,17,17,18,18,19,19,19,20,20,21,21,21,22,23,23,23,24,24,24,25,25,26,26,27,27,27,27,27,29,30,30,30,30,30,31,31,31,32,33,33,33,34,34,34,34,35,35,35,35,35,35,36,36,37,37,37,38,39,39,39,40,40,40,41,41,41,42,42,43,44,45,45,45,45,45,46,47,48,48,48,49,49,50] },
  'KMChC 2026 제1차 · 심화': { q: 50, base: [] },
  'KMChC 2025 제2차 · 심화': { q: 50, base: [] },
  'KMChC 2025 제1차 · 일반': { q: 50, base: [] },
  'KMChC 2025 제1차 · 심화': { q: 50, base: [] },
  'KMChC 2024 제2차': { q: 60, base: [36] },
  'KMChC 2024 제1차': { q: 60, base: [30,33,39,50,53,54] },
  '화올 2024': { q: 60, base: [30,33,39,50,53,54] },
  'KMChC 2024 제1차 · 동형 2세트': { q: 60, base: [30,33,39,50,53,54] },
  'KMChC 2023': { q: 60, base: [14,21,25,31,31,34,34,34,36,36,38,38,38,38,43,52,53,54,54] },
  '화올 2023': { q: 60, base: [14,21,25,31,31,34,34,34,36,36,38,38,38,38,43,52,53,54,54] },
  'KMChC 2022': { q: 60, base: [17,21,25,28,28,29,29,30,31,31,34,34,34,35,35,35,36,36,37,37,38,39,40,41,43,44,49,50,52,52,53,57,57] },
  '화올 2022': { q: 60, base: [17,21,25,28,28,29,29,30,31,31,34,34,34,35,35,35,36,36,37,37,38,39,40,41,43,44,49,50,52,52,53,57,57] },
  'KMChC 2021': { q: 60, base: [19,20,22,23,23,23,23,24,25,27,27,28,28,28,29,29,30,30,32,32,32,32,33,34,35,35,35,35,35,36,37,38,39,39,39,40,40,41,43,43,43,44,45,46,49,49,50,51,52,52,52,56,56,56,57,58,60] },
  '화올 2021': { q: 60, base: [19,20,22,23,23,23,23,24,25,27,27,28,28,28,29,29,30,30,32,32,32,32,33,34,35,35,35,35,35,36,37,38,39,39,39,40,40,41,43,43,43,44,45,46,49,49,50,51,52,52,52,56,56,56,57,58,60] },
  'KMChC 2019': { q: 60, base: [15,16,20,21,23,25,25,26,26,26,27,28,28,28,28,28,29,29,29,30,30,31,31,32,32,32,32,33,34,34,35,36,36,36,36,37,37,37,37,38,38,38,38,39,40,40,40,40,40,41,41,41,42,42,42,43,43,44,44,44,44,46,46,47,48,48,48,48,48,49,49,49,49,49,50,51,52,53,54,55,57,57,58,59] },
  '화올 2019': { q: 60, base: [15,16,20,21,23,25,25,26,26,26,27,28,28,28,28,28,29,29,29,30,30,31,31,32,32,32,32,33,34,34,35,36,36,36,36,37,37,37,37,38,38,38,38,39,40,40,40,40,40,41,41,41,42,42,42,43,43,44,44,44,44,46,46,47,48,48,48,48,48,49,49,49,49,49,50,51,52,53,54,55,57,57,58,59] },
  'KMChC 2019 · 동형 2세트': { q: 60, base: [15,16,20,21,23,25,25,26,26,26,27,28,28,28,28,28,29,29,29,30,30,31,31,32,32,32,32,33,34,34,35,36,36,36,36,37,37,37,37,38,38,38,38,39,40,40,40,40,40,41,41,41,42,42,42,43,43,44,44,44,44,46,46,47,48,48,48,48,48,49,49,49,49,49,50,51,52,53,54,55,57,57,58,59] },
  'KMChC 2018': { q: 60, base: [8,14,16,20,21,22,22,23,23,23,24,24,24,26,26,26,26,27,27,27,28,28,28,28,28,28,29,29,29,29,29,30,30,30,31,31,31,32,33,33,34,34,34,34,34,34,34,34,34,35,35,35,35,35,36,36,36,36,36,37,37,37,38,38,39,39,39,39,39,40,40,40,41,41,41,41,41,41,42,42,42,43,43,44,44,47,48,48,49,49,49,50,50,50,50,50,51,51,51,52,54,56,57] },
  '화올 2018': { q: 60, base: [8,14,16,20,21,22,22,23,23,23,24,24,24,26,26,26,26,27,27,27,28,28,28,28,28,28,29,29,29,29,29,30,30,30,31,31,31,32,33,33,34,34,34,34,34,34,34,34,34,35,35,35,35,35,36,36,36,36,36,37,37,37,38,38,39,39,39,39,39,40,40,40,41,41,41,41,41,41,42,42,42,43,43,44,44,47,48,48,49,49,49,50,50,50,50,50,51,51,51,52,54,56,57] },
  'KMChC 2018 · 동형 2세트': { q: 60, base: [8,14,16,20,21,22,22,23,23,23,24,24,24,26,26,26,26,27,27,27,28,28,28,28,28,28,29,29,29,29,29,30,30,30,31,31,31,32,33,33,34,34,34,34,34,34,34,34,34,35,35,35,35,35,36,36,36,36,36,37,37,37,38,38,39,39,39,39,39,40,40,40,41,41,41,41,41,41,42,42,42,43,43,44,44,47,48,48,49,49,49,50,50,50,50,50,51,51,51,52,54,56,57] },
  'KMChC 2017': { q: 60, base: [5,5,9,14,15,16,17,17,18,18,19,19,21,21,22,22,22,23,23,23,23,23,24,24,25,25,25,25,26,26,26,26,26,27,27,28,28,28,28,28,28,29,29,29,29,30,30,30,30,30,30,31,31,31,31,31,32,32,32,32,32,33,34,34,35,35,36,36,37,37,38,38,38,39,39,39,40,41,42,42,42,44,45,45,45,46,46,46,46,46,47,48,48,49,49,51,51,52,53,56] },
  '화올 2017': { q: 60, base: [5,5,9,14,15,16,17,17,18,18,19,19,21,21,22,22,22,23,23,23,23,23,24,24,25,25,25,25,26,26,26,26,26,27,27,28,28,28,28,28,28,29,29,29,29,30,30,30,30,30,30,31,31,31,31,31,32,32,32,32,32,33,34,34,35,35,36,36,37,37,38,38,38,39,39,39,40,41,42,42,42,44,45,45,45,46,46,46,46,46,47,48,48,49,49,51,51,52,53,56] },
  'KMChC 2016': { q: 60, base: [] },
  '화올 2016': { q: 60, base: [] },
  'KMChC 2015': { q: 60, base: [] },
  '화올 2015': { q: 60, base: [] },
  'KMChC 2014': { q: 60, base: [] },
  '화올 2014': { q: 60, base: [] },
  'KMChC 2013': { q: 60, base: [] },
  '화올 2013': { q: 60, base: [] },
  'KMChC 2012': { q: 60, base: [] },
  'KMChC 2011': { q: 60, base: [] },
  'KMChC 2010': { q: 60, base: [] },
  'KMChC 2009': { q: 60, base: [] },
};

/* 학교명 오타·표기 교정(필요 시 여기에 추가). 이름 기준으로 학생을 묶으므로 석차엔 영향 없지만 표시를 바로잡는다. */
var _SCHOOL_FIX = { '휘뭉중': '휘문중' };

function _normName(s) { return String(s == null ? '' : s).replace(/\s+/g, '').trim(); }

/* 같은 응시가 시트에 이미 있나 — 있으면 그 **행 번호**(1부터), 없으면 0.

   같음의 열쇠는 **시험 + 이름 + 답안**이다. 앱의 `subSig` 와 같은 규칙이라야
   «시트에 있으니 그만 보내라» 가 양쪽에서 같은 말이 된다. 저장시각은 안 본다 —
   다시 보낸 것은 시각만 다르지 같은 응시다.

   답안이 다르면 **다시 푼 것**이므로 다른 줄이다(그건 덧붙이는 게 맞다). */
function _findSameAttempt_(sheet, d) {
  try {
    var last = sheet.getLastRow();
    if (last <= 1) return 0;
    var vals = sheet.getRange(2, 1, last - 1, HEADER.length).getValues();
    var wantExam = String(d.exam || '');
    var wantName = _normName(d.name);
    var wantAns = String(d.answers || '').replace(/^'/, '').replace(/[^0-4]/g, '');
    if (!wantAns || !wantName) return 0;
    for (var i = vals.length - 1; i >= 0; i--) {     // 뒤에서부터 — 최근 것이 먼저
      var r = vals[i];
      if (String(r[0] || '') !== wantExam) continue;
      if (_normName(r[1]) !== wantName) continue;
      var ans = String(r[16] || '').replace(/^'/, '').replace(/[^0-4]/g, '');
      if (ans !== wantAns) continue;
      return i + 2;                                   // 머리글 한 줄을 더한다
    }
  } catch (err) {}
  return 0;
}

/* 누가 같은 학생인가 — 이름·학교·학년이 **모두** 같아야 같은 사람이다.
   final.html 의 rosterKey 와 같은 규칙. 이름만 있고 학교·학년이 비면 다른 사람으로 센다. */
function _whoKey(row) {
  return [_normName(row[1]), _normName(row[6]), _normName(row[7])].join('\u0001');
}

/* 클라이언트(grade-j0.html)의 rankPct와 동일한 규칙: 나보다 높은 사람 수+1 = 석차, 백분위=(미만+동점/2)/n */
function _rankPct(value, arr) {
  var n = arr.length, below = 0, equal = 0;
  for (var i = 0; i < n; i++) { var v = arr[i]; if (v < value) below++; else if (v === value) equal++; }
  return { rank: (n - below - equal) + 1, pct: n ? ((below + 0.5 * equal) / n) * 100 : 0, n: n };
}

function _fmtNum(x) { return Math.round(Number(x) * 10) / 10; }  // 소수 1자리, .0은 자동으로 사라짐

/* 그 시각이 **서울에서 몇 년인가.**

   ⚠ `getFullYear()` 는 이 스크립트가 걸린 시간대로 답한다. 그 시간대는
     appsscript.json 에 들어 있고, 그 파일은 배포된 프로젝트에서 끌어오므로
     **저장소에서는 아무도 볼 수 없다**(clasp pull 로 보존만 한다). 서울이
     아니면 연말연시 몇 시간 동안 해가 어긋난다 — 이 저장소가 도는 UTC 로
     재어 보면 2027-01-01 05:00 KST 에 낸 답안이 **2026년으로 세어진다.**
     그만큼 학생 몇 명이 엉뚱한 해의 반석차 모집단에 들어가고, 그 숫자가
     그대로 학부모 문자에 실린다. 한 해에 한 번, 조용히 틀리는 자리다.

     그래서 시간대를 묻지 않는다. **서울로 못박아** 읽는다 — 이 파일이 다른
     자리에서 이미 그렇게 하고 있다(Utilities.formatDate(…, 'Asia/Seoul', …)). */
function _seoulYear_(d) {
  if (!(d instanceof Date) || isNaN(d.getTime())) return 0;
  var y = Number(Utilities.formatDate(d, 'Asia/Seoul', 'yyyy'));
  return (isNaN(y) || y < 2000 || y > 2100) ? 0 : y;
}

/* 저장시각에서 연도만. 값이 없거나 날짜가 아니면 0 — 모르는 것을 올해로 세지 않는다. */
function _yearOf(t) {
  if (!t) return 0;
  var d = (t instanceof Date) ? t : new Date(Number(t));
  return _seoulYear_(d);
}

/* 그 해에 채점한 학생 안에서의 등수. 누적 석차 한 줄만 보내면 "우리 반에서는
   몇 등이냐" 를 반드시 되묻는다. 한 해치가 한 명뿐이면 적지 않는다 — 1/1 은
   등수가 아니라 아직 아무도 없다는 뜻이다. */
function _yearRankLine(year, yrp) {
  if (!year || !yrp || yrp.n < 2) return '';
  return '· ' + year + '년 반석차 ' + yrp.rank + '/' + yrp.n + '\n';
}

/* 원점수 줄. 감점이 있는 회차는 앱이 보내 준 값이라야 맞다 — 여기서 correct*3
   으로 지어내면 오답 감점만큼 부풀려 나간다. 값이 없는 옛 행은 줄을 통째로 뺀다. */
function _rawLine(raw, qCount) {
  if (raw === '' || raw == null || isNaN(Number(raw))) return '';
  return '· 원점수 ' + Number(raw) + '/' + (qCount * 3) + '점\n';
}

function _msgExam(title, name, total, max, pct100, correct, qCount, percentile, rank, n, link, raw, year, yrp) {
  return '[다원교육 영재관 · 화학 조준모]\n'
    + name + ' 학생 ' + title + ' 성적표입니다.\n'
    + _rawLine(raw, qCount)
    + '· 정답 ' + correct + '/' + qCount + '문항 · 백점환산 ' + pct100 + '점\n'
    + '· 백분위 ' + percentile + ' · 연도누적 총석차 ' + rank + '/' + n + '\n'
    + _yearRankLine(year, yrp)
    + '아래 링크에서 영역별 정오와 취약 개념을 확인하세요.\n'
    + link;
}

/* 조준모의고사 0회 전용 진입점 */
function recomputeJ0() { recomputeExam('조준모의고사 0회', J0_BASE_TOTALS, 60); }

/* 시트에 쌓인 **모든 회차**를 다시 맞춘다.
 * 제출 때마다 이 함수가 돈다(doPost). 한 회차만 맞추면 다른 회차의 옛 행은
 * 굳은 채 남고, 선생님은 그게 언제 풀릴지 알 수 없다.
 *
 * 시트를 **한 번 읽고 한 번 쓴다.** 회차마다 따로 읽고 쓰면 38회차 × (읽기+쓰기)
 * 라 저장 한 번이 몇십 초가 되고, 학생이 기다리는 동안 실행 시간 제한에 걸린다.
 * 설정이 없는 제목(EXAM_COHORT 에 없는 옛 시험)은 손대지 않고 지나간다. */
function recomputeAllExams() {
  /* 겹친 저장을 만나면 **다시 읽어서 다시 맞춘다.** 물러나기만 하면 그 회차는
     저장 순간의 인원(1명 중 1등)이 굳은 채 다음 저장까지 남는다 — 그날 마지막
     학생이면 새벽 트리거까지 하루다. 다시 읽으면 방금 들어온 줄까지 함께
     세니, 물러나기의 안전함은 그대로 두고 굳는 것만 없앤다.

     세 번까지다. 그 사이에 또 저장이 들어왔다는 뜻이고, 그 저장이 스스로
     전부 맞춘다. 그래도 못 맞췄으면 조금 뒤에 혼자 다시 돈다(예약). */
  for (var t = 1; t <= 3; t++) {
    var r = _recomputeAllOnce_();
    if (r !== false) return r;
    Logger.log('recomputeAllExams · 겹친 저장 ' + t + '번째 — 다시 읽어 맞춘다');
  }
  var booked = _bookRecompute_();
  Logger.log('recomputeAllExams · 세 번 다 겹쳤다 — '
    + (booked === true ? '조금 뒤로 예약했다' : booked === 'have' ? '이미 예약돼 있다' : '예약도 못 걸었다'));
  return false;
}

function _recomputeAllOnce_() {
  var sheet = _gradeSheet();
  if (!sheet) return;
  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, WIDE).getValues();

  var titles = [], seen = {};
  data.forEach(function (r) {
    var t = String(r[0] || '').trim();
    if (t && !seen[t]) { seen[t] = true; titles.push(t); }
  });

  var drop = [], done = 0, skip = [];
  titles.forEach(function (t) {
    var cfg = _recomputeConfigFor(t);
    if (!cfg) { skip.push(t); return; }
    // 한 회차가 실패해도 나머지는 계속 맞춘다.
    try { drop = drop.concat(_recalcRows(data, t, cfg.base, cfg.qCount)); done++; }
    catch (e) { Logger.log('재계산 실패 · ' + t + ' : ' + e); }
  });

  /* 읽을 때의 줄 수를 같이 넘긴다 — 그 사이에 저장이 들어왔으면 물러난다. */
  var wrote = _flushRows(sheet, data, drop, data.length);
  if (!wrote) return false;
  try { fillReportMessages(); } catch (eM) { Logger.log('문자 생성 실패: ' + eM); }
  Logger.log('recomputeAllExams 완료 · ' + done + '/' + titles.length + '개 회차 · 중복삭제 '
    + drop.length + '행' + (skip.length ? ' · 설정 없어 건너뜀: ' + skip.join(', ') : ''));
  return { done: done, of: titles.length, dropped: drop.length, skipped: skip };
}

/* ============================================================
   못 맞춘 채로 두지 않는다 — 조금 뒤에 혼자 다시 돈다
   ------------------------------------------------------------
   세 번 다시 읽어도 계속 겹친다면 채점이 몰리는 중이다. 그 저장들이 스스로
   맞추겠지만, **마지막 저장이 겹쳐서 물러난 경우**가 남는다 — 뒤에 아무도
   없으니 아무도 다시 안 맞춘다. 그 자리를 이 예약이 메운다.

   한 번에 하나만 걸어 둔다. 열 명이 몰아 채점하면 예약도 열 개가 되고,
   앱스크립트 트리거는 20개가 상한이다.
   ============================================================ */
/* 돌려주는 값 세 가지를 구분해야 한다 —
     true   방금 걸었다
     'have' 이미 걸려 있다(또 걸 필요 없다)
     false  못 걸었다 → 부른 쪽이 직접 돌려야 한다 */
function _bookRecompute_(ms) {
  try {
    var pending = ScriptApp.getProjectTriggers().some(function (t) {
      return t.getHandlerFunction() === 'recomputeSoon';
    });
    if (pending) return 'have';
    ScriptApp.newTrigger('recomputeSoon').timeBased().after(ms || 30 * 1000).create();
    return true;
  } catch (e) { Logger.log('재계산 예약 실패: ' + e); return false; }
}

/* 예약이 부르는 자리. 자기 예약을 먼저 지우고 돈다 — 그래야 이번에도 겹쳤을 때
   다시 걸 수 있다(안 지우면 '이미 걸려 있다' 로 보여 영영 안 걸린다).

   ⚠ **저장과 같은 잠금**을 쥐고 돈다. 안 쥐면 재계산이 시트를 다시 쓰는 사이에
   저장이 줄을 덧붙이고, 그러면 _flushRows 가 물러난다 — 물러나면 또 예약하고,
   그 예약이 또 겹치는 고리가 된다. 잠금을 쥐면 그 고리가 아예 안 생긴다.
   재계산 한 번은 몇 초라, 그동안 저장이 기다려도 줄이 서지 않는다. */
function recomputeSoon() {
  try {
    ScriptApp.getProjectTriggers().forEach(function (t) {
      if (t.getHandlerFunction() === 'recomputeSoon') ScriptApp.deleteTrigger(t);
    });
  } catch (e) { Logger.log('예약 정리 실패: ' + e); }
  var lock = null;
  try { lock = LockService.getScriptLock(); lock.waitLock(60000); } catch (eL) { lock = null; }
  try { recomputeAllExams(); }
  finally { if (lock) { try { lock.releaseLock(); } catch (eU) {} } }
}

/* 성적기록 시트 + 성적표 문자 머리글 보장. 없거나 비었으면 null. */
/* 성적기록의 실제 열 폭. 17열까지가 HEADER 이고, 뒤의 둘은 나중에 붙였다.
   [주의] 9번째 열 이름은 '원점수' 지만 그 안에 든 값은 **맞은 문항 수**다
   (앱이 `total: correct` 로 보낸다). 석차·백분위가 그 값으로 매겨지므로
   의미를 바꾸면 안 된다. 감점을 반영한 진짜 원점수는 RAW_COL 에 따로 받는다. */
var MSG_COL = 18, RAW_COL = 19, WIDE = 19;

function _gradeSheet() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('성적기록');
  if (!sheet || sheet.getLastRow() < 2) { Logger.log('성적기록 시트가 비어 있습니다.'); return null; }
  if (String(sheet.getRange(1, MSG_COL).getValue() || '') !== '성적표 문자') {
    sheet.getRange(1, MSG_COL).setValue('성적표 문자').setFontWeight('bold');
  }
  if (String(sheet.getRange(1, RAW_COL).getValue() || '') !== '원점수(감점 반영)') {
    sheet.getRange(1, RAW_COL).setValue('원점수(감점 반영)').setFontWeight('bold');
  }
  return sheet;
}

/* 고친 값을 시트에 한 번에 반영하고, 지울 행은 아래→위로 지운다.
   위에서부터 지우면 그 아래 행 번호가 하나씩 밀려 엉뚱한 줄이 날아간다.

   ⚠ **읽은 뒤에 줄이 늘었으면 쓰지 않는다.**
   여기서 쓰는 `data` 는 재계산을 시작할 때 찍은 **사진**이다. 그 사이에 다른
   저장이 줄을 덧붙였으면, 옛 사진을 그 위에 덮어써서 **방금 채점한 학생이
   시트에서 사라진다.**

   2026-08-05 JMChC 11회에서 실제로 그랬다. 열 명을 이어서 채점했는데 셋
   (김규민·전준·최민준)이 사라졌다 — 저장은 됐다가 뒤늦게 끝난 옛 재계산이
   그 줄을 덮었다. 저장마다 잠금을 걸지만 20초 안에 못 얻으면 잠금 없이
   진행하게 되어 있어서, 채점이 몰리면 겹친다.

   물러나도 잃는 것이 없다. 부른 쪽(recomputeAllExams · recomputeExam)이 **다시
   읽어서 다시 맞춘다** — 그때는 방금 들어온 줄까지 함께 센다. 반대로 한 번
   덮어쓴 줄은 되돌릴 방법이 없다. */
function _flushRows(sheet, data, dropRows, expectRows) {
  if (expectRows != null) {
    var now = sheet.getLastRow() - 1;
    if (now !== expectRows) {
      Logger.log('[재계산] 읽은 뒤 줄이 ' + expectRows + '→' + now +
                 ' 로 바뀌었다 — 덮어쓰지 않고 물러난다(다시 읽어 맞춘다)');
      return false;
    }
  }
  sheet.getRange(2, 1, data.length, WIDE).setValues(data);
  dropRows.map(function (ri) { return ri + 2; }).sort(function (a, b) { return b - a; })
    .forEach(function (r) { sheet.deleteRow(r); });
  return true;
}

/* 한 회차만 다시 맞춘다(수동 복구용). 평상시에는 recomputeAllExams 가 돈다. */
function recomputeExam(title, baseTotals, qCount) {
  /* 여기도 겹치면 다시 읽어서 다시 맞춘다 — recomputeAllExams 와 같은 이유다. */
  for (var t = 1; t <= 3; t++) {
    var sheet = _gradeSheet();
    if (!sheet) return false;
    var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, WIDE).getValues();
    if (_flushRows(sheet, data, _recalcRows(data, title, baseTotals, qCount), data.length)) return true;
    Logger.log('recomputeExam · ' + title + ' 겹친 저장 ' + t + '번째 — 다시 읽어 맞춘다');
  }
  _bookRecompute_();
  return false;
}

/* ------------------------------------------------------------------
   한 회차의 행들을 **메모리 위에서** 다시 계산한다. 시트는 건드리지 않고,
   지워야 할 행 번호(data 기준 0-based)만 돌려준다. 여러 회차를 한 번의
   읽기·쓰기로 처리하려고 이렇게 갈라 놓았다.

   백분위·석차·전체누적인원은 저장하는 그 순간의 인원으로 한 번 계산되어
   행에 박제된다. 그래서 학생이 며칠에 걸쳐 응시하면 같은 점수인데도
   먼저 본 학생과 나중에 본 학생의 인원이 제각각(40, 44, 48 …)이 된다.
   여기서 모든 행을 "하나의 최종 코호트"에 대해 다시 계산해 맞춘다.
   ------------------------------------------------------------------ */
function _recalcRows(data, title, baseTotals, qCount) {
  // 열: [0]시험 [1]이름 [2]링크 [3]저장시각 [4]수험번호 [5]응시일 [6]학교 [7]학년
  //     [8]원점수 [9]만점 [10]백점환산 [11]백분위 [12]석차 [13]전체누적인원 [14]맞은개수 [15]영역별 [16]답안 [17]성적표문자
  var idx = [];
  for (var i = 0; i < data.length; i++) { if (String(data[i][0]) === title) idx.push(i); }
  if (!idx.length) return [];

  // 1) 완전 중복(이름+답안) 제거 — 저장시각 최신 1건만 유지
  var ts = function (ri) { return (data[ri][3] instanceof Date) ? data[ri][3].getTime() : 0; };
  var order = idx.slice().sort(function (a, b) { return ts(b) - ts(a); });
  var seen = {}, dropRows = [];
  order.forEach(function (ri) {
    var sig = _normName(data[ri][1]) + '|' + String(data[ri][16] || '').replace(/^'/, '').replace(/[^0-4]/g, '');
    if (seen[sig]) dropRows.push(ri); else seen[sig] = true;
  });
  var keep = idx.filter(function (ri) { return dropRows.indexOf(ri) < 0; });

  // 2) 학교명 오타 교정
  keep.forEach(function (ri) { var s = String(data[ri][6] || ''); if (_SCHOOL_FIX[s]) data[ri][6] = _SCHOOL_FIX[s]; });

  // 3) 코호트 = 기준분포 + 학생별 최신 1건
  //    누가 같은 학생인가는 **이름·학교·학년이 모두 같을 때**다(선생님이 정한 규칙,
  //    final.html 의 rosterKey 와 같다). 예전에는 이름만 봤다 — 동명이인 둘이
  //    한 사람으로 합쳐져 인원이 한 명 모자랐다.
  var latest = {};
  keep.forEach(function (ri) {
    var nm = _normName(data[ri][1]); if (!nm) return;
    var who = _whoKey(data[ri]);
    var t = ts(ri), tot = Number(data[ri][8]) || 0;
    if (!latest[who] || t >= latest[who].ts) latest[who] = { ts: t, total: tot };
  });
  var cohort = (baseTotals || []).slice();
  for (var who in latest) cohort.push(latest[who].total);

  /* 연도별 코호트. 누적 석차는 몇 해치가 섞여 있어서 "올해 우리 학생들
     안에서는 몇 등이냐" 를 답하지 못한다. 저장한 해로 갈라 따로 센다.
     기준분포(baseTotals)는 지난 회차의 응시 결과라 여기 넣지 않는다.
     저장시각이 없는 옛 행은 어느 해인지 알 수 없으니 뺀다 — 모르는 것을
     올해로 세면 반 석차가 소리 없이 부풀어 오른다. */
  var byYear = {};
  for (var who2 in latest) {
    var y2 = _yearOf(latest[who2].ts); if (!y2) continue;
    (byYear[y2] = byYear[y2] || []).push(latest[who2].total);
  }

  // 4)+5) 각 행 재계산 및 문자 재작성
  keep.forEach(function (ri) {
    var total = Number(data[ri][8]) || 0;
    var rp = _rankPct(total, cohort);
    var pct = _fmtNum(rp.pct);
    data[ri][11] = pct;       // 백분위
    data[ri][12] = rp.rank;   // 석차
    data[ri][13] = rp.n;      // 전체누적인원
    var name = String(data[ri][1] || '');
    var max = Number(data[ri][9]) || (qCount * 3);
    var correct = Number(data[ri][14]) || 0;
    var yr = _yearOf(ts(ri)), yp = yr ? byYear[yr] : null;
    var yrp = yp ? _rankPct(total, yp) : null;
    data[ri][MSG_COL - 1] = _msgExam(title, name, total, max, data[ri][10], correct, qCount,
                            pct, rp.rank, rp.n, String(data[ri][2] || ''), data[ri][RAW_COL - 1],
                            yr, yrp);
  });

  Logger.log(title + ' · 유지 ' + keep.length + '행 · 중복삭제 ' + dropRows.length
    + '행 · 코호트 ' + cohort.length + '명(기준 ' + (baseTotals || []).length
    + ' + 학생 ' + Object.keys(latest).length + ')');
  return dropRows;
}

/* ============================================================
   트리거 원클릭 설치 · 상태 확인
   ------------------------------------------------------------
   setupAllTriggers : 편집기에서 1회 실행 → 아래 트리거를 전부 설치(중복 자동 제거)
     · recomputeAllExams  매일 새벽 5시(KST) — 안전망.
       평상시 재계산은 **저장하는 즉시** doPost 가 모든 회차를 맞춘다. 겹쳐서
       물러나면 다시 읽어 세 번까지 다시 맞추고, 그래도 겹치면 recomputeSoon
       예약(30초 뒤)이 마무리한다. 이 트리거를 기다릴 일은 없다.
       남겨 두는 이유는 하나뿐이다 — 스프레드시트를 손으로 고치면 앱은 그걸
       모르고, 다음 저장이 없으면 그 손질이 반영되지 않는다.
       예전에는 조준모의고사 0회만 도는 recomputeJ0 가 걸려 있었다.
     · recomputeSoon  여기서 설치하지 않는다. 필요할 때만 스스로 걸고, 돌면서
       자기를 지운다(1회용).
   triggerStatus   : 현재 설치된 트리거 목록을 로그로 출력(설치 여부 확인용)
   ============================================================ */
function setupAllTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    var h = t.getHandlerFunction();
    if (h === 'recomputeJ0' || h === 'recomputeAllExams') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('recomputeAllExams').timeBased()
    .everyDays(1).atHour(5).inTimezone('Asia/Seoul').create();
  Logger.log('설치 완료: recomputeAllExams 매일 05시(KST) 백업 재계산');
  triggerStatus();
}

function triggerStatus() {
  var ts = ScriptApp.getProjectTriggers();
  if (!ts.length) { Logger.log('설치된 트리거 없음'); return; }
  ts.forEach(function (t) {
    Logger.log('트리거: ' + t.getHandlerFunction() + ' · ' + t.getEventType());
  });
  Logger.log('총 ' + ts.length + '개 트리거 설치됨');
}

/* ============================================================
   성적 분석 개인화 문자 생성 → '성적문자' 탭 A열에 작성
   ------------------------------------------------------------
   '성적기록'의 각 행(이름·시험·백점환산·백분위·맞은개수·영역별 득점·링크)을
   읽어, 회차별 다룬 내용 + 학생 개별 강·약점 + 성적분석 + 명언 + 마무리 +
   성적표 링크가 자연스럽게 녹은 문자를 만들어 별도 탭 '성적문자'의
   맨 왼쪽(A열)에 한 셀씩 채운다. (데이터 시트 구조는 건드리지 않음)

   실행:  학생/교사가 답안을 제출할 때마다 doPost가 자동으로 호출한다.
          (수동으로 다시 채우려면 편집기에서 fillReportMessages 선택 → 실행)
   ============================================================ */
var MSG_EXAMS = {
  'JMChC 모의고사 1회': { topic: '양적관계·몰과부피·원소분석장치·방사성붕괴·화학식량', mode: 'tier' },
  'JMChC 모의고사 2회': { topic: '몰과부피·양적관계·화학식량·원소분석장치·방사성붕괴', mode: 'perc' },
  'JMChC 모의고사 3회': { topic: '이온화에너지·분자의모양·원자반지름·분자의구조·수소스펙트럼', mode: 'perc' },
  'JMChC 모의고사 4회': { topic: '이온화에너지·분자의모양·원자반지름·전기음성도', mode: 'perc' },
  'JMChC 모의고사 5회': { topic: '쌍극자모멘트·산화환원반응·산과염기·탄소화합물·산화수', mode: 'perc' },
  'JMChC 모의고사 6회': { topic: '쌍극자모멘트·산화환원반응·반응성·아미노산·탄소화합물', mode: 'perc' },
  'JMChC 모의고사 7회': { topic: '분자운동속도·실제기체·용액의농도·분자간인력·액체', mode: 'perc' },
  'JMChC 모의고사 8회': { topic: '실제기체·분자운동속도·고체의구조·용액의농도·끓는점', mode: 'perc' },
  'JMChC 모의고사 9회': { topic: '깁스자유에너지·평형상수·평형농도·엔탈피·결합에너지', mode: 'perc' },
  'JMChC 모의고사 10회': { topic: '깁스자유에너지·조건반대·결합에너지·삼투압·평형상수', mode: 'perc' },
  'JMChC 모의고사 11회': { topic: 'pH·용해도·중화반응·상평형·용해평형', mode: 'perc' },
  'JMChC 모의고사 11-1회': { topic: 'pH·용해도·중화반응·상평형·용해평형', mode: 'perc' },
  '산과염기 60제': { topic: 'pH·평형상수·염의액성·중화반응·완충용액', mode: 'perc' },
  'JMChC 모의고사 12회': { topic: '염의가수분해·중화반응·용해도·상평형·용해평형', mode: 'perc' },
  'JMChC 모의고사 13회': { topic: '에너지·속도론·분자오비탈·기타·배위화학', mode: 'perc' },
  'JMChC 모의고사 14회': { topic: '기타·반응차수·분자오비탈·전지·에너지', mode: 'perc' },
  '기출동형 1회': { topic: '열화학·산과염기·원자모형·분자의모양·산화환원', mode: 'perc' },
  '기출동형 2회': { topic: '산과염기·원자모형·열화학·반응속도', mode: 'perc' },
  '기출동형 3회': { topic: '산과염기·원자모형·분자의모양·기체', mode: 'perc' },
  '기출동형 4회': { topic: '산과염기·분자의모양·열화학·몰과양적관계·원자모형', mode: 'perc' },
  'KMChC 2026 제1차 · 심화': { topic: '산화환원·반응속도·고체·분자의모양·열화학', mode: 'perc' },
  'KMChC 2025 제2차 · 심화': { topic: '반응속도·화학평형·산화환원·열화학', mode: 'perc' },
  'KMChC 2025 제1차 · 일반': { topic: '산화환원·원자모형·분자의모양·기체·주기율', mode: 'perc' },
  'KMChC 2025 제1차 · 심화': { topic: '기체·분자의모양·액체,용액·산화환원·원자모형', mode: 'perc' },
  'KMChC 2024 제2차': { topic: '열화학·산화환원·원자모형·분자의모양·기체', mode: 'perc' },
  'KMChC 2024 제1차': { topic: '분자의모양·산화환원·반응속도·몰과양적관계·열화학', mode: 'perc' },
  '화올 2024': { topic: '분자의모양·산화환원·반응속도·몰과양적관계·열화학', mode: 'perc' },
  'KMChC 2024 제1차 · 동형 2세트': { topic: '분자의모양·산화환원·반응속도·몰과양적관계·열화학', mode: 'perc' },
  'KMChC 2023': { topic: '열화학·화학평형·몰과양적관계·산과염기·산화환원', mode: 'perc' },
  '화올 2023': { topic: '열화학·화학평형·몰과양적관계·산과염기·산화환원', mode: 'perc' },
  'KMChC 2022': { topic: '원자모형·액체,용액·열화학·반응속도·고체', mode: 'perc' },
  '화올 2022': { topic: '원자모형·액체,용액·열화학·반응속도·고체', mode: 'perc' },
  'KMChC 2021': { topic: '열화학·액체,용액·원자모형·분자의모양·고체', mode: 'perc' },
  '화올 2021': { topic: '열화학·액체,용액·원자모형·분자의모양·고체', mode: 'perc' },
  'KMChC 2019': { topic: '산과염기·원자모형·분자의모양·고체·열화학', mode: 'perc' },
  '화올 2019': { topic: '산과염기·원자모형·분자의모양·고체·열화학', mode: 'perc' },
  'KMChC 2019 · 동형 2세트': { topic: '산과염기·원자모형·분자의모양·고체·열화학', mode: 'perc' },
  'KMChC 2018': { topic: '반응속도·원자모형·몰과양적관계·분자의모양·산화환원', mode: 'perc' },
  '화올 2018': { topic: '반응속도·원자모형·몰과양적관계·분자의모양·산화환원', mode: 'perc' },
  'KMChC 2018 · 동형 2세트': { topic: '반응속도·원자모형·몰과양적관계·분자의모양·산화환원', mode: 'perc' },
  'KMChC 2017': { topic: '산과염기·분자의모양·원자모형·열화학·기체', mode: 'perc' },
  '화올 2017': { topic: '산과염기·분자의모양·원자모형·열화학·기체', mode: 'perc' },
  'KMChC 2016': { topic: '산과염기·원자모형·열화학·반응속도', mode: 'perc' },
  '화올 2016': { topic: '산과염기·원자모형·열화학·반응속도', mode: 'perc' },
  'KMChC 2015': { topic: '열화학·산과염기·원자모형·분자의모양·산화환원', mode: 'perc' },
  '화올 2015': { topic: '열화학·산과염기·원자모형·분자의모양·산화환원', mode: 'perc' },
  'KMChC 2014': { topic: '산화환원·산과염기·몰과양적관계·분자의모양·기체', mode: 'perc' },
  '화올 2014': { topic: '산화환원·산과염기·몰과양적관계·분자의모양·기체', mode: 'perc' },
  'KMChC 2013': { topic: '산과염기·몰과양적관계·원자모형·분자의모양·열화학', mode: 'perc' },
  '화올 2013': { topic: '산과염기·몰과양적관계·원자모형·분자의모양·열화학', mode: 'perc' },
  'KMChC 2012': { topic: '분자의모양·고체의구조·고체·기체·양적관계', mode: 'perc' },
  'KMChC 2011': { topic: '분자의모양·반응속도·평형상수·화학평형·양적관계', mode: 'perc' },
  'KMChC 2010': { topic: '열역학·원자모형·양적관계·기체·분자의모양', mode: 'perc' },
  'KMChC 2009': { topic: '열역학·산화환원·원자모형·산과염기·화학평형', mode: 'perc' },
  'KMChC 2026 제1차 · 일반': { topic: '산화환원·분자의모양·반응속도·고체·열화학', mode: 'perc' },
  'KMChC 2025 제2차 · 일반': { topic: '반응속도·화학평형·분자의모양·열화학·원자모형', mode: 'perc' },
  '조준모의고사 0회': { topic: '화학 전 범위(원자의 구조·주기율·화학 결합·기체·열화학·용액·산화환원)를 아우르는 중등 화올 종합 진단', mode: 'perc' },
};
var MSG_CUT = [0, 4, 9, 13, 18], MSG_TIERS = ['대상', '금상', '은상', '동상', '장려상'];
/* 명언 풀 — 학생마다 다른 명언이 붙도록 밴드별로 넉넉하게. fillReportMessages가
 * 밴드별 순차 배정(_band 카운터)으로 나눠 주므로 같은 밴드 학생끼리도 겹치지 않는다. */
var MSG_QUOTES = {
  high: [
    '“재능은 노력을 이기지 못하고, 노력은 즐기는 자를 이기지 못한다.”',
    '“정상에 오르는 길은 늘 오르막이다 — 지금의 실력이 그 증거입니다.”',
    '“탁월함은 습관이다 — 오늘의 정답들이 그 습관을 증명합니다.”',
    '“높이 나는 새가 멀리 본다 — 지금의 시야를 더 넓혀 갑시다.”',
    '“실력은 조용히 쌓이고, 결정적인 순간에 말한다.”',
    '“최고의 자리는 오르는 것보다 지키는 것이 어렵다 — 그 도전을 응원합니다.”',
    '“아는 것을 완벽히 하는 사람만이 모르는 것을 정복한다.”',
    '“천재는 1%의 영감과 99%의 노력 — 지금 그 99%가 보입니다.”',
    '“강물은 바위를 힘이 아니라 끈기로 뚫는다.”',
    '“배움에는 끝이 없고, 정상에도 더 높은 봉우리가 있다.”',
    '“좋은 성적은 목적지가 아니라 더 큰 도약의 출발점입니다.”',
    '“디테일이 완성을 만든다 — 남은 오답 하나가 최상위를 가릅니다.”',
    '“실력자는 쉬운 문제에서 방심하지 않는다.”',
    '“오늘의 최고 점수를 내일의 기본기로 삼읍시다.”',
    '“정확함은 재능이 아니라 훈련의 결과입니다.”',
    '“앞서가는 사람일수록 더 겸손하게 복습한다.”',
    '“한 발 앞선 사람이 결국 열 발 앞선다.”',
    '“잘하는 것을 넘어, 남을 이끄는 실력으로 나아갑시다.”'
  ],
  mid: [
    '“천 리 길도 한 걸음부터 — 오늘 짚은 한 개념이 내일의 실력이 됩니다.”',
    '“꾸준함은 재능을 이깁니다 — 지금의 방향이 맞습니다.”',
    '“성장은 어제의 나를 넘어서는 데서 시작됩니다.”',
    '“느리게 가도 멈추지 않으면 반드시 도착합니다.”',
    '“오늘 메운 개념 하나가 다음 시험의 한 문제를 살립니다.”',
    '“실력은 계단처럼 오릅니다 — 지금은 한 칸을 딛는 중입니다.”',
    '“방향이 옳다면 속도는 문제가 되지 않습니다.”',
    '“어제보다 한 문제 더 — 그 차이가 결국 등수를 바꿉니다.”',
    '“노력은 배신하지 않습니다 — 지금의 땀이 곧 답이 됩니다.”',
    '“계속하는 힘이 재능보다 멀리 갑니다.”',
    '“작은 습관이 큰 실력을 만든다 — 오늘의 복습이 그 시작입니다.”',
    '“오르막이 힘든 건 위로 가고 있다는 증거입니다.”',
    '“한 걸음씩이면 어떤 정상도 오를 수 있습니다.”',
    '“아직 도착하지 않았을 뿐, 가는 방향은 정확합니다.”',
    '“매일의 1%가 쌓이면 100일 뒤 완전히 다른 실력이 됩니다.”',
    '“배움은 채우는 게 아니라 쌓는 것 — 지금 잘 쌓이고 있습니다.”',
    '“포기하지 않는 평범함이 포기하는 비범함을 이깁니다.”',
    '“오늘의 노력은 내일의 여유가 됩니다.”'
  ],
  low: [
    '“틀린 문제는 가장 좋은 스승입니다 — 오늘의 오답이 내일의 정답이 됩니다.”',
    '“실패는 성공의 어머니 — 지금 메우는 개념 하나가 판을 바꿉니다.”',
    '“시작이 반이다 — 오늘 한 걸음을 뗀 것만으로 충분히 잘했습니다.”',
    '“넘어진 자리에서 일어서면, 그 자리가 출발선이 됩니다.”',
    '“가장 어두운 새벽 뒤에 아침이 옵니다 — 지금이 그 새벽입니다.”',
    '“모르는 것을 아는 것이 배움의 첫걸음입니다 — 오늘 그 걸음을 뗐습니다.”',
    '“천 번을 넘어져도 천한 번 일어서면 됩니다.”',
    '“오늘의 부족함은 내일 채우면 될 여백일 뿐입니다.”',
    '“뿌리가 깊은 나무는 늦게 자라도 크게 자랍니다.”',
    '“한 개념씩 다시 세우면 반드시 단단해집니다.”',
    '“지금의 오답 하나하나가 실력의 지도를 그려 줍니다.”',
    '“늦게 피는 꽃이 오래 갑니다 — 기초부터 차근차근 갑시다.”',
    '“어제의 나와 비교하세요 — 오늘 이미 한 걸음 나아갔습니다.”',
    '“기초가 튼튼하면 어떤 문제도 결국 풀립니다.”',
    '“포기만 하지 않으면 실패는 과정일 뿐입니다.”',
    '“작은 이해 하나가 쌓여 큰 실력이 됩니다 — 그 시작을 응원합니다.”',
    '“오르막의 시작은 늘 가장 가파릅니다 — 여기만 넘으면 쉬워집니다.”',
    '“다시 도전하는 용기가 재능보다 값집니다.”'
  ]
};
/* ── 문장 돌려 쓰기 ────────────────────────────────────────────────────
   문자에서 인사·안내·마무리가 매번 글자 하나까지 똑같이 나갔다. 명언만
   돌아가고 나머지는 고정이라, 같은 학부모가 회차마다 같은 문장을 받았다.
   "방향이 정확합니다. 오답 개념만 촘촘히 메우면…" 이 대표적이다.

   그래서 자리마다 여러 벌을 두고, **시험 제목 + 학생 이름**으로 고른다.
   - 같은 회차의 학생끼리 서로 다른 문장을 받는다
   - 같은 학생이 다음 회차에는 다른 문장을 받는다(제목이 바뀌므로)
   - 다시 돌려도 같은 학생·같은 회차면 같은 문장이 나온다(고쳐 보내도 안 튄다)

   문장을 더 넣고 싶으면 그냥 목록에 한 줄 추가하면 된다.
   {이름}·{제목}·{범위}·{강점}·{보완} 자리는 _fill 이 채운다. */
var MSG_OPEN = [
  '안녕하세요. 화학올림피아드 담당하는 조준모입니다.',
  '안녕하세요, 학부모님. 화학올림피아드를 맡고 있는 조준모입니다.',
  '안녕하세요. 다원교육 영재관에서 화학올림피아드를 지도하는 조준모입니다.',
  '학부모님, 안녕하세요. 화학올림피아드 담당 조준모입니다.',
  '안녕하세요. 이번 회차 채점을 마치고 연락드립니다. 화학올림피아드 담당 조준모입니다.',
  '안녕하세요. 화학올림피아드반 조준모입니다. 이번 시험 결과 전해 드립니다.'
];
var MSG_LEAD = [
  '{이름} 학생의 「{제목}」 성적표입니다. 아래 링크에서 문항별 정오와 개념 클리닉, 학습 처방을 확인하실 수 있습니다.',
  '{이름} 학생의 「{제목}」 결과를 정리해 보내 드립니다. 링크를 열면 문항별 정오표와 오답 개념 클리닉, 다음 학습 처방이 함께 담겨 있습니다.',
  '「{제목}」 채점이 끝나 {이름} 학생 성적표를 보내 드립니다. 아래 링크에 문항별 정오와 틀린 개념 해설, 학습 처방을 담았습니다.',
  '{이름} 학생의 「{제목}」 성적표를 아래 링크에 올려 두었습니다. 문항별 정오, 오개념 진단, 다음 학습 순서까지 한 번에 보실 수 있습니다.',
  '「{제목}」 {이름} 학생 성적표입니다. 링크에서 어떤 문항을 왜 틀렸는지, 무엇부터 복습해야 하는지 확인하실 수 있습니다.',
  '{이름} 학생의 「{제목}」 성적표가 준비됐습니다. 아래 링크 하나에 정오표·오개념 해설·학습 처방을 모두 모아 두었습니다.'
];
var MSG_TOPIC = [
  '오늘은 {범위}{을} 다룬 시험이었습니다.',
  '이번 회차는 {범위} 중심으로 출제했습니다.',
  '이번 시험은 {범위}에서 골고루 물었습니다.',
  '{범위}{을} 얼마나 자기 것으로 만들었는지 보는 회차였습니다.',
  '이번엔 {범위}에서 손이 실제로 움직이는지를 확인했습니다.',
  '출제 범위는 {범위}였습니다.'
];
var MSG_STRONG = {
  some: [
    '특히 {강점} 영역에서 안정적인 강점을 보였습니다.',
    '{강점} 영역은 흔들림이 없었습니다.',
    '{강점}에서는 개념이 확실히 자리 잡은 모습입니다.',
    '{강점} 영역은 이미 득점원으로 삼아도 좋겠습니다.',
    '{강점}{을} 다루는 손이 안정적입니다.',
    '{강점} 쪽은 이번에도 제 몫을 했습니다.'
  ],
  none: [
    '전 영역에서 고르게 응답했습니다.',
    '어느 한 영역에 치우치지 않고 고른 분포를 보였습니다.',
    '영역별 편차 없이 비슷한 수준으로 답했습니다.',
    '아직 뚜렷한 주무기가 드러나지는 않았습니다.'
  ]
};
var MSG_WEAK = {
  some: [
    '반면 {보완} 영역은 보완이 필요합니다 — 아래 성적표의 개념 클리닉으로 우선 복습을 권합니다.',
    '다만 {보완}에서 점수가 많이 샜습니다. 성적표의 개념 클리닉부터 짚어 주세요.',
    '{보완}{은} 개념부터 다시 세워야 합니다. 링크의 오답 클리닉에 문항별로 정리해 두었습니다.',
    '가장 급한 곳은 {보완}입니다. 성적표에서 그 부분만 먼저 보셔도 좋습니다.',
    '{보완}에서 반복해 걸렸습니다 — 같은 유형을 한 번 더 풀어 보게 해 주세요.',
    '{보완}{은} 이번 등급을 좌우한 영역입니다. 개념 클리닉을 우선 순위로 잡았습니다.'
  ],
  none: [
    '뚜렷한 취약 영역 없이 균형이 좋습니다. 심화 문항으로 난도를 올려 보세요.',
    '무너진 영역이 없습니다. 이제는 난도를 올려 시험할 때입니다.',
    '어느 영역도 크게 비어 있지 않습니다. 다음은 고난도 문항에서의 정확도입니다.',
    '균형이 잡혀 있어 특별히 급한 보강은 없습니다. 응용 문항으로 넓혀 가겠습니다.'
  ]
};
var MSG_CLOSE = {
  high: [
    '지금의 실력을 유지하며 고난도 문항에서의 회복력을 키우면 최상위권이 충분히 가능합니다.',
    '이 수준을 지키는 것 자체가 다음 목표입니다. 흔들리는 한두 문항만 잡으면 됩니다.',
    '남은 것은 실수 관리입니다. 아는 문항을 끝까지 지키는 훈련을 함께 하겠습니다.',
    '여기서부터는 어려운 문항을 몇 개 더 가져오느냐의 싸움입니다. 그 지점을 집중해 보겠습니다.',
    '기본기가 이미 단단합니다. 이제 낯선 문제 앞에서의 판단 속도를 올리겠습니다.',
    '상위권에서의 한 문항 차이는 결국 복습의 밀도에서 갈립니다. 그 부분을 챙기겠습니다.'
  ],
  mid: [
    '방향이 정확합니다. 오답 개념만 촘촘히 메우면 다음 시험에서 확실한 도약이 기대됩니다.',
    '점수를 만드는 자리와 잃는 자리가 분명히 보입니다. 잃는 쪽부터 손대면 빠르게 올라갑니다.',
    '지금 필요한 것은 새로운 진도가 아니라 틀린 개념의 회복입니다. 그 순서로 잡아 가겠습니다.',
    '아깝게 놓친 문항이 적지 않습니다. 그 몇 개를 지키는 것만으로 등급이 달라집니다.',
    '기초는 서 있습니다. 이제 반복해서 걸리는 유형 하나씩만 끊어 내면 됩니다.',
    '한 번에 다 잡으려 하지 않아도 됩니다. 이번엔 취약 영역 하나만 확실히 끝내 보겠습니다.'
  ],
  low: [
    '기초 개념부터 하나씩 다시 세우면 반드시 오릅니다. 끝까지 함께 책임지고 끌어올리겠습니다.',
    '지금은 점수보다 개념을 다시 세울 때입니다. 성적표의 순서대로 천천히 따라오면 됩니다.',
    '어디가 비어 있는지가 이번 시험으로 분명해졌습니다. 그 자리를 하나씩 메우겠습니다.',
    '조급해하지 않으셔도 됩니다. 밑돌부터 다시 놓으면 뒤에 훨씬 빨리 올라옵니다.',
    '틀린 문항이 곧 다음 수업의 교재입니다. 하나씩 확실히 끝내 가겠습니다.',
    '이 시기의 부진은 흔한 과정입니다. 개념 회복만 붙들면 반드시 따라옵니다.'
  ]
};

/* 이름·제목으로 뽑는다. 같은 사람 같은 회차면 언제 돌려도 같은 문장이 나온다.

   ⚠ 여기서 **문장 은행의 절반이 죽어 있었다.**
   FNV-1a 는 마지막 한 글자의 홀짝이 결과의 가장 낮은 자리에 거의 그대로
   남는다. 그런데 자리마다 열쇠 끝이 '|l'·'|t' 처럼 **고정**이라, 6 으로
   나누면 짝수 번호만 나왔다. 400명 × 38회차로 재어 보니:

       MSG_LEAD  0번 33.0% · 1번 0.0% · 2번 33.6% · 3번 0.0% · 4번 33.4% · 5번 0.0%
       MSG_TOPIC 0번 33.6% · 1번 0.0% · 2번 33.5% · 3번 0.0% · 4번 32.9% · 5번 0.0%

   여섯 벌을 써 놓고 **세 벌은 학부모에게 한 번도 나간 적이 없다.** 게다가
   같은 회차에서 여는 문장과 이끄는 문장의 번호가 **0.0%** 로 어긋났다 —
   서로 다른 자리인데 완전히 붙어 움직였다는 뜻이다.

   그래서 마지막에 한 번 더 섞는다(murmur3 마무리). 낮은 자리에만 남던
   규칙이 위아래로 흩어져, 나머지 연산이 고르게 갈린다. */
function _seed(s) { var h = 2166136261; s = String(s);
  for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 16777619) >>> 0; }
  h ^= h >>> 16; h = Math.imul(h, 2246822507) >>> 0;
  h ^= h >>> 13; h = Math.imul(h, 3266489909) >>> 0;
  h ^= h >>> 16;
  return h >>> 0; }
function _pick(list, key) { return list[_seed(key) % list.length]; }
function _fill(tpl, v) {
  // \w 는 한글을 잡지 못한다. {이름}·{범위} 가 그대로 찍혀 나왔다.
  return String(tpl).replace(/\{([^{}]+)\}/g, function (m, k) {
    if (k === '을') return _EL(v.__last || '');
    if (k === '은') return _EN(v.__last || '');
    var val = v[k] == null ? '' : String(v[k]);
    v.__last = val;
    return val;
  });
}
function _band(pct100) { return pct100 >= 80 ? 'high' : (pct100 >= 55 ? 'mid' : 'low'); }
function _hasJong(s) { s = String(s).replace(/[)\]」』”"'’\s]+$/, ''); var ch = s.charAt(s.length - 1); if (!ch) return false;
  var c = ch.charCodeAt(0); if (c < 0xAC00 || c > 0xD7A3) { var m = { '0':0,'1':1,'2':0,'3':1,'4':0,'5':0,'6':1,'7':1,'8':1,'9':0 }; return !!m[ch]; }
  return (c - 0xAC00) % 28 !== 0; }
function _EN(s) { return _hasJong(s) ? '은' : '는'; }
function _EL(s) { return _hasJong(s) ? '을' : '를'; }
function _parseAreas(str) {  // "원자 6/12, 열화학 0/18" → [{name,c,t,r}]
  return String(str || '').split(',').map(function (x) {
    var m = x.trim().match(/^(.+?)\s+(\d+)\s*\/\s*(\d+)$/); if (!m) return null;
    var c = +m[2], t = +m[3]; return { name: m[1].trim(), c: c, t: t, r: t ? c / t : 0 };
  }).filter(function (a) { return a; });
}
function _award(wrong) { var idx = -1; for (var i = 0; i < MSG_CUT.length; i++) { if (wrong <= MSG_CUT[i]) { idx = i; break; } }
  if (idx < 0) return { name: '수상권 밖', inA: false, need: Math.max(1, wrong - MSG_CUT[4]) };
  return { name: MSG_TIERS[idx], inA: true, next: idx > 0 ? MSG_TIERS[idx - 1] : null, gap: idx > 0 ? wrong - MSG_CUT[idx - 1] : 0 }; }

/* 문항 수는 회차마다 다르다(60문항 32개 · 50문항 6개). 60을 박아 두면
   50문항 회차 학생이 40/50 을 맞히고도 학부모는 '정답 40/60' 을 받는다.
   시트 9열(만점)에 앱이 보낸 문항 수가 들어 있고, 없으면 EXAM_COHORT 로 찾는다. */
function _qCountOf(title, max) {
  var n = Number(max) || 0;
  if (n > 0 && n <= 200) return n;
  var cfg = _recomputeConfigFor(title);
  return (cfg && cfg.qCount) || 60;
}

function _buildReportMsg(title, name, correct, pct100, perc, areasStr, link, qi, qCount, raw) {
  var cfg = MSG_EXAMS[title] || { topic: '화학 개념과 문제 해결', mode: 'perc' };
  var nQ = qCount || 60;
  var nm = name || '학생', wrong = nQ - correct;
  var band = _band(pct100);
  /* 원점수는 **앱이 보내 준 값만** 쓴다. 예전에는 correct*3 으로 계산했는데,
     오답 감점이 있는 회차(KMChC·동형 등 23개)에서는 그만큼 부풀려 나간다.
     값이 없는 옛 행은 원점수를 아예 말하지 않는다 — 지어내지 않는다. */
  var rawTxt = (raw === '' || raw == null || isNaN(Number(raw)))
    ? '' : '원점수 ' + Number(raw) + '/' + (nQ * 3) + '점, ';
  var analysis;
  if (cfg.mode === 'tier') {
    var aw = _award(wrong);
    if (aw.inA) analysis = rawTxt + '정답 ' + correct + '/' + nQ + '문항, 틀린 문항 ' + wrong + '개로 현재 ' + aw.name + '권입니다'
      + (aw.next && aw.gap <= 2 ? '. ' + aw.gap + '문항만 더 지키면 ' + aw.next + '권입니다.' : '.');
    else analysis = rawTxt + '정답 ' + correct + '/' + nQ + '문항입니다. 장려상까지 ' + aw.need + '문항 — 오답 ' + aw.need + '개 유형만 회복하면 수상권에 진입합니다.';
  } else {
    analysis = rawTxt + '정답 ' + correct + '/' + nQ + '문항(백점환산 ' + pct100 + '점)으로'
      + ((perc !== '' && perc != null) ? ' 누적 응시자 기준 백분위 ' + perc + '입니다.' : ' 집계되었습니다.');
  }
  var areas = _parseAreas(areasStr), able = areas.filter(function (a) { return a.t >= 2; });
  var strong = able.filter(function (a) { return a.r >= 0.8; }).sort(function (x, y) { return y.r - x.r; }).slice(0, 3).map(function (a) { return a.name; });
  var weak = able.filter(function (a) { return a.r < 0.5; }).sort(function (x, y) { return x.r - y.r; }).slice(0, 3).map(function (a) { return a.name; });
  // 자리마다 여러 벌 중 하나를 고른다. 열쇠는 '회차 + 이름' 이라
  // 같은 회차의 학생끼리, 또 같은 학생의 회차끼리 문장이 겹치지 않는다.
  var key = title + '|' + nm;
  var V = { 이름: nm, 제목: title, 범위: cfg.topic, 강점: strong.join(', '), 보완: weak.join(', ') };
  var strongTxt = _fill(_pick(strong.length ? MSG_STRONG.some : MSG_STRONG.none, key + '|s'), V);
  var weakTxt = _fill(_pick(weak.length ? MSG_WEAK.some : MSG_WEAK.none, key + '|w'), V);
  var closing = _fill(_pick(MSG_CLOSE[band], key + '|c'), V);
  // 명언은 밴드 안에서 차례로 돌리되(한 번에 보내는 묶음 안에서 안 겹치게),
  // 회차마다 시작점을 옮긴다. 그러지 않으면 첫 학생은 늘 같은 명언을 받는다.
  var quote = MSG_QUOTES[band][(qi + _seed(title)) % MSG_QUOTES[band].length];
  // 링크를 문자 앞쪽에 배치(카톡 링크 미리보기가 첫 URL을 잡도록).
  return [_pick(MSG_OPEN, key + '|o'),
    _fill(_pick(MSG_LEAD, key + '|l'), V),
    link,
    _fill(_pick(MSG_TOPIC, key + '|t'), V),
    nm + ' 학생은 ' + analysis,
    strongTxt + ' ' + weakTxt,
    quote, closing,
    '— 다원교육 영재관 · 화학 조준모 올림'].join('\n');
}

function fillReportMessages() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var src = ss.getSheetByName('성적기록');
  if (!src || src.getLastRow() < 2) { Logger.log('성적기록 시트가 비어 있습니다.'); return; }
  var data = src.getRange(2, 1, src.getLastRow() - 1, WIDE).getValues();
  var out = ss.getSheetByName('성적문자') || ss.insertSheet('성적문자');
  out.clear();
  var head = ['성적표 문자(복사용)', '이름', '학교', '학년', '시험', '정답', '백점환산', '공유링크'];
  out.appendRow(head);
  out.getRange(1, 1, 1, head.length).setFontWeight('bold').setBackground('#0E5A4C').setFontColor('#ffffff');
  out.setFrozenRows(1);
  var rows = [], bands = [], bandCtr = { high: 0, mid: 0, low: 0 };
  for (var i = 0; i < data.length; i++) {
    var r = data[i], title = String(r[0] || ''); if (!title) continue;
    var name = String(r[1] || ''), link = String(r[2] || ''), school = String(r[6] || ''), grade = String(r[7] || '');
    var pct100 = r[10], perc = r[11], correct = Number(r[14]) || 0, areasStr = String(r[15] || '');
    // 밴드별 순차 배정 → 같은 성취 밴드 학생끼리도 명언이 겹치지 않음
    var bd = _band(pct100), qi = bandCtr[bd]++;
    var nQ = _qCountOf(title, r[9]);
    var msg = _buildReportMsg(title, name, correct, pct100, perc, areasStr, link, qi, nQ, r[RAW_COL - 1]);
    rows.push([msg, name, school, grade, title, correct + '/' + nQ, pct100, link]);
    bands.push(bd);
  }
  if (rows.length) {
    var n = rows.length;
    out.getRange(2, 1, n, 8).setValues(rows);
    out.getRange(2, 1, n, 1).setWrap(true).setVerticalAlignment('top');
    out.setColumnWidth(1, 640);
    for (var w = 2; w <= 8; w++) out.setColumnWidth(w, w === 8 ? 260 : 70);

    // ── 색상: 성취 밴드(상위·중위·기초)로 한눈에 구분 ──
    // ROW = 행 전체 옅은 배경, ST = 정답·백점환산 칸 진한 강조색, FC = 강조 글자색
    var C = {
      high: { row: '#EAF4EF', st: '#CDE8DD', fc: '#0E5A4C' },   // 상위(≥80): 초록
      mid:  { row: '#FBF5E7', st: '#F5E4BE', fc: '#8A6D1F' },   // 중위(55~79): 황금
      low:  { row: '#FBEBE7', st: '#F4D4CC', fc: '#B3452B' }    // 기초(<55): 주황
    };
    var rowBg = [], stBg = [], stFc = [];
    for (var k = 0; k < n; k++) {
      var c = C[bands[k]] || C.mid;
      rowBg.push([c.row, c.row, c.row, c.row, c.row, c.st, c.st, '#ffffff']); // 문자·이름·학교·학년·시험 옅게, 정답·백점 진하게, 링크 흰색
      stBg.push([c.st]); stFc.push([c.fc]);
    }
    out.getRange(2, 1, n, 8).setBackgrounds(rowBg);
    // 정답·백점환산: 가운데 정렬 + 굵게 + 밴드 글자색
    out.getRange(2, 6, n, 2).setHorizontalAlignment('center').setFontWeight('bold');
    out.getRange(2, 6, n, 1).setFontColors(stFc);
    out.getRange(2, 7, n, 1).setFontColors(stFc);
    // 이름 굵게, 학교·학년·시험 가운데 정렬
    out.getRange(2, 2, n, 1).setFontWeight('bold');
    out.getRange(2, 3, n, 3).setHorizontalAlignment('center');
    // 테두리(행 구분이 또렷하게)
    out.getRange(1, 1, n + 1, 8).setBorder(true, true, true, true, true, true, '#D8D2C4', SpreadsheetApp.BorderStyle.SOLID);
  }
  // 범례: 오른쪽 여백에 밴드 색 안내
  out.getRange(1, 10).setValue('색 안내').setFontWeight('bold');
  out.getRange(2, 10).setValue('상위 ≥80').setBackground('#CDE8DD').setFontColor('#0E5A4C').setFontWeight('bold').setHorizontalAlignment('center');
  out.getRange(3, 10).setValue('중위 55~79').setBackground('#F5E4BE').setFontColor('#8A6D1F').setFontWeight('bold').setHorizontalAlignment('center');
  out.getRange(4, 10).setValue('기초 <55').setBackground('#F4D4CC').setFontColor('#B3452B').setFontWeight('bold').setHorizontalAlignment('center');
  out.setColumnWidth(10, 100);
  Logger.log('성적문자 작성 완료 · ' + rows.length + '명 (탭: 성적문자, A열=문자, 밴드별 색상 적용)');
}

/* ══════════════════════════════════════════════════════════════════════
   깃허브 자동 저장 · 자동 점검
   ----------------------------------------------------------------------
   여태 학생 응시 기록은 **이 시트에만** 있었다. 코드·문항·해설은 깃허브에
   있지만 기록은 사본이 없다. 잘못 지우거나 덮어써도 되돌릴 방법이 없었다.

   매일 한 번 시트를 통째로 깃허브에 커밋한다. 커밋 이력 자체가 "언제 무엇이
   바뀌었나" 가 되고, 잘못 건드린 날 이전으로 되돌릴 수 있다.

   ── 이름은 싣지 않는다 ────────────────────────────────────────────────
   저장소는 공개다. 학생 이름·학교가 그대로 올라가면 검색에 걸린다.
   이름 대신 **코드**를 싣는다(s7k3m2… 12자). 같은 학생은 늘 같은 코드라
   날짜별 백업끼리 견줄 수 있고, 코드만으로는 누구인지 알 수 없다.

   이름↔코드 표는 이 시트의 '_이름코드' 탭에만 둔다. 그래서:
     · 행을 잘못 지웠다 → 깃허브에서 되살리고 표로 이름을 붙인다 (완전 복구)
     · 시트를 통째로 잃었다 → 기록은 다 남지만 누구 것인지는 모른다
   구글 시트에는 버전 기록과 휴지통이 있어 통째로 잃는 일은 드물다. 이 백업이
   막으려는 것은 **잘못된 수정·삭제** 쪽이고, 거기에는 코드로 충분하다.

   ── 설치 (한 번만) ────────────────────────────────────────────────────
   1) 깃허브에서 토큰 발급 (Fine-grained, 이 저장소 Contents: Read and write)
   2) Apps Script 편집기 > 프로젝트 설정 > 스크립트 속성에 GITHUB_TOKEN 추가
   3) 편집기에서 setupBackupTriggers() 를 한 번 실행
   토큰이 없으면 아무것도 안 하고 조용히 넘어간다(채점은 그대로 돌아간다).
   ══════════════════════════════════════════════════════════════════════ */

var GH_OWNER = 'Chemistreal', GH_REPO = 'exam', GH_BRANCH = 'main';
/* 기록 탭 이름. 위쪽 코드는 문자열을 그대로 쓰고 있어 여기서만 이름을 둔다. */
var REC_TAB = '성적기록';
var CODE_TAB = '_이름코드';

function _ghToken_() {
  try { return (PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN') || '').trim(); }
  catch (e) { return ''; }
}

/* 깃허브에 파일 하나를 쓴다(있으면 덮어쓴다). 실패는 예외로 올린다 —
   조용히 넘어가면 백업이 안 되고 있는 줄도 모른다. */
function _ghPut_(path, text, message) {
  var token = _ghToken_();
  if (!token) throw new Error('GITHUB_TOKEN 스크립트 속성이 없습니다');
  var api = 'https://api.github.com/repos/' + GH_OWNER + '/' + GH_REPO + '/contents/' + path;
  var sha = '';
  try {
    var got = UrlFetchApp.fetch(api + '?ref=' + GH_BRANCH, {
      method: 'get', muteHttpExceptions: true,
      headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' } });
    if (got.getResponseCode() === 200) sha = JSON.parse(got.getContentText()).sha || '';
  } catch (e) {}
  var body = { message: message || ('자동 저장: ' + path), branch: GH_BRANCH,
               content: Utilities.base64Encode(text, Utilities.Charset.UTF_8) };
  if (sha) body.sha = sha;
  var res = UrlFetchApp.fetch(api, {
    method: 'put', contentType: 'application/json', muteHttpExceptions: true,
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' },
    payload: JSON.stringify(body) });
  var code = res.getResponseCode();
  if (code >= 300) throw new Error('깃허브 저장 실패 ' + code + ': ' + res.getContentText().slice(0, 200));
  return true;
}

/* ── 이름 → 코드 ──────────────────────────────────────────────────────
   같은 학생은 늘 같은 코드여야 한다(날짜별 백업을 견주려면). 이름을 그냥
   해시하면 이름만 알면 코드를 만들어 볼 수 있으므로, 이 프로젝트에만 있는
   소금을 섞는다. 소금은 스크립트 속성에 두고 한 번 만들면 안 바꾼다 —
   바꾸면 예전 백업의 코드와 이어지지 않는다. */
function _codeSalt_() {
  var p = PropertiesService.getScriptProperties();
  var s = p.getProperty('CODE_SALT');
  if (!s) { s = Utilities.getUuid(); p.setProperty('CODE_SALT', s); }
  return s;
}
function _codeOf_(name, school) {
  var key = _normName(name) + '|' + String(school || '').trim();
  if (!_normName(name)) return '';
  var raw = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, key + '|' + _codeSalt_(),
                                    Utilities.Charset.UTF_8);
  var s = '';
  for (var i = 0; i < raw.length && s.length < 12; i++) {
    s += ('0' + (raw[i] & 255).toString(36)).slice(-2);
  }
  return 's' + s.slice(0, 11);
}
/* 이름↔코드 표를 시트에 쌓아 둔다. 되살릴 때 이것으로 이름을 붙인다. */
function _rememberCode_(ss, map) {
  var sh = ss.getSheetByName(CODE_TAB);
  if (!sh) { sh = ss.insertSheet(CODE_TAB); sh.appendRow(['코드', '이름', '학교', '처음 본 날']);
             sh.getRange(1, 1, 1, 4).setFontWeight('bold'); sh.setFrozenRows(1); }
  var have = {};
  if (sh.getLastRow() > 1) {
    sh.getRange(2, 1, sh.getLastRow() - 1, 1).getValues().forEach(function (r) { have[String(r[0])] = 1; });
  }
  var add = [];
  for (var code in map) if (!have[code]) add.push([code, map[code].name, map[code].school, new Date()]);
  if (add.length) sh.getRange(sh.getLastRow() + 1, 1, add.length, 4).setValues(add);
  return add.length;
}

/* ── ① 응시 기록 일일 백업 ────────────────────────────────────────────
   시트 전체를 하루 한 벌 깃허브에. 이름은 코드로 바꿔 싣는다.
   같은 날 두 번 돌면 그날 파일을 덮어쓴다(하루 한 장). */
function dailyBackup() {
  if (!_ghToken_()) { Logger.log('[백업] GITHUB_TOKEN 없음 — 건너뜀'); return; }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(REC_TAB);
  if (!sh || sh.getLastRow() < 2) { Logger.log('[백업] 기록 없음'); return; }

  /* HEADER 는 17열까지지만 시트는 19열이다(성적표문자·감점 반영 원점수가 뒤에
     붙었다). HEADER.length 로 읽으면 그 둘이 백업에서 조용히 빠진다. */
  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, WIDE).getValues();
  var map = {}, out = [];
  rows.forEach(function (r) {
    var code = _codeOf_(r[1], r[6]);
    if (!code) return;                                   // 이름 없는 줄은 싣지 않는다
    map[code] = { name: String(r[1] || ''), school: String(r[6] || '') };
    out.push({
      code: code, exam: String(r[0] || ''),
      saved: (r[3] instanceof Date) ? r[3].toISOString() : String(r[3] || ''),
      date: (r[5] instanceof Date) ? Utilities.formatDate(r[5], 'Asia/Seoul', 'yyyy-MM-dd') : String(r[5] || ''),
      grade: String(r[7] || ''), correct: r[8], max: r[9], pct100: r[10],
      percentile: r[11], rank: String(r[12] || ''), n: r[13],
      areas: String(r[15] || ''),
      answers: String(r[16] || '').replace(/^'/, ''),
      raw: r[18]
      /* 이름·학교·공유링크는 싣지 않는다. 링크에는 이름이 들어 있다. */
    });
  });
  _rememberCode_(ss, map);

  var day = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd');
  var text = JSON.stringify({ savedAt: new Date().toISOString(), n: out.length,
                              note: '이름은 코드로 바꿔 저장. 이름↔코드 표는 시트의 ' + CODE_TAB + ' 탭에만 있다.',
                              rows: out }, null, 1);
  _ghPut_('backup/' + day + '.json', text, '자동 백업 ' + day + ' · ' + out.length + '건');
  Logger.log('[백업] ' + day + ' · ' + out.length + '건');
}

/* ── ② 기준 기록 자동 갱신 ────────────────────────────────────────────
   석차·또래 정답률의 모집단이다. 여태 사람이 엑셀로 만들어 넣었다. 시트가
   원본이니 여기서 만든다 — 이름은 애초에 안 들어간다(점수 분포와 정답자 수뿐).

   손으로 넣어 둔 회차는 건드리지 않는다. 엑셀에는 이 시트에 없는 옛 응시자가
   들어 있어서, 시트만으로 덮으면 모집단이 확 줄어든다.

   ⚠ 그 '건드리지 않는다' 가 **두 번 다 안 먹었다.**

     2026-08-03 04:52  또래 정답률(q·qc)이 열 회차에서 사라짐 — 4시간 빨간불
     2026-08-04 04:52  같은 일이 또. 게다가 모집단이 387명 → 225명으로 줄었다
                       (jmchc-1 은 46명 → 11명). 그 숫자로 석차가 나가고 있었다.

   `byHand` 깃발 하나에만 기댔기 때문이다. 엑셀에서 만든 회차에 그 깃발이 안
   찍혀 있으면 장치가 통째로 없는 것과 같다 — 실제로 안 찍혀 있었다. 깃발은
   사람이 기억해야 하는 것이라, 잊으면 조용히 데이터가 사라진다.

   그래서 **깃발 말고 내용을 본다.** 두 가지를 지킨다.

     ① 내가 못 만드는 것을 갖고 있으면 손대지 않는다.
        여기서 만드는 것은 n·hist 뿐이다. q·qc(문항별 통계)를 가진 회차는
        엑셀에서 온 것이고, 덮으면 그 통계가 영영 사라진다.
     ② 인원이 줄어드는 갱신은 하지 않는다.
        시트에는 옛 응시자가 없다. 46명이 11명이 되는 것은 '새 자료' 가 아니라
        **자료를 잃는 것**이다. 늘어나는 갱신만 받는다.

   둘 다 지나간 것만 갱신한다. 막힌 회차는 로그에 남긴다 — 조용히 건너뛰면
   왜 안 늘어나는지 아무도 모른다. */
function rebuildBaseline() {
  if (!_ghToken_()) { Logger.log('[기준] GITHUB_TOKEN 없음 — 건너뜀'); return; }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(REC_TAB);
  if (!sh || sh.getLastRow() < 2) return;

  var cur = {};
  try {
    var got = UrlFetchApp.fetch('https://raw.githubusercontent.com/' + GH_OWNER + '/' + GH_REPO +
                                '/' + GH_BRANCH + '/cohort/baseline.json', { muteHttpExceptions: true });
    if (got.getResponseCode() === 200) cur = JSON.parse(got.getContentText()) || {};
  } catch (e) {}
  var exams = (cur && cur.exams) || {};
  var handmade = {};
  for (var k in exams) if (exams[k] && exams[k].byHand) handmade[k] = 1;

  /* ⚠ **시험 목록(exams.json)에 있는 회차만** 만든다.
     시트에는 앱에서 내린 옛 회차의 기록도 남아 있다. 제목→id 표(EXAM_TITLES)는
     옛 제목까지 알고 있어서, 그대로 두면 목록에 없는 회차의 기준 기록이
     저절로 생긴다 — 2026-08-05 에 `j0`(조준모의고사 0회, 18명)가 그렇게
     되살아났다. 사람이 지운 것이 밤새 돌아온 것이다.
     목록을 못 읽으면 **새로 만들지 않는다**(있는 것 갱신은 그대로) —
     모르는 채로 만드는 것보다 안 만드는 편이 되돌리기 쉽다. */
  var known = null;
  try {
    var gx = UrlFetchApp.fetch('https://raw.githubusercontent.com/' + GH_OWNER + '/' + GH_REPO +
                               '/' + GH_BRANCH + '/exams.json', { muteHttpExceptions: true });
    if (gx.getResponseCode() === 200) {
      var list = JSON.parse(gx.getContentText()) || [];
      known = {};
      for (var q = 0; q < list.length; q++) if (list[q] && list[q].id) known[list[q].id] = 1;
    }
  } catch (eX) {}

  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, WIDE).getValues();
  var by = {};                                            // 시험 id → {코드: 맞은수}
  rows.forEach(function (r) {
    var id = _idOfTitle_(r[0]); if (!id) return;
    var code = _codeOf_(r[1], r[6]); if (!code) return;
    var c = Number(r[8]); if (!isFinite(c)) return;
    (by[id] || (by[id] = {}))[code] = c;                  // 같은 학생은 최신 한 번만
  });
  var made = 0, kept = [];
  for (var id in by) {
    var hist = {}, n = 0;
    for (var code in by[id]) { var s = by[id][code]; hist[s] = (hist[s] || 0) + 1; n++; }
    if (n < 2) continue;                                  // 한 명뿐이면 모집단이 아니다
    if (!exams[id]) {
      /* 새로 만드는 회차. 시험 목록에 없으면 만들지 않는다. */
      if (known === null) { kept.push(id + '(목록을 못 읽음)'); continue; }
      if (!known[id]) { kept.push(id + '(시험 목록에 없다)'); continue; }
    }
    var why = _baselineKeepWhy_(exams[id], n, handmade[id]);
    if (why) { kept.push(id + '(' + why + ')'); continue; }
    exams[id] = { n: n, hist: hist, from: 'sheet',
                  at: Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd') };
    made++;
  }
  if (kept.length) Logger.log('[기준] 그대로 둔 회차: ' + kept.join(', '));
  if (!made) { Logger.log('[기준] 새로 만들 회차 없음'); return; }
  _ghPut_('cohort/baseline.json', JSON.stringify({ exams: exams }, null, 1),
          '기준 기록 자동 갱신 · ' + made + '회차');
  Logger.log('[기준] ' + made + '회차 갱신');
}

/* 이 회차를 그대로 둘 이유. 없으면 빈 문자열(= 갱신해도 된다).
   ⚠ 여기가 이 장치의 전부다. 세 줄이지만 두 번의 사고가 여기서 났다. */
function _baselineKeepWhy_(old, n, byHandFlag) {
  if (!old) return '';                       // 처음 만드는 회차 — 잃을 것이 없다
  if (byHandFlag) return '손입력';            // 사람이 그렇게 적어 뒀다
  /* 여기서 만드는 것은 n·hist 뿐이다. 문항별 통계를 가진 회차를 덮으면
     또래 정답률이 사라진다 — 다시 만들려면 엑셀 원본이 있어야 한다. */
  if (old.q || old.qc) return '문항별통계';
  /* 시트에는 옛 응시자가 없다. 46명이 11명이 되는 것은 새 자료가 아니라
     자료를 잃는 것이다. 늘어나는 갱신만 받는다. */
  if (Number(old.n) > n) return '인원감소 ' + old.n + '→' + n;
  return '';
}

/* ── ③ 주간 리포트 ────────────────────────────────────────────────────
   한 주에 무슨 일이 있었나를 한 장으로. 학기말에 되짚을 수 있게 남긴다.
   이름은 안 적는다 — 숫자와 회차뿐이다. */
function weeklyReport() {
  if (!_ghToken_()) return;
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(REC_TAB);
  if (!sh || sh.getLastRow() < 2) return;
  var rows = sh.getRange(2, 1, sh.getLastRow() - 1, WIDE).getValues();
  var now = new Date(), from = new Date(now.getTime() - 7 * 86400000);
  var byExam = {}, people = {}, tot = 0;
  rows.forEach(function (r) {
    var t = (r[3] instanceof Date) ? r[3] : null; if (!t || t < from) return;
    var title = String(r[0] || '(제목 없음)');
    var g = byExam[title] || (byExam[title] = { n: 0, sum: 0, best: 0 });
    var pct = Number(r[10]); if (!isFinite(pct)) pct = 0;
    g.n++; g.sum += pct; if (pct > g.best) g.best = pct;
    people[_codeOf_(r[1], r[6])] = 1; tot++;
  });
  if (!tot) { Logger.log('[주간] 이번 주 채점 없음'); return; }
  var wk = Utilities.formatDate(now, 'Asia/Seoul', 'yyyy-\'W\'ww');
  var L = ['# 주간 리포트 · ' + wk, '',
           '- 채점 ' + tot + '건 · 학생 ' + Object.keys(people).length + '명', '',
           '| 회차 | 채점 | 평균 | 최고 |', '|---|---:|---:|---:|'];
  Object.keys(byExam).sort().forEach(function (t) {
    var g = byExam[t];
    L.push('| ' + t + ' | ' + g.n + ' | ' + Math.round(g.sum / g.n) + ' | ' + Math.round(g.best) + ' |');
  });
  L.push('', '<sub>자동 생성 · 이름은 싣지 않는다</sub>');
  _ghPut_('report/' + wk + '.md', L.join('\n'), '주간 리포트 ' + wk);
  Logger.log('[주간] ' + wk + ' · ' + tot + '건');
}

/* ── 설치 ─────────────────────────────────────────────────────────────
   편집기에서 한 번 실행한다. 두 번 실행해도 겹치지 않게 먼저 지운다. */
function setupBackupTriggers() {
  var want = { dailyBackup: 1, rebuildBaseline: 1, weeklyReport: 1 };
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (want[t.getHandlerFunction()]) ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('dailyBackup').timeBased()
    .everyDays(1).atHour(3).inTimezone('Asia/Seoul').create();
  ScriptApp.newTrigger('rebuildBaseline').timeBased()
    .everyDays(1).atHour(4).inTimezone('Asia/Seoul').create();
  ScriptApp.newTrigger('weeklyReport').timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY).atHour(20).inTimezone('Asia/Seoul').create();
  Logger.log('설치 완료 · 백업 매일 03시 · 기준 기록 04시 · 주간 리포트 일 20시 (KST)');
  if (!_ghToken_()) Logger.log('⚠ GITHUB_TOKEN 스크립트 속성이 아직 없습니다 — 넣어야 실제로 올라갑니다');
}

/* ── 설정이 맞았는지 한 번에 확인 ─────────────────────────────────────
   토큰을 넣고 이 함수를 실행하면 무엇이 되고 무엇이 안 되는지 한 번에 알려
   준다. 안 되면 무엇을 고쳐야 하는지까지 적는다 — 실행 기록만 보고 되돌아갈
   수 있어야 한다.

   실제로 파일을 쓰지는 않는다. 무엇이 올라갈지만 세어 본다.
   개인 정보는 찍지 않는다(실행 기록도 남는 곳이다). */
function checkBackupSetup() {
  var L = ['── 깃허브 자동 저장 설정 점검 ──'], bad = 0;

  var token = _ghToken_();
  if (!token) {
    L.push('✗ GITHUB_TOKEN 없음');
    L.push('   → 프로젝트 설정 › 스크립트 속성에 GITHUB_TOKEN 을 추가하세요.');
    L.push('   → 토큰은 github.com › Settings › Developer settings ›');
    L.push('      Personal access tokens › Fine-grained 에서 만듭니다.');
    L.push('      Repository access: ' + GH_OWNER + '/' + GH_REPO);
    L.push('      Permissions › Repository › Contents: Read and write');
    Logger.log(L.join('\n')); return;
  }
  L.push('✓ GITHUB_TOKEN 있음 (' + token.length + '자)');

  var api = 'https://api.github.com/repos/' + GH_OWNER + '/' + GH_REPO;
  var res;
  try {
    res = UrlFetchApp.fetch(api, { muteHttpExceptions: true,
      headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' } });
  } catch (e) {
    L.push('✗ 깃허브에 닿지 못함: ' + e); Logger.log(L.join('\n')); return;
  }
  var code = res.getResponseCode();
  if (code === 401) { L.push('✗ 토큰이 유효하지 않습니다(401) — 만료됐거나 잘못 붙여넣었습니다'); bad++; }
  else if (code === 404) {
    L.push('✗ 저장소를 못 찾습니다(404) — 토큰의 Repository access 에');
    L.push('   ' + GH_OWNER + '/' + GH_REPO + ' 이 들어 있는지 확인하세요'); bad++;
  } else if (code !== 200) { L.push('✗ 깃허브 응답 ' + code); bad++; }
  else {
    var repo = JSON.parse(res.getContentText());
    var perm = repo.permissions || {};
    L.push('✓ 저장소 확인 · ' + repo.full_name + (repo['private'] ? ' (비공개)' : ' (공개)'));
    if (perm.push) L.push('✓ 쓰기 권한 있음');
    else { L.push('✗ 쓰기 권한 없음 — 토큰 Permissions › Contents 를 Read and write 로'); bad++; }
    if (!repo['private']) L.push('  ※ 공개 저장소입니다 — 그래서 이름 대신 코드를 싣습니다');
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(REC_TAB);
  if (!sh || sh.getLastRow() < 2) { L.push('✗ 기록 탭(' + REC_TAB + ')이 비어 있습니다'); bad++; }
  else {
    var n = sh.getLastRow() - 1;
    L.push('✓ 기록 ' + n + '줄 읽힘 (백업하면 이만큼 올라갑니다)');
    var first = sh.getRange(2, 1, 1, WIDE).getValues()[0];
    var c = _codeOf_(first[1], first[6]);
    // 코드만 찍는다. 이름은 안 찍는다 — 실행 기록도 남는 곳이다.
    L.push(c ? ('✓ 이름 → 코드 됨 (예: ' + c + ')') : '✗ 코드가 안 만들어집니다');
    if (!c) bad++;
  }

  var have = {};
  ScriptApp.getProjectTriggers().forEach(function (t) { have[t.getHandlerFunction()] = 1; });
  ['dailyBackup', 'rebuildBaseline', 'weeklyReport'].forEach(function (f) {
    if (have[f]) L.push('✓ 자동 실행 걸림 · ' + f);
    else { L.push('✗ 자동 실행 안 걸림 · ' + f + ' → setupBackupTriggers() 를 실행하세요'); bad++; }
  });

  L.push(bad ? ('\n▲ ' + bad + '가지를 고쳐야 합니다.')
             : '\n● 모두 정상입니다. 오늘 밤부터 저절로 올라갑니다.');
  L.push('   지금 바로 한 번 올려 보려면 dailyBackup() 을 실행하세요.');
  Logger.log(L.join('\n'));
}

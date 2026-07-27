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
 * [보안] 이 파일은 공개 저장소(github.com/Chemistreal/exam)에 그대로 올라가고,
 *        머지되면 자동 배포까지 된다. 그래서 열쇠를 이 코드에 적으면 안 된다 —
 *        적는 순간 열쇠가 아니다. 스크립트 속성에 넣어 두고 여기서는 읽기만 한다.
 *
 *        열쇠를 정하는 방법 (한 번만):
 *          1) Apps Script 편집기에서 아래 `열쇠설정` 함수의 따옴표 안에 원하는
 *             값을 넣고 한 번 실행한다. 실행이 끝나면 그 줄을 다시 비운다
 *             (저장소에 올라가지 않도록). 또는
 *          2) 편집기 왼쪽 ⚙ 프로젝트 설정 > 스크립트 속성 > 속성 추가에서
 *             이름 `SECRET`, 값에 원하는 열쇠를 직접 넣는다.
 *          3) 앱의 "동기화 키" 버튼에 같은 값을 1회 입력한다.
 *
 *        열쇠가 비어 있으면 **이 URL 을 아는 사람은 누구나 학생 이름·학교·점수를
 *        읽고 쓸 수 있다.** 그 상태에서는 응답에 warning 을 실어 알린다.
 */

/* 열쇠는 코드가 아니라 스크립트 속성에서 온다. 한 번 읽어 두고 재사용한다
   (doPost 가 매번 부르는 자리라 속성 조회를 반복하지 않는다). */
var _SECRET_CACHE = null;
function _secret() {
  if (_SECRET_CACHE === null) {
    try {
      _SECRET_CACHE = PropertiesService.getScriptProperties().getProperty('SECRET') || '';
    } catch (e) {
      _SECRET_CACHE = '';
    }
  }
  return _SECRET_CACHE;
}

/* 편집기에서 한 번 실행해 열쇠를 정한다. 실행 뒤 따옴표 안을 다시 비운다. */
function 열쇠설정() {
  var value = '';           // ← 여기에 열쇠를 넣고 실행한 뒤, 다시 비운다
  if (!value) {
    Logger.log('따옴표 안에 열쇠를 넣고 다시 실행하세요. 지금 상태: ' +
               (_secret() ? '열쇠 설정됨' : '열쇠 없음(누구나 접근 가능)'));
    return;
  }
  PropertiesService.getScriptProperties().setProperty('SECRET', value);
  _SECRET_CACHE = null;
  Logger.log('열쇠를 저장했습니다. 이제 이 함수의 따옴표 안을 다시 비우고 저장하세요.');
}

/* 지금 열쇠가 걸려 있는지만 확인한다(값은 찍지 않는다). */
function 열쇠확인() {
  Logger.log(_secret() ? '열쇠 설정됨 — 키를 가진 요청만 통과합니다'
                       : '열쇠 없음 — URL 을 아는 누구나 읽고 쓸 수 있습니다');
}

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
  'jmchc-12':            ['JMChC 모의고사 12회'],
  'jmchc-13':            ['JMChC 모의고사 13회'],
  'jmchc-14':            ['JMChC 모의고사 14회'],
  'donghyung-1':         ['기출동형 1회 (2015)'],
  'donghyung-2':         ['기출동형 2회 (2016)'],
  'donghyung-3':         ['기출동형 3회 (2017)'],
  'donghyung-4':         ['기출동형 4회 (2013)'],
  'sanyeom-60':          ['산과염기 60제'],
  'kmchc-2026-1-ilban':  ['KMChC 2026 제1차 · 일반'],
  'kmchc-2026-1-simhwa': ['KMChC 2026 제1차 · 심화'],
  'kmchc-2025-2-ilban':  ['KMChC 2025 제2차 · 일반'],
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
  'kmchc-2018':          ['KMChC 2018', '화올 2018', 'KMChC 2018 · 동형 2세트'],
  'kmchc-2019':          ['KMChC 2019', '화올 2019', 'KMChC 2019 · 동형 2세트'],
  'kmchc-2024-1':        ['KMChC 2024 제1차', '화올 2024', 'KMChC 2024 제1차 · 동형 2세트'],
};

var HEADER = [
  '시험', '학생이름', '공유링크', '저장시각', '수험번호', '응시일', '학교', '학년',
  '원점수', '만점', '백점환산', '백분위', '석차', '전체누적인원',
  '맞은개수', '영역별 득점', '답안(60)'
];

function _keyOk(provided) {
  var secret = _secret();
  if (!secret) return true;          // 열쇠 미설정 — 통과시키되 응답에 warning 을 싣는다
  return String(provided || '') === secret;
}

/* 열쇠가 없으면 응답에 경고를 얹는다. 조용히 열려 있는 것이 가장 나쁘다 —
   열쇠를 안 걸었다는 사실 자체를 잊어버리기 때문이다. */
function _warn(payload) {
  if (!_secret()) {
    payload.warning = '동기화 열쇠가 설정돼 있지 않습니다. 이 URL 을 아는 누구나 ' +
                      '학생 이름·학교·점수를 읽고 쓸 수 있습니다. Apps Script 편집기에서 ' +
                      '열쇠설정() 을 한 번 실행하세요.';
  }
  return payload;
}

function doPost(e) {
  var lock = null;
  try {
    // 동시 제출이 겹쳐도 재계산이 꼬이지 않게 직렬화 (최대 20초 대기, 실패 시 잠금 없이 진행)
    try { lock = LockService.getScriptLock(); lock.waitLock(20000); } catch (eL) { lock = null; }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('성적기록') || ss.insertSheet('성적기록');

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADER);
      sheet.getRange(1, 1, 1, HEADER.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    var d = JSON.parse(e.postData.contents);
    if (!_keyOk(d.key)) {
      return ContentService
        .createTextOutput(JSON.stringify({ ok: false, error: 'unauthorized' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    sheet.appendRow([
      d.exam, d.name, d.link || '', new Date(), d.examno, d.date, d.school, d.grade,
      d.total, d.max, d.pct100, d.percentile, d.rank, d.n,
      d.correct, d.areas, "'" + d.answers
    ]);

    // [자동 재계산] 저장 직후 이 시험의 전체 석차·백분위·인원·성적표 문자를 최종 코호트로 재정렬.
    // 실패해도 저장 자체는 성공 처리(재계산은 일일 백업 트리거나 수동 recomputeJ0로 복구 가능).
    try {
      SpreadsheetApp.flush();
      var cfg = _recomputeConfigFor(d.exam);
      if (cfg) recomputeExam(d.exam, cfg.base, cfg.qCount);
    } catch (eR) { Logger.log('자동 재계산 실패(저장은 완료): ' + eR); }

    // [자동 문자 생성] 저장 직후 '성적문자' 탭을 최신 성적기록으로 통째로 다시 채운다.
    // 실패해도 저장은 성공 처리(수동 fillReportMessages로 복구 가능).
    try { fillReportMessages(); } catch (eM) { Logger.log('자동 문자 생성 실패(저장은 완료): ' + eM); }

    return ContentService
      .createTextOutput(JSON.stringify(_warn({ ok: true })))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    if (lock) try { lock.releaseLock(); } catch (eU) {}
  }
}

/* 시험 제목 → 자동 재계산 설정. 기준분포가 있는 시험만 등록(없으면 저장만 하고 재계산 생략). */
function _recomputeConfigFor(title) {
  if (String(title) === '조준모의고사 0회') return { base: J0_BASE_TOTALS, qCount: 60 };
  return null;
}

/**
 * doGet: 앱의 "시트 동기화" 버튼(JSONP)이 호출.
 *   ?action=list&exam=<시험ID>&callback=<함수명>  →  callback({students:[...]})
 * 요청 시험 id를 제목으로 바꿔, '시험' 열이 일치하는 행만 돌려준다(시험 섞임 방지).
 * 매핑에 없는 id면 거르지 않고 전체를 돌려준다(하위호환). 브라우저로 열면 상태만 표시.
 */
function doGet(e) {
  var p = (e && e.parameter) || {};
  var cb = p.callback;
  if (p.action === 'list') {
    if (!_keyOk(p.key)) {
      var deny = JSON.stringify({ ok: false, error: 'unauthorized' });
      return cb
        ? ContentService.createTextOutput(cb + '(' + deny + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
        : ContentService.createTextOutput(deny).setMimeType(ContentService.MimeType.JSON);
    }
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
            answers: ans,
            ts: (r[3] instanceof Date) ? r[3].getTime() : 0   // 저장시각
          });
        }
      }
    } catch (err) {}
    var out = JSON.stringify(_warn({ ok: true, students: students }));
    return cb
      ? ContentService.createTextOutput(cb + '(' + out + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
  }
  var status = JSON.stringify(_warn({ ok: true, msg: 'Chemistreal endpoint live' }));
  return cb
    ? ContentService.createTextOutput(cb + '(' + status + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
    : ContentService.createTextOutput(status).setMimeType(ContentService.MimeType.JSON);
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
   3) 코호트 = 기준분포(J0_BASE_TOTALS 40명) + 학생별 최신 1건(이름 기준)
   4) 각 행의 백분위·석차·전체누적인원을 이 코호트로 재계산
   5) 성적표 문자(18열)도 새 수치로 다시 채움

   실행:
   - 평상시에는 실행할 필요 없음 — 학생이 제출할 때마다 doPost가 자동으로 재계산한다.
   - 시트를 손으로 고쳤거나 상태가 의심될 때만: 편집기에서 recomputeJ0 선택 → 실행 (수동 복구용)
   - setupAllTriggers()를 1회 실행하면 매일 새벽 5시 백업 재계산 트리거도 설치된다.
   ============================================================ */

/* 조준모의고사 0회 기준 코호트 총점 분포(익명 40명) — index.html의 BASE_TOTALS['j0']와 동일 */
var J0_BASE_TOTALS = [12,21,32,37,40,44,54,54,54,59,59,60,60,63,69,69,71,75,78,82,86,87,87,93,93,96,99,100,102,105,108,111,112,117,126,129,129,141,144,171];

/* 학교명 오타·표기 교정(필요 시 여기에 추가). 이름 기준으로 학생을 묶으므로 석차엔 영향 없지만 표시를 바로잡는다. */
var _SCHOOL_FIX = { '휘뭉중': '휘문중' };

function _normName(s) { return String(s == null ? '' : s).replace(/\s+/g, '').trim(); }

/* 클라이언트(grade-j0.html)의 rankPct와 동일한 규칙: 나보다 높은 사람 수+1 = 석차, 백분위=(미만+동점/2)/n */
function _rankPct(value, arr) {
  var n = arr.length, below = 0, equal = 0;
  for (var i = 0; i < n; i++) { var v = arr[i]; if (v < value) below++; else if (v === value) equal++; }
  return { rank: (n - below - equal) + 1, pct: n ? ((below + 0.5 * equal) / n) * 100 : 0, n: n };
}

function _fmtNum(x) { return Math.round(Number(x) * 10) / 10; }  // 소수 1자리, .0은 자동으로 사라짐

function _msgExam(title, name, total, max, pct100, correct, qCount, percentile, rank, n, link) {
  return '[다원교육 영재관 · 화학 조준모]\n'
    + name + ' 학생 ' + title + ' 성적표입니다.\n'
    + '· 원점수 ' + total + '/' + max + '점 · 백점환산 ' + pct100 + '점\n'
    + '· 정답 ' + correct + '/' + qCount + '문항\n'
    + '· 백분위 ' + percentile + ' · 석차 ' + rank + '/' + n + '\n'
    + '아래 링크에서 영역별 정오와 취약 개념을 확인하세요.\n'
    + link;
}

/* 조준모의고사 0회 전용 진입점 */
function recomputeJ0() { recomputeExam('조준모의고사 0회', J0_BASE_TOTALS, 60); }

function recomputeExam(title, baseTotals, qCount) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('성적기록');
  if (!sheet || sheet.getLastRow() < 2) { Logger.log('성적기록 시트가 비어 있습니다.'); return; }

  // 성적표 문자 헤더(18열) 보장
  if (String(sheet.getRange(1, 18).getValue() || '') !== '성적표 문자') {
    sheet.getRange(1, 18).setValue('성적표 문자').setFontWeight('bold');
  }

  var last = sheet.getLastRow();
  var data = sheet.getRange(2, 1, last - 1, 18).getValues();
  // 열: [0]시험 [1]이름 [2]링크 [3]저장시각 [4]수험번호 [5]응시일 [6]학교 [7]학년
  //     [8]원점수 [9]만점 [10]백점환산 [11]백분위 [12]석차 [13]전체누적인원 [14]맞은개수 [15]영역별 [16]답안 [17]성적표문자

  var idx = [];
  for (var i = 0; i < data.length; i++) { if (String(data[i][0]) === title) idx.push(i); }
  if (!idx.length) { Logger.log('해당 시험 행이 없습니다: ' + title); return; }

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

  // 3) 코호트 = 기준분포 + 학생별 최신 1건(이름 기준)
  var latest = {};
  keep.forEach(function (ri) {
    var nm = _normName(data[ri][1]); if (!nm) return;
    var t = ts(ri), tot = Number(data[ri][8]) || 0;
    if (!latest[nm] || t >= latest[nm].ts) latest[nm] = { ts: t, total: tot };
  });
  var cohort = baseTotals.slice();
  for (var nm in latest) cohort.push(latest[nm].total);

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
    var pct100 = data[ri][10];
    var correct = Number(data[ri][14]) || 0;
    var link = String(data[ri][2] || '');
    data[ri][17] = _msgExam(title, name, total, max, pct100, correct, qCount, pct, rp.rank, rp.n, link);
  });

  // 시트 일괄 반영 후 중복 행 삭제(아래→위)
  sheet.getRange(2, 1, data.length, 18).setValues(data);
  dropRows.map(function (ri) { return ri + 2; }).sort(function (a, b) { return b - a; })
    .forEach(function (r) { sheet.deleteRow(r); });

  Logger.log('recomputeExam 완료 · 유지 ' + keep.length + '행 · 중복삭제 ' + dropRows.length + '행 · 코호트 ' + cohort.length + '명(기준 ' + baseTotals.length + ' + 학생 ' + Object.keys(latest).length + ')');
}

/* ============================================================
   트리거 원클릭 설치 · 상태 확인
   ------------------------------------------------------------
   setupAllTriggers : 편집기에서 1회 실행 → 아래 트리거를 전부 설치(중복 자동 제거)
     · recomputeJ0  매일 새벽 5시(KST) — 백업용 재계산.
       (평상시 재계산은 제출 즉시 doPost가 수행하므로, 이 트리거는
        손으로 시트를 고친 날 등을 대비한 안전망이다)
   triggerStatus   : 현재 설치된 트리거 목록을 로그로 출력(설치 여부 확인용)
   ============================================================ */
function setupAllTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'recomputeJ0') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('recomputeJ0').timeBased()
    .everyDays(1).atHour(5).inTimezone('Asia/Seoul').create();
  Logger.log('설치 완료: recomputeJ0 매일 05시(KST) 백업 재계산');
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
  '조준모의고사 0회': { topic: '화학 전 범위(원자의 구조·주기율·화학 결합·기체·열화학·용액·산화환원)를 아우르는 중등 화올 종합 진단', mode: 'perc' },
  'JMChC 모의고사 1회': { topic: '원자의 구조와 원소의 기원, 원자량·동위원소, 몰과 양적관계, 원소분석 등 화학의 정량적 기초', mode: 'tier' }
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

/* 이름·제목으로 뽑는다. 같은 사람 같은 회차면 언제 돌려도 같은 문장이 나온다. */
function _seed(s) { var h = 2166136261; s = String(s);
  for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h * 16777619) >>> 0; }
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

function _buildReportMsg(title, name, correct, pct100, perc, areasStr, link, qi) {
  var cfg = MSG_EXAMS[title] || { topic: '화학 개념과 문제 해결', mode: 'perc' };
  var nm = name || '학생', score = correct * 3, wrong = 60 - correct;
  var band = _band(pct100);
  var analysis;
  if (cfg.mode === 'tier') {
    var aw = _award(wrong);
    if (aw.inA) analysis = '원점수 ' + score + '점(정답 ' + correct + '/60), 틀린 문항 ' + wrong + '개로 현재 ' + aw.name + '권입니다'
      + (aw.next && aw.gap <= 2 ? '. ' + aw.gap + '문항만 더 지키면 ' + aw.next + '권입니다.' : '.');
    else analysis = '원점수 ' + score + '점(정답 ' + correct + '/60)입니다. 장려상까지 ' + aw.need + '문항 — 오답 ' + aw.need + '개 유형만 회복하면 수상권에 진입합니다.';
  } else {
    analysis = '원점수 ' + score + '점(백점환산 ' + pct100 + '점), 정답 ' + correct + '/60문항으로'
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
  var data = src.getRange(2, 1, src.getLastRow() - 1, 18).getValues();
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
    var msg = _buildReportMsg(title, name, correct, pct100, perc, areasStr, link, qi);
    rows.push([msg, name, school, grade, title, correct + '/60', pct100, link]);
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

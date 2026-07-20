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
 * [보안] SECRET 을 본인만 아는 값으로 바꾸면 그 키를 가진 사람만 읽기/쓰기 가능.
 *        앱의 "동기화 키" 버튼에 같은 값을 1회 입력. 빈 값('')이면 키 검증 없이 동작.
 */
var SECRET = '';

/* 동기화 시 '시험' 열로 거르기 위한 시험 id → 제목 매핑.
 * 저장(doPost)은 시험 제목을, 동기화(doGet)는 시험 id를 보내므로 이 표가 필요하다.
 * [중요] index.html 의 EXAMS 제목을 바꾸면 아래 값도 똑같이 맞춰야 한다. */
var EXAM_TITLES = {
  'kch1to3':   '화학1 1-3단원 모의고사',
  'kch1to2':   '화학1 1-2단원 모의고사',
  'kch1u1':    '화학1 1단원 모의고사',
  'kch2final': '화학2 총괄평가',
  'chem2-1':   '화학2 1단원 모의고사',
  'kch1to3-b': '화학1 1-3단원 모의고사 (동형)',
  'kch1to2-b': '화학1 1-2단원 모의고사 (동형)',
  'kch2to3':   '화학2 1-3단원 모의고사',
  'j0':        '조준모의고사 0회'
};

var HEADER = [
  '시험', '학생이름', '공유링크', '저장시각', '수험번호', '응시일', '학교', '학년',
  '원점수', '만점', '백점환산', '백분위', '석차', '전체누적인원',
  '맞은개수', '영역별 득점', '답안(60)'
];

function _keyOk(provided) {
  if (!SECRET) return true;
  return String(provided || '') === SECRET;
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
      var want = EXAM_TITLES[p.exam] || null;   // null이면 필터하지 않음(하위호환)
      var ss = SpreadsheetApp.getActiveSpreadsheet();
      var sheet = ss.getSheetByName('성적기록');
      if (sheet && sheet.getLastRow() > 1) {
        var rows = sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADER.length).getValues();
        // 새 열 순서: [0시험,1이름,2링크,3저장시각,4수험번호,5응시일,6학교,7학년,...,16답안]
        for (var i = 0; i < rows.length; i++) {
          var r = rows[i];
          if (want && String(r[0]) !== want) continue;   // '시험' 열로 필터
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
    var out = JSON.stringify({ ok: true, students: students });
    return cb
      ? ContentService.createTextOutput(cb + '(' + out + ')').setMimeType(ContentService.MimeType.JAVASCRIPT)
      : ContentService.createTextOutput(out).setMimeType(ContentService.MimeType.JSON);
  }
  var status = JSON.stringify({ ok: true, msg: 'Chemistreal endpoint live' });
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

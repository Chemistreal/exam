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
  'kch2to3':   '화학2 1-3단원 모의고사'
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
  try {
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

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
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

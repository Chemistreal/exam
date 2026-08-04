/* ============================================================
   앱스크립트 흉내 — 한자리에서
   ------------------------------------------------------------
   AppsScript-Code.gs 의 함수를 node 로 오려 돌릴 때 필요한 전역들이다.
   여태 검사마다 제각각 세웠고, 그중 여럿이 `Utilities: {}` 처럼 **빈
   껍데기**였다. 껍데기여도 그 함수를 안 부르는 동안에는 아무 일이 없다가,
   부르는 순간 조용히 깨진다.

   실제로 그랬다. 연도 계산을 시간대에 안 기대게 고치면서
   `Utilities.formatDate(d,'Asia/Seoul','yyyy')` 를 쓰기 시작했는데,
   rank-recompute 의 껍데기 Utilities 때문에 그 검사만 통째로 어긋났다
   (인원이 [11,12,1] 로 나왔다). 흉내를 갈라 두면 이런 일이 되풀이된다.

   ⚠ 흉내는 **진짜와 같게** 만든다. formatDate 를 그냥 `String(d)` 로 두면
     서울 시간대를 못박은 자리가 검사에서 그냥 지나간다 — 검사가 거짓말을
     하는 것이 안 하느니만 못하다.
   ============================================================ */
'use strict';

/* Utilities.formatDate — 진짜처럼 시간대를 지켜서 찍는다. */
function formatDate(d, tz, fmt) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: tz || 'Asia/Seoul', hour12: false,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }).formatToParts(d);
  const g = k => (parts.find(x => x.type === k) || {}).value || '';
  return String(fmt || 'yyyy-MM-dd')
    .replace(/yyyy/g, g('year'))
    .replace(/MM/g, g('month'))
    .replace(/dd/g, g('day'))
    .replace(/HH/g, g('hour') === '24' ? '00' : g('hour'))
    .replace(/mm/g, g('minute'))
    .replace(/ss/g, g('second'));
}

/* 검사가 쓰는 기본 전역 한 벌. 필요한 것만 골라 덮어쓰면 된다. */
module.exports = function gasEnv(extra) {
  const base = {
    console, Date,
    Utilities: { formatDate: formatDate },
    Session: { getScriptTimeZone: () => 'Asia/Seoul' },
    Logger: { log() {} },
  };
  for (const k in (extra || {})) base[k] = extra[k];
  return base;
};
module.exports.formatDate = formatDate;

/* ============================================================
   검사는 실제 시트를 건드리지 않는다
   ------------------------------------------------------------
   파이널 앱은 열릴 때마다 시트와 맞춘다(그게 '웹이 원본' 이다). 그래서 검사도
   브라우저를 띄우는 순간 **운영 시트를 읽는다.**

   CI 에 브라우저를 깔자마자 이것이 드러났다: roster-admin 이 심어 둔 학생 넷
   위로 진짜 명단 서른한 명이 얹혀서, 지우기 검사가 엉뚱한 사람을 찾고 있었다.
   내 컴퓨터에서는 통과했다 — 여기서는 script.google.com 에 못 나가서 맞추기가
   조용히 실패했을 뿐이다. 즉 이 검사는 **네트워크에 따라 답이 달라졌다.**

   그리고 검사가 학원 시트를 읽는 것 자체가 안 될 일이다. PR 마다 실제 학생
   이름·점수가 러너 로그로 흘러나온다(위 실패 로그에 그대로 찍혔다).

   그래서 창구를 막는다. 앱스크립트는 CORS 가 없어 JSONP(<script src>)로 부르는데,
   그것도 라우팅에 걸린다 — 콜백 이름을 그대로 불러 주며 **빈 답**을 돌려준다.
   막기만 하면 앱이 '맞추는 중' 에서 안 넘어가는 자리가 있다.

   쓰는 법 (페이지를 연 **뒤**, 첫 goto **앞**):
       const noSheet = require('./_nosheet.js');
       await noSheet(page);
   ============================================================ */
'use strict';

module.exports = async function noSheet(page) {
  await page.route('**/macros/s/**', route => {
    let cb = '';
    try { cb = new URL(route.request().url()).searchParams.get('callback') || ''; }
    catch (e) {}
    /* 창구마다 답의 이름표가 다르다(rows·students·passed…). 다 비워서 준다 —
       무엇을 물었든 '아무것도 없다' 로 답하는 것이 이 검사들이 원하는 상태다. */
    const body = { ok: true, rows: [], students: [], classes: [], list: [],
                   passed: [], pending: [], sent: [], snoozed: [], changed: 0 };
    const json = JSON.stringify(body);
    return route.fulfill({
      status: 200,
      contentType: cb ? 'application/javascript' : 'application/json',
      body: cb ? cb + '(' + json + ');' : json,
    });
  });
};

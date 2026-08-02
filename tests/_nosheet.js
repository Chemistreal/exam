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
   이름·점수가 러너 로그로 흘러나온다(실패 로그에 그대로 찍혔다).

   ⚠ **브라우저에 건다. 페이지 하나에 걸면 샌다.**
   share-link 는 browser.newPage() 로 화면을 여섯 장 연다(선생님·학부모·공유…).
   처음 한 장에만 걸었더니 나머지가 그대로 시트로 나갔고, CI 는
   "__fsheet… is not defined" 로 죽었다 — 콜백을 지운 뒤에 진짜 응답이
   도착한 것이다. 앞으로 열릴 화면까지 덮으려면 newPage/newContext 를 감싼다.

   창구는 막지 않고 **빈 답**을 준다. 앱스크립트는 CORS 가 없어 JSONP(<script src>)
   로 부르는데, 그냥 끊으면 앱이 '맞추는 중' 에서 안 넘어가는 자리가 있다.

   쓰는 법 (launch 바로 뒤):
       const noSheet = require('./_nosheet.js');
       await noSheet(browser);
   페이지·컨텍스트를 넘겨도 된다(그 하나에만 걸린다).
   ============================================================ */
'use strict';

const PATTERN = '**/macros/s/**';

/* 가로챈 횟수. 화면 하나에만 걸렸는지(=나머지가 새고 있는지) 검사가 이걸로
   가늠한다 — 여러 화면을 여는 검사에서 이 수가 0 이면 아무것도 안 막힌 것이다. */
const seen = { n: 0, hosts: [] };

function handler(route) {
  let cb = '';
  try { cb = new URL(route.request().url()).searchParams.get('callback') || ''; }
  catch (e) {}
  /* 창구마다 답의 이름표가 다르다(rows·students·passed…). 다 비워서 준다 —
     무엇을 물었든 '아무것도 없다' 로 답하는 것이 이 검사들이 원하는 상태다. */
  const body = { ok: true, rows: [], students: [], classes: [], list: [],
                 passed: [], pending: [], sent: [], snoozed: [], changed: 0 };
  const json = JSON.stringify(body);
  seen.n++;
  try { const h = new URL(route.request().url()).host;
        if (seen.hosts.indexOf(h) < 0) seen.hosts.push(h); } catch (e) {}
  return route.fulfill({
    status: 200,
    contentType: cb ? 'application/javascript' : 'application/json',
    body: cb ? cb + '(' + json + ');' : json,
  });
}

module.exports = noSheet;
noSheet.seen = seen;
async function noSheet(target) {
  if (!target) return;
  // 이미 열려 있는 화면·컨텍스트
  if (typeof target.route === 'function') { await target.route(PATTERN, handler); return; }
  // 브라우저: 앞으로 열릴 화면까지 덮는다
  if (typeof target.newPage === 'function') {
    const openPage = target.newPage.bind(target);
    target.newPage = async function () {
      const p = await openPage.apply(null, arguments);
      await p.route(PATTERN, handler);
      return p;
    };
  }
  if (typeof target.newContext === 'function') {
    const openCtx = target.newContext.bind(target);
    target.newContext = async function () {
      const c = await openCtx.apply(null, arguments);
      await c.route(PATTERN, handler);
      return c;
    };
  }
}

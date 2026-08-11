/* ============================================================
   검사들이 **자기 서버를 띄우는 자리** — 포트를 골라 주고, 뜰 때까지 기다린다
   ------------------------------------------------------------
   2026-08-11, 선생님 결정 #43 — *"`offline.js` 가 다른 검사와 겹치면 흔들린다"*.

   무엇이 겹쳤나
   -------------
   제 서버를 띄우는 검사가 열 개인데, 열 개가 다 **고정 포트**를 박아 두고
   있었다(8933·8934·8935·8936·8937·8938·8940·8942·8945·8947).

       그래서 같은 저장소에서 검사를 두 벌 돌리면 뒤엣것이 그 포트를 못 잡고,
       화면이 `ERR_CONNECTION_REFUSED` 로 열린다. 그러면 검사는 "화면에 그게
       없다" 고 말한다 — **고장난 곳을 정확히 짚는 것처럼 보이는 거짓말**이다.

   실제로 이 파일을 쓰기 직전에 그 일이 또 있었다. DT 저장소를 8938 에 띄워
   두고 exam 검사를 돌렸더니 `hub-a11y` 만 실패했다. 8938 이 hub-a11y 의
   포트였다. 검사도, 사람도, 아무 잘못이 없었다.

   그리고 열 개가 다 서버를 띄운 뒤 **700ms 를 그냥 기다렸다**. 느린 기계에서는
   모자라고, 빠른 기계에서는 버리는 시간이다(열 개면 7초).
   `tools/blind_wait.py` 가 경계하는 바로 그 모양이다.

   여기서 하는 것
   --------------
     · **빈 포트를 그 자리에서 받는다.** 아무도 안 쓰는 번호를 운영체제가 준다
     · 서버가 **실제로 대답할 때까지** 기다린다 — 초를 세지 않는다
     · 끝나면 확실히 내린다

   쓰는 법:
       const { serve } = require('./_serve.js');
       const srv = await serve(ROOT);        // { port, base, stop() }
       …
       srv.stop();
   ============================================================ */
'use strict';
const http = require('http');
const net = require('net');
const { spawn } = require('child_process');

/* 운영체제에게 빈 번호를 물어본다. 잠깐 잡았다 놓는 사이에 남이 채 갈 수도
   있지만(TOCTOU), 고정 번호를 열 개 박아 두는 것보다는 비교가 안 되게 낫다.
   그리고 아래에서 **실제로 대답하는지** 확인하므로, 못 잡았으면 그 자리에서
   드러난다 — 조용히 남의 서버에 붙는 일은 없다. */
function freePort() {
  return new Promise((res, rej) => {
    const s = net.createServer();
    s.on('error', rej);
    s.listen(0, '127.0.0.1', () => {
      const p = s.address().port;
      s.close(() => res(p));
    });
  });
}

/* 초를 세지 않는다. **대답할 때까지** 물어본다. */
function waitUp(port, timeoutMs = 15000) {
  const t0 = Date.now();
  return new Promise((res, rej) => {
    (function knock() {
      const req = http.get({ host: '127.0.0.1', port, path: '/', timeout: 800 }, r => {
        r.resume(); res();
      });
      req.on('error', () => {
        if (Date.now() - t0 > timeoutMs) return rej(new Error('서버가 안 뜬다: ' + port));
        setTimeout(knock, 40);
      });
      req.on('timeout', () => req.destroy());
    })();
  });
}

/* 아이가 돌릴 글.
 *
 * ⚠ `listen(PORT)` 에 주소를 **붙이지 않는다.** 127.0.0.1 에만 묶었더니,
 *   검사가 부르는 `localhost` 가 이 기계에서 ::1 로 먼저 풀려서 매 요청마다
 *   한 번 헛걸음했다. 258장을 도는 narrow 가 113초에서 260초를 넘겼다 —
 *   고장이 아니라 **느려지기만 해서** 원인이 안 보이는 갈래다.
 *
 * ⚠ `node -e` 에는 **스크립트 경로가 없다.** 그래서 argv 가 한 칸 앞이다 —
 *   argv[0] 은 node, argv[1] 부터가 우리가 준 값이다. 여기를 [2]·[3] 으로
 *   적었다가 서버가 아예 안 떴고, stdio 를 버리고 있어서 **아무 말도 없이**
 *   "서버가 안 뜬다" 만 나왔다. 그래서 아래에서 아이의 말을 받아 둔다.
 *
 * ⚠ 그리고 이 설명을 아래 글 **안에** 적었다가 파일이 통째로 깨졌다.
 *   글이 백틱으로 묶여 있어서, 설명에 쓴 백틱 하나가 글을 거기서 끊었다.
 *   **아이에게 줄 글 안에는 아무 말도 적지 않는다.**
 */
const CHILD = `
const http=require('http'),fs=require('fs'),p=require('path');
const ROOT=process.argv[1], PORT=Number(process.argv[2]);
const T={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8',
         '.json':'application/json','.css':'text/css','.png':'image/png',
         '.jpg':'image/jpeg','.svg':'image/svg+xml','.woff2':'font/woff2'};
http.createServer((q,s)=>{
  const f=p.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f,(e,d)=>e?(s.writeHead(404),s.end())
    :(s.writeHead(200,{'Content-Type':T[p.extname(f)]||'application/octet-stream'}),s.end(d)));
}).listen(PORT);
`;

/* 저장소를 내주는 작은 서버. 검사마다 하나씩 띄운다.
   `PORT` 를 손으로 준 경우에는 그것을 쓴다 — CI 가 그렇게 부르는 자리가 있다. */
async function serve(root, opts) {
  opts = opts || {};
  const port = Number(opts.port || process.env.PORT_FIXED || 0) || await freePort();
  const child = spawn(process.execPath, ['-e', CHILD, root, String(port)],
                      { stdio: ['ignore', 'ignore', 'pipe'] });
  /* 아이가 죽은 까닭을 들고 있는다. 버리면 "서버가 안 뜬다" 한 줄만 남아,
     정작 무엇이 잘못됐는지(경로·포트·문법)를 알 수 없다. */
  let cry = '';
  child.stderr.on('data', d => { cry += d; });
  try {
    await waitUp(port);
  } catch (e) {
    try { child.kill(); } catch (e2) {}
    throw new Error(e.message + (cry ? '\n  아이가 남긴 말: ' + cry.trim().split('\n')[0] : ''));
  }
  return {
    port,
    base: `http://localhost:${port}/`,
    stop() { try { child.kill(); } catch (e) {} }
  };
}

module.exports = { serve, freePort, waitUp };

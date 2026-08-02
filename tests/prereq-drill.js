/* ============================================================
   선수 개념 드릴 회귀 테스트 (브라우저 필요 — CI 에서는 돌지 않는다)
   ------------------------------------------------------------
   선수 개념 지도는 원래도 있었다. "산과염기가 약한 것은 화학평형이 안 잡혀서"
   까지는 짚어 줬는데, 거기서 끝나서 "그래서 뭘 하라는 건데"가 남았다.

   이제 무너진 선수 영역이 있으면 **그 영역 문제를 바로 풀게** 한다. 위층을
   붙들고 있는 것보다 아래층부터 메우는 것이 빠르기 때문에 굳이 아래층 문제를
   내준다. 문항은 개념 색인(donghyung/index.json)에서 끌어오고 누를 때 받는다.

   여기서 지키는 것:
   - 선수 영역이 무너졌을 때만 드릴이 붙는다
   - 버튼과 문제 제목에 그 영역 이름이 나온다(그냥 '같은 개념 문제'가 아니라)
   - 접혀 있다가 누를 때 받아 오고, 받아 온 문제도 눌러서 풀 수 있다
   - **선수 연습은 회복 기록에 섞이지 않는다.** 특정 오답 문항에 묶인 것이
     아니므로 '몇 번을 회복했다'로 세면 안 된다

   실행 (먼저 저장소 루트에서 `python3 -m http.server 8931`):
       PLAYWRIGHT_MODULE=<경로> CHROMIUM_PATH=<경로> node tests/prereq-drill.js
   ============================================================ */
'use strict';
/* 검사가 운영 시트를 읽으면 실 데이터가 심어 둔 데이터를 덮는다.
   실제로 CI 에서 그렇게 깨졌다 — tests/_nosheet.js 의 주석 참고. */
const noSheet = require('./_nosheet.js');
const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
const PORT = Number(process.env.PORT || 8931);
let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  /* 브라우저를 깔아 놓고도 조용히 건너뛰면 초록불이 '브라우저 검사까지
     통과했다' 로 읽힌다. 실제로 그랬다 — 통합 셸의 브라우저 검사가 몇 달
     동안 CI 에서 한 번도 안 돌았는데 초록불이었다. 깔아 둔 자리에서는 멈춘다. */
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}
let fail=0; const chk=(n,g,w)=>{const ok=JSON.stringify(g)===JSON.stringify(w);
  console.log((ok?'  PASS  ':'  FAIL  ')+n+(ok?'':`  got=${JSON.stringify(g)} want=${JSON.stringify(w)}`));if(!ok)fail++;};
(async()=>{
  const b=await chromium.launch({executablePath:CHROMIUM,args:['--no-sandbox']});
  const p=await b.newPage(); await p.setViewportSize({width:900,height:1200});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await noSheet(p);
  await p.goto(`http://localhost:${PORT}/final.html`,{waitUntil:'networkidle'});
  await p.waitForTimeout(700);

  // 선수 개념이 무너진 학생을 만든다: 어떤 영역과 그 선수 영역을 함께 틀리게
  const setup=await p.evaluate(()=>{
    localStorage.clear();
    // PREREQ 를 만족하는 (상위, 하위) 쌍이 둘 다 들어 있는 시험을 찾는다
    const broad=a=>RX[a]?a:(RXMAP[a]||a);
    let found=null;
    for(const e of FINAL_EXAMS){
      if(!e.area||e.area.length!==e.nQ) continue;
      const doms={}; e.area.forEach(a=>{const d=broad(a); if(d) doms[d]=(doms[d]||0)+1;});
      for(const up in PREREQ){
        for(const lo of (PREREQ[up]||[])){
          if((doms[up]||0)>=3&&(doms[lo]||0)>=3){ found={exam:e.id,up:up,lo:lo}; break; }
        }
        if(found) break;
      }
      if(found) break;
    }
    return found;
  });
  console.log('시험:',setup.exam,'· 상위',setup.up,'← 선수',setup.lo);

  const r=await p.evaluate(async(cfg)=>{
    const broad=a=>RX[a]?a:(RXMAP[a]||a);
    openExam(cfg.exam);
    document.getElementById('nm').value='선수테스트';
    for(let q=1;q<=cur.nQ;q++){
      const acc=(cur.multi&&cur.multi[q])||[cur.key[q-1]];
      const good=acc[0]||1;
      const d=broad(cur.area[q-1]);
      // 상위·선수 영역은 전부 틀리게, 나머지는 맞게
      setAns(q,(d===cfg.up||d===cfg.lo)?((good%4)+1):good);
    }
    scoreAuto();
    await new Promise(r=>setTimeout(r,2500));
    const drill=document.querySelector('.pq-drill');
    return {섹션:document.body.innerText.includes('선수 개념 지도'),
            드릴있음:!!drill,
            버튼:drill?drill.querySelector('summary').textContent.trim():'',
            펼침:drill?drill.open:null};
  },setup);
  console.log('결과:',JSON.stringify(r));
  chk('선수 개념 지도가 뜬다',r.섹션,true);
  chk('선수 영역 연습 버튼이 붙는다',r.드릴있음,true);
  chk('버튼에 선수 영역 이름',new RegExp(setup.lo).test(r.버튼),true);
  chk('처음엔 접혀 있음',r.펼침,false);

  // 펼치면 그 영역 문제가 나오는가
  const opened=await p.evaluate(async()=>{
    const d=document.querySelector('.pq-drill'); d.open=true;
    await new Promise(r=>setTimeout(r,3500));
    const items=d.querySelectorAll('.wb-dh');
    return {n:items.length,
            live:d.querySelectorAll('.wb-opts.is-live').length,
            body:d.querySelector('.wb-more-body').textContent.slice(0,30)};
  });
  console.log('펼친 결과:',JSON.stringify(opened));
  chk('선수 영역 문제를 받아 온다',opened.n>0,true);
  chk('그 문제도 눌러서 풀 수 있다',opened.live,opened.n);
  chk('"불러오는 중"이 남아 있지 않음',/불러오는 중/.test(opened.body),false);

  // 눌러도 회복 기록으로 새지 않아야 한다(오답 문항에 묶인 게 아니므로)
  const after=await p.evaluate(async(examId)=>{
    const ol=document.querySelector('.pq-drill .wb-opts.is-live');
    if(ol) ol.querySelector('li[data-c="'+Number(ol.dataset.ans)+'"]').click();
    await new Promise(r=>setTimeout(r,300));
    return JSON.parse(localStorage.getItem('final:dhlog:'+examId)||'[]').length;
  },setup.exam);
  chk('선수 연습은 회복 기록에 섞이지 않음',after,0);
  chk('JS 오류 없음',errs,[]);
  await b.close(); console.log(fail?`\n실패 ${fail}건`:'\n전부 통과'); process.exit(fail?1:0);
})().catch(e=>{console.error('ERR',e.message);process.exit(1);});

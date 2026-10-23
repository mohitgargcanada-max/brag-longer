"""Author this fictional example's visual layer; no real product UI is represented."""
from pathlib import Path
import json
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
(ROOT / 'brand/brand.css').write_text('''
:root{--font-display:"Segoe UI",Arial,sans-serif;--font-body:"Segoe UI",Arial,sans-serif;--stage-bg:#f6f4ee;--accent:#5345e8;--glow-1:#d6d0ff;--glow-2:#b4e3cf}
*{box-sizing:border-box}body,#stage{background:#f6f4ee!important;color:#202138!important}
.film-header{position:absolute;left:92px;right:92px;top:54px;display:flex;justify-content:space-between;align-items:center;font-size:25px;font-weight:600;color:#27243b}
.film-mark{display:flex;gap:14px;align-items:center}.mark{width:34px;height:34px;background:#5345e8;border-radius:12px;display:inline-block;transform:rotate(-12deg)}
.fiction{font-size:18px;font-weight:500;color:#59566c;border:1px solid #d8d4e4;border-radius:30px;padding:10px 20px;background:#ffffffa8}
.side{position:absolute;left:110px;top:248px;width:430px}.kicker{font-size:19px;font-weight:700;color:#6257bd;letter-spacing:3px;text-transform:uppercase;margin-bottom:26px}
.headline{font-size:66px;line-height:1.08;letter-spacing:-2.5px;font-weight:650;color:#25243b;margin:0 0 28px}.subhead{font-size:25px;line-height:1.6;color:#777387;max-width:390px}
.shell{position:absolute;left:600px;top:172px;width:1200px;height:688px;background:#fff;border:1px solid #e6e2ed;border-radius:26px;overflow:hidden;box-shadow:0 28px 70px #39305716}
.shell-bar{height:72px;border-bottom:1px solid #eeeaf3;display:flex;align-items:center;justify-content:space-between;padding:0 32px;font-size:22px;color:#413c58}.shell-bar .small{font-size:17px;color:#9892a5}.avatar{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;background:#e9e6ff;color:#5345e8;font-size:16px;font-weight:700}
.shell-inner{display:flex;height:616px}.nav{width:195px;padding:34px 20px;background:#fbfafc;border-right:1px solid #eeeaf3;font-size:18px;color:#888196}.nav div{padding:14px 18px;margin-bottom:8px;border-radius:12px}.nav .active{background:#ece8ff;color:#5345e8;font-weight:600}
.main{flex:1;padding:38px 40px}.main h2{font-size:34px;letter-spacing:-1px;margin:0 0 8px;color:#302b43}.muted-copy{font-size:18px;color:#968da4;margin-bottom:30px}.task{display:flex;align-items:center;gap:17px;border:1px solid #e7e2ef;padding:22px;border-radius:16px;margin-bottom:15px;background:#fff;font-size:23px;color:#3e3653;box-shadow:0 5px 10px #30264a04}
.box{width:25px;height:25px;flex-shrink:0;border:2px solid #c9c1d9;border-radius:8px}.task-label{flex:1}.pill{font-size:14px;background:#efecff;color:#6b5bb9;border-radius:30px;padding:7px 13px;white-space:nowrap}.pill.green{background:#dff5e9;color:#388363}.pill.gray{background:#f4f1f7;color:#9c91a9}
.loose-card{position:absolute;width:450px;background:#fff;padding:30px;border-radius:22px;box-shadow:0 16px 44px #51456b12;border:1px solid #e9e3ef;color:#494059;font-size:27px}.loose-card small{display:block;font-size:16px;letter-spacing:1px;color:#9b8daf;margin-bottom:18px}.loose-card strong{display:block;font-size:30px;line-height:1.3;font-weight:600}.loose-card p{font-size:21px;color:#9a8ba9;margin:14px 0 0}
.big-note{position:absolute;left:220px;top:232px;width:900px}.big-note .headline{font-size:92px;max-width:900px}.big-note .subhead{max-width:800px;font-size:29px}.floating-label{position:absolute;font-size:20px;padding:15px 24px;border-radius:50px;background:#e9e5fd;color:#6253ba}
.check-list .task{padding:20px}.priority{font-size:17px;color:#7567b4;margin:22px 0 0}.schedule{display:grid;grid-template-columns:90px 1fr;gap:15px;align-items:center;font-size:18px;color:#a299ad}.slot{padding:17px 20px;border-radius:13px;border-left:4px solid #9e91df;background:#f1edff;color:#6e6099}.slot.mint{background:#e5f5ed;color:#5b9277;border-color:#88c6a8}.slot.empty{background:#faf8fc;border-color:#e5dfed;color:#a99fb4}
.board{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.column{padding:16px;background:#f8f6fb;border-radius:14px;min-height:335px}.column h3{font-size:17px;color:#857893;font-weight:600;margin:0 0 20px}.board-card{font-size:19px;line-height:1.5;background:#fff;border:1px solid #e9e4f0;border-radius:12px;padding:20px;margin-bottom:15px;box-shadow:0 5px 13px #35234405}.board-card .avatar{margin-top:24px;width:29px;height:29px;font-size:12px}
.focus{position:absolute;left:670px;top:200px;width:1050px;padding:60px;background:#fff;border-radius:30px;border:1px solid #e6e0ee;box-shadow:0 24px 80px #46375c12}.focus h2{font-size:44px;letter-spacing:-1px;margin:18px 0 30px;color:#30283e}.focus .task{font-size:24px}.complete-mark{width:100px;height:100px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#e0f4e9;color:#3b966b;font-size:54px;margin:0 auto 32px}.center-copy{text-align:center;color:#4b405d;font-size:25px;line-height:1.6}.center-copy h2{font-size:64px;color:#2b243c;letter-spacing:-2px;margin:0 0 20px}.center-copy p{margin:0;color:#988ba6}.end-card{position:absolute;left:180px;right:180px;top:205px;text-align:center}.end-card h1{font-size:100px;font-weight:650;letter-spacing:-4px;color:#2b2440;margin:28px 0 20px}.end-card p{font-size:31px;color:#9486a8;line-height:1.5}.credits{font-size:22px!important;color:#8b809d!important;margin-top:54px!important;line-height:1.8!important}.end-tag{display:inline-block;background:#e5f4ea;color:#54886a;border-radius:40px;padding:14px 26px;font-size:21px}
.footer-note{position:absolute;left:110px;bottom:146px;font-size:17px;letter-spacing:.5px;color:#a79caf}
''', encoding='utf-8')

original_kit = (ROOT / 'build/scenes/kit.js').read_text(encoding='utf-8').split('// ---- Example-specific')[0]
kit = r'''
// ---- Example-specific fictional visual language. All data and screens are invented.
function frame(layer, section){
  layer.append(h(`<div class="film-header"><div class="film-mark"><i class="mark"></i>A clearer day</div><div class="fiction">Fictional product demo</div></div>`));
  layer.append(h(`<div class="footer-note">${section} &nbsp; / &nbsp; A Brag Longer example</div>`));
}
function side(layer,kicker,title,subtitle){
 const el=h(`<div class="side"><div class="kicker">${kicker}</div><h1 class="headline">${title}</h1><div class="subhead">${subtitle}</div></div>`);layer.append(el);return el;
}
function shell(layer,title,body,active='Inbox'){
 const el=h(`<div class="shell"><div class="shell-bar"><b>Day studio <span class="small"> / fictional workspace</span></b><span class="avatar">AL</span></div><div class="shell-inner"><div class="nav">${['Inbox','Today','Team','Completed'].map(x=>`<div class="${x===active?'active':''}">${x}</div>`).join('')}</div><div class="main"><h2>${title}</h2>${body}</div></div></div>`);layer.append(el);return el;
}
function task(text,pill='',extra=''){return `<div class="task ${extra}"><i class="box"></i><span class="task-label">${text}</span>${pill?`<span class="pill">${pill}</span>`:''}</div>`;}
function enter(el,T,start,delay=0){reveal(el,T,start+delay,{dur:.9,dy:28});}
function tick(el,T,start){const p=prog(T,start,.5);el.style.background=p>.5?'#e4f5eb':'#fff';const box=el.querySelector('.box');if(box){box.style.background=p>.5?'#72b794':'#fff';box.style.borderColor=p>.5?'#72b794':'#c9c1d9';box.innerHTML=p>.5?'<span style="color:white;font-size:18px;position:relative;top:-3px;left:3px">✓</span>':'';}}
function buildExample(C){
 const n=C.n, split=C.para(1), S=C.sent, W=C.word;
 return [{from:0,hideLabel:true,build(layer){
   frame(layer,String(n).padStart(2,'0'));
   let update;
   if(n===1){
    const title=side(layer,'The morning','Everything.<br>Everywhere.','A busy day needs a place to begin.');
    const cards=[['MESSAGE','Can we move the review?','One more thing to remember',760,240,-5],['IDEA','A stronger opening','Saved somewhere. Find it later.',1110,430,6],['TODAY','Client presentation','The deadline is getting closer.',760,610,-3]].map(([label,text,sub,x,y,r])=>{const el=h(`<div class="loose-card" style="left:${x}px;top:${y}px"><small>${label}</small><strong>${text}</strong><p>${sub}</p></div>`);layer.append(el);return {el,r};});
    update=T=>{enter(title,T,0);cards.forEach(({el,r},i)=>{const p=prog(T,S(Math.min(i+1,C.sentences.length-1)),.8);el.style.opacity=p;el.style.transform=`translateY(${(1-p)*35}px) rotate(${r}deg)`;});};
   }else if(n===2){
    const title=side(layer,'Gather','One place.<br>Less searching.','Capture the loose ends before choosing the next step.');
    const app=shell(layer,'Your inbox',`<div class="muted-copy">A little room for everything on your mind.</div>${task('Prepare the presentation','Today')}${task('Review the first draft','Team')}${task('Send the follow-up','Later')}`);
    const rows=[...app.querySelectorAll('.task')];
    update=T=>{enter(title,T,0);enter(app,T,.3);rows.forEach((el,i)=>enter(el,T,S(Math.min(2+i,C.sentences.length-1))));};
   }else if(n===3){
    const title=side(layer,'Break it down','Small steps.<br>Clear progress.','A vague task becomes something you can start.');
    const app=shell(layer,'Prepare the presentation',`<div class="muted-copy">Today · Alex · Client work</div><div class="check-list">${task('Check the outline')}${task('Choose the strongest examples')}${task('Rehearse the opening')}</div><div class="priority">One next step is enough to begin.</div>`,'Today');
    const rows=[...app.querySelectorAll('.task')];
    update=T=>{enter(title,T,0);enter(app,T,.2);rows.forEach((el,i)=>enter(el,T,S(Math.min(i+1,C.sentences.length-1))));};
   }else if(n===4){
    const title=side(layer,'Share the plan','Less guessing.<br>More clarity.','The next step is visible to everyone.');
    const app=shell(layer,'The studio board',`<div class="muted-copy">An illustrative team view, with fictional tasks.</div><div class="board"><div class="column"><h3>Planned</h3><div class="board-card">Send the follow-up<br><span class="avatar">AL</span></div></div><div class="column"><h3>In progress</h3><div class="board-card">Client presentation<br><span class="avatar">AL</span></div></div><div class="column"><h3>Ready</h3><div class="board-card">First draft<br><span class="avatar">TM</span></div></div></div>`,'Team');
    update=T=>{enter(title,T,0);enter(app,T,.3);[...app.querySelectorAll('.board-card')].forEach((el,i)=>enter(el,T,S(Math.min(i+1,C.sentences.length-1))));};
   }else if(n===5){
    const title=side(layer,'Focus','One thing.<br>Then the next.','Keep the next step close. Give the work some space.');
    const app=h(`<div class="focus"><div class="kicker">Focus / Client presentation</div><h2>Make the story clear.</h2>${task('Check the outline')}${task('Choose the strongest examples')}${task('Rehearse the opening')}</div>`);layer.append(app);const rows=[...app.querySelectorAll('.task')];
    update=T=>{enter(title,T,0);enter(app,T,.3);rows.forEach((el,i)=>tick(el,T,S(Math.min(i+1,C.sentences.length-1))));};
   }else{
    const title=side(layer,'Reflect','A clearer<br>finish.','Close the day with a practical place to begin again.');
    const app=h(`<div class="focus"><div class="complete-mark">✓</div><div class="center-copy"><h2>Enough for today.</h2><p>The presentation is ready.<br>The next step can wait until morning.</p></div></div>`);layer.append(app);
    update=T=>{enter(title,T,0);enter(app,T,.4);};
   }
   return (t,T)=>update(T);
 }},{from:split,hideLabel:true,build(layer){
   frame(layer,String(n).padStart(2,'0'));
   let update;
   if(n===1){
    const big=h(`<div class="big-note"><div class="kicker">Meet Alex · Fictional studio owner</div><h1 class="headline">The work is everywhere.<br><span style="color:#6a59cb">The plan is nowhere.</span></h1><div class="subhead">A presentation. A review. A dozen loose ends.</div></div>`);layer.append(big);
    const note=h(`<div class="loose-card" style="left:1270px;top:360px;width:440px;background:#e8e3fb"><small>THE NEXT STEP</small><strong>Find a clearer<br>place to begin.</strong><p>A fictional product story</p></div>`);layer.append(note);
    update=T=>{enter(big,T,split);enter(note,T,split,1.2);};
   }else if(n===2){
    const title=side(layer,'Choose','Your day.<br>Your priorities.','A list captures the work. You decide what matters.');
    const app=shell(layer,'Choose what matters',`<div class="muted-copy">Start with one meaningful next step.</div>${task('Prepare the presentation','First priority')}${task('Review the first draft','Next')}${task('Send the follow-up','Later')}`);const rows=[...app.querySelectorAll('.task')];
    update=T=>{enter(title,T,split);enter(app,T,split,.3);rows[0].style.borderColor='#9b8bda';rows[0].style.background='#f5f2ff';};
   }else if(n===3){
    const title=side(layer,'Make room','Plan what fits.<br>Leave space.','A useful day has room to breathe.');
    const app=shell(layer,'Today, with a little space',`<div class="muted-copy">A fictional schedule for Alex.</div><div class="schedule"><span>09:00</span><div class="slot">Prepare the presentation</div><span>10:30</span><div class="slot mint">Take a break</div><span>11:00</span><div class="slot">Review the first draft</div><span>12:00</span><div class="slot empty">Space for the unexpected</div></div>`,'Today');
    update=T=>{enter(title,T,split);enter(app,T,split,.3);[...app.querySelectorAll('.slot')].forEach((el,i)=>enter(el,T,split,1+i*1.2));};
   }else if(n===4){
    const title=side(layer,'Stay aligned','One update.<br>A clear next step.','Simple context keeps the work moving.');
    const app=shell(layer,'Client presentation',`<div class="muted-copy">Shared task · Fictional studio</div>${task('Finish the final review','In progress')}<div class="board-card" style="margin-top:26px;font-size:25px;padding:30px"><span class="avatar">AL</span><br><strong style="display:block;margin:20px 0 10px">Alex updated the next step</strong><span style="color:#9a8aa8">Ready to present after the final review.</span></div>`,'Team');
    update=T=>{enter(title,T,split);enter(app,T,split,.3);enter(app.querySelector('.board-card'),T,split,1.2);};
   }else if(n===5){
    const title=side(layer,'Adapt','Plans change.<br>Clarity stays.','Let the plan respond to the day.');
    const app=shell(layer,'A thoughtful afternoon',`<div class="muted-copy">Finish what matters. Move what can wait.</div>${task('Presentation ready','Complete','done')}${task('Send the follow-up','Tomorrow')}<div class="priority">Tomorrow has a place of its own.</div>`,'Today');
    update=T=>{enter(title,T,split);enter(app,T,split,.3);tick(app.querySelector('.done'),T,split+1);};
   }else{
    const end=h(`<div class="end-card"><div class="end-tag">A fictional product story</div><h1>Make your story clear.</h1><p>Made with Brag Longer.<br>Script. Voice. Scenes. A complete film.</p><p class="credits">Customized by Mohit Garg · ScaleQor<br>Inspired by /brag by Shunit Haviv Hakimi<br><span style="font-size:17px">github.com/mohitgargcanada-max/brag-longer</span></p></div>`);layer.append(end);
    update=T=>{enter(end,T,split);};
   }
   return (t,T)=>update(T);
 }}];
}
'''
(ROOT / 'build/scenes/kit.js').write_text(original_kit + kit, encoding='utf-8')
for n in range(1, 7):
    (ROOT / f'build/scenes/ch{n:02d}.js').write_text(f'Demo.chapter({n}, buildExample);\n', encoding='utf-8')
cfg = json.loads((ROOT / 'video.json').read_text())
cfg.update(fps=24, music_bpm=104)
(ROOT / 'video.json').write_text(json.dumps(cfg, indent=2) + '\n')
print('Authored six chapters / twelve scenes, all explicitly fictional.')

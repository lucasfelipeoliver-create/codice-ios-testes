/* CAMADA IPHONE do Códice — Direção 1 do canvas "Códice iPhone" (aprovada em 24/09/2026). Arquivo novo, injetado
   pelo mobile_ios.py DEPOIS da camada Android: usa as rotas dela (history/VOLTAR) e só acrescenta o que o iPhone pede.
   1. html.ios em iPhone/iPad (iPadOS se anuncia como Mac: MacIntel + toque) e html.ios-app no app instalado;
   2. compartilhar da ficha com o glifo do iOS (quadrado com seta para cima);
   3. arrastar da borda esquerda fecha a ficha no app instalado (lá não há barra do Safari nem VOLTAR físico);
   4. folha "Instale o Códice no iPhone": só no Safari do iPhone, fora do app instalado, depois da 2ª busca, e some
      para sempre no × (localStorage codice.ios.instalar); em navegador de outro app (Chrome, Instagram, WhatsApp…)
      a folha diz para abrir no Safari — só o Safari instala;
   5. aviso de login separado na tela de entrada, só dentro do app instalado.
   Ganchos de teste: window.__codiceIOS (estado e mostrarInstalar) e window.__codiceIOSForcar = {ios, app} antes do boot. */
(function(){
  "use strict";
  var F=window.__codiceIOSForcar||{};
  var ua=navigator.userAgent||"";
  var ios=F.ios!==undefined?!!F.ios:(/iPhone|iPad|iPod/.test(ua)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1));
  var app=F.app!==undefined?!!F.app:(navigator.standalone===true||!!(window.matchMedia&&window.matchMedia("(display-mode: standalone)").matches));
  var outroNav=/CriOS|FxiOS|EdgiOS|OPiOS|GSA\/|Instagram|FBAN|FBAV|Line\/|WhatsApp|LinkedInApp|Twitter/.test(ua);
  var ST={ios:ios,app:app,safari:ios&&!outroNav,buscas:0,instalarVisto:false};
  window.__codiceIOS=ST;
  if(!ios) return;
  var raiz=document.documentElement;
  raiz.classList.add("ios"); if(app) raiz.classList.add("ios-app");

  function $(id){ return document.getElementById(id); }
  function lerLS(k){ try{ return localStorage.getItem(k); }catch(_e){ return null; } }
  function gravarLS(k,v){ try{ localStorage.setItem(k,v); }catch(_e){} }

  var GLIFO_SHARE='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M7 8l5-5 5 5"/><path d="M5 13v7h14v-7"/></svg>';
  var SIMBOLO='<svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true"><polygon points="6,28 20,35 34,28 20,21" fill="#c2410c"/><polygon points="6,20 20,27 34,20 20,13" fill="#0ea5e9"/><polygon points="6,12 20,19 34,12 20,5" fill="#244569" stroke="#93c5fd" stroke-width=".6"/></svg>';

  /* 2 · glifo do iOS no compartilhar da barra da ficha (a barra é recriada a cada ficha: observa) */
  function trocarGlifo(){
    var b=document.querySelector('.m-ficha-acoes button[data-m-ficha="share"]');
    if(b&&!b.getAttribute("data-ios")){ b.innerHTML=GLIFO_SHARE; b.setAttribute("data-ios","1"); }
  }

  /* 3 · borda esquerda fecha a ficha (só no app instalado; no Safari o gesto é do navegador) */
  function gestoBorda(){
    if(!app) return;
    var x0=-1,y0=0;
    document.addEventListener("touchstart",function(e){
      var f=$("lista-ficha"); var t=e.touches&&e.touches[0];
      x0=(f&&f.classList.contains("on")&&t&&t.clientX<24)?t.clientX:-1; y0=t?t.clientY:0;
    },{passive:true});
    document.addEventListener("touchend",function(e){
      if(x0<0) return; var t=e.changedTouches&&e.changedTouches[0]; var dx=t?t.clientX-x0:0, dy=t?Math.abs(t.clientY-y0):99; x0=-1;
      if(dx>70&&dy<50){ var x=document.querySelector("#lista-ficha.on .fic-x"); if(x) x.click(); }
    },{passive:true});
  }

  /* 4 · folha de instalação */
  function montarInstalar(){
    if(app||$("m-ios-instalar")) return null;
    var d=document.createElement("div"); d.id="m-ios-instalar"; d.setAttribute("role","dialog"); d.setAttribute("aria-label","Instalar o Códice no iPhone");
    var corpo=ST.safari
      ? '<div class="ii-passo"><span class="ii-n">1</span><span>Toque em <b>Compartilhar</b> <svg class="ii-g" viewBox="0 0 24 24" fill="none" stroke="#0a84ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M7 8l5-5 5 5"/><path d="M5 13v7h14v-7"/></svg> na barra do Safari (ou em <b>•••</b> e depois Compartilhar)</span></div>'+
        '<div class="ii-passo"><span class="ii-n">2</span><span>Role e escolha <b>Adicionar à Tela de Início</b></span></div>'+
        '<div class="ii-passo"><span class="ii-n">3</span><span>Toque em <b>Adicionar</b>. Abra pelo ícone, não pelo Safari.</span></div>'
      : '<div class="ii-passo"><span class="ii-n">!</span><span>No iPhone, só o <b>Safari</b> instala apps da web. Copie o link e abra no Safari.</span></div>'+
        '<button type="button" class="ii-bt" data-ii="copiar">Copiar o link</button>';
    d.innerHTML='<div class="ii-cab"><div class="ii-ic">'+SIMBOLO+'</div><div><div class="ii-tit">Instale o Códice no iPhone</div>'+
      '<div class="ii-sub">Tela cheia, ícone na tela de início, abre sem internet.</div></div>'+
      '<button type="button" class="ii-x" data-ii="fechar" aria-label="Fechar"><span>×</span></button></div>'+corpo;
    d.addEventListener("click",function(ev){
      var b=ev.target.closest("[data-ii]"); if(!b) return;
      var q=b.getAttribute("data-ii");
      if(q==="fechar"){ d.classList.remove("on"); gravarLS("codice.ios.instalar","dispensado"); }
      else if(q==="copiar"){ var u=location.origin+location.pathname;
        try{ navigator.clipboard.writeText(u).then(function(){ b.textContent="Link copiado — cole no Safari"; }); }catch(_e){ b.textContent=u; } }
    });
    document.body.appendChild(d);
    return d;
  }
  function mostrarInstalar(forcar){
    if(app) return false;
    if(!forcar&&lerLS("codice.ios.instalar")==="dispensado") return false;
    var d=montarInstalar()||$("m-ios-instalar"); if(!d) return false;
    d.classList.add("on"); ST.instalarVisto=true; return true;
  }
  ST.mostrarInstalar=mostrarInstalar;
  function contarBuscas(){
    var i=$("busca"); if(!i||app) return;
    var ultimo="", tm=null;
    i.addEventListener("input",function(){
      clearTimeout(tm); tm=setTimeout(function(){
        var v=(i.value||"").trim().toLowerCase();
        if(v.length>=3&&v!==ultimo){ ultimo=v; ST.buscas++; if(ST.buscas>=2&&!ST.instalarVisto) mostrarInstalar(false); }
      },1500);
    });
  }

  /* 5 · aviso de login separado. A tela de entrada do celular nasce DEPOIS do boot, que no WebKit levou 9,4 s (medido
     24/09/2026) — uma busca com prazo de 10 s perdia a tela; observa o DOM sem prazo e também quando ela renasce
     (sair da conta recria a tela). */
  function avisoLogin(){
    if(!app) return;
    function por(){
      var g=$("codice-mobile-auth-gate");
      if(!g||g.querySelector("#m-ios-login-aviso")) return;
      var alvo=g.querySelector(".gate-form")||g.querySelector(".gate-tabs");
      if(!alvo) return;
      var a=document.createElement("div"); a.id="m-ios-login-aviso";
      a.textContent="O app instalado guarda o login separado do Safari. Entre uma vez aqui; depois ele lembra.";
      alvo.parentNode.insertBefore(a,alvo);
    }
    por();
    try{ new MutationObserver(por).observe(document.body,{childList:true,subtree:true}); }catch(_e){}
  }

  function iniciar(){
    gestoBorda(); contarBuscas(); avisoLogin(); trocarGlifo();
    try{ new MutationObserver(trocarGlifo).observe(document.body,{childList:true,subtree:true}); }catch(_e){}
    ST.pronto=true;
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",iniciar); else iniciar();
})();

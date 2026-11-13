// Interações globais e alternância de tema em todas as telas.
(function(){
  const root=document.documentElement;
  function applyTheme(theme){
    const dark=theme==='dark';
    root.dataset.theme=dark?'dark':'light';
    try{localStorage.setItem('lapetite-theme',dark?'dark':'light');}catch(e){}
    const button=document.querySelector('.theme-toggle');
    if(button){
      button.setAttribute('aria-pressed',String(dark));
      button.setAttribute('aria-label',dark?'Ativar tema claro':'Ativar tema escuro');
      button.title=dark?'Ativar tema claro':'Ativar tema escuro';
      const icon=button.querySelector('.theme-icon');
      if(icon)icon.textContent=dark?'☀':'☾';
    }
  }
  document.addEventListener('DOMContentLoaded',()=>{
    applyTheme(root.dataset.theme==='dark'?'dark':'light');
    const toggle=document.querySelector('.theme-toggle');
    if(toggle)toggle.addEventListener('click',()=>applyTheme(root.dataset.theme==='dark'?'light':'dark'));
    document.querySelectorAll('form').forEach(f=>f.addEventListener('submit',()=>{const b=f.querySelector('button[type=submit],button:not([type])');if(b){b.dataset.original=b.textContent;b.disabled=true;b.textContent='Enviando...';setTimeout(()=>{b.disabled=false;b.textContent=b.dataset.original||'Enviar';},2500);}}));
  });
})();

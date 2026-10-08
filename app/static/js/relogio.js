function atualiza(){
  const h=document.getElementById('relogio-hora');
  const d=document.getElementById('relogio-data');
  if(!h||!d)return;
  const n=new Date();
  h.textContent=n.toLocaleTimeString('pt-BR');
  d.textContent=n.toLocaleDateString('pt-BR');
}
setInterval(atualiza,1000); atualiza();

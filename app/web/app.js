const APP_VERSION='__APP_VERSION__';   // lo rellena ventana.pagina() con el de el_atril/__init__.py
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const plegar=s=>Array.from(s).map(c=>c.normalize('NFD')[0].toLowerCase()).join('');
const slug=t=>plegar(t).trim().replace(/[^\p{L}\p{N}\s_-]/gu,'').replace(/\s/g,'-');

let carpeta=null;            // {nombre, ruta, indice, inicio, truncada} de la carpeta abierta
let indice=[];               // hojas .md y Excel de la carpeta
let hist=[],pos=-1;          // historial para Atrás / Adelante
let actual=null;             // ruta de la hoja que se ve ahora
let marcas=[],mi=-1;         // coincidencias resaltadas en la hoja y la seleccionada

function dirDe(r){const i=r.lastIndexOf('/');return i<0?'':r.slice(0,i+1)}
function resolver(base,href){
  const partes=(dirDe(base)+href).split('/'),o=[];
  for(const p of partes){if(p==='.'||p==='')continue;if(p==='..')o.pop();else o.push(p)}
  return o.join('/');
}

// --- Carpeta ---------------------------------------------------------------------------

async function iniciar(){
  const r=await pywebview.api.estado();
  if(r)cargar(r);else bienvenida();
}
function bienvenida(){
  $('md').innerHTML=`<div class="bienvenida"><h1>El Atril</h1>
    <p>Abre una carpeta con documentos Markdown (<code>.md</code>) para leerlos aquí. Verás todas sus hojas
    en el panel de la izquierda, con buscador y enlaces entre ellas.</p>
    <button class="grande" onclick="abrirCarpeta()">📂 Abrir carpeta…</button>
    <p>También con Ctrl+O</p>
    <p class="version">Versión ${APP_VERSION}</p></div>`;
  $('lado').innerHTML='<p class="vacio">Todavía no hay ninguna carpeta abierta.</p>';
  $('titulo').textContent='';
  activarBarra(false);
}
let abriendo=false;
async function abrirCarpeta(){
  if(abriendo)return;
  abriendo=true;
  try{const r=await pywebview.api.abrir_carpeta();if(r)cargar(r)}
  finally{abriendo=false}
}
function cargar(r){
  carpeta=r;indice=r.indice;hist=[];pos=-1;actual=null;
  $('q').value='';marcas=[];mi=-1;$('cuenta').textContent='';
  pintarLado();activarBarra(true);
  if(r.inicio){ir(r.inicio);return}
  $('md').innerHTML=`<div class="bienvenida"><h1>${esc(r.nombre)}</h1>
    <p>En esta carpeta no hay ninguna hoja <code>.md</code>.</p>
    <button class="grande" onclick="abrirCarpeta()">📂 Abrir otra carpeta…</button></div>`;
  $('titulo').textContent=r.ruta;
}
function activarBarra(si){
  for(const id of ['recargar','q','prev','next','todas'])$(id).disabled=!si;
  flechas();
}
function flechas(){$('atras').disabled=pos<=0;$('adelante').disabled=pos>=hist.length-1}

function pintarLado(){
  const l=$('lado');l.innerHTML='';
  if(carpeta.truncada){
    const p=document.createElement('p');p.className='aviso';
    p.textContent=`Carpeta muy grande: solo se muestran las primeras ${indice.filter(f=>f.tipo==='md').length} hojas.`;
    l.appendChild(p);
  }
  if(!indice.length){l.innerHTML+='<p class="vacio">No hay hojas .md en esta carpeta.</p>';return}
  let grupo=null;
  for(const f of indice){
    if(f.grupo!==grupo){grupo=f.grupo;const h=document.createElement('h4');h.textContent=grupo||carpeta.nombre;l.appendChild(h)}
    const a=document.createElement('a');a.dataset.ruta=f.ruta;
    a.innerHTML=f.tipo==='xlsx'?`📊 ${esc(f.titulo)}<small>se abre en Excel</small>`:`${esc(f.titulo)}<small>${esc(f.ruta)}</small>`;
    if(f.ruta===actual)a.className='act';
    a.onclick=()=>f.tipo==='xlsx'?pywebview.api.abrir(f.ruta):ir(f.ruta);
    l.appendChild(a);
  }
}

// --- Hojas y navegación ----------------------------------------------------------------

async function ir(ruta,ancla,guardar=true,buscar){
  if(guardar&&pos>=0&&hist[pos].ruta===ruta&&!ancla&&!buscar){return}
  const html=await pywebview.api.leer(ruta);
  if(guardar){hist=hist.slice(0,pos+1);hist.push({ruta,ancla,buscar});pos=hist.length-1}
  mostrar(ruta,html,ancla,buscar);
}
function mostrar(ruta,html,ancla,buscar){
  actual=ruta;$('md').innerHTML=html;$('titulo').textContent=ruta;
  document.querySelectorAll('#md h1,#md h2,#md h3,#md h4,#md h5,#md h6').forEach(h=>{h.id=slug(h.textContent)});
  document.querySelectorAll('#md a[href]').forEach(a=>{
    const h=a.getAttribute('href');
    if(/^(https?|mailto):/i.test(h)){a.target='_blank';return}
    if(h.startsWith('#')){a.onclick=e=>{e.preventDefault();salto(h.slice(1))};return}
    const m=h.match(/^([^#]*)(#(.*))?$/);const dest=resolver(ruta,decodeURIComponent(m[1]));
    if(dest.toLowerCase().endsWith('.md')&&indice.some(x=>x.ruta===dest)){
      a.onclick=e=>{e.preventDefault();ir(dest,m[3]?decodeURIComponent(m[3]):null)};
    }else if(indice.some(x=>x.ruta===dest&&x.tipo==='xlsx')){
      a.title='Se abre en Excel';a.onclick=e=>{e.preventDefault();pywebview.api.abrir(dest)};
    }else{a.className='muerto';a.title='No se abre aquí (no es una hoja .md de esta carpeta)';a.onclick=e=>e.preventDefault()}
  });
  document.querySelectorAll('#lado a[data-ruta]').forEach(a=>a.classList.toggle('act',a.dataset.ruta===ruta));
  flechas();
  $('doc').scrollTop=0;
  const q=buscar||$('q').value;
  if(buscar)$('q').value=buscar;
  resaltar(q.trim());
  if(ancla)salto(ancla);
}
function salto(id){
  let e=document.getElementById(id);
  if(!e){const s=slug(id);e=document.getElementById(s)||Array.from(document.querySelectorAll('#md [id]')).find(x=>x.id.startsWith(s))}
  if(e)e.scrollIntoView({block:'start'});
}
function volverA(p){pos=p;const h=hist[pos];pywebview.api.leer(h.ruta).then(x=>mostrar(h.ruta,x,h.ancla,h.buscar))}
function atras(){if(pos>0)volverA(pos-1)}
function adelante(){if(pos<hist.length-1)volverA(pos+1)}
async function recargar(){
  if(!carpeta)return;
  const st=$('doc').scrollTop;
  indice=await pywebview.api.listar();
  pintarLado();
  if(actual){
    const html=await pywebview.api.leer(actual);
    mostrar(actual,html,null,$('q').value.trim()||null);
    $('doc').scrollTop=st;
  }
}

// --- Búsqueda --------------------------------------------------------------------------

function limpiar(){
  document.querySelectorAll('#md mark').forEach(m=>{const p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize()});
  marcas=[];mi=-1;
}
function resaltar(q){
  limpiar();$('cuenta').textContent='';
  if(q.length<2||!actual)return;
  const fq=plegar(q);
  const w=document.createTreeWalker($('md'),NodeFilter.SHOW_TEXT);const nodos=[];
  while(w.nextNode())nodos.push(w.currentNode);
  for(const n of nodos){
    const t=n.nodeValue,ft=plegar(t);let i=ft.indexOf(fq);if(i<0)continue;
    const frag=document.createDocumentFragment();let ult=0;
    while(i>=0){
      frag.appendChild(document.createTextNode(t.slice(ult,i)));
      const m=document.createElement('mark');m.textContent=t.slice(i,i+fq.length);frag.appendChild(m);marcas.push(m);
      ult=i+fq.length;i=ft.indexOf(fq,ult);
    }
    frag.appendChild(document.createTextNode(t.slice(ult)));n.parentNode.replaceChild(frag,n);
  }
  if(marcas.length){mi=-1;siguiente(1)}else $('cuenta').textContent='0 de 0';
}
function siguiente(d){
  if(!marcas.length)return;
  if(mi>=0)marcas[mi].classList.remove('cur');
  mi=(mi+d+marcas.length)%marcas.length;
  marcas[mi].classList.add('cur');marcas[mi].scrollIntoView({block:'center'});
  $('cuenta').textContent=`${mi+1} de ${marcas.length}`;
}
async function buscarTodas(){
  if(!carpeta)return;
  const q=$('q').value.trim();if(q.length<2)return;
  const r=await pywebview.api.buscar(q);
  const l=$('lado');l.innerHTML='';
  const c=document.createElement('a');c.innerHTML='← Volver a la lista de hojas';c.onclick=()=>pintarLado();l.appendChild(c);
  const h=document.createElement('h4');h.textContent=`"${q}" en ${r.length} hojas`;l.appendChild(h);
  for(const f of r){
    const a=document.createElement('a');a.innerHTML=`${esc(f.titulo)}<small>${f.total} coincidencias · ${esc(f.ruta)}</small>`;
    a.onclick=()=>ir(f.ruta,null,true,q);l.appendChild(a);
    for(const s of f.trozos){
      const d=document.createElement('div');d.className='res';
      d.innerHTML=s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(/\u0001(.*?)\u0002/g,'<b>$1</b>');
      d.onclick=()=>ir(f.ruta,null,true,q);l.appendChild(d);
    }
  }
}

// --- Arranque y teclado ----------------------------------------------------------------

if(window.pywebview&&window.pywebview.api&&window.pywebview.api.estado)iniciar();
else window.addEventListener('pywebviewready',iniciar);

document.addEventListener('DOMContentLoaded',()=>{
  $('abrir').onclick=abrirCarpeta;
  $('atras').onclick=atras;$('adelante').onclick=adelante;
  $('todas').onclick=buscarTodas;$('recargar').onclick=recargar;
  $('q').addEventListener('input',()=>resaltar($('q').value.trim()));
  $('q').addEventListener('keydown',e=>{
    if(e.key==='Enter'){e.preventDefault();if(e.ctrlKey)buscarTodas();else siguiente(e.shiftKey?-1:1)}
    if(e.key==='Escape'){$('q').value='';resaltar('');$('q').blur()}
  });
  $('prev').onclick=()=>siguiente(-1);$('next').onclick=()=>siguiente(1);
});
document.addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(e.ctrlKey&&k==='o'){e.preventDefault();abrirCarpeta()}
  if(e.ctrlKey&&k==='f'&&carpeta){e.preventDefault();$('q').focus();$('q').select()}
  if(e.altKey&&e.key==='ArrowLeft'){e.preventDefault();atras()}
  if(e.altKey&&e.key==='ArrowRight'){e.preventDefault();adelante()}
  if(e.key==='F5'||(e.ctrlKey&&k==='r')){e.preventDefault();recargar()}
  if(e.key==='F3'){e.preventDefault();siguiente(e.shiftKey?-1:1)}
});

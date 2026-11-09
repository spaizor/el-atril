const APP_VERSION='__APP_VERSION__';   // lo rellena ventana.pagina() con el de app/__init__.py
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
// Minúsculas y sin tildes, sin cambiar la longitud del texto (así las posiciones encontradas
// valen en el original). Los caracteres de dos unidades (emojis) se dejan tal cual.
const plegar=s=>Array.from(s).map(c=>c.length>1?c:c.normalize('NFD')[0].toLowerCase()[0]).join('');
const slug=t=>plegar(t).trim().replace(/[^\p{L}\p{N}\s_-]/gu,'').replace(/\s/g,'-');

let carpeta=null;            // {nombre, ruta, indice, inicio, truncada} de la carpeta abierta
let indice=[];               // hojas .md y Excel de la carpeta
let hist=[],pos=-1;          // historial para Atrás / Adelante
let actual=null;             // ruta de la hoja que se ve ahora
let marcas=[],mi=-1;         // coincidencias resaltadas en la hoja y la seleccionada
let enBusqueda=false;        // el panel enseña resultados de "Buscar en todas", no la lista
let apartados=[];            // índice de la hoja: [{h: título en la hoja, a: enlace en el panel}]
let letra=100;               // tamaño de letra de la hoja, en %

function dirDe(r){const i=r.lastIndexOf('/');return i<0?'':r.slice(0,i+1)}
function resolver(base,href){
  const partes=(dirDe(base)+href).split('/'),o=[];
  for(const p of partes){if(p==='.'||p==='')continue;if(p==='..')o.pop();else o.push(p)}
  return o.join('/');
}

// --- Carpeta ---------------------------------------------------------------------------

async function iniciar(){
  ponerLetra(await pywebview.api.letra());
  const r=await pywebview.api.estado();
  if(r)cargar(r);else bienvenida();
}
function bienvenida(){
  carpeta=null;indice=[];hist=[];pos=-1;actual=null;
  $('q').value='';marcas=[];mi=-1;$('cuenta').textContent='';
  $('md').innerHTML=`<div class="bienvenida"><h1>El Atril</h1>
    <p>Abre una carpeta con documentos Markdown (<code>.md</code>) para leerlos aquí. Verás todas sus hojas
    en el panel de la izquierda, con buscador y enlaces entre ellas.</p>
    <button class="grande" onclick="abrirCarpeta()">📂 Abrir carpeta…</button>
    <p>También con Ctrl+O</p>
    <p class="version">Versión ${APP_VERSION}</p></div>`;
  $('titulo').textContent='';
  activarBarra(false);
  pintarRecientes();
}
async function pintarRecientes(lista){
  if(!lista)lista=await pywebview.api.recientes();
  const l=$('lado');l.innerHTML='';
  if(!lista.length){l.innerHTML='<p class="vacio">Todavía no has abierto ninguna carpeta. Aquí saldrán las últimas que abras.</p>';return}
  const h=document.createElement('h4');h.textContent='Carpetas recientes';l.appendChild(h);
  for(const c of lista){
    const a=document.createElement('a');a.className='reciente'+(c.existe?'':' falta');
    a.innerHTML=`📁 ${esc(c.nombre)}<small>${c.existe?'':'No se encuentra · '}${esc(c.ruta)}</small>`;
    a.title=c.existe?c.ruta:'Esta carpeta ya no existe (o está en una unidad que no está conectada)';
    a.onclick=()=>abrirReciente(c.ruta);
    const x=document.createElement('span');x.className='quitar';x.textContent='×';x.title='Quitar de la lista';
    x.onclick=async e=>{e.stopPropagation();pintarRecientes(await pywebview.api.quitar_reciente(c.ruta))};
    a.appendChild(x);l.appendChild(a);
  }
}
async function cerrarCarpeta(){
  if(!carpeta)return;
  await guardarPos();
  await pywebview.api.cerrar();
  bienvenida();
}
async function abrirReciente(ruta){
  if(abriendo)return;
  abriendo=true;
  try{await guardarPos();const r=await pywebview.api.abrir_reciente(ruta);if(r)cargar(r);else pintarRecientes()}
  finally{abriendo=false}
}
let abriendo=false;
async function abrirCarpeta(){
  if(abriendo)return;
  abriendo=true;
  try{await guardarPos();const r=await pywebview.api.abrir_carpeta();if(r)cargar(r)}
  finally{abriendo=false}
}
function cargar(r){
  carpeta=r;indice=r.indice;hist=[];pos=-1;actual=null;
  firmaHoja={ruta:null,valor:null};firmaCarpeta=null;
  $('q').value='';marcas=[];mi=-1;$('cuenta').textContent='';
  pintarLado();activarBarra(true);
  if(r.inicio){
    // Si ya se había leído la carpeta, inicio es la última hoja y scroll por dónde se iba.
    ir(r.inicio).then(()=>{if(r.scroll){const d=$('doc');d.scrollTop=r.scroll*(d.scrollHeight-d.clientHeight)}});
    return;
  }
  $('md').innerHTML=`<div class="bienvenida"><h1>${esc(r.nombre)}</h1>
    <p>En esta carpeta no hay ninguna hoja <code>.md</code>.</p>
    <button class="grande" onclick="abrirCarpeta()">📂 Abrir otra carpeta…</button></div>`;
  $('titulo').textContent=r.ruta;
}
function activarBarra(si){
  for(const id of ['cerrar','q','prev','next','todas'])$(id).disabled=!si;
  flechas();
}
function flechas(){$('atras').disabled=pos<=0;$('adelante').disabled=pos>=hist.length-1}

function pintarLado(){
  const l=$('lado');l.innerHTML='';enBusqueda=false;
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
  pintarApartados();
}

// Índice de la hoja abierta: sus títulos (#, ##, ###) colgando de ella en el panel.
// El primer # no sale si es el único, porque es el título de la hoja.
function pintarApartados(){
  document.querySelectorAll('#lado .toc').forEach(x=>x.remove());apartados=[];
  const act=document.querySelector('#lado a.act[data-ruta]');if(!act||!actual)return;
  let hs=Array.from(document.querySelectorAll('#md h1,#md h2,#md h3'));
  if(hs.length&&hs[0].tagName==='H1'&&hs.filter(h=>h.tagName==='H1').length===1)hs=hs.slice(1);
  if(hs.length<2)return;
  const min=Math.min(...hs.map(h=>+h.tagName[1]));
  const caja=document.createElement('div');caja.className='toc';
  for(const h of hs){
    const a=document.createElement('a');a.className='n'+(h.tagName[1]-min);
    a.textContent=a.title=h.textContent.trim();
    a.onclick=()=>h.scrollIntoView({block:'start'});
    caja.appendChild(a);apartados.push({h,a});
  }
  act.after(caja);
  marcarApartado();
}
// Resalta en el índice el apartado que se está leyendo (el último título que ya ha pasado
// por arriba).
function marcarApartado(){
  if(!apartados.length)return;
  const tope=$('doc').getBoundingClientRect().top+80;
  let cur=null;
  for(const x of apartados){if(x.h.getBoundingClientRect().top<=tope)cur=x;else break}
  for(const x of apartados)x.a.classList.toggle('aqui',x===cur);
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
  const externos=[];   // enlaces a otros ficheros (PDF, imágenes...): se pregunta a Python si se pueden abrir
  document.querySelectorAll('#md a[href]').forEach(a=>{
    const h=a.getAttribute('href');
    if(/^(https?|mailto):/i.test(h)){a.target='_blank';a.className='externo';a.title=h;return}
    if(h.startsWith('#')){a.onclick=e=>{e.preventDefault();salto(h.slice(1))};return}
    a.onclick=e=>e.preventDefault();
    // Otros esquemas (file:, C:/...) no: solo rutas relativas dentro de la carpeta.
    if(/^[a-z][a-z0-9+.-]*:/i.test(h)){muerto(a,'No se abre aquí (solo se abren ficheros de esta carpeta)');return}
    const m=h.match(/^([^#]*)(#(.*))?$/);
    let dest='',ancla=null;
    try{dest=m[1]&&resolver(ruta,decodeURIComponent(m[1]));ancla=m[3]?decodeURIComponent(m[3]):null}catch(e){dest=''}
    if(!dest){muerto(a,'No se abre aquí');return}
    if(dest.toLowerCase().endsWith('.md')){
      if(indice.some(x=>x.ruta===dest&&x.tipo==='md'))a.onclick=e=>{e.preventDefault();ir(dest,ancla)};
      else muerto(a,'Esta hoja no está en el panel (no existe o está en una carpeta que no se recorre)');
      return;
    }
    if(indice.some(x=>x.ruta===dest&&x.tipo==='xlsx')){
      a.title='Se abre en Excel';a.onclick=e=>{e.preventDefault();pywebview.api.abrir(dest)};return;
    }
    muerto(a,'Comprobando…');externos.push({a,dest});
  });
  if(externos.length)comprobarEnlaces(ruta,externos);
  document.querySelectorAll('#lado a[data-ruta]').forEach(a=>a.classList.toggle('act',a.dataset.ruta===ruta));
  flechas();
  $('doc').scrollTop=0;
  pintarApartados();
  const q=buscar||$('q').value;
  if(buscar)$('q').value=buscar;
  resaltar(q.trim());
  if(ancla)salto(ancla);
  guardarLuego();
}
function muerto(a,aviso){a.className='muerto';a.title=aviso}
// Los enlaces a ficheros que no son hojas se abren con su programa de Windows (el PDF con el
// lector de PDF, la imagen con el visor...), salvo programas y scripts, que Python bloquea.
const AVISOS={bloqueado:'Por seguridad, El Atril no abre programas ni scripts',
  falta:'No se encuentra este fichero en la carpeta'};
async function comprobarEnlaces(ruta,lista){
  const r=await pywebview.api.enlaces([...new Set(lista.map(x=>x.dest))]);
  if(ruta!==actual)return;   // mientras tanto se ha cambiado de hoja
  for(const {a,dest} of lista){
    const st=r[dest];
    if(st==='fichero'||st==='carpeta'){
      a.className='externo';
      a.title=st==='carpeta'?'Se abre en el Explorador de Windows':'Se abre con su programa de Windows';
      a.onclick=e=>{e.preventDefault();pywebview.api.abrir(dest)};
    }else muerto(a,AVISOS[st]||AVISOS.falta);
  }
}
function salto(id){
  let e=document.getElementById(id);
  if(!e){const s=slug(id);e=document.getElementById(s)||Array.from(document.querySelectorAll('#md [id]')).find(x=>x.id.startsWith(s))}
  if(e)e.scrollIntoView({block:'start'});
}
function volverA(p){pos=p;const h=hist[pos];pywebview.api.leer(h.ruta).then(x=>mostrar(h.ruta,x,h.ancla,h.buscar))}
function atras(){if(pos>0)volverA(pos-1)}
function adelante(){if(pos<hist.length-1)volverA(pos+1)}
// F5: lo mismo que hace solo la vigilancia, pero a mano y de golpe (por si acaso, p. ej. en
// unidades de red donde Windows no siempre actualiza las fechas a tiempo).
async function recargar(){
  if(!carpeta)return;
  await refrescarIndice(true);
  if(actual)await refrescarHoja();
}
// Vuelve a leer la hoja abierta sin moverse de donde se estaba leyendo.
async function refrescarHoja(){
  const ruta=actual,html=await pywebview.api.leer(ruta);
  if(ruta!==actual)return;
  const st=$('doc').scrollTop;
  mostrar(ruta,html,null,$('q').value.trim()||null);
  $('doc').scrollTop=st;
}
// Vuelve a leer la lista de hojas. Si el panel está enseñando resultados de "Buscar en
// todas", no se toca (salvo con F5), para no quitárselos al usuario.
async function refrescarIndice(forzar){
  const c=carpeta,nuevo=await pywebview.api.listar();
  if(c!==carpeta)return;
  indice=nuevo;
  if(enBusqueda&&!forzar)return;
  const sc=$('lado').scrollTop;pintarLado();$('lado').scrollTop=sc;
}

// --- Vigilancia: recargar sola la hoja y la lista cuando cambian en disco ---------------
// Cada segundo se pregunta a Python la fecha y tamaño de la hoja abierta (no la lee: es
// casi gratis), y cada 3 segundos una huella de la carpeta (fechas de todas las hojas, sin
// leerlas). Solo si algo ha cambiado se vuelve a leer. Con la ventana oculta no se mira.

let firmaHoja={ruta:null,valor:null},firmaCarpeta=null,tic=0,vigilando=false;
async function vigilar(){
  if(vigilando||!carpeta||document.hidden)return;
  vigilando=true;
  try{
    const c=carpeta,hoja=actual,conCarpeta=tic++%3===0;
    const r=await pywebview.api.vigilar(hoja,conCarpeta);
    if(c!==carpeta)return;   // mientras tanto se ha cambiado de carpeta
    if(conCarpeta&&r.carpeta){
      if(firmaCarpeta&&r.carpeta!==firmaCarpeta)await refrescarIndice();
      firmaCarpeta=r.carpeta;
    }
    // Si la hoja ha desaparecido (null) no se toca: hay editores que al guardar la borran y
    // la vuelven a crear, y al reaparecer se recarga.
    if(hoja&&hoja===actual&&r.hoja){
      if(firmaHoja.ruta===hoja&&firmaHoja.valor&&r.hoja!==firmaHoja.valor)await refrescarHoja();
      firmaHoja={ruta:hoja,valor:r.hoja};
    }
  }catch(e){/* un fallo suelto no para la vigilancia */}
  finally{vigilando=false}
}
setInterval(vigilar,1000);

// --- Memoria: última hoja y scroll de cada carpeta -------------------------------------

let tPos=null;
// Apunta en Python la hoja y por dónde va (0 = arriba, 1 = abajo). Se llama con await antes
// de cambiar de carpeta, para que no se pierda ni se apunte en la carpeta equivocada.
function guardarPos(){
  clearTimeout(tPos);tPos=null;
  if(!carpeta||!actual)return Promise.resolve();
  const d=$('doc'),max=d.scrollHeight-d.clientHeight;
  return pywebview.api.recordar(carpeta.ruta,actual,max>0?d.scrollTop/max:0);
}
function guardarLuego(){clearTimeout(tPos);tPos=setTimeout(guardarPos,600)}

// --- Tamaño de letra -------------------------------------------------------------------

const LETRA_MIN=70,LETRA_MAX=200;
let tLetra=null,rueda=0;
function ponerLetra(v){
  v=Math.max(LETRA_MIN,Math.min(LETRA_MAX,Math.round(v/10)*10));
  const d=$('doc'),max=d.scrollHeight-d.clientHeight,f=max>0?d.scrollTop/max:0;
  letra=v;$('md').style.fontSize=v+'%';$('letra').textContent=v+'%';
  $('menos').disabled=v<=LETRA_MIN;$('mas').disabled=v>=LETRA_MAX;
  const m2=d.scrollHeight-d.clientHeight;if(m2>0)d.scrollTop=f*m2;   // seguir en el mismo sitio
}
function cambiarLetra(v){
  const antes=letra;ponerLetra(v);
  if(letra!==antes){clearTimeout(tLetra);tLetra=setTimeout(()=>pywebview.api.poner_letra(letra),500)}
}

// --- Tema claro / oscuro ---------------------------------------------------------------
// La página ya nace con su tema (ventana.pagina() rellena data-tema), así no parpadea.

function pintarTema(){
  $('tema').title=document.documentElement.dataset.tema==='claro'?'Cambiar a tema oscuro':'Cambiar a tema claro';
}
function cambiarTema(){
  const t=document.documentElement.dataset.tema==='claro'?'oscuro':'claro';
  document.documentElement.dataset.tema=t;pintarTema();
  pywebview.api.poner_tema(t);
}

// --- Búsqueda --------------------------------------------------------------------------

function limpiar(){
  document.querySelectorAll('#md mark').forEach(m=>{const p=m.parentNode;p.replaceChild(document.createTextNode(m.textContent),m);p.normalize()});
  marcas=[];mi=-1;
}
// Bloque al que pertenece un trozo de texto: la búsqueda junta los trozos de un mismo bloque
// (en el código coloreado o con una **negrita** en medio, una frase son varios trozos), pero
// no junta bloques distintos.
const BLOQUES='p,li,pre,td,th,h1,h2,h3,h4,h5,h6,blockquote,dt,dd,div';
function resaltar(q){
  limpiar();$('cuenta').textContent='';
  if(q.length<2||!actual)return;
  const fq=plegar(q);
  // Todo el texto de la hoja, plegado, con '\n' entre bloques (la búsqueda nunca lleva '\n').
  const w=document.createTreeWalker($('md'),NodeFilter.SHOW_TEXT);
  const nodos=[];let texto='',bloqueAnt=null;
  while(w.nextNode()){
    const n=w.currentNode,b=n.parentElement.closest(BLOQUES);
    if(nodos.length&&b!==bloqueAnt)texto+='\n';
    bloqueAnt=b;nodos.push({n,ini:texto.length,trozos:[]});texto+=plegar(n.nodeValue);
  }
  // Cada coincidencia se reparte entre los trozos que toca: una marca por trozo.
  let k=0,total=0;
  for(let i=texto.indexOf(fq);i>=0;i=texto.indexOf(fq,i+fq.length)){
    const fin=i+fq.length;
    while(nodos[k].ini+nodos[k].n.nodeValue.length<=i)k++;
    for(let j=k;j<nodos.length&&nodos[j].ini<fin;j++){
      const x=nodos[j];if(!x.n.nodeValue.length)continue;
      x.trozos.push([Math.max(i,x.ini)-x.ini,Math.min(fin,x.ini+x.n.nodeValue.length)-x.ini,total]);
    }
    total++;
  }
  marcas=Array.from({length:total},()=>[]);
  for(const {n,trozos} of nodos){
    if(!trozos.length)continue;
    const t=n.nodeValue,frag=document.createDocumentFragment();let ult=0;
    for(const [a,b,c] of trozos){
      frag.appendChild(document.createTextNode(t.slice(ult,a)));
      const m=document.createElement('mark');m.textContent=t.slice(a,b);frag.appendChild(m);marcas[c].push(m);
      ult=b;
    }
    frag.appendChild(document.createTextNode(t.slice(ult)));n.parentNode.replaceChild(frag,n);
  }
  if(marcas.length){mi=-1;siguiente(1)}else $('cuenta').textContent='0 de 0';
}
function siguiente(d){
  if(!marcas.length)return;
  if(mi>=0)marcas[mi].forEach(m=>m.classList.remove('cur'));
  mi=(mi+d+marcas.length)%marcas.length;
  marcas[mi].forEach(m=>m.classList.add('cur'));marcas[mi][0].scrollIntoView({block:'center'});
  $('cuenta').textContent=`${mi+1} de ${marcas.length}`;
}
async function buscarTodas(){
  if(!carpeta)return;
  const q=$('q').value.trim();if(q.length<2)return;
  const r=await pywebview.api.buscar(q);
  const l=$('lado');l.innerHTML='';enBusqueda=true;
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
  $('abrir').onclick=abrirCarpeta;$('cerrar').onclick=cerrarCarpeta;
  $('atras').onclick=atras;$('adelante').onclick=adelante;
  $('todas').onclick=buscarTodas;
  $('q').addEventListener('input',()=>resaltar($('q').value.trim()));
  $('q').addEventListener('keydown',e=>{
    if(e.key==='Enter'){e.preventDefault();if(e.ctrlKey)buscarTodas();else siguiente(e.shiftKey?-1:1)}
    if(e.key==='Escape'){$('q').value='';resaltar('');$('q').blur()}
  });
  $('prev').onclick=()=>siguiente(-1);$('next').onclick=()=>siguiente(1);
  $('menos').onclick=()=>cambiarLetra(letra-10);$('mas').onclick=()=>cambiarLetra(letra+10);
  $('letra').onclick=()=>cambiarLetra(100);
  $('tema').onclick=cambiarTema;pintarTema();
  let raf=0;
  $('doc').addEventListener('scroll',()=>{
    if(!raf)raf=requestAnimationFrame(()=>{raf=0;marcarApartado()});
    if(carpeta&&actual)guardarLuego();
  });
});
// Ctrl+rueda: se acumula el giro para que el panel táctil (que manda muchos giros pequeños)
// no dispare la letra de golpe.
document.addEventListener('wheel',e=>{
  if(!e.ctrlKey)return;
  e.preventDefault();rueda+=e.deltaY;
  if(Math.abs(rueda)>=50){cambiarLetra(letra+(rueda<0?10:-10));rueda=0}
},{passive:false});
document.addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(e.ctrlKey&&k==='o'){e.preventDefault();abrirCarpeta()}
  if(e.ctrlKey&&k==='w'){e.preventDefault();cerrarCarpeta()}
  if(e.ctrlKey&&k==='f'&&carpeta){e.preventDefault();$('q').focus();$('q').select()}
  if(e.altKey&&e.key==='ArrowLeft'){e.preventDefault();atras()}
  if(e.altKey&&e.key==='ArrowRight'){e.preventDefault();adelante()}
  if(e.key==='F5'||(e.ctrlKey&&k==='r')){e.preventDefault();recargar()}
  if(e.key==='F3'){e.preventDefault();siguiente(e.shiftKey?-1:1)}
  if(e.ctrlKey&&(e.key==='+'||e.key==='='||e.code==='NumpadAdd')){e.preventDefault();cambiarLetra(letra+10)}
  if(e.ctrlKey&&(e.key==='-'||e.code==='NumpadSubtract')){e.preventDefault();cambiarLetra(letra-10)}
  if(e.ctrlKey&&(e.key==='0'||e.code==='Numpad0')){e.preventDefault();cambiarLetra(100)}
});

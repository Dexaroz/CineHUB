// =====================
//   CONFIGURACIÓN API
// =====================
const API_BASE_URL = localStorage.getItem('apiBaseUrl') || 'http://localhost:5000';
// false => backend real; true => datos mock
const USE_MOCK = JSON.parse(localStorage.getItem('useMock') ?? 'false');

window.CineHub = {
  setApi(url){ localStorage.setItem('apiBaseUrl', url); location.reload(); },
  toggleMock(value){ localStorage.setItem('useMock', String(value)); location.reload(); }
};

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));

function toast(msg, ms=1800){
  const el = $('#toast'); el.textContent = msg; el.classList.add('show');
  setTimeout(()=> el.classList.remove('show'), ms);
}

function openModal(editItem){
  $('#modal').classList.add('open');
  $('#modalTitle').textContent = editItem ? 'Editar película' : 'Nueva película';
  if (editItem){
    $('#id').value = editItem.id ?? '';
    $('#title').value = editItem.title ?? '';
    $('#year').value = editItem.year ?? '';
    $('#genre').value = editItem.genre ?? '';
    $('#rating').value = editItem.rating ?? '';
    $('#director').value = editItem.director ?? '';
    $('#poster').value = editItem.poster ?? '';
    $('#plot').value = editItem.plot ?? '';
    $('#runtime').value = editItem.runtime ?? '';
  } else {
    $('#form').reset(); $('#id').value = '';
  }
}
function closeModal(){ $('#modal').classList.remove('open'); }

function renderStars(r=0){
  const n = Math.max(0, Math.min(5, Number(r)||0));
  const full = Math.floor(n), half = n - full >= 0.5 ? 1 : 0, empty = 5 - full - half;
  const starFull = '<svg class="star" viewBox="0 0 24 24" fill="#fbbf24" aria-hidden="true"><path d="M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.168L12 18.897 4.664 23.165l1.402-8.168L.132 9.21l8.2-1.192z"/></svg>';
  const starHalf = '<svg class="star" viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="g"><stop offset="50%" stop-color="#fbbf24"/><stop offset="50%" stop-color="#1f2937"/></linearGradient></defs><path fill="url(#g)" d="M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.168L12 18.897 4.664 23.165l1.402-8.168L.132 9.21l8.2-1.192z"/></svg>';
  const starEmpty = '<svg class="star" viewBox="0 0 24 24" fill="#1f2a44" stroke="#334155" stroke-width="1.2" aria-hidden="true"><path d="M12 .587l3.668 7.431 8.2 1.192-5.934 5.787 1.402 8.168L12 18.897 4.664 23.165l1.402-8.168L.132 9.21l8.2-1.192z"/></svg>';
  return starFull.repeat(full) + starHalf.repeat(half) + starEmpty.repeat(empty);
}

function skeletonCards(n=6){
  return Array.from({length:n}, () => `
    <div class="card" aria-busy="true">
      <div class="poster"></div>
      <div class="badge" style="opacity:.4;width:80px; margin-top:10px">&nbsp;</div>
      <div class="title" style="height:24px;background:#0b1020;border-radius:8px;margin:12px 0 8px"></div>
      <div class="muted" style="height:14px;background:#0b1020;border-radius:6px;width:70%"></div>
      <div class="card-actions" style="margin-top:18px">
        <div class="pill" style="opacity:.4">&nbsp;&nbsp;&nbsp;&nbsp;</div>
        <div class="pill" style="opacity:.4">&nbsp;&nbsp;&nbsp;&nbsp;</div>
      </div>
    </div>`).join('');
}

// =====================
//   DATOS (mock/API)
// =====================
const mock = {
  items: [
    { id: 'mv01', title: 'Spirited Away', year: 2001, genre: 'Animación, Fantasía', rating: 4.8, director: 'Hayao Miyazaki', poster: 'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg', plot: 'Chihiro entra en un mundo mágico gobernado por dioses, brujas y espíritus.', runtime:125 },
    { id: 'mv02', title: 'The Matrix', year: 1999, genre: 'Acción, Sci-Fi', rating: 4.6, director: 'Lana & Lilly Wachowski', poster: 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg', plot: 'Un hacker descubre la verdadera naturaleza de su realidad.', runtime:136 },
    { id: 'mv03', title: 'Parasite', year: 2019, genre: 'Drama, Thriller', rating: 4.9, director: 'Bong Joon Ho', poster: 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg', plot: 'Una familia pobre se infiltra en la vida de una familia rica con consecuencias inesperadas.', runtime:132 },
    { id: 'mv04', title: 'The Shawshank Redemption', year: 1994, genre: 'Drama', rating: 4.9, director: 'Frank Darabont', poster: 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg', plot: 'Un hombre acusado injustamente encuentra esperanza y amistad en la cárcel de Shawshank.', runtime:142 },
    { id: 'mv05', title: 'Pulp Fiction', year: 1994, genre: 'Crimen, Drama', rating: 4.7, director: 'Quentin Tarantino', poster: 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg', plot: 'Historias entrelazadas de crimen y redención en Los Ángeles.', runtime:154 },
    { id: 'mv06', title: 'The Dark Knight', year: 2008, genre: 'Acción, Crimen, Drama', rating: 4.9, director: 'Christopher Nolan', poster: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg', plot: 'Batman se enfrenta al Joker, que desata el caos en Gotham.', runtime:152 },
    { id: 'mv07', title: 'Avatar', year: 2009, genre: 'Aventura, Sci-Fi', rating: 4.3, director: 'James Cameron', poster: 'https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg', plot: 'Un ex marine se involucra en el conflicto entre humanos y Na’vi en Pandora.', runtime:162 },
    { id: 'mv08', title: 'Your Name', year: 2016, genre: 'Animación, Romance, Fantasía', rating: 4.8, director: 'Makoto Shinkai', poster: 'https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg', plot: 'Dos adolescentes empiezan a intercambiar sus cuerpos a través de los sueños.', runtime:112 },
    { id: 'mv09', title: 'La La Land', year: 2016, genre: 'Romance, Drama, Música', rating: 4.4, director: 'Damien Chazelle', poster: 'https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg', plot: 'Una actriz y un pianista persiguen sus sueños en Los Ángeles mientras lidian con el amor y la ambición.', runtime:128 },
  ]
};

// Normaliza del backend (rate/synopsis/duration) a frontend (rating/plot/runtime)
function toUiModel(item){
  if (!item) return item;
  return {
    id: item.id,
    title: item.title,
    year: Number(item.year ?? item.year) || undefined,
    genre: item.genre,
    director: item.director,
    poster: item.poster,
    rating: item.rating ?? item.rate ?? 0,
    plot: item.plot ?? item.synopsis ?? '',
    runtime: item.runtime ?? item.duration ?? 0,
  };
}

// Inversa: del formulario/frontend al payload que espera el backend
function toApiPayload(movie){
  return {
    title: movie.title,
    year: movie.year,
    genre: movie.genre,
    director: movie.director,
    poster: movie.poster,
    synopsis: movie.plot ?? '',
    duration: movie.runtime ?? 0,
    rate: movie.rating ?? 0
  };
}

async function api(path='', options={}){
  if (USE_MOCK){
    await new Promise(r=>setTimeout(r, 280));
    const url = new URL(path, 'http://mock.local');
    const id = url.pathname.split('/').pop();
    if (options.method === 'POST'){
      const body = JSON.parse(options.body);
      body.id = 'm' + Math.random().toString(36).slice(2,7);
      const ui = toUiModel(body);
      mock.items.push(ui);
      return { ok:true, json: async()=> ui };
    }
    if (options.method === 'PUT'){
      const body = JSON.parse(options.body);
      const idx = mock.items.findIndex(x=>x.id===id);
      if (idx>-1) mock.items[idx]= toUiModel({ id, ...body });
      return { ok:true, json: async()=> mock.items[idx] };
    }
    if (options.method === 'DELETE'){
      const idx = mock.items.findIndex(x=>x.id===id);
      if (idx>-1) mock.items.splice(idx,1);
      return { ok:true, json: async()=> ({deleted:id}) };
    }
    // GET
    if (id && id !== 'items'){
      const item = mock.items.find(x=>x.id===id);
      return { ok: !!item, json: async()=> item };
    }
    return { ok:true, json: async()=> mock.items };
  }

  try {
    const res = await fetch(API_BASE_URL + path, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    return res;
  } catch (e){
    console.error('Network error', e);
    toast('No se pudo contactar con la API', 2200);
    throw e;
  }
}

// =====================
//   CRUD + Render
// =====================
async function listMovies(){
  $('#list').innerHTML = skeletonCards();
  const q = ($('#q').value||'').toLowerCase();

  try {
    const res = await api('/movies'); // evita 308 si el handler es @bp.get("/")
    if (!res.ok){
      const txt = await res.text().catch(()=> '');
      console.error('GET /movies failed', res.status, txt);
      toast(`Error listando (${res.status})`, 2200);
      $('#list').innerHTML = '';
      return;
    }
    const data = await res.json();
    const items = (Array.isArray(data) ? data : []).map(toUiModel);

    const filtered = items.filter(m =>
      !q || `${m.title} ${m.genre} ${m.director}`.toLowerCase().includes(q)
    );
    renderList(filtered);
  } catch (_) {
    $('#list').innerHTML = '';
  }
}

async function createMovie(movie){
  const payload = toApiPayload(movie);
  try {
    const res = await api('/movies', { method:'POST', body: JSON.stringify(payload) });
    if (!res.ok){
      const txt = await res.text().catch(()=> '');
      console.error('POST /movies/ failed', res.status, txt);
      return toast('Error al crear', 2000);
    }
    toast('Película creada');
    listMovies();
  } catch (_) {}
}

async function updateMovie(id, movie){
  const payload = toApiPayload(movie);
  try {
    const res = await api(`/movies/${id}`, { method:'PUT', body: JSON.stringify(payload) });
    if (!res.ok){
      const txt = await res.text().catch(()=> '');
      console.error(`PUT /movies/${id} failed`, res.status, txt);
      return toast('Error al actualizar', 2000);
    }
    toast('Película actualizada');
    listMovies();
  } catch (_) {}
}

async function deleteMovie(id){
  if (!confirm('¿Eliminar esta película?')) return;
  try {
    const res = await api(`/movies/${id}`, { method:'DELETE' });
    if (!res.ok){
      const txt = await res.text().catch(()=> '');
      console.error(`DELETE /movies/${id} failed`, res.status, txt);
      return toast('Error al eliminar', 2000);
    }
    toast('Película eliminada');
    listMovies();
  } catch (_) {}
}

function renderList(items){
  const list = $('#list');
  if (!items || !items.length){
    list.innerHTML = '';
    $('#empty').hidden = false;
    updateKpis([]);
    return;
  }
  $('#empty').hidden = true;
  list.innerHTML = items.map(m => `
    <div class="card">
      <img class="poster" alt="Poster de ${m.title||''}" src="${m.poster||''}" onerror="this.src='data:image/svg+xml;utf8,${encodeURIComponent(posterPlaceholder(m.title))}'" />
      <div class="badge">${(m.genre||'—')}</div>
      <div class="title">${escapeHtml(m.title||'Sin título')}</div>
      <div class="muted">${m.director||'Autor desconocido'} · ${m.year||'—'} · ${m.runtime? m.runtime+' min':'—'}</div>
      <div class="rating" aria-label="Valoración ${m.rating??'0'} de 5">${renderStars(m.rating)}</div>
      <div class="card-actions">
        <button class="pill" onclick='editMovie(${JSON.stringify(m)})'>Editar</button>
        <button class="pill" onclick='deleteMovie("${m.id}")'>Eliminar</button>
      </div>
    </div>
  `).join('');
  updateKpis(items);
}

function updateKpis(items){
  const total = items.length;
  const avg = total? (items.reduce((a,b)=> a + (Number(b.rating)||0), 0)/total).toFixed(1) : '–';
  const latest = total? Math.max(...items.map(i=> Number(i.year)||0)) : '–';
  $('#kpiTotal').textContent = total||'–';
  $('#kpiAvg').textContent = avg;
  $('#kpiYear').textContent = latest||'–';
}

// ===== Tema (light/dark) con botón =====
(function initThemeButton() {
  const saved = localStorage.getItem('theme'); // 'light' | 'dark' | null
  const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  const theme = saved || (systemPrefersLight ? 'light' : 'dark');
  applyTheme(theme);

  const btn = document.getElementById('themeBtn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    const next = (document.documentElement.getAttribute('data-theme') === 'light') ? 'dark' : 'light';
    applyTheme(next);
  });
})();

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);

  const btn = document.getElementById('themeBtn');
  if (btn) {
    const isLight = theme === 'light';
    btn.setAttribute('aria-pressed', String(isLight));
    btn.title = isLight ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro';
    const icon = btn.querySelector('.theme-icon');
    const text = btn.querySelector('.theme-text');
    if (icon) icon.textContent = isLight ? '☀️' : '🌙';
    if (text) text.textContent = isLight ? 'Claro' : 'Oscuro';
  }
}

function posterPlaceholder(title='?'){
  const t = encodeURIComponent(String(title||'?').slice(0,20));
  return `<svg xmlns='http://www.w3.org/2000/svg' width='400' height='533' viewBox='0 0 400 533'>
    <defs>
      <linearGradient id='g' x1='0' x2='1'>
        <stop offset='0%' stop-color='%2322d3ee'/>
        <stop offset='100%' stop-color='%238b5cf6'/>
      </linearGradient>
    </defs>
    <rect width='400' height='533' fill='%23111620'/>
    <rect x='20' y='20' width='360' height='493' rx='18' fill='url(%23g)' opacity='0.18'/>
    <text x='200' y='270' fill='%23e6e9ef' font-family='Inter, Arial' font-size='28' text-anchor='middle'>${t}</text>
  </svg>`;
}

function escapeHtml(s=''){ return s.replace(/[&<>"]/g, c=> ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

// Expose edit for inline handler
window.editMovie = (m) => openModal(m);

// =====================
//   Eventos UI
// =====================
$('#newBtn').addEventListener('click', () => openModal());
$('#cancelBtn').addEventListener('click', closeModal);
$('#refreshBtn').addEventListener('click', listMovies);
$('#q').addEventListener('input', () => listMovies());

$('#form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const movie = {
    id: $('#id').value || undefined,
    title: $('#title').value.trim(),
    year: Number($('#year').value)||undefined,
    genre: $('#genre').value.trim(),
    rating: $('#rating').value===''? undefined : Number($('#rating').value),
    director: $('#director').value.trim(),
    poster: $('#poster').value.trim(),
    plot: $('#plot').value.trim(),
    runtime: $('#runtime').value===''? undefined : Number($('#runtime').value)
  };
  if (!movie.title){ toast('El título es obligatorio', 2000); return; }
  closeModal();
  if (movie.id){ await updateMovie(movie.id, movie); }
  else { await createMovie(movie); }
});

listMovies();

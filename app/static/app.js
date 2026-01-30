/* app.js — UI logic only (scroll-based infinite) */

const PAGE_LIMIT = 100;

let offset = 0;
let loading = false;
let hasMore = true;

async function api(url, opts = {}) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(r.status);
  return r.json();
}

function qs(id) {
  return document.getElementById(id);
}

/* ---------- STATUS ---------- */
async function loadStatus() {
  const el = qs("status-badge");
  if (!el) return;
  const s = await api("/status");
  el.textContent = s.status;
}

/* ---------- TOP ---------- */
async function loadNextTop() {
  if (loading || !hasMore) return;
  loading = true;

  const data = await api(`/top?offset=${offset}&limit=${PAGE_LIMIT}`);
  const tbody = qs("top-table");
  const frag = document.createDocumentFragment();

  data.items.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="rank">${row.rank}</td>
      <td class="title">
        <a href="/static/movie.html?title=${encodeURIComponent(row.title)}">
          ${row.title}
        </a>
      </td>
      <td class="downloads">${row.downloads}</td>
    `;
    frag.appendChild(tr);
  });

  tbody.appendChild(frag);

  offset += data.items.length;
  hasMore = data.has_more;

  if (!hasMore) showEndOfList();

  loading = false;
}

function showEndOfList() {
  if (qs("end-of-list")) return;
  const div = document.createElement("div");
  div.id = "end-of-list";
  div.textContent = "Конец списка";
  qs("top-table").parentElement.appendChild(div);
}

/* ---------- SCROLL ---------- */
function bindScroll() {
  window.addEventListener("scroll", () => {
    if (!hasMore || loading) return;
    const nearBottom =
      window.innerHeight + window.scrollY >=
      document.body.offsetHeight - 200;
    if (nearBottom) {
      loadNextTop().catch(console.error);
    }
  });
}

/* ---------- MOVIE ---------- */
async function loadMovie() {
  const titleEl = qs("movie-title");
  if (!titleEl) return;

  const params = new URLSearchParams(location.search);
  const title = params.get("title");
  if (!title) return;

  const data = await api(`/movie?title=${encodeURIComponent(title)}`);

  titleEl.textContent = title;
  qs("movie-downloads").textContent = data.downloads || 0;

  const tbody = qs("topics-table");
  tbody.innerHTML = "";

  (data.topics || []).forEach(t => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="downloads">${t.downloads}</td>
      <td class="title">
        <a href="${t.url}" target="_blank">${t.url}</a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

/* ---------- FORUMS ---------- */
async function loadForums() {
  const list = qs("forums-list");
  if (!list) return;

  const data = await api("/forums");
  list.innerHTML = "";

  data.forums.forEach(url => {
    const li = document.createElement("li");
    li.innerHTML = `
      ${url}
      <button data-parse>Parse</button>
      <button data-remove>Remove</button>
    `;

    li.querySelector("[data-parse]").onclick = async () => {
      await api(`/parse?url=${encodeURIComponent(url)}`, { method: "POST" });
      alert("Parsing started");
    };

    li.querySelector("[data-remove]").onclick = async () => {
      await api(`/forum?url=${encodeURIComponent(url)}`, { method: "DELETE" });
      loadForums();
    };

    list.appendChild(li);
  });
}

function bindAddForum() {
  const btn = qs("add-forum");
  if (!btn) return;

  btn.onclick = async () => {
    const input = qs("forum-url");
    const url = input.value.trim();
    if (!url) return;
    await api(`/parse?url=${encodeURIComponent(url)}`, { method: "POST" });
    input.value = "";
    loadForums();
  };
}

/* ---------- SCHEDULER ---------- */
async function loadScheduler() {
  const en = qs("scheduler-enabled");
  const it = qs("scheduler-interval");
  if (!en && !it) return;

  const data = await api("/schedule/status");
  if (en) en.textContent = data.enabled;
  if (it) it.textContent = data.interval;
}

function bindScheduler() {
  const enBtn = qs("scheduler-enable");
  const disBtn = qs("scheduler-disable");

  if (enBtn) {
    enBtn.onclick = async () => {
      const val = qs("interval-input").value;
      await api(`/schedule/enable?interval=${encodeURIComponent(val)}`, { method: "POST" });
      loadScheduler();
    };
  }

  if (disBtn) {
    disBtn.onclick = async () => {
      await api("/schedule/disable", { method: "POST" });
      loadScheduler();
    };
  }
}

/* ---------- INIT ---------- */
(async function init() {
  try {
    await loadStatus();
    await loadMovie();
    await loadForums();
    await loadScheduler();
    bindAddForum();
    bindScheduler();

    const tbody = qs("top-table");
    if (tbody) {
      await loadNextTop();
      bindScroll();
    }
  } catch (e) {
    alert("API error: " + e.message);
  }
})();

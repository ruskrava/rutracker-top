/* app.js — UI for rutracker-top */

async function api(url, opts = {}) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(r.status);
  return r.json();
}

function qs(id) {
  return document.getElementById(id);
}

/* -------- STATUS -------- */
async function loadStatus() {
  const el = qs("status-badge");
  if (!el) return;
  const s = await api("/status");
  el.textContent = s.status;
}

/* -------- TOP -------- */
async function loadTop() {
  const tbody = qs("top-table");
  if (!tbody) return;

  const data = await api("/top?n=50");
  tbody.innerHTML = "";

  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.rank}</td>
      <td>
        <a href="/static/movie.html?title=${encodeURIComponent(row.title)}">
          ${row.title}
        </a>
      </td>
      <td>${row.downloads}</td>
    `;
    tbody.appendChild(tr);
  });
}

/* -------- MOVIE -------- */
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
      <td>${t.downloads}</td>
      <td><a href="${t.url}" target="_blank">${t.url}</a></td>
    `;
    tbody.appendChild(tr);
  });
}

/* -------- FORUMS -------- */
async function loadForums() {
  const list = qs("forums-list");
  if (!list) return;

  const forums = await api("/forums");
  list.innerHTML = "";

  forums.forEach(url => {
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

/* -------- SCHEDULER -------- */
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

/* -------- INIT -------- */
(async function init() {
  try {
    await loadStatus();
    await loadTop();
    await loadMovie();
    await loadForums();
    await loadScheduler();
    bindAddForum();
    bindScheduler();
  } catch (e) {
    alert("API error: " + e.message);
  }
})();

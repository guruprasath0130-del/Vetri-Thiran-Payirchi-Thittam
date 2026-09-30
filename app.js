const TOKEN_KEY = "pocketsmart_token";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  updateNav();
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  updateNav();
}

function requireAuth() {
  if (!getToken()) location.href = "/login";
}

function updateNav() {
  const token = getToken();
  const login = document.getElementById("loginLink");
  const logout = document.getElementById("logoutBtn");
  if (login) login.classList.toggle("hidden", !!token);
  if (logout) logout.classList.toggle("hidden", !token);
}

async function api(path, options = {}) {
  const opts = {...options, headers: {...(options.headers || {})}};
  if (options.auth) {
    const token = getToken();
    if (!token) {
      location.href = "/login";
      throw new Error("Authentication required");
    }
    opts.headers["Authorization"] = `Bearer ${token}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    opts.headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, opts);
  let data = {};
  try { data = await response.json(); } catch (_) {}

  if (response.status === 401) {
    clearToken();
    if (options.auth) location.href = "/login";
  }
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map(x => x.msg).join(", ")
      : data.detail || "Request failed";
    throw new Error(detail);
  }
  return data;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

function money(value) {
  return new Intl.NumberFormat("en-IN", {
    style:"currency", currency:"INR", maximumFractionDigits:0
  }).format(Number(value || 0));
}

function renderRecommendation(data, targetId) {
  const box = document.getElementById(targetId);
  box.classList.remove("hidden");

  const breakdown = (data.budget_breakdown || []).map(x =>
    `<span class="chip">${escapeHtml(x.category)} · ${money(x.amount)}</span>`
  ).join("");

  const recs = (data.recommendations || []).map(x => `
    <article class="rec-card">
      <div class="rec-meta"><span>${escapeHtml(x.category)}</span><span>${escapeHtml(x.platform)}</span></div>
      <h3>${escapeHtml(x.title)}</h3>
      <div class="rec-price">${money(x.estimated_price)} × ${escapeHtml(x.quantity)}</div>
      <p>${escapeHtml(x.reason)}</p>
      <a class="rec-link" href="${escapeHtml(x.search_url)}" target="_blank" rel="noopener noreferrer">Search on ${escapeHtml(x.platform)} →</a>
    </article>
  `).join("");

  const tips = (data.tips || []).map(x => `<li>${escapeHtml(x)}</li>`).join("");

  box.innerHTML = `
    <div class="panel" style="padding:28px">
      <div class="result-head">
        <div><span class="eyebrow">${escapeHtml(data.planner_type).toUpperCase()} PLAN</span>
        <h2>${escapeHtml(data.title)}</h2></div>
        <div class="result-total">${money(data.estimated_total)}<small>of ${money(data.budget)} budget · ${money(data.remaining_budget)} remaining</small></div>
      </div>
      <p class="result-summary">${escapeHtml(data.summary)}</p>
      <div class="breakdown">${breakdown}</div>
      <div class="recommend-grid">${recs}</div>
      <div style="margin-top:22px"><h3>Tips</h3><ul>${tips}</ul></div>
    </div>`;
  box.scrollIntoView({behavior:"smooth", block:"start"});
}

document.addEventListener("DOMContentLoaded", () => {
  updateNav();
  const logout = document.getElementById("logoutBtn");
  if (logout) logout.addEventListener("click", () => {
    clearToken();
    location.href = "/";
  });
});

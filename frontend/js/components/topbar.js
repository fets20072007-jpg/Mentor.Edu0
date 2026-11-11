import { icon } from "./icons.js";
import { roleLabel } from "../core/permissions.js";
import { searchRoutes } from "../core/global-search.js";

function initials(name = "Usuário") {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    return (parts.length > 1 ? `${parts[0][0]}${parts.at(-1)[0]}` : parts[0]?.[0] || "U").toUpperCase();
}

export function renderTopbar({ user, role, title = "Dashboard", unread = 0, onMenu, onNotifications, onSearchNavigate }) {
    const root = document.getElementById("topbar");
    const year = new Date().getFullYear();
    root.innerHTML = `<div class="topbar-left"><button id="mobileMenuButton" class="mobile-menu-button" type="button" aria-label="Alternar menu">${icon("menu")}</button><div class="topbar-title"><h1 id="pageTitle">${title}</h1><small>${roleLabel(role) === "Aluno" ? "Painel do Aluno" : roleLabel(role) === "Professor" ? "Área do Professor" : roleLabel(role) === "Administração" ? "Painel de Administração" : "Área de Suporte"}</small></div></div><div class="topbar-center"><div class="search-shell">${icon("search")}<input class="topbar-search" type="search" placeholder="Buscar no Mentor.Edu..." aria-label="Buscar no Mentor.Edu" autocomplete="off"><div class="search-results" data-search-results hidden></div></div></div><div class="topbar-actions"><div class="year-chip">${icon("calendar")}<span>${year}</span></div><button id="notificationButton" class="icon-button" type="button" aria-label="Notificações">${icon("bell")}${unread > 0 ? `<span class="notification-dot">${Math.min(unread,99)}</span>` : ""}</button><div class="user-chip"><div class="avatar">${initials(user.nome)}</div><div><strong>${user.nome}</strong><small>${roleLabel(role)}</small></div></div></div>`;
    root.querySelector("#mobileMenuButton")?.addEventListener("click", onMenu);
    root.querySelector("#notificationButton")?.addEventListener("click", onNotifications);
    const input=root.querySelector('.topbar-search'); const results=root.querySelector('[data-search-results]');
    const hide=()=>{ results.hidden=true; results.innerHTML=''; };
    const draw=()=>{ const rows=searchRoutes(role,input.value); if(!rows.length){hide();return;} results.innerHTML=rows.map(r=>`<button type="button" data-search-route="${r.route}">${icon('search')}<span>${r.label}</span></button>`).join(''); results.hidden=false; results.querySelectorAll('[data-search-route]').forEach(b=>b.addEventListener('click',()=>{onSearchNavigate?.(b.dataset.searchRoute);input.value='';hide();})); };
    input?.addEventListener('input',draw);
    input?.addEventListener('keydown',e=>{ if(e.key==='Escape') hide(); if(e.key==='Enter'){ const first=searchRoutes(role,input.value)[0]; if(first){e.preventDefault();onSearchNavigate?.(first.route);input.value='';hide();} } });
    document.addEventListener('click',e=>{ if(!root.querySelector('.search-shell')?.contains(e.target)) hide(); },{once:false});
}

export function setTopbarTitle(title) {
    const target = document.getElementById("pageTitle");
    if (target) target.textContent = title;
}

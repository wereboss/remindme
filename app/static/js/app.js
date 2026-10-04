// PWA Service Worker Registration
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js")
      .then((reg) => console.log("Service Worker registered:", reg.scope))
      .catch((err) => console.error("Service Worker registration failed:", err));
  });
}

// State
let currentUser = null;
let currentFilter = "all";
let searchQuery = "";
let selectedTag = "";
let isRegisterMode = false;
let notesData = [];
let searchDebounceTimer = null;

// DOM Elements
const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const authNav = document.getElementById("authNav");
const navUsername = document.getElementById("navUsername");
const logoutBtn = document.getElementById("logoutBtn");

const authTitle = document.getElementById("authTitle");
const authError = document.getElementById("authError");
const authForm = document.getElementById("authForm");
const usernameInput = document.getElementById("usernameInput");
const passwordInput = document.getElementById("passwordInput");
const authSubmitBtn = document.getElementById("authSubmitBtn");
const toggleLoginBtn = document.getElementById("toggleLoginBtn");
const toggleRegisterBtn = document.getElementById("toggleRegisterBtn");

const fabBtn = document.getElementById("fabBtn");
const searchInput = document.getElementById("searchInput");
const searchClearBtn = document.getElementById("searchClearBtn");

const activeTagBanner = document.getElementById("activeTagBanner");
const activeTagName = document.getElementById("activeTagName");
const clearTagBtn = document.getElementById("clearTagBtn");

const filterBtns = document.querySelectorAll(".filter-btn");
const notesGrid = document.getElementById("notesGrid");
const notesCount = document.getElementById("notesCount");
const emptyNotesMsg = document.getElementById("emptyNotesMsg");

// Unified Note Modal
const noteModal = document.getElementById("noteModal");
const noteModalForm = document.getElementById("noteModalForm");
const modalTitle = document.getElementById("modalTitle");
const modalNoteId = document.getElementById("modalNoteId");
const modalNoteTitle = document.getElementById("modalNoteTitle");
const modalNoteContent = document.getElementById("modalNoteContent");
const modalNoteDeadline = document.getElementById("modalNoteDeadline");
const modalNoteTags = document.getElementById("modalNoteTags");
const modalCompletedGroup = document.getElementById("modalCompletedGroup");
const modalIsCompleted = document.getElementById("modalIsCompleted");
const closeNoteModal = document.getElementById("closeNoteModal");
const cancelModalBtn = document.getElementById("cancelModalBtn");
const offlineBanner = document.getElementById("offlineBanner");

// Network status listeners
window.addEventListener("online", () => offlineBanner.classList.add("hidden"));
window.addEventListener("offline", () => offlineBanner.classList.remove("hidden"));

// Init
document.addEventListener("DOMContentLoaded", () => {
  checkAuth();
  setupEventListeners();
});

function setupEventListeners() {
  toggleLoginBtn.addEventListener("click", () => setAuthMode(false));
  toggleRegisterBtn.addEventListener("click", () => setAuthMode(true));
  authForm.addEventListener("submit", handleAuthSubmit);
  logoutBtn.addEventListener("click", handleLogout);

  // FAB & Modal
  fabBtn.addEventListener("click", openCreateModal);
  closeNoteModal.addEventListener("click", closeModal);
  cancelModalBtn.addEventListener("click", closeModal);
  noteModalForm.addEventListener("submit", handleModalSubmit);

  // Close modal when clicking outside content
  noteModal.addEventListener("click", (e) => {
    if (e.target === noteModal) closeModal();
  });

  // Filter Buttons
  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      loadNotes();
    });
  });

  // Search
  searchInput.addEventListener("input", () => {
    clearTimeout(searchDebounceTimer);
    const val = searchInput.value.trim();
    if (val) {
      searchClearBtn.classList.remove("hidden");
    } else {
      searchClearBtn.classList.add("hidden");
    }
    searchDebounceTimer = setTimeout(() => {
      searchQuery = val;
      loadNotes();
    }, 300);
  });

  searchClearBtn.addEventListener("click", () => {
    searchInput.value = "";
    searchQuery = "";
    searchClearBtn.classList.add("hidden");
    loadNotes();
  });

  // Tag filter banner clear
  clearTagBtn.addEventListener("click", () => {
    selectedTag = "";
    activeTagBanner.classList.add("hidden");
    loadNotes();
  });
}

function setAuthMode(register) {
  isRegisterMode = register;
  authError.classList.add("hidden");
  if (isRegisterMode) {
    authTitle.textContent = "Create Account";
    authSubmitBtn.textContent = "Register";
    toggleRegisterBtn.classList.add("active");
    toggleLoginBtn.classList.remove("active");
  } else {
    authTitle.textContent = "Sign In";
    authSubmitBtn.textContent = "Sign In";
    toggleLoginBtn.classList.add("active");
    toggleRegisterBtn.classList.remove("active");
  }
}

async function checkAuth() {
  try {
    const res = await fetch("/api/me");
    if (res.ok) {
      currentUser = await res.json();
      showApp();
    } else {
      showAuth();
    }
  } catch (err) {
    showAuth();
  }
}

function showAuth() {
  currentUser = null;
  authNav.classList.add("hidden");
  appSection.classList.add("hidden");
  fabBtn.classList.add("hidden");
  authSection.classList.remove("hidden");
  usernameInput.value = "";
  passwordInput.value = "";
}

function showApp() {
  authSection.classList.add("hidden");
  authNav.classList.remove("hidden");
  appSection.classList.remove("hidden");
  fabBtn.classList.remove("hidden");
  navUsername.textContent = `@${currentUser.username}`;
  loadNotes();
}

async function handleAuthSubmit(e) {
  e.preventDefault();
  authError.classList.add("hidden");

  const endpoint = isRegisterMode ? "/api/register" : "/api/login";
  const body = {
    username: usernameInput.value.trim(),
    password: passwordInput.value,
  };

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    if (!res.ok) {
      authError.textContent = data.error || "Authentication failed.";
      authError.classList.remove("hidden");
      return;
    }

    currentUser = data.user;
    showApp();
  } catch (err) {
    authError.textContent = "Network error. Please try again.";
    authError.classList.remove("hidden");
  }
}

async function handleLogout() {
  try {
    await fetch("/api/logout", { method: "POST" });
  } catch (err) {
    console.error(err);
  }
  showAuth();
}

async function loadNotes() {
  try {
    let url = `/api/notes?filter=${encodeURIComponent(currentFilter)}`;
    if (searchQuery) url += `&q=${encodeURIComponent(searchQuery)}`;
    if (selectedTag) url += `&tag=${encodeURIComponent(selectedTag)}`;

    const res = await fetch(url);
    if (!res.ok) {
      if (res.status === 401) showAuth();
      return;
    }
    notesData = await res.json();
    renderNotes();
  } catch (err) {
    console.error("Failed to load notes", err);
  }
}

function formatDeadline(isoString) {
  if (!isoString) return "";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}

function renderBadge(status, deadline, isArchived) {
  if (isArchived) {
    return `<span class="badge badge-archived">📦 Archived</span>`;
  }
  if (status === "completed") {
    return `<span class="badge badge-completed">✓ Done</span>`;
  }
  if (!deadline || status === "none") {
    return "";
  }
  const formatted = formatDeadline(deadline);
  if (status === "overdue") {
    return `<span class="badge badge-overdue" title="Overdue">⚠️ Overdue (${formatted})</span>`;
  }
  if (status === "due_today") {
    return `<span class="badge badge-today" title="Due today">🔔 Due Today (${formatted})</span>`;
  }
  if (status === "upcoming") {
    return `<span class="badge badge-upcoming" title="Upcoming deadline">📅 Due: ${formatted}</span>`;
  }
  return "";
}

function renderNotes() {
  notesGrid.innerHTML = "";
  notesCount.textContent = `${notesData.length} note${notesData.length === 1 ? "" : "s"}`;

  if (notesData.length === 0) {
    emptyNotesMsg.classList.remove("hidden");
    return;
  }
  emptyNotesMsg.classList.add("hidden");

  notesData.forEach((note) => {
    const card = document.createElement("div");
    card.className = `note-card ${note.is_completed ? "completed" : ""} ${note.is_archived ? "archived" : ""}`;
    card.dataset.id = note.id;

    const badgeHtml = renderBadge(note.status, note.deadline, note.is_archived);

    // Render tags
    let tagsHtml = "";
    if (note.tags && note.tags.length > 0) {
      tagsHtml = `<div class="note-tags">` + 
        note.tags.map(t => `<span class="tag-chip" data-tag="${escapeHtml(t)}">#${escapeHtml(t)}</span>`).join("") + 
        `</div>`;
    }

    const archiveBtnLabel = note.is_archived ? "Restore" : "Archive";
    const archiveBtnAction = note.is_archived ? "restore" : "archive";

    card.innerHTML = `
      <div>
        <div class="note-header">
          <div class="note-title-wrap">
            <input type="checkbox" class="note-checkbox" ${note.is_completed ? "checked" : ""} aria-label="Toggle completion">
            <span class="note-title">${escapeHtml(note.title)}</span>
          </div>
        </div>
        ${note.content ? `<div class="note-content">${escapeHtml(note.content)}</div>` : ""}
        ${tagsHtml}
      </div>
      <div class="note-footer">
        <div>${badgeHtml}</div>
        <div class="note-actions">
          <button class="btn btn-secondary btn-sm edit-btn">Edit</button>
          <button class="btn btn-secondary btn-sm archive-btn" data-action="${archiveBtnAction}">${archiveBtnLabel}</button>
          <button class="btn btn-danger btn-sm delete-btn">Delete</button>
        </div>
      </div>
    `;

    // Event listeners
    const checkbox = card.querySelector(".note-checkbox");
    checkbox.addEventListener("change", () => toggleCompletion(note));

    const editBtn = card.querySelector(".edit-btn");
    editBtn.addEventListener("click", () => openEditModal(note));

    const archiveBtn = card.querySelector(".archive-btn");
    archiveBtn.addEventListener("click", () => toggleArchive(note));

    const deleteBtn = card.querySelector(".delete-btn");
    deleteBtn.addEventListener("click", () => deleteNote(note.id));

    // Tag chip clicks
    card.querySelectorAll(".tag-chip").forEach((chip) => {
      chip.addEventListener("click", (e) => {
        e.stopPropagation();
        filterByTag(chip.dataset.tag);
      });
    });

    notesGrid.appendChild(card);
  });
}

function filterByTag(tag) {
  selectedTag = tag;
  activeTagName.textContent = `#${tag}`;
  activeTagBanner.classList.remove("hidden");
  loadNotes();
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function openCreateModal() {
  modalTitle.textContent = "Create Note or Reminder";
  modalNoteId.value = "";
  modalNoteTitle.value = "";
  modalNoteContent.value = "";
  modalNoteDeadline.value = "";
  modalNoteTags.value = selectedTag ? selectedTag : "";
  modalCompletedGroup.classList.add("hidden");
  modalIsCompleted.checked = false;
  noteModal.classList.remove("hidden");
  modalNoteTitle.focus();
}

function openEditModal(note) {
  modalTitle.textContent = "Edit Note";
  modalNoteId.value = note.id;
  modalNoteTitle.value = note.title;
  modalNoteContent.value = note.content || "";
  modalNoteTags.value = note.tags_str || (note.tags ? note.tags.join(", ") : "");
  
  if (note.deadline) {
    const d = new Date(note.deadline);
    if (!isNaN(d.getTime())) {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const hours = String(d.getHours()).padStart(2, "0");
      const minutes = String(d.getMinutes()).padStart(2, "0");
      modalNoteDeadline.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    } else {
      modalNoteDeadline.value = "";
    }
  } else {
    modalNoteDeadline.value = "";
  }

  modalCompletedGroup.classList.remove("hidden");
  modalIsCompleted.checked = Boolean(note.is_completed);
  noteModal.classList.remove("hidden");
  modalNoteTitle.focus();
}

function closeModal() {
  noteModal.classList.add("hidden");
}

async function handleModalSubmit(e) {
  e.preventDefault();
  const id = modalNoteId.value;
  const isEditing = Boolean(id);

  const payload = {
    title: modalNoteTitle.value.trim(),
    content: modalNoteContent.value,
    deadline: modalNoteDeadline.value || null,
    tags: modalNoteTags.value,
  };

  if (isEditing) {
    payload.is_completed = modalIsCompleted.checked;
  }

  const endpoint = isEditing ? `/api/notes/${id}` : "/api/notes";
  const method = isEditing ? "PUT" : "POST";

  try {
    const res = await fetch(endpoint, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      closeModal();
      loadNotes();
    } else {
      const data = await res.json();
      alert(data.error || "Failed to save note.");
    }
  } catch (err) {
    alert("Network error saving note.");
  }
}

async function toggleCompletion(note) {
  const updatedStatus = !note.is_completed;
  try {
    const res = await fetch(`/api/notes/${note.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_completed: updatedStatus }),
    });
    if (res.ok) {
      loadNotes();
    }
  } catch (err) {
    console.error("Failed to toggle completion", err);
  }
}

async function toggleArchive(note) {
  const endpoint = note.is_archived ? `/api/notes/${note.id}/unarchive` : `/api/notes/${note.id}/archive`;
  try {
    const res = await fetch(endpoint, { method: "POST" });
    if (res.ok) {
      loadNotes();
    }
  } catch (err) {
    console.error("Failed to toggle archive", err);
  }
}

async function deleteNote(id) {
  if (!confirm("Are you sure you want to permanently delete this note?")) return;

  try {
    const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
    if (res.ok) {
      loadNotes();
    }
  } catch (err) {
    alert("Network error deleting note.");
  }
}

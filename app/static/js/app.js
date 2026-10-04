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
let isRegisterMode = false;
let notesData = [];

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

const createNoteForm = document.getElementById("createNoteForm");
const noteTitle = document.getElementById("noteTitle");
const noteContent = document.getElementById("noteContent");
const noteDeadline = document.getElementById("noteDeadline");

const filterBtns = document.querySelectorAll(".filter-btn");
const notesGrid = document.getElementById("notesGrid");
const notesCount = document.getElementById("notesCount");
const emptyNotesMsg = document.getElementById("emptyNotesMsg");

const editModal = document.getElementById("editModal");
const editNoteForm = document.getElementById("editNoteForm");
const editNoteId = document.getElementById("editNoteId");
const editTitle = document.getElementById("editTitle");
const editContent = document.getElementById("editContent");
const editDeadline = document.getElementById("editDeadline");
const editIsCompleted = document.getElementById("editIsCompleted");
const closeEditModal = document.getElementById("closeEditModal");
const cancelEditBtn = document.getElementById("cancelEditBtn");
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
  createNoteForm.addEventListener("submit", handleCreateNote);

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter;
      loadNotes();
    });
  });

  closeEditModal.addEventListener("click", () => editModal.classList.add("hidden"));
  cancelEditBtn.addEventListener("click", () => editModal.classList.add("hidden"));
  editNoteForm.addEventListener("submit", handleEditSubmit);
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
  authSection.classList.remove("hidden");
  usernameInput.value = "";
  passwordInput.value = "";
}

function showApp() {
  authSection.classList.add("hidden");
  authNav.classList.remove("hidden");
  appSection.classList.remove("hidden");
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
    const res = await fetch(`/api/notes?filter=${encodeURIComponent(currentFilter)}`);
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

function renderBadge(status, deadline) {
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
    card.className = `note-card ${note.is_completed ? "completed" : ""}`;
    card.dataset.id = note.id;

    const badgeHtml = renderBadge(note.status, note.deadline);

    card.innerHTML = `
      <div>
        <div class="note-header">
          <div class="note-title-wrap">
            <input type="checkbox" class="note-checkbox" ${note.is_completed ? "checked" : ""} aria-label="Toggle completion">
            <span class="note-title">${escapeHtml(note.title)}</span>
          </div>
        </div>
        ${note.content ? `<div class="note-content">${escapeHtml(note.content)}</div>` : ""}
      </div>
      <div class="note-footer">
        <div>${badgeHtml}</div>
        <div class="note-actions">
          <button class="btn btn-secondary btn-sm edit-btn">Edit</button>
          <button class="btn btn-danger btn-sm delete-btn">Delete</button>
        </div>
      </div>
    `;

    // Event listeners
    const checkbox = card.querySelector(".note-checkbox");
    checkbox.addEventListener("change", () => toggleCompletion(note));

    const editBtn = card.querySelector(".edit-btn");
    editBtn.addEventListener("click", () => openEditModal(note));

    const deleteBtn = card.querySelector(".delete-btn");
    deleteBtn.addEventListener("click", () => deleteNote(note.id));

    notesGrid.appendChild(card);
  });
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

async function handleCreateNote(e) {
  e.preventDefault();
  const title = noteTitle.value.trim();
  if (!title) return;

  const payload = {
    title: title,
    content: noteContent.value,
    deadline: noteDeadline.value || null,
  };

  try {
    const res = await fetch("/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      createNoteForm.reset();
      loadNotes();
    } else {
      const data = await res.json();
      alert(data.error || "Failed to create note.");
    }
  } catch (err) {
    alert("Network error creating note.");
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

function openEditModal(note) {
  editNoteId.value = note.id;
  editTitle.value = note.title;
  editContent.value = note.content || "";
  
  // Format datetime-local input (YYYY-MM-DDTHH:MM)
  if (note.deadline) {
    const d = new Date(note.deadline);
    if (!isNaN(d.getTime())) {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const hours = String(d.getHours()).padStart(2, "0");
      const minutes = String(d.getMinutes()).padStart(2, "0");
      editDeadline.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    } else {
      editDeadline.value = "";
    }
  } else {
    editDeadline.value = "";
  }

  editIsCompleted.checked = Boolean(note.is_completed);
  editModal.classList.remove("hidden");
}

async function handleEditSubmit(e) {
  e.preventDefault();
  const id = editNoteId.value;
  const payload = {
    title: editTitle.value.trim(),
    content: editContent.value,
    deadline: editDeadline.value || null,
    is_completed: editIsCompleted.checked,
  };

  try {
    const res = await fetch(`/api/notes/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      editModal.classList.add("hidden");
      loadNotes();
    } else {
      const data = await res.json();
      alert(data.error || "Failed to update note.");
    }
  } catch (err) {
    alert("Network error updating note.");
  }
}

async function deleteNote(id) {
  if (!confirm("Are you sure you want to delete this note?")) return;

  try {
    const res = await fetch(`/api/notes/${id}`, { method: "DELETE" });
    if (res.ok) {
      loadNotes();
    }
  } catch (err) {
    alert("Network error deleting note.");
  }
}

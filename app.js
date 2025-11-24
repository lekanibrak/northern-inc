// Simple tab navigation between screens
const navItems = document.querySelectorAll(".nav-item");
const screens = document.querySelectorAll(".screen");

navItems.forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.getAttribute("data-target");

    // Toggle active nav button
    navItems.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    // Show correct screen
    screens.forEach((screen) => {
      if (screen.id === targetId) {
        screen.classList.add("active");
      } else {
        screen.classList.remove("active");
      }
    });
  });
});

// --- Dynamic data loading from backend API ---
async function loadMessages() {
  try {
    const res = await fetch('/api/messages');
    if (!res.ok) throw new Error('Network response was not ok');
    const messages = await res.json();

    const list = document.querySelector('.message-list');
    list.innerHTML = ''; // clear placeholder items

    messages.forEach((m) => {
      const li = document.createElement('li');
      li.className = 'message-item';

      li.innerHTML = `
        <div class="avatar">${m.avatar}</div>
        <div class="message-body">
          <p class="message-title">${m.title}</p>
          <p class="message-snippet">${m.snippet}</p>
          <span class="message-meta">${m.meta}</span>
        </div>
        ${m.unread ? `<span class="badge">${m.unread}</span>` : ''}
      `;

      list.appendChild(li);
    });
  } catch (err) {
    console.error('Failed to load messages', err);
  }
}

async function loadAvailability() {
  try {
    const res = await fetch('/api/availability');
    if (!res.ok) throw new Error('Network response was not ok');
    const data = await res.json();
    const el = document.querySelector('.banner-timer');
    if (el && data.expiresIn) el.textContent = data.expiresIn;
  } catch (err) {
    console.error('Failed to load availability', err);
  }
}

// Initialize dynamic parts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  loadMessages();
  loadAvailability();
});

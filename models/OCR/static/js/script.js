document.querySelectorAll('.service-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    console.log('Navigating to:', e.target.textContent);
  });
});

document.querySelector('.login-btn')?.addEventListener('click', () => {
  console.log('Login clicked');
});

let chatContext = "";

function openForm() {
  const el = document.getElementById("myForm");
  if (el) el.style.display = "block";
}

function closeForm() {
  const el = document.getElementById("myForm");
  if (el) el.style.display = "none";
}

async function sendMessage(event) {
  event.preventDefault();
  const messageInput = document.getElementById("message");
  const messagesDiv = document.getElementById("messages");
  const userMessage = (messageInput && messageInput.value) ? messageInput.value.trim() : "";
  if (!userMessage || !messagesDiv) return;

  messagesDiv.innerHTML += `<p class='user'><b>You:</b> ${escapeHtml(userMessage)}</p>`;
  messageInput.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userMessage, context: chatContext }),
    });
    const data = await response.json();
    if (data.updated_context !== undefined) chatContext = data.updated_context;
    messagesDiv.innerHTML += `<p class='bot'><b>Assistant:</b> ${escapeHtml(data.answer || "No response.")}</p>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  } catch (err) {
    console.error("Chatbot error:", err);
    messagesDiv.innerHTML += `<p class='error'><b>Error:</b> Unable to reach the assistant.</p>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

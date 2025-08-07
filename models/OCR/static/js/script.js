// Add click event listeners for the service cards
document.querySelectorAll('.service-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      // This will be replaced with actual navigation logic later
      console.log('Navigating to:', e.target.textContent);
    });
  });
  
  // Add click event listener for the login button
  document.querySelector('.login-btn').addEventListener('click', () => {
    // This will be replaced with actual login logic later
    console.log('Login clicked');
  });

  // chatbot 
  let context = "";

// Function to open chat popup
function openForm() {
  document.getElementById("myForm").style.display = "block";
}

// Function to close chat popup
function closeForm() {
  document.getElementById("myForm").style.display = "none";
}

// Function to send a message to the chatbot backend
async function sendMessage(event) {
  event.preventDefault();

  let messageInput = document.getElementById("message");
  let messagesDiv = document.getElementById("messages");
  let userMessage = messageInput.value.trim();

  if (!userMessage) return; // Prevent empty messages

  // Display user's message
  messagesDiv.innerHTML += `<p class='user'><b>You:</b> ${userMessage}</p>`;
  messageInput.value = "";

  try {
      // Send message to backend chatbot API
      let response = await fetch("http://127.0.0.1:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: userMessage })
      });

      let data = await response.json();

      // Display chatbot's response
      messagesDiv.innerHTML += `<p class='bot'><b>Bot:</b> ${data.answer}</p>`;

      // Auto-scroll to the latest message
      messagesDiv.scrollTop = messagesDiv.scrollHeight;

  } catch (error) {
      console.error("Error communicating with chatbot:", error);
      messagesDiv.innerHTML += `<p class='error'><b>Error:</b> Unable to get a response from the chatbot.</p>`;
  }
}

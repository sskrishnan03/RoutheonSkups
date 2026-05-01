document.addEventListener("DOMContentLoaded", function () {
  const fab = document.getElementById("chatbot-fab");
  const chatWindow = document.getElementById("chatbot-window");
  const closeChat = document.getElementById("close-chat");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-chat");
  const messagesContainer = document.getElementById("chat-messages");

  if (fab) {
    fab.addEventListener("click", () => {
      chatWindow.classList.toggle("hidden");
    });

    closeChat.addEventListener("click", () => {
      chatWindow.classList.add("hidden");
    });

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  }

  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    appendMessage("user", text);
    chatInput.value = "";

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();
      appendMessage("bot", data.response);

      if (data.images && data.images.length > 0) {
        appendImages(data.images);
      }
    } catch (error) {
      console.error("Chat error:", error);
      appendMessage("bot", "Sorry, something went wrong.");
    }
  }

  function appendMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}-msg`;
    div.innerHTML = `<p>${text}</p>`;
    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendImages(images) {
    const div = document.createElement("div");
    div.className = "message bot-msg chat-images";
    div.style.display = "grid";
    div.style.gridTemplateColumns = "repeat(2, 1fr)";
    div.style.gap = "5px";
    div.style.marginTop = "10px";

    images.forEach((url) => {
      const img = document.createElement("img");
      img.src = url;
      img.style.width = "100%";
      img.style.height = "100px";
      img.style.objectFit = "cover";
      img.style.borderRadius = "8px";
      div.appendChild(img);
    });

    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
});

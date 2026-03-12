const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newSessionBtn = document.getElementById("new-session-btn");

let sessionId = null;

async function createSession() {
  const resp = await fetch("/api/session/new", { method: "POST" });
  const data = await resp.json();
  sessionId = data.session_id;
  messagesEl.innerHTML = "";
}

function addMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML = renderMarkdown(content);
  messagesEl.appendChild(div);
  messagesEl.parentElement.scrollTop = messagesEl.parentElement.scrollHeight;
  return div;
}

function renderMarkdown(text) {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  const lines = html.split("\n");
  let inTable = false;
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith("|") && line.endsWith("|")) {
      if (!inTable) {
        result.push("<table>");
        inTable = true;
        const cells = line.split("|").filter((c) => c.trim());
        result.push("<tr>" + cells.map((c) => `<th>${c.trim()}</th>`).join("") + "</tr>");
      } else if (line.replace(/[|\-\s:]/g, "") === "") {
        continue;
      } else {
        const cells = line.split("|").filter((c) => c.trim());
        result.push("<tr>" + cells.map((c) => `<td>${c.trim()}</td>`).join("") + "</tr>");
      }
    } else {
      if (inTable) {
        result.push("</table>");
        inTable = false;
      }
      result.push(line);
    }
  }
  if (inTable) result.push("</table>");

  return result.join("\n");
}

async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) return;

  if (!sessionId) await createSession();

  addMessage("user", message);
  inputEl.value = "";
  sendBtn.disabled = true;

  const loadingDiv = addMessage("assistant", "思考中");
  loadingDiv.classList.add("loading");

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);

    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    const data = await resp.json();
    loadingDiv.classList.remove("loading");
    loadingDiv.innerHTML = renderMarkdown(data.reply || "未获取到回答");
  } catch (err) {
    loadingDiv.classList.remove("loading");
    if (err.name === "AbortError") {
      loadingDiv.textContent = "请求超时（3分钟），请稍后重试。";
    } else {
      loadingDiv.textContent = `请求失败：${err.message}，请稍后重试。`;
    }
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

sendBtn.addEventListener("click", sendMessage);

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

newSessionBtn.addEventListener("click", createSession);

// Initialize
createSession();

const $ = (id) => document.getElementById(id);

const statusEl = $("status");
const fileInput = $("file-input");
const dropzone = $("dropzone");
const uploadMsg = $("upload-msg");
const messages = $("messages");
const questionEl = $("question");
const sendBtn = $("send");

let hasDocument = false;
let asking = false;

/* ---------- status bar ---------- */
async function refreshStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    if (!s.ollama) {
      setStatus("Ollama is not running. Start the project with Start.bat.", "bad");
    } else if (!s.llm_ready) {
      setStatus(`Model "${s.llm_model}" is not installed yet.`, "bad");
    } else if (!s.embed_ready) {
      setStatus(`Ready (using keyword search; "${s.embed_model}" is not installed).`, "warn");
    } else {
      setStatus(`Ready · ${s.llm_model}`, "ok");
    }
  } catch {
    setStatus("Cannot reach the backend.", "bad");
  }
}

function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = "status " + kind;
}

/* ---------- upload ---------- */
async function uploadPdf(file) {
  if (!file) return;
  setUploadMsg("Reading and indexing the PDF…", "busy");

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed.");

    $("doc-name").textContent = data.filename;
    $("doc-pages").textContent = data.pages;
    $("doc-search").textContent =
      data.search_mode === "embeddings" ? "Semantic" : "Keyword (fallback)";
    $("doc-info").hidden = false;

    hasDocument = true;
    messages.innerHTML = "";
    setUploadMsg("PDF is ready.", "");
    updateComposer();
    questionEl.focus();
  } catch (err) {
    setUploadMsg(err.message, "error");
  } finally {
    fileInput.value = "";
  }
}

function setUploadMsg(text, kind) {
  uploadMsg.textContent = text;
  uploadMsg.className = "note " + kind;
}

fileInput.addEventListener("change", () => uploadPdf(fileInput.files[0]));

["dragenter", "dragover"].forEach((t) =>
  dropzone.addEventListener(t, (e) => { e.preventDefault(); dropzone.classList.add("drag"); }));
["dragleave", "drop"].forEach((t) =>
  dropzone.addEventListener(t, (e) => { e.preventDefault(); dropzone.classList.remove("drag"); }));
dropzone.addEventListener("drop", (e) => uploadPdf(e.dataTransfer.files[0]));

/* ---------- questions ---------- */
function updateComposer() {
  questionEl.disabled = !hasDocument || asking;
  sendBtn.disabled = !hasDocument || asking || !questionEl.value.trim();
}

function addMessage(question) {
  const li = document.createElement("li");

  const q = document.createElement("div");
  q.className = "q";
  q.dir = "auto";
  q.textContent = question;

  const a = document.createElement("div");
  a.className = "a pending";
  a.dir = "auto";
  a.textContent = "Thinking…";

  const src = document.createElement("div");
  src.className = "src";

  li.append(q, a, src);
  messages.append(li);
  messages.scrollTop = messages.scrollHeight;
  return { a, src };
}

async function ask() {
  const question = questionEl.value.trim();
  if (!question || asking) return;

  asking = true;
  questionEl.value = "";
  updateComposer();
  const { a, src } = addMessage(question);

  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Something went wrong.");

    a.className = "a";
    a.textContent = data.answer;
    src.textContent = "Pages: " + data.pages.join(", ");
  } catch (err) {
    a.className = "a error";
    a.textContent = err.message;
  } finally {
    asking = false;
    updateComposer();
    questionEl.focus();
    messages.scrollTop = messages.scrollHeight;
  }
}

sendBtn.addEventListener("click", ask);
questionEl.addEventListener("input", updateComposer);
questionEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(); }
});

refreshStatus();
setInterval(refreshStatus, 10000);

const conversation = document.querySelector("#conversation");
const messages = document.querySelector("#messages");
const emptyState = document.querySelector("#empty-state");
const chatForm = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question-input");
const sendButton = document.querySelector("#send-button");
const characterCount = document.querySelector("#character-count");
const serviceStatus = document.querySelector("#service-status");
const serviceStatusText = document.querySelector("#service-status-text");
const suggestionButtons = document.querySelectorAll(".suggestion");

const MAX_INPUT_LENGTH = Number(questionInput.maxLength);
let sending = false;

function setSending(value) {
    sending = value;
    chatForm.classList.toggle("is-sending", value);
    questionInput.disabled = value;
    sendButton.disabled = value || !questionInput.value.trim();
    chatForm.setAttribute("aria-busy", String(value));
}

function setServiceOnline(value) {
    serviceStatus.classList.toggle("is-offline", !value);
    serviceStatusText.textContent = value ? "服务在线" : "连接异常";
}

function updateInputState() {
    const length = questionInput.value.length;
    characterCount.textContent = `${length} / ${MAX_INPUT_LENGTH}`;
    sendButton.disabled = sending || !questionInput.value.trim();
    questionInput.style.height = "auto";
    questionInput.style.height = `${Math.min(questionInput.scrollHeight, 140)}px`;
}

function hideEmptyState() {
    emptyState.classList.add("is-hidden");
}

function scrollToLatest(behavior = "smooth") {
    requestAnimationFrame(() => {
        conversation.scrollTo({
            top: conversation.scrollHeight,
            behavior,
        });
    });
}

function appendUserMessage(text) {
    const row = document.createElement("article");
    row.className = "message message-user";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    content.append(bubble);
    row.append(content);
    messages.append(row);
    scrollToLatest();
}

function appendPendingMessage() {
    const row = document.createElement("article");
    row.className = "message message-assistant";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "A";

    const content = document.createElement("div");
    content.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble is-pending";
    bubble.setAttribute("aria-label", "正在生成回答");

    const dots = document.createElement("span");
    dots.className = "loading-dots";
    dots.setAttribute("aria-hidden", "true");
    for (let index = 0; index < 3; index += 1) {
        dots.append(document.createElement("span"));
    }

    bubble.append(dots);
    content.append(bubble);
    row.append(avatar, content);
    messages.append(row);
    scrollToLatest();
    return row;
}

function formatSourceName(source) {
    if (!source) {
        return "知识库";
    }
    return source.split(/[\\/]/).pop();
}

function normalizeAnswer(text) {
    return text
        .replace(/\*\*([^*]+)\*\*/g, "$1")
        .replace(/`([^`]+)`/g, "$1")
        .replace(/^#{1,6}\s+/gm, "");
}

function appendSources(content, rawSources) {
    if (!Array.isArray(rawSources) || rawSources.length === 0) {
        return;
    }

    const seen = new Set();
    const sources = rawSources.filter((source) => {
        if (!source || typeof source !== "object") {
            return false;
        }
        const key = `${source.source ?? ""}:${source.chunk_id ?? ""}`;
        if (seen.has(key)) {
            return false;
        }
        seen.add(key);
        return true;
    });

    if (sources.length === 0) {
        return;
    }

    const sourceList = document.createElement("div");
    sourceList.className = "source-list";

    const label = document.createElement("span");
    label.className = "source-label";
    label.textContent = "来源";
    sourceList.append(label);

    sources.forEach((source) => {
        const item = document.createElement("span");
        item.className = "source-item";
        const chunk = source.chunk_id === undefined || source.chunk_id === null
            ? ""
            : ` · 片段 ${source.chunk_id}`;
        item.textContent = `${formatSourceName(source.source)}${chunk}`;
        sourceList.append(item);
    });

    content.append(sourceList);
}

function replacePendingWithAnswer(pendingRow, data) {
    const content = pendingRow.querySelector(".message-content");
    const bubble = pendingRow.querySelector(".message-bubble");
    bubble.classList.remove("is-pending");
    bubble.removeAttribute("aria-label");
    bubble.textContent = typeof data.answer === "string" && data.answer.trim()
        ? normalizeAnswer(data.answer)
        : "暂时没有生成有效回答。";
    appendSources(content, data.sources);
}

function replacePendingWithError(pendingRow, message, question) {
    const content = pendingRow.querySelector(".message-content");
    content.replaceChildren();

    const errorBlock = document.createElement("div");
    errorBlock.className = "error-block";
    const errorText = document.createElement("p");
    errorText.textContent = message;
    const retryButton = document.createElement("button");
    retryButton.className = "retry-button";
    retryButton.type = "button";
    retryButton.textContent = "重试";
    retryButton.addEventListener("click", () => {
        if (sending) {
            return;
        }
        pendingRow.remove();
        requestAnswer(question);
    });

    errorBlock.append(errorText, retryButton);
    content.append(errorBlock);
}

function getErrorMessage(response, data) {
    if (typeof data?.detail === "string" && data.detail.trim()) {
        return data.detail;
    }
    if (response.status >= 500) {
        return "服务暂时没有返回结果，请稍后重试。";
    }
    return "请求没有成功，请稍后重试。";
}

async function requestAnswer(question) {
    setSending(true);
    const pendingRow = appendPendingMessage();
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 90000);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
            signal: controller.signal,
        });

        let data = {};
        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            throw new Error(getErrorMessage(response, data));
        }

        replacePendingWithAnswer(pendingRow, data);
        setServiceOnline(true);
    } catch (error) {
        const message = error.name === "AbortError"
            ? "等待回答超时，请稍后重试。"
            : error.message || "网络连接失败，请检查服务是否在线。";
        replacePendingWithError(pendingRow, message, question);
        if (!error.message || error instanceof TypeError) {
            setServiceOnline(false);
        }
    } finally {
        window.clearTimeout(timeout);
        setSending(false);
        scrollToLatest();
    }
}

async function submitQuestion(rawQuestion) {
    const question = rawQuestion.trim();
    if (!question || sending) {
        return;
    }

    hideEmptyState();
    appendUserMessage(question);
    questionInput.value = "";
    updateInputState();
    await requestAnswer(question);
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await submitQuestion(questionInput.value);
});

questionInput.addEventListener("input", updateInputState);

questionInput.addEventListener("keydown", async (event) => {
    if (
        event.key === "Enter"
        && !event.shiftKey
        && !event.isComposing
    ) {
        event.preventDefault();
        if (!sending && questionInput.value.trim()) {
            await submitQuestion(questionInput.value);
        }
    }
});

suggestionButtons.forEach((button) => {
    button.addEventListener("click", async () => {
        await submitQuestion(button.dataset.question || "");
    });
});

updateInputState();

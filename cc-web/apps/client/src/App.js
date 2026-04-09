import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from "react";
export function App() {
    const [user, setUser] = useState(null);
    const [username, setUsername] = useState("admin");
    const [password, setPassword] = useState("");
    const [sessions, setSessions] = useState([]);
    const [activeSessionId, setActiveSessionId] = useState("");
    const [runs, setRuns] = useState([]);
    const [draftName, setDraftName] = useState("QA 工作台");
    const [message, setMessage] = useState("");
    const [liveText, setLiveText] = useState({});
    const [uploads, setUploads] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [pendingDeleteSession, setPendingDeleteSession] = useState(null);
    const chatScrollRef = useRef(null);
    const downloadedArtifactsRef = useRef(new Set());
    const chatEntries = runs.map((run) => ({
        run,
        userText: run.promptPreview,
        assistantText: liveText[run.id] ??
            run.resultText ??
            run.errorMessage ??
            (run.status === "running" ? "处理中..." : "等待输出..."),
    }));
    useEffect(() => {
        void fetchCurrentUser();
    }, []);
    useEffect(() => {
        if (!user) {
            return;
        }
        void loadSessions();
    }, [user]);
    useEffect(() => {
        if (!activeSessionId) {
            return;
        }
        const eventSource = new EventSource(`/api/sessions/${activeSessionId}/events`, {
            withCredentials: true,
        });
        eventSource.addEventListener("snapshot", (incoming) => {
            const event = JSON.parse(incoming.data);
            const snapshot = event.payload;
            setRuns(snapshot.runs);
            setLiveText({});
            downloadedArtifactsRef.current = new Set();
        });
        for (const eventName of [
            "assistant.delta",
            "assistant.completed",
            "run.failed",
            "run.cancelled",
            "artifact.created",
        ]) {
            eventSource.addEventListener(eventName, (incoming) => {
                const event = JSON.parse(incoming.data);
                if (event.type === "assistant.delta" && event.runId) {
                    const runId = event.runId;
                    setLiveText((current) => ({
                        ...current,
                        [runId]: `${current[runId] ?? ""}${String(event.payload.text ?? "")}`,
                    }));
                }
                if (event.type === "assistant.completed" && event.runId) {
                    const runId = event.runId;
                    const text = String(event.payload.text ?? "");
                    setLiveText((current) => ({ ...current, [runId]: text }));
                    setRuns((current) => current.map((run) => run.id === runId ? { ...run, status: "completed", resultText: text, completedAt: event.createdAt } : run));
                }
                if (event.type === "run.failed" && event.runId) {
                    const runId = event.runId;
                    const payload = event.payload;
                    setRuns((current) => current.map((run) => run.id === runId
                        ? {
                            ...run,
                            status: "failed",
                            errorCode: payload.errorCode ?? "error",
                            errorMessage: payload.errorMessage ?? "Run failed",
                        }
                        : run));
                }
                if (event.type === "run.cancelled" && event.runId) {
                    const runId = event.runId;
                    setRuns((current) => current.map((run) => (run.id === runId ? { ...run, status: "cancelled" } : run)));
                }
                if (event.type === "artifact.created") {
                    const artifact = event.payload;
                    if (shouldAutoDownloadArtifact(artifact) && !downloadedArtifactsRef.current.has(artifact.id)) {
                        downloadedArtifactsRef.current.add(artifact.id);
                        void autoDownloadArtifact(activeSessionId, artifact);
                    }
                }
            });
        }
        eventSource.onerror = () => {
            eventSource.close();
        };
        return () => eventSource.close();
    }, [activeSessionId]);
    useEffect(() => {
        if (!chatScrollRef.current) {
            return;
        }
        chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }, [chatEntries]);
    async function fetchCurrentUser() {
        try {
            const response = await fetch("/api/auth/me", {
                credentials: "include",
            });
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            setUser(data.user);
        }
        catch {
            return;
        }
    }
    async function loadSessions() {
        const response = await fetch("/api/sessions", {
            credentials: "include",
        });
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        const nextSessions = data.sessions;
        setSessions(nextSessions);
        if (!activeSessionId && nextSessions[0]) {
            setActiveSessionId(nextSessions[0].id);
        }
    }
    async function login() {
        setError("");
        setLoading(true);
        try {
            const response = await fetch("/api/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify({ username, password }),
            });
            if (!response.ok) {
                setError("登录失败");
                return;
            }
            const data = await response.json();
            setUser(data.user);
            setPassword("");
        }
        finally {
            setLoading(false);
        }
    }
    async function logout() {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "include",
        });
        window.location.reload();
    }
    async function createSession() {
        if (!draftName.trim()) {
            return;
        }
        const response = await fetch("/api/sessions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({ name: draftName }),
        });
        if (!response.ok) {
            setError("创建会话失败");
            return;
        }
        const data = await response.json();
        const session = data.session;
        setSessions((current) => [session, ...current]);
        setActiveSessionId(session.id);
        setUploads([]);
        setRuns([]);
        setLiveText({});
        downloadedArtifactsRef.current = new Set();
    }
    async function sendMessage() {
        if (!activeSessionId) {
            return;
        }
        const response = await fetch(`/api/sessions/${activeSessionId}/messages`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
                action: "custom",
                text: message,
                uploadPaths: uploads.map((item) => item.relativePath),
            }),
        });
        if (!response.ok) {
            const data = await response.json();
            setError(data.message || "发送失败");
            return;
        }
        const data = await response.json();
        if (data.run) {
            setRuns((current) => [...current, data.run]);
        }
        setMessage("");
        setError("");
    }
    async function uploadFile(file) {
        if (!activeSessionId) {
            return;
        }
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`/api/sessions/${activeSessionId}/uploads`, {
            method: "POST",
            body: formData,
            credentials: "include",
        });
        if (!response.ok) {
            setError("上传失败");
            return;
        }
        const data = await response.json();
        setUploads((current) => [...current, data.uploaded]);
    }
    async function cancelRun(runId) {
        await fetch(`/api/runs/${runId}/cancel`, {
            method: "POST",
            credentials: "include",
        });
    }
    async function deleteSession(session) {
        const response = await fetch(`/api/sessions/${session.id}`, {
            method: "DELETE",
            credentials: "include",
        });
        const data = response.ok ? null : await response.json().catch(() => null);
        if (!response.ok) {
            setError(data?.message || "删除会话失败");
            return;
        }
        const nextSessions = sessions.filter((item) => item.id !== session.id);
        setSessions(nextSessions);
        setPendingDeleteSession(null);
        setError("");
        if (activeSessionId === session.id) {
            const nextActive = nextSessions[0]?.id ?? "";
            setActiveSessionId(nextActive);
            setRuns([]);
            setLiveText({});
            setUploads([]);
            downloadedArtifactsRef.current = new Set();
        }
    }
    if (!user) {
        return (_jsx("main", { className: "login-shell", children: _jsxs("section", { className: "login-panel", children: [_jsx("div", { className: "login-kicker", children: "Claude Code QA LAN Gateway" }), _jsx("h1", { children: "cc-web" }), _jsx("p", { children: "\u628A\u672C\u673A QA skill \u6258\u7BA1\u6210\u53EF\u767B\u5F55\u3001\u53EF\u6D41\u5F0F\u3001\u53EF\u53D1\u5E03\u7684\u5C40\u57DF\u7F51\u5DE5\u4F5C\u53F0\u3002" }), _jsxs("label", { children: [_jsx("span", { children: "\u7528\u6237\u540D" }), _jsx("input", { value: username, onChange: (event) => setUsername(event.target.value) })] }), _jsxs("label", { children: [_jsx("span", { children: "\u5BC6\u7801" }), _jsx("input", { type: "password", value: password, onChange: (event) => setPassword(event.target.value) })] }), _jsx("button", { disabled: loading, onClick: login, children: loading ? "登录中..." : "登录" }), error ? _jsx("div", { className: "error-banner", children: error }) : null] }) }));
    }
    return (_jsxs("main", { className: "app-shell", children: [_jsxs("aside", { className: "panel session-panel", children: [_jsx("div", { className: "panel-title", children: "\u4F1A\u8BDD" }), _jsxs("div", { className: "session-header", children: [_jsx("div", { className: "user-pill", children: user.username }), _jsx("button", { className: "ghost mini", onClick: logout, children: "\u9000\u51FA" })] }), _jsxs("div", { className: "new-session", children: [_jsx("input", { value: draftName, onChange: (event) => setDraftName(event.target.value), placeholder: "\u65B0\u4F1A\u8BDD\u540D\u79F0" }), _jsx("button", { onClick: createSession, children: "\u65B0\u5EFA" })] }), _jsx("div", { className: "session-list", children: sessions.map((session) => (_jsxs("article", { className: `session-item ${session.id === activeSessionId ? "active" : ""}`, children: [_jsxs("button", { className: "session-main", onClick: () => setActiveSessionId(session.id), children: [_jsx("strong", { children: session.name }), _jsx("span", { children: session.status })] }), _jsx("button", { className: "ghost mini session-delete", onClick: () => setPendingDeleteSession(session), children: "\u5220\u9664" })] }, session.id))) })] }), _jsxs("section", { className: "panel timeline-panel", children: [_jsx("div", { className: "panel-title", children: "\u804A\u5929\u6D41" }), _jsx("div", { className: "chat-shell", children: _jsxs("div", { ref: chatScrollRef, className: "chat-history", children: [chatEntries.length === 0 ? _jsx("div", { className: "chat-empty", children: "\u8FD8\u6CA1\u6709\u4F1A\u8BDD\u5185\u5BB9\u3002\u9009\u62E9\u52A8\u4F5C\u540E\u8F93\u5165\u9700\u6C42\u6216\u4E0A\u4F20\u6587\u6863\u5F00\u59CB\u3002" }) : null, chatEntries.map(({ run, userText, assistantText }) => (_jsxs("article", { className: "chat-turn", children: [_jsxs("div", { className: "chat-bubble user", children: [_jsxs("div", { className: "chat-meta", children: [_jsx("span", { children: "\u4F60" }), _jsx("span", { className: `status-tag ${run.status}`, children: formatStatus(run.status) })] }), _jsx("div", { className: "chat-text", children: userText })] }), _jsxs("div", { className: "chat-bubble assistant", children: [_jsxs("div", { className: "chat-meta", children: [_jsx("span", { children: "Claude" }), run.status === "running" ? (_jsx("button", { className: "ghost mini", onClick: () => cancelRun(run.id), children: "\u53D6\u6D88" })) : null] }), _jsx("div", { className: "chat-text", children: assistantText })] })] }, run.id)))] }) }), _jsxs("div", { className: "composer", children: [_jsx("textarea", { value: message, onChange: (event) => setMessage(event.target.value), placeholder: "\u76F4\u63A5\u8F93\u5165\u9700\u6C42\u3001\u8865\u5145\u8BF4\u660E\uFF0C\u6216\u8F93\u5165 /qa \u6307\u4EE4" }), _jsxs("div", { className: "composer-footer", children: [_jsxs("label", { className: "upload-button", children: ["\u4E0A\u4F20\u6587\u4EF6", _jsx("input", { type: "file", onChange: (event) => {
                                                    const file = event.target.files?.[0];
                                                    if (file) {
                                                        void uploadFile(file);
                                                    }
                                                } })] }), _jsx("button", { onClick: sendMessage, children: "\u53D1\u9001" })] }), uploads.length > 0 ? (_jsx("div", { className: "upload-list", children: uploads.map((item) => (_jsx("span", { children: item.relativePath }, item.relativePath))) })) : null, error ? _jsx("div", { className: "error-banner", children: error }) : null] })] }), pendingDeleteSession ? (_jsx("div", { className: "modal-backdrop", onClick: () => setPendingDeleteSession(null), children: _jsxs("div", { className: "modal-card", onClick: (event) => event.stopPropagation(), children: [_jsx("div", { className: "modal-title", children: "\u5220\u9664\u4F1A\u8BDD" }), _jsxs("div", { className: "modal-body", children: ["\u786E\u8BA4\u5220\u9664\u201C", pendingDeleteSession.name, "\u201D\u5417\uFF1F\u4F1A\u8BDD\u8BB0\u5F55\u548C\u4E34\u65F6\u5DE5\u4F5C\u533A\u4F1A\u4E00\u8D77\u5220\u9664\u3002"] }), _jsxs("div", { className: "modal-actions", children: [_jsx("button", { className: "ghost", onClick: () => setPendingDeleteSession(null), children: "\u53D6\u6D88" }), _jsx("button", { onClick: () => void deleteSession(pendingDeleteSession), children: "\u786E\u8BA4\u5220\u9664" })] })] }) })) : null] }));
}
function formatStatus(status) {
    switch (status) {
        case "queued":
            return "queued";
        case "running":
            return "running";
        case "completed":
            return "done";
        case "failed":
            return "failed";
        case "cancelled":
            return "cancelled";
    }
}
function shouldAutoDownloadArtifact(artifact) {
    if (artifact.relativePath.endsWith("testcases/testcase-index.json")) {
        return false;
    }
    if (artifact.relativePath.endsWith("testcases/i18n-index.json")) {
        return false;
    }
    return /\.(xlsx|json|csv|txt|docx)$/i.test(artifact.relativePath);
}
async function autoDownloadArtifact(sessionId, artifact) {
    const response = await fetch(`/api/sessions/${sessionId}/artifacts/${artifact.id}/download`, {
        credentials: "include",
    });
    if (!response.ok) {
        return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = artifact.relativePath.split("/").pop() || "download";
    anchor.style.display = "none";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}
//# sourceMappingURL=App.js.map
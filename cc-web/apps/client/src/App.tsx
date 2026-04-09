import { useEffect, useRef, useState } from "react";
import type {
  ArtifactRecord,
  AuthUser,
  RunSummary,
  SessionSnapshot,
  WebSessionSummary,
} from "@cc-web/shared";

type UploadFile = {
  name: string;
  relativePath: string;
};

export function App() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [sessions, setSessions] = useState<WebSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>("");
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [draftName, setDraftName] = useState("QA 工作台");
  const [message, setMessage] = useState("");
  const [liveText, setLiveText] = useState<Record<string, string>>({});
  const [uploads, setUploads] = useState<UploadFile[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingDeleteSession, setPendingDeleteSession] = useState<WebSessionSummary | null>(null);
  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const downloadedArtifactsRef = useRef<Set<string>>(new Set());

  const chatEntries = runs.map((run) => ({
    run,
    userText: run.promptPreview,
    assistantText:
      liveText[run.id] ??
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
      const event = JSON.parse((incoming as MessageEvent).data) as { payload: SessionSnapshot };
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
        const event = JSON.parse((incoming as MessageEvent).data) as {
          type: string;
          runId?: string;
          createdAt: string;
          payload: unknown;
        };

        if (event.type === "assistant.delta" && event.runId) {
          const runId = event.runId;
          setLiveText((current) => ({
            ...current,
            [runId]: `${current[runId] ?? ""}${String((event.payload as { text?: string }).text ?? "")}`,
          }));
        }

        if (event.type === "assistant.completed" && event.runId) {
          const runId = event.runId;
          const text = String((event.payload as { text?: string }).text ?? "");
          setLiveText((current) => ({ ...current, [runId]: text }));
          setRuns((current) =>
            current.map((run) =>
              run.id === runId ? { ...run, status: "completed", resultText: text, completedAt: event.createdAt } : run,
            ),
          );
        }

        if (event.type === "run.failed" && event.runId) {
          const runId = event.runId;
          const payload = event.payload as { errorCode?: string; errorMessage?: string };
          setRuns((current) =>
            current.map((run) =>
              run.id === runId
                ? {
                    ...run,
                    status: "failed",
                    errorCode: payload.errorCode ?? "error",
                    errorMessage: payload.errorMessage ?? "Run failed",
                  }
                : run,
            ),
          );
        }

        if (event.type === "run.cancelled" && event.runId) {
          const runId = event.runId;
          setRuns((current) => current.map((run) => (run.id === runId ? { ...run, status: "cancelled" } : run)));
        }

        if (event.type === "artifact.created") {
          const artifact = event.payload as ArtifactRecord;
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
      setUser(data.user as AuthUser);
    } catch {
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
    const nextSessions = data.sessions as WebSessionSummary[];
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
      setUser(data.user as AuthUser);
      setPassword("");
    } finally {
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
    const session = data.session as WebSessionSummary;
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
      setRuns((current) => [...current, data.run as RunSummary]);
    }
    setMessage("");
    setError("");
  }

  async function uploadFile(file: File) {
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
    setUploads((current) => [...current, data.uploaded as UploadFile]);
  }

  async function cancelRun(runId: string) {
    await fetch(`/api/runs/${runId}/cancel`, {
      method: "POST",
      credentials: "include",
    });
  }

  async function deleteSession(session: WebSessionSummary) {
    const response = await fetch(`/api/sessions/${session.id}`, {
      method: "DELETE",
      credentials: "include",
    });
    const data = response.ok ? null : await response.json().catch(() => null);
    if (!response.ok) {
      setError((data as { message?: string } | null)?.message || "删除会话失败");
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
    return (
      <main className="login-shell">
        <section className="login-panel">
          <div className="login-kicker">Claude Code QA LAN Gateway</div>
          <h1>cc-web</h1>
          <p>把本机 QA skill 托管成可登录、可流式、可发布的局域网工作台。</p>
          <label>
            <span>用户名</span>
            <input value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label>
            <span>密码</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </label>
          <button disabled={loading} onClick={login}>
            {loading ? "登录中..." : "登录"}
          </button>
          {error ? <div className="error-banner">{error}</div> : null}
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside className="panel session-panel">
        <div className="panel-title">会话</div>
        <div className="session-header">
          <div className="user-pill">{user.username}</div>
          <button className="ghost mini" onClick={logout}>
            退出
          </button>
        </div>
        <div className="new-session">
          <input value={draftName} onChange={(event) => setDraftName(event.target.value)} placeholder="新会话名称" />
          <button onClick={createSession}>新建</button>
        </div>
        <div className="session-list">
          {sessions.map((session) => (
            <article key={session.id} className={`session-item ${session.id === activeSessionId ? "active" : ""}`}>
              <button className="session-main" onClick={() => setActiveSessionId(session.id)}>
                <strong>{session.name}</strong>
                <span>{session.status}</span>
              </button>
              <button className="ghost mini session-delete" onClick={() => setPendingDeleteSession(session)}>
                删除
              </button>
            </article>
          ))}
        </div>
      </aside>

      <section className="panel timeline-panel">
        <div className="panel-title">聊天流</div>
        <div className="chat-shell">
          <div ref={chatScrollRef} className="chat-history">
            {chatEntries.length === 0 ? <div className="chat-empty">还没有会话内容。选择动作后输入需求或上传文档开始。</div> : null}
            {chatEntries.map(({ run, userText, assistantText }) => (
              <article key={run.id} className="chat-turn">
                <div className="chat-bubble user">
                  <div className="chat-meta">
                    <span>你</span>
                    <span className={`status-tag ${run.status}`}>{formatStatus(run.status)}</span>
                  </div>
                  <div className="chat-text">{userText}</div>
                </div>
                <div className="chat-bubble assistant">
                  <div className="chat-meta">
                    <span>Claude</span>
                    {run.status === "running" ? (
                      <button className="ghost mini" onClick={() => cancelRun(run.id)}>
                        取消
                      </button>
                    ) : null}
                  </div>
                  <div className="chat-text">{assistantText}</div>
                </div>
              </article>
            ))}
          </div>
        </div>
        <div className="composer">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="直接输入需求、补充说明，或输入 /qa 指令"
          />
          <div className="composer-footer">
            <label className="upload-button">
              上传文件
              <input
                type="file"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void uploadFile(file);
                  }
                }}
              />
            </label>
            <button onClick={sendMessage}>发送</button>
          </div>
          {uploads.length > 0 ? (
            <div className="upload-list">
              {uploads.map((item) => (
                <span key={item.relativePath}>{item.relativePath}</span>
              ))}
            </div>
          ) : null}
          {error ? <div className="error-banner">{error}</div> : null}
        </div>
      </section>

      {pendingDeleteSession ? (
        <div className="modal-backdrop" onClick={() => setPendingDeleteSession(null)}>
          <div className="modal-card" onClick={(event) => event.stopPropagation()}>
            <div className="modal-title">删除会话</div>
            <div className="modal-body">确认删除“{pendingDeleteSession.name}”吗？会话记录和临时工作区会一起删除。</div>
            <div className="modal-actions">
              <button className="ghost" onClick={() => setPendingDeleteSession(null)}>
                取消
              </button>
              <button onClick={() => void deleteSession(pendingDeleteSession)}>确认删除</button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

function formatStatus(status: RunSummary["status"]): string {
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

function shouldAutoDownloadArtifact(artifact: ArtifactRecord): boolean {
  if (artifact.relativePath.endsWith("testcases/testcase-index.json")) {
    return false;
  }
  if (artifact.relativePath.endsWith("testcases/i18n-index.json")) {
    return false;
  }
  return /\.(xlsx|json|csv|txt|docx)$/i.test(artifact.relativePath);
}

async function autoDownloadArtifact(sessionId: string, artifact: ArtifactRecord) {
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

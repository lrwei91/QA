export type QuickAction = "generate" | "supplement" | "analyze" | "export" | "i18n" | "custom";
export type RunStatus = "queued" | "running" | "completed" | "failed" | "cancelled";
export type ArtifactStatus = "ready" | "published";
export type PublishJobStatus = "preview" | "running" | "completed" | "failed";
export interface AuthUser {
    id: string;
    username: string;
    role: "admin" | "member";
    createdAt: string;
}
export interface WebSessionSummary {
    id: string;
    name: string;
    claudeSessionId: string | null;
    workspaceMode: "git-worktree" | "snapshot-copy";
    status: "idle" | "running";
    createdAt: string;
    updatedAt: string;
    lastRunId: string | null;
}
export interface RunSummary {
    id: string;
    sessionId: string;
    action: QuickAction;
    promptPreview: string;
    status: RunStatus;
    claudeSessionId: string | null;
    resultText: string | null;
    errorCode: string | null;
    errorMessage: string | null;
    startedAt: string;
    completedAt: string | null;
    createdAt: string;
    updatedAt: string;
}
export interface ArtifactRecord {
    id: string;
    sessionId: string;
    runId: string;
    relativePath: string;
    artifactPath: string;
    publishTargetPath: string;
    status: ArtifactStatus;
    sizeBytes: number;
    mimeType: string;
    checksum: string;
    createdAt: string;
    updatedAt: string;
    publishedAt: string | null;
}
export interface PublishConflict {
    artifactId: string;
    relativePath: string;
    targetPath: string;
    exists: boolean;
    changed: boolean;
}
export interface PublishPreview {
    conflicts: PublishConflict[];
    selected: ArtifactRecord[];
}
export interface SseEvent<T = unknown> {
    id: string;
    type: "snapshot" | "run.started" | "assistant.delta" | "assistant.completed" | "tool.started" | "tool.output" | "tool.completed" | "artifact.created" | "run.failed" | "run.cancelled";
    runId?: string;
    payload: T;
    createdAt: string;
}
export interface SessionSnapshot {
    session: WebSessionSummary;
    runs: RunSummary[];
    artifacts: ArtifactRecord[];
}
export interface MessageRequest {
    action: QuickAction;
    text?: string;
    uploadPaths?: string[];
}
export interface CreateSessionRequest {
    name: string;
}
export interface PublishRequest {
    artifactIds: string[];
    confirm?: boolean;
    force?: boolean;
}

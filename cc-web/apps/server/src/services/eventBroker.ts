import type { FastifyReply } from "fastify";
import type { SseEvent } from "@cc-web/shared";

type SessionSink = {
  reply: FastifyReply;
  heartbeat: NodeJS.Timeout;
};

export class EventBroker {
  private readonly sessions = new Map<string, Set<SessionSink>>();

  subscribe(sessionId: string, reply: FastifyReply): () => void {
    const sinks = this.sessions.get(sessionId) ?? new Set<SessionSink>();
    const heartbeat = setInterval(() => {
      reply.raw.write(": ping\n\n");
    }, 15000);
    const sink: SessionSink = { reply, heartbeat };
    sinks.add(sink);
    this.sessions.set(sessionId, sinks);

    return () => {
      clearInterval(heartbeat);
      const active = this.sessions.get(sessionId);
      if (!active) {
        return;
      }
      active.delete(sink);
      if (active.size === 0) {
        this.sessions.delete(sessionId);
      }
    };
  }

  publish(sessionId: string, event: SseEvent): void {
    const sinks = this.sessions.get(sessionId);
    if (!sinks) {
      return;
    }
    const payload = `id: ${event.id}\nevent: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`;
    for (const sink of sinks) {
      sink.reply.raw.write(payload);
    }
  }
}

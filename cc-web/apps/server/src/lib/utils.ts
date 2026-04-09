import { createHash, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";

export function nowIso(): string {
  return new Date().toISOString();
}

export function newId(prefix: string): string {
  return `${prefix}_${randomBytes(8).toString("hex")}`;
}

export function hashPassword(password: string): string {
  const salt = randomBytes(16).toString("hex");
  const digest = scryptSync(password, salt, 64).toString("hex");
  return `scrypt:${salt}:${digest}`;
}

export function verifyPassword(password: string, storedHash: string): boolean {
  const [algorithm, salt, digest] = storedHash.split(":");
  if (algorithm !== "scrypt" || !salt || !digest) {
    return false;
  }
  const candidate = scryptSync(password, salt, 64);
  const actual = Buffer.from(digest, "hex");
  return candidate.length === actual.length && timingSafeEqual(candidate, actual);
}

export function checksumBuffer(buffer: Buffer): string {
  return createHash("sha256").update(buffer).digest("hex");
}

export function normalizeName(input: string): string {
  return input.trim().replace(/\s+/g, " ");
}

export function toErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function assertNever(_: never): never {
  throw new Error("Unexpected value");
}

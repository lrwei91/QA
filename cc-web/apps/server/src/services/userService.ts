import type { AppConfig } from "../config/env.js";
import type { DatabaseClient, DbUserRow } from "../db/client.js";
import { mapUser } from "../db/client.js";
import { hashPassword, newId, verifyPassword } from "../lib/utils.js";

export class UserService {
  constructor(private readonly db: DatabaseClient, private readonly config: AppConfig) {}

  bootstrapAdmin(): void {
    if (!this.config.bootstrapAdminUsername || !this.config.bootstrapAdminPassword) {
      return;
    }
    const existing = this.findByUsername(this.config.bootstrapAdminUsername);
    if (existing) {
      return;
    }
    this.createUser(this.config.bootstrapAdminUsername, this.config.bootstrapAdminPassword, "admin");
  }

  createUser(username: string, password: string, role: "admin" | "member" = "member") {
    const now = new Date().toISOString();
    const row: DbUserRow = {
      id: newId("usr"),
      username,
      password_hash: hashPassword(password),
      role,
      created_at: now,
    };
    this.db.sqlite
      .prepare("INSERT INTO users (id, username, password_hash, role, created_at) VALUES (@id, @username, @password_hash, @role, @created_at)")
      .run(row);
    return mapUser(row);
  }

  findByUsername(username: string): DbUserRow | undefined {
    return this.db.sqlite.prepare("SELECT * FROM users WHERE username = ?").get(username) as DbUserRow | undefined;
  }

  findById(id: string): DbUserRow | undefined {
    return this.db.sqlite.prepare("SELECT * FROM users WHERE id = ?").get(id) as DbUserRow | undefined;
  }

  authenticate(username: string, password: string) {
    const user = this.findByUsername(username);
    if (!user || !verifyPassword(password, user.password_hash)) {
      return null;
    }
    return mapUser(user);
  }
}

import path from "node:path";
import { z } from "zod";
import { loadConfig } from "../config/env.js";
import { createDatabase } from "../db/client.js";
import { UserService } from "../services/userService.js";

const cliSchema = z.object({
  username: z.string().trim().min(1),
  password: z.string().min(1),
  role: z.enum(["admin", "member"]).default("member"),
});

function parseArgs(args: string[]) {
  const values: Record<string, string> = {};
  for (let index = 0; index < args.length; index += 1) {
    const current = args[index];
    if (!current.startsWith("--")) {
      continue;
    }
    const key = current.slice(2);
    const value = args[index + 1];
    if (!value || value.startsWith("--")) {
      continue;
    }
    values[key] = value;
  }
  return cliSchema.parse(values);
}

const input = parseArgs(process.argv.slice(2));
const config = loadConfig();
const db = createDatabase(path.join(config.dataDir, "meta.sqlite"));
const service = new UserService(db, config);

if (service.findByUsername(input.username)) {
  console.error(`User already exists: ${input.username}`);
  process.exit(1);
}

const created = service.createUser(input.username, input.password, input.role);
console.log(`Created user ${created.username} (${created.role})`);
db.close();

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const defaultCcWebRoot = resolveCcWebRoot(process.cwd()) ?? path.resolve(__dirname, "../../../../..");
const defaultRepoRoot = path.resolve(defaultCcWebRoot, "..");
const defaultDataDir = path.join(defaultRepoRoot, ".cc-web");

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  CC_WEB_HOST: z.string().default("0.0.0.0"),
  CC_WEB_PORT: z.coerce.number().int().positive().default(3030),
  CC_WEB_ALLOWED_ORIGINS: z.string().default("http://localhost:5173,http://127.0.0.1:5173"),
  CC_WEB_JWT_SECRET: z.string().min(8).default("change-me"),
  CC_WEB_SOURCE_REPO: z.string().default(defaultRepoRoot),
  CC_WEB_DATA_DIR: z.string().default(defaultDataDir),
  CC_WEB_BOOTSTRAP_ADMIN_USERNAME: z.string().trim().min(1).optional(),
  CC_WEB_BOOTSTRAP_ADMIN_PASSWORD: z.string().trim().min(1).optional(),
  CC_WEB_DEFAULT_MODEL: z.string().trim().optional(),
});

export type AppConfig = {
  nodeEnv: "development" | "test" | "production";
  host: string;
  port: number;
  allowedOrigins: string[];
  jwtSecret: string;
  sourceRepo: string;
  dataDir: string;
  bootstrapAdminUsername?: string;
  bootstrapAdminPassword?: string;
  defaultModel?: string;
  clientDistDir: string;
};

export function loadConfig(overrides?: Partial<Record<keyof NodeJS.ProcessEnv, string>>): AppConfig {
  const parsed = envSchema.parse({
    ...process.env,
    ...overrides,
  });

  return {
    nodeEnv: parsed.NODE_ENV,
    host: parsed.CC_WEB_HOST,
    port: parsed.CC_WEB_PORT,
    allowedOrigins: parsed.CC_WEB_ALLOWED_ORIGINS.split(",").map((item) => item.trim()).filter(Boolean),
    jwtSecret: parsed.CC_WEB_JWT_SECRET,
    sourceRepo: path.resolve(parsed.CC_WEB_SOURCE_REPO),
    dataDir: path.resolve(parsed.CC_WEB_DATA_DIR),
    bootstrapAdminUsername: parsed.CC_WEB_BOOTSTRAP_ADMIN_USERNAME,
    bootstrapAdminPassword: parsed.CC_WEB_BOOTSTRAP_ADMIN_PASSWORD,
    defaultModel: parsed.CC_WEB_DEFAULT_MODEL || undefined,
    clientDistDir: path.join(defaultCcWebRoot, "apps/client/dist"),
  };
}

function resolveCcWebRoot(startDir: string): string | null {
  let current = path.resolve(startDir);
  while (true) {
    const packagePath = path.join(current, "package.json");
    if (fs.existsSync(packagePath)) {
      try {
        const parsed = JSON.parse(fs.readFileSync(packagePath, "utf8")) as { name?: string };
        if (parsed.name === "cc-web") {
          return current;
        }
      } catch {
        return null;
      }
    }
    const parent = path.dirname(current);
    if (parent === current) {
      return null;
    }
    current = parent;
  }
}

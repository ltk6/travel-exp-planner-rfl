import { z } from "zod";
import fs from "fs";
import path from "path";

const serverSchema = z.object({
  BACKEND_URL: z.string().url().default("http://127.0.0.1:8000"),
  INTERNAL_API_KEY: z.string().default(""),
  BACKEND_TIMEOUT_MS: z.coerce.number().int().positive().default(120000),
});

function loadRootEnv() {
  try {
    // Next.js cwd is frontend/n16_web_ui
    const rootEnvPath = path.resolve(process.cwd(), "../../.env");
    const content = fs.readFileSync(rootEnvPath, "utf-8");
    const parsed: Record<string, string> = {};
    content.split("\n").forEach((line) => {
      const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)?\s*$/);
      if (match) {
        const key = match[1];
        let value = match[2] || "";
        // Remove basic quotes
        if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
        else if (value.startsWith("'") && value.endsWith("'")) value = value.slice(1, -1);
        parsed[key] = value;
      }
    });
    return parsed;
  } catch (err) {
    return {};
  }
}

const rootEnv = loadRootEnv();

// Derive backend URL from the global config if not explicitly provided
const apiHost = rootEnv.API_HOST || "127.0.0.1";
const apiPort = rootEnv.API_PORT || "8000";
const derivedBackendUrl = `http://${apiHost === "0.0.0.0" ? "127.0.0.1" : apiHost}:${apiPort}`;

const rawBackendUrl = process.env.BACKEND_URL || rootEnv.BACKEND_URL || derivedBackendUrl;
const safeBackendUrl = rawBackendUrl.replace("localhost", "127.0.0.1");

export const env = serverSchema.parse({
  BACKEND_URL: safeBackendUrl,
  INTERNAL_API_KEY: process.env.INTERNAL_API_KEY || rootEnv.INTERNAL_API_KEY,
  BACKEND_TIMEOUT_MS: process.env.BACKEND_TIMEOUT_MS || rootEnv.BACKEND_TIMEOUT_MS,
});

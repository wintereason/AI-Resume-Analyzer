import { Hono } from "npm:hono";
import type { Context } from "npm:hono";
import type { Next } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import { createClient } from "npm:@supabase/supabase-js@2";
import * as kv from "./kv_store.tsx";

type AppEnv = {
  Variables: {
    userId: string;
  };
};

type StoredRecord = Record<string, unknown> & {
  id: string;
  createdAt: string;
  updatedAt: string;
};

const app = new Hono<AppEnv>();

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
const healthResponse = (c: Context) => {
  return c.json({ status: "ok" });
};
app.get("/health", healthResponse);
app.get("/server/health", healthResponse);
app.get("/make-server-91bd2624/health", healthResponse);
app.get("/server/make-server-91bd2624/health", healthResponse);

const bootstrapAdmin = async (c: Context) => {
  const body = await c.req.json<{ email?: string; password?: string }>();
  const email = body.email?.trim().toLowerCase();
  const password = body.password;

  if (!email || !password || password.length < 8) {
    return c.json({ error: "A valid email and password are required." }, 400);
  }

  const supabaseAdmin = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );
  const { data, error } = await supabaseAdmin.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
    user_metadata: { name: "Suraj Jangde", role: "Admin" },
  });

  if (error) {
    if (error.message.toLowerCase().includes("already") || error.message.toLowerCase().includes("registered")) {
      return c.json({ error: "Admin account has already been initialized." }, 409);
    }
    console.error("Could not bootstrap the admin account:", error);
    return c.json({ error: "Could not initialize the admin account." }, 500);
  }

  return c.json({ id: data.user.id }, 201);
};
app.post("/bootstrap-admin", bootstrapAdmin);
app.post("/server/bootstrap-admin", bootstrapAdmin);
app.post("/make-server-91bd2624/bootstrap-admin", bootstrapAdmin);
app.post("/server/make-server-91bd2624/bootstrap-admin", bootstrapAdmin);

const routePrefixes = ["", "/server", "/make-server-91bd2624", "/server/make-server-91bd2624"];
const routePaths = (path: string) => routePrefixes.map((prefix) => `${prefix}${path}`);

async function requireUser(c: Context<AppEnv>, next: Next) {
  const authorization = c.req.header("Authorization");
  const token = authorization?.startsWith("Bearer ") ? authorization.slice(7) : "";
  if (!token) return c.json({ error: "Authentication is required." }, 401);

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_ANON_KEY") ?? Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    { auth: { autoRefreshToken: false, persistSession: false } },
  );
  const { data, error } = await supabase.auth.getUser(token);
  if (error || !data.user) return c.json({ error: "Your session is invalid or has expired." }, 401);
  c.set("userId", data.user.id);
  return next();
}

app.use("*", async (c, next) => {
  const path = new URL(c.req.url).pathname;
  if (
    path.endsWith("/health") ||
    path.endsWith("/bootstrap-admin") ||
    path.endsWith("/make-server-91bd2624/health") ||
    path.endsWith("/make-server-91bd2624/bootstrap-admin")
  ) {
    return next();
  }
  return requireUser(c, next);
});

function storageKey(userId: string, collection: string, id: string) {
  return `talentflow:${userId}:${collection}:${id}`;
}

function collectionPrefix(userId: string, collection: string) {
  return `talentflow:${userId}:${collection}:`;
}

async function readJson(c: Context<AppEnv>) {
  try {
    const value = await c.req.json();
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      return { error: "Request body must be a JSON object." };
    }
    return { value: value as Record<string, unknown> };
  } catch {
    return { error: "Request body must contain valid JSON." };
  }
}

function now() {
  return new Date().toISOString();
}

function recordFromPayload(payload: Record<string, unknown>, fallbackId?: string): StoredRecord | null {
  const id = typeof payload.id === "string" && payload.id.trim() ? payload.id.trim() : fallbackId ?? crypto.randomUUID();
  return {
    ...payload,
    id,
    createdAt: typeof payload.createdAt === "string" ? payload.createdAt : now(),
    updatedAt: now(),
  };
}

async function listRecords(c: Context<AppEnv>, collection: string) {
  const values = await kv.getByPrefix(collectionPrefix(c.get("userId"), collection));
  const records = values.filter((value): value is StoredRecord => Boolean(value && typeof value === "object" && typeof value.id === "string"));
  records.sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  const pageSize = Math.min(Math.max(Number(c.req.query("pageSize") ?? "100") || 100, 1), 500);
  return c.json({ data: records.slice(0, pageSize) });
}

async function createRecord(c: Context<AppEnv>, collection: string) {
  const parsed = await readJson(c);
  if (parsed.error) return c.json({ error: parsed.error }, 400);
  const record = recordFromPayload(parsed.value!);
  if (!record) return c.json({ error: "The record could not be created." }, 400);
  await kv.set(storageKey(c.get("userId"), collection, record.id), record);
  return c.json({ data: record }, 201);
}

async function updateRecord(c: Context<AppEnv>, collection: string) {
  const id = c.req.param("id");
  if (!id) return c.json({ error: "A record ID is required." }, 400);
  const existing = await kv.get(storageKey(c.get("userId"), collection, id));
  if (!existing) return c.json({ error: "The requested record was not found." }, 404);
  const parsed = await readJson(c);
  if (parsed.error) return c.json({ error: parsed.error }, 400);
  const record = recordFromPayload(
    { ...(existing as Record<string, unknown>), ...parsed.value },
    id,
  );
  if (!record) return c.json({ error: "The record could not be updated." }, 400);
  await kv.set(storageKey(c.get("userId"), collection, id), record);
  return c.json({ data: record });
}

async function deleteRecord(c: Context<AppEnv>, collection: string) {
  const id = c.req.param("id");
  if (!id) return c.json({ error: "A record ID is required." }, 400);
  const key = storageKey(c.get("userId"), collection, id);
  if (!(await kv.get(key))) return c.json({ error: "The requested record was not found." }, 404);
  await kv.del(key);
  return c.body(null, 204);
}

for (const path of routePaths("/analyses")) {
  app.get(path, (c) => listRecords(c, "analyses"));
  app.post(path, (c) => createRecord(c, "analyses"));
}
for (const path of routePaths("/analyses/:id")) {
  app.delete(path, (c) => deleteRecord(c, "analyses"));
}
for (const path of routePaths("/analyses/:id/recruitment-status")) {
  app.patch(path, async (c) => {
    const id = c.req.param("id");
    const parsed = await readJson(c);
    const recruitmentStatus = parsed.value?.recruitmentStatus;
    const allowed = ["New", "Shortlisted", "Interview Scheduled", "Rejected"];
    if (parsed.error || typeof recruitmentStatus !== "string" || !allowed.includes(recruitmentStatus)) {
      return c.json({ error: "A valid recruitment status is required." }, 400);
    }
    const key = storageKey(c.get("userId"), "analyses", id);
    const existing = await kv.get(key);
    if (!existing) return c.json({ error: "The requested record was not found." }, 404);
    const record = recordFromPayload(
      { ...(existing as Record<string, unknown>), recruitmentStatus },
      id,
    );
    if (!record) return c.json({ error: "The record could not be updated." }, 400);
    await kv.set(key, record);
    return c.json({ data: record });
  });
}

for (const collection of ["job-roles", "interviews"]) {
  for (const path of routePaths(`/${collection}`)) {
    app.get(path, (c) => listRecords(c, collection));
    app.post(path, (c) => createRecord(c, collection));
  }
  for (const path of routePaths(`/${collection}/:id`)) {
    app.put(path, (c) => updateRecord(c, collection));
    app.delete(path, (c) => deleteRecord(c, collection));
  }
}

Deno.serve(app.fetch);
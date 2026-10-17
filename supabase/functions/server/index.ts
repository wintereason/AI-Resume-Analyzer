import { Hono } from "npm:hono";
import type { Context } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import { createClient } from "npm:@supabase/supabase-js@2";
import * as kv from "./kv_store.tsx";
const app = new Hono();

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

Deno.serve(app.fetch);
import { createClient } from "@supabase/supabase-js";
import { projectId, publicAnonKey } from "../../utils/supabase/info";

const API_BASE_URL = `https://${projectId}.supabase.co/functions/v1/server/make-server-91bd2624`;
const SUPABASE_URL = `https://${projectId}.supabase.co`;
const AUTH_STORAGE_KEY = `sb-${projectId}-auth-token`;
const ADMIN_EMAIL = "surajjangde1312@gmail.com";

export const supabase = createClient(SUPABASE_URL, publicAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    storageKey: AUTH_STORAGE_KEY,
  },
});

type ApiOptions = RequestInit & { authenticated?: boolean };

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { authenticated = true, headers, ...requestOptions } = options;
  const { data } = await supabase.auth.getSession();
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...requestOptions,
      headers: {
        "Content-Type": "application/json",
        ...(authenticated && data.session?.access_token
          ? { Authorization: `Bearer ${data.session.access_token}` }
          : {}),
        ...headers,
      },
    });
  } catch {
    throw new Error(
      "The TalentFlow Supabase service is unavailable. Deploy the connected Edge Function and try again.",
    );
  }
  if (response.status === 204) return undefined as T;
  const responseText = await response.text();
  let body: { error?: string } = {};
  try {
    body = JSON.parse(responseText) as { error?: string };
  } catch {
    if (responseText) body.error = responseText;
  }
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(
        "The TalentFlow Edge Function is not deployed. Deploy the `server` function in Supabase and try again.",
      );
    }
    throw new Error(body.error ?? "The server could not complete this request.");
  }
  return body as T;
}

export async function loginRecruiter(email: string, password: string) {
  const normalizedEmail = email.trim().toLowerCase();
  let result = await supabase.auth.signInWithPassword({ email: normalizedEmail, password });
  if (result.error && normalizedEmail === ADMIN_EMAIL) {
    try {
      await apiRequest("/bootstrap-admin", {
        method: "POST",
        authenticated: false,
        body: JSON.stringify({ email: normalizedEmail, password }),
      });
      result = await supabase.auth.signInWithPassword({ email: normalizedEmail, password });
    } catch (bootstrapError) {
      if (!String(bootstrapError).toLowerCase().includes("already")) throw bootstrapError;
      result = await supabase.auth.signInWithPassword({ email: normalizedEmail, password });
    }
  }
  if (result.error || !result.data.user) {
    throw new Error(result.error?.message ?? "Email or password is incorrect.");
  }
  const user = {
    id: result.data.user.id,
    name: String(result.data.user.user_metadata.name ?? "Suraj Jangde"),
    email: result.data.user.email ?? normalizedEmail,
    role: String(result.data.user.user_metadata.role ?? "Admin"),
  };
  localStorage.setItem("talentflow-user", JSON.stringify(user));
  return user;
}

export function hasAuthToken() {
  return Boolean(localStorage.getItem(AUTH_STORAGE_KEY));
}

export function logoutRecruiter() {
  localStorage.removeItem("talentflow-user");
  void supabase.auth.signOut();
}

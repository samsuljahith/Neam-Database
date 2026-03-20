const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  // Collections
  listCollections: () => req("GET", "/collections"),
  createCollection: (name) => req("POST", "/collections", { name }),
  deleteCollection: (name) => req("DELETE", `/collections/${name}`),

  // Ingest
  ingest: (collection, text, source) =>
    req("POST", "/ingest", { collection, text, source }),

  // Query
  query: (collection, query, top_k, search_mode) =>
    req("POST", "/query", { collection, query, top_k, search_mode }),

  // Models
  listModels: () => req("GET", "/models"),
  currentModel: () => req("GET", "/models/current"),

  // Health
  health: () => req("GET", "/health"),
};

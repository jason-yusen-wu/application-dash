const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function fetchApplications() {
  const res = await fetch(`${API_BASE}/applications`);
  return res.json();
}

export async function updateApplicationStatus(id, status) {
  const res = await fetch(`${API_BASE}/applications/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  return res.json();
}

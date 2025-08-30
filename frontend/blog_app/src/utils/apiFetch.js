export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    ...(options.headers || {}),
    Authorization: token ? `Bearer ${token}` : undefined,
  };

  const response = await fetch(url, { ...options, headers });

  if (response.status === 401) {
    alert("Session expired. Please login again.");
    localStorage.removeItem("access_token");
    window.location.href = "/"; // always redirect to home
    throw new Error("Unauthorized");
  }

  return response;
}
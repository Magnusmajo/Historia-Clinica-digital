import axios from "axios";

const csrfCookieName = import.meta.env.VITE_CSRF_COOKIE_NAME || "hcd_csrf";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 10000,
  withCredentials: true,
});

let refreshPromise = null;

function readCookie(name) {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));
  return cookie ? cookie.split("=").slice(1).join("=") : "";
}

function formatApiDetail(detail) {
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .filter(Boolean)
      .join(". ");
  }

  if (detail && typeof detail === "object") {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  return "";
}

api.interceptors.request.use((config) => {
  const method = (config.method || "get").toUpperCase();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = readCookie(csrfCookieName);
    if (csrfToken) {
      config.headers["X-CSRF-Token"] = decodeURIComponent(csrfToken);
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;
    const status = error?.response?.status;
    const url = originalRequest?.url || "";
    const canRefresh =
      status === 401 &&
      originalRequest &&
      !originalRequest.__retried &&
      !url.includes("/auth/login") &&
      !url.includes("/auth/refresh");

    if (canRefresh) {
      originalRequest.__retried = true;
      try {
        refreshPromise =
          refreshPromise || api.post("/auth/refresh").finally(() => {
            refreshPromise = null;
          });
        await refreshPromise;
        return api(originalRequest);
      } catch {
        window.dispatchEvent(new Event("auth:logout"));
      }
    } else if (status === 401 && !url.includes("/auth/login")) {
      window.dispatchEvent(new Event("auth:logout"));
    }
    return Promise.reject(error);
  }
);

export function getApiError(error, fallback = "Ocurrio un error inesperado") {
  return (
    formatApiDetail(error?.response?.data?.detail) ||
    error?.message ||
    fallback
  );
}

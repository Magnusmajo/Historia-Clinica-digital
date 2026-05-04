import axios from "axios";

const apiKey =
  import.meta.env.VITE_API_KEY ||
  (import.meta.env.DEV ? "dev-local-api-key" : "");

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: apiKey ? { "X-API-Key": apiKey } : {},
});

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
  const token = window.localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
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

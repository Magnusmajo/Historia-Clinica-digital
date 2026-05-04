import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
  headers: {
    "X-API-Key": import.meta.env.VITE_API_KEY || "dev-local-api-key",
  },
});

<<<<<<< HEAD
function formatApiDetail(detail) {
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message)
      .filter(Boolean)
      .join(". ");
  }

  return "";
}

export function getApiError(error, fallback = "Ocurrio un error inesperado") {
  return (
    formatApiDetail(error?.response?.data?.detail) ||
    error?.message ||
    fallback
  );
=======
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
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join(". ");
  }
  if (detail && typeof detail === "object") {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  return detail || error?.message || fallback;
>>>>>>> 8590154e1a428b6a387f3f56918abb8ed5f80ce0
}

import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
});

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
}

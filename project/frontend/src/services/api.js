import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
});

export function getApiError(error, fallback = "Ocurrio un error inesperado") {
  return error?.response?.data?.detail || error?.message || fallback;
}

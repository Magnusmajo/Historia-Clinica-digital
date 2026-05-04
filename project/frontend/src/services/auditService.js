import { api } from "./api";

export const getAuditLogs = async (limit = 100) => {
  const response = await api.get("/audit-logs/", { params: { limit } });
  return response.data;
};

import { api } from "./api";

export const getSummary = async () => {
  const response = await api.get("/stats/summary");
  return response.data;
};

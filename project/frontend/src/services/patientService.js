import { api } from "./api";

export const createPatient = async (data) => {
  const response = await api.post("/patients", data);
  return response.data;
};

export const getPatients = async () => {
  const response = await api.get("/patients");
  return response.data;
};
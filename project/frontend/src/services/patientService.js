import { api } from "./api";

export const createPatient = async (data) => {
  const response = await api.post("/patients/", data);
  return response.data;
};

export const getPatients = async (search = "") => {
  const response = await api.get("/patients/", {
    params: search ? { search } : undefined,
  });
  return response.data;
};

export const getPatient = async (id) => {
  const response = await api.get(`/patients/${id}`);
  return response.data;
};

export const updatePatient = async (id, data) => {
  const response = await api.patch(`/patients/${id}`, data);
  return response.data;
};

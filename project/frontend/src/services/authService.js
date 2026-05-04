import { api } from "./api";

export const login = async ({ email, password }) => {
  const response = await api.post("/auth/login", { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get("/auth/me");
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get("/auth/users");
  return response.data;
};

export const createUser = async (data) => {
  const response = await api.post("/auth/users", data);
  return response.data;
};

export const updateUser = async (id, data) => {
  const response = await api.patch(`/auth/users/${id}`, data);
  return response.data;
};

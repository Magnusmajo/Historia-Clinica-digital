import { api } from "./api";

export const getGoogleCalendarStatus = async () => {
  const response = await api.get("/google-calendar/status");
  return response.data;
};

export const getGoogleCalendarAuthUrl = async () => {
  const response = await api.get("/google-calendar/auth-url");
  return response.data.auth_url;
};

export const getAppointments = async () => {
  const response = await api.get("/appointments/");
  return response.data;
};

export const createAppointment = async (data) => {
  const response = await api.post("/appointments/", data);
  return response.data;
};

export const syncAppointment = async (id) => {
  const response = await api.post(`/appointments/${id}/sync`);
  return response.data;
};

export const deleteAppointment = async (id) => {
  await api.delete(`/appointments/${id}`);
};

import { api } from "./api";

export const getPatientPhotos = async (patientId) => {
  const response = await api.get(`/patients/${patientId}/photos/`);
  return response.data;
};

export const uploadPatientPhoto = async (patientId, { file, view, notes, takenAt }) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("view", view || "");
  formData.append("notes", notes || "");
  formData.append("taken_at", takenAt || "");

  const response = await api.post(`/patients/${patientId}/photos/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const deletePatientPhoto = async (patientId, photoId) => {
  await api.delete(`/patients/${patientId}/photos/${photoId}`);
};

export const getPhotoUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  return `${api.defaults.baseURL}${url}`;
};

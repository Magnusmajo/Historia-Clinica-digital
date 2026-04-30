import { api } from "./api";

export const createConsultation = async (patientId) => {
  const response = await api.post("/consultations/", { patient_id: patientId });
  return response.data;
};

export const createImplantArea = async ({ consultationId, drawingData, grafts }) => {
  const response = await api.post("/implant-areas/", {
    consultation_id: consultationId,
    drawing_data: drawingData,
    grafts,
  });
  return response.data;
};

export const deleteImplantArea = async (areaId) => {
  await api.delete(`/implant-areas/${areaId}`);
};

export const getClinicalNotes = async (patientId) => {
  const response = await api.get(`/patients/${patientId}/clinical-notes/`);
  return response.data?.notes || {};
};

export const saveClinicalNotes = async (patientId, notes) => {
  const response = await api.put(`/patients/${patientId}/clinical-notes/`, {
    notes,
  });
  return response.data.notes;
};

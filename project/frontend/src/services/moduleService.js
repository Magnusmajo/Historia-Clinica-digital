import { api } from "./api";

const unwrapRecord = (record) => ({
  id: record.id,
  createdAt: record.created_at,
  updatedAt: record.updated_at,
  ...record.payload,
});

export const getModuleRecords = async (module) => {
  const response = await api.get(`/modules/${module}/records`);
  return response.data.map(unwrapRecord);
};

export const createModuleRecord = async (module, payload) => {
  const response = await api.post(`/modules/${module}/records`, { payload });
  return unwrapRecord(response.data);
};

export const updateModuleRecord = async (module, id, payload) => {
  const response = await api.patch(`/modules/${module}/records/${id}`, {
    payload,
  });
  return unwrapRecord(response.data);
};

export const deleteModuleRecord = async (module, id) => {
  await api.delete(`/modules/${module}/records/${id}`);
};

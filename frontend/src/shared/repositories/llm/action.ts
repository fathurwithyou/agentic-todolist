import { jsonFetcher } from "../../lib/fetcher";

interface ModelsResponse {
  provider: string;
  models: string[];
}

export const getModels = async (provider: string) => {
  const response = await jsonFetcher<ModelsResponse>(`/api/v1/api-keys/models/${provider}`);
  return response.models;
};
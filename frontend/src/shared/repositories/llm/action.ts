import { jsonFetcher } from "../../lib/fetcher";

export const getModels = async (provider: string) => {
  const response = await jsonFetcher<string[]>(`/api/v1/api-keys/models/${provider}`);
  return response;
};
import axios, { type AxiosRequestConfig } from "axios";

const API_HOST = import.meta.env.VITE_API_HOST;
const API_PORT = import.meta.env.VITE_API_PORT;

const api = axios.create({
  baseURL: `${API_HOST}:${API_PORT}`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const apiFetcher = async <T>(
  url: string,
  options?: AxiosRequestConfig,
): Promise<T> => {
  console.info(
    `[apiFetcher] Request: ${options?.method || "GET"} ${url}`,
    options?.data ? { body: options.data } : {},
  );
  const response = await api.request<T>({ url, ...options });
  return response.data;
};

export const jsonFetcher = async <T>(
  url: string,
  options?: AxiosRequestConfig,
): Promise<T> => {
  try {
    const response = await apiFetcher<T>(url, options);
    console.info(
      `[jsonFetcher] Response: ${options?.method || "GET"} ${url}`,
      response,
    );
    return response;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(
        `[jsonFetcher] Error: ${options?.method || "GET"} ${url}`,
        error.response?.data,
      );
      throw new Error(error.response?.data?.message || "Unknown error");
    }
    throw error;
  }
};
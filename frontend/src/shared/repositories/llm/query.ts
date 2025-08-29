import { useQuery } from "@tanstack/react-query";
import { getModels } from "./action";

export const useGetModelsQuery = (provider: string, enabled: boolean) => {
  return useQuery({
    queryKey: ["models", provider],
    queryFn: () => getModels(provider),
    enabled: enabled && !!provider,
  });
};
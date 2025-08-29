import { useQuery } from "@tanstack/react-query";
import { getListApiKeys } from "./action";

export const useGetListApiKeysQuery = () => {
  return useQuery({
    queryKey: ["api-keys"],
    queryFn: getListApiKeys,
  });
};
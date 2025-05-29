import {useBoundStore} from "@/store/use-bound-store.tsx";
import {useCallback} from "react";
import {useQuery} from "@tanstack/react-query";
import {useShallow} from "zustand/react/shallow";
import type {GlobalConfig} from "@/pb/dev_observer/api/types/config.ts";
import type {QueryResultCommon} from "@/hooks/queries.tsx";

const configKeys = {
  global: ['globalConfig'] as const,
};

export function useGlobalConfig(): { config: GlobalConfig | undefined } & QueryResultCommon {
  const {fetchGlobalConfig} = useBoundStore();
  const queryFn = useCallback(async () => {
    await fetchGlobalConfig();
    return true
  }, [fetchGlobalConfig])
  const {isFetching, error, refetch} = useQuery({queryKey: configKeys.global, queryFn});
  const config = useBoundStore(useShallow(s => s.globalConfig));
  return {
    config, loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}
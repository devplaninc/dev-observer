import type {GlobalConfig} from "@/pb/dev_observer/api/types/config";
import type {StateCreator} from "zustand";
import {configAPI} from "@/store/apiPaths.tsx";
import {
  GetGlobalConfigResponse,
  UpdateGlobalConfigRequest,
  UpdateGlobalConfigResponse
} from "@/pb/dev_observer/api/web/config.ts";

export interface ConfigState {
  globalConfig: GlobalConfig | undefined;

  fetchGlobalConfig: () => Promise<void>;
  updateGlobalConfig: (configUpdate: Partial<GlobalConfig>) => Promise<void>;
}

export const createConfigSlice: StateCreator<
  ConfigState,
  [],
  [],
  ConfigState
> = ((set, get) => ({
  globalConfig: undefined,
  fetchGlobalConfig: async () => fetch(configAPI())
    .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {

      const {config} = GetGlobalConfigResponse.fromJSON(js)
      set(s => ({...s, globalConfig: config}))
    }),
  updateGlobalConfig: async update => fetch(configAPI(),
    {
      method: "POST", body: JSON.stringify(UpdateGlobalConfigRequest.toJSON(
        {config: {...get().globalConfig!, ...update}}
      ))
    }
  ).then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const {config} = UpdateGlobalConfigResponse.fromJSON(js)
      set(s => ({...s, globalConfig: config}))
    }),
}))
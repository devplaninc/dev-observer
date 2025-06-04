import type {StateCreator} from "zustand";
import {observationAPI, observationsAPI} from "@/store/apiPaths.tsx";
import type {Observation, ObservationKey} from "@/pb/dev_observer/api/types/observations.ts";
import {GetObservationResponse, GetObservationsResponse} from "@/pb/dev_observer/api/web/observations.ts";

export interface ObservationsState {
  observationKeys: Record<string, ObservationKey[]>;
  observations: Record<string, Observation>;

  fetchObservations: (kind: string) => Promise<void>;
  fetchObservation: (key: ObservationKey) => Promise<void>;
}

export const createObservationsSlice: StateCreator<
  ObservationsState,
  [],
  [],
  ObservationsState
> = ((set, get) => ({
  observationKeys: {},
  observations: {},
  fetchObservations: async kind => fetch(observationsAPI(kind))
    .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const {keys} = GetObservationsResponse.fromJSON(js)
      set(s => ({...s, observationKeys: {...s.observationKeys, [kind]: (keys ?? [])}}))
    }),
  fetchObservation: async key => fetch(observationAPI(key.kind, key.name, key.key))
    .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const k = observationKeyStr(key)
      const {observation} = GetObservationResponse.fromJSON(js)
      if (observation) {
        set(s => ({...s, observations: {...s.observations, [k]: observation}}))
      } else {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const {[k]: _, ...observations} = get().observations
        set(s => ({...s, observations}))
      }
    }),
}))

export function observationKeyStr(k: ObservationKey) {
  return `${k.kind}__${k.name}__${k.key}`
}
import type {StateCreator} from "zustand";
import {observationAPI, observationsAPI} from "@/store/apiPaths.tsx";
import type {Observation, ObservationKey} from "@devplan/observer-api";
import {GetObservationResponse, GetObservationsResponse} from "@devplan/observer-api";
import {fetchWithAuth} from "@/store/api.tsx";

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
  fetchObservations: async kind => fetchWithAuth(observationsAPI(kind), GetObservationsResponse)
    .then(r => set(s => ({...s, observationKeys: {...s.observationKeys, [kind]: (r.keys ?? [])}}))),
  fetchObservation: async key => fetchWithAuth(observationAPI(key.kind, key.name, key.key), GetObservationResponse)
    .then(r => {
      const k = observationKeyStr(key)
      const {observation} = r
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
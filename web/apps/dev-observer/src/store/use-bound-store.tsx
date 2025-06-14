import {createWithEqualityFn as create} from "zustand/traditional";
import {type ConfigState, createConfigSlice} from "@/store/configStore.tsx";
import {createRepositoriesSlice, type RepositoryState} from "@/store/repositoryStore.tsx";
import {createObservationsSlice, type ObservationsState} from "@/store/observationsStore.tsx";

export const useBoundStore = create<
  ConfigState & RepositoryState & ObservationsState
>()((...a) => ({
  ...createConfigSlice(...a),
  ...createRepositoriesSlice(...a),
  ...createObservationsSlice(...a),
}))
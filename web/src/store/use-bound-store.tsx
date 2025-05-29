import {createWithEqualityFn as create} from "zustand/traditional";
import {type ConfigState, createConfigSlice} from "@/store/configStore.tsx";
import {createRepositoriesSlice, type RepositoryState} from "@/store/repositoryStore.tsx";

export const useBoundStore = create<
  ConfigState & RepositoryState
>()((...a) => ({
  ...createConfigSlice(...a),
  ...createRepositoriesSlice(...a),
}))
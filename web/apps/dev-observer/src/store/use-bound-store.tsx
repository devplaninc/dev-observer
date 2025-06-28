import {createWithEqualityFn as create} from "zustand/traditional";
import {type ConfigState, createConfigSlice} from "@/store/configStore.tsx";
import {createRepositoriesSlice, type RepositoryState} from "@/store/repositoryStore.tsx";
import {createObservationsSlice, type ObservationsState} from "@/store/observationsStore.tsx";
import {createWebSitesSlice, type WebSiteState} from "@/store/websiteStore.tsx";

export const useBoundStore = create<
  ConfigState & RepositoryState & ObservationsState & WebSiteState
>()((...a) => ({
  ...createConfigSlice(...a),
  ...createRepositoriesSlice(...a),
  ...createObservationsSlice(...a),
  ...createWebSitesSlice(...a),
}))

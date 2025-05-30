export const ownDomain = "http://localhost:8090"

export function baseAPI() {
  return `${ownDomain}/api/v1` as const;
}

export function configAPI() {
  return `${baseAPI()}/config` as const;
}

export function reposAPI() {
  return `${baseAPI()}/repositories` as const;
}

export function repoAPI<R extends string>(repoId: R) {
  return `${reposAPI()}/${repoId}` as const;
}

export function repoRescanAPI<R extends string>(repoId: R) {
  return `${repoAPI(repoId)}/rescan` as const;
}
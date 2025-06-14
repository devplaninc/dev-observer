export const ownDomain = import.meta.env.VITE_KEEP_OWN_DOMAIN !== undefined ? "" : "http://localhost:8090";

export function baseAPI() {
  return `${ownDomain}/api/v1` as const;
}

export function configAPI() {
  return `${baseAPI()}/config` as const;
}

export function usersStatusAPI() {
  return `${configAPI()}/users/status` as const;
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

export function observationsAPI<K extends string>(kind: K) {
  return `${baseAPI()}/observations/kind/${kind}` as const;
}

export function observationAPI<K extends string, N extends string, C extends string>(kind: K, name: N, key: C) {
  return `${baseAPI()}/observation/${kind}/${encodeURIComponent(name)}/${enc(key)}` as const;
}

// Encodes as base64
function enc(v: string): string {
  // TODO: perform safe encoding
  return v.replace(/\//g, '|');
}

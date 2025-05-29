export const ownDomain = "http://localhost:8090"

export function baseAPI() {
  return `${ownDomain}/api/v1` as const;
}

export function configAPI() {
  return `${baseAPI()}/config` as const;
}
import {useBoundStore} from "@/store/use-bound-store.tsx";

export interface ParseableMessage<T> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  fromJSON(object: any): T;
}

export class VoidParser implements ParseableMessage<void> {

  fromJSON(): void {
    return
  }
}

type WindowWithClerk = Window & {
  Clerk?: {
    session?: {
      getToken(): Promise<string | null>
    }
  }
}

const getSessionToken = async () => {
  if (!(window as WindowWithClerk).Clerk?.session) return null
  return (await (window as WindowWithClerk)?.Clerk?.session?.getToken()) ?? null
}

export async function fetchWithAuth<T>(
  url: string,
  response: ParseableMessage<T>,
  options: RequestInit = {},
) {
  const headers = new Headers(options.headers);
  if (useBoundStore.getState().usersStatus?.enabled) {
    const token = await getSessionToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }
  return fetch(url, {...options, headers,})
    .then(res => res.ok ? res.json() : Promise.reject(new Error(res.statusText)))
    .then(js => response.fromJSON(js))
}
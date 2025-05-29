export interface QueryResultCommon {
  error: Error | null
  loading: boolean,
  reload: () => Promise<void>
}
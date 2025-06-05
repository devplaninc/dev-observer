/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_KEEP_OWN_DOMAIN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
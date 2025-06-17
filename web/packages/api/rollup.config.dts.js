import dts from 'rollup-plugin-dts';
import { defineConfig } from 'rollup';

export default defineConfig({
  input: 'dist/dts/index.d.ts',
  output: {
    file: 'dist/index.d.ts',
    format: 'es',
  },
  plugins: [dts()],
});
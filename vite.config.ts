import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
    build: {
        lib: {
            entry: resolve(__dirname, "src/transport-card.ts"),
            name: "TransportCard",
            fileName: "transport-card",
            formats: ["es"],
        },
        outDir: "dist",
        emptyOutDir: true,
    },
});

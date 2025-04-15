import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import proxyOptions from "./proxyOptions";
import tailwindcss from "@tailwindcss/vite";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss()],
    server: {
        port: 8080,
        host: "0.0.0.0",
        proxy: proxyOptions,
        allowedHosts: ["suntek.test", "suntek-dev.frappe.cloud", "suntekerp.frappe.cloud", "suntek.local"],
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "src"),
        },
    },
    build: {
        outDir: "../suntek_app/public/dashboard",
        emptyOutDir: true,
        target: "es2015",
    },
});

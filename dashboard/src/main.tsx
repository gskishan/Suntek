import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { FrappeProvider } from "frappe-react-sdk";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <FrappeProvider enableSocket={false}>
            <App />
        </FrappeProvider>
    </StrictMode>,
);

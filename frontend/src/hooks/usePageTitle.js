import { useEffect } from "react";

const BASE = "ServiciosBogotá";

export default function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} · ${BASE}` : `${BASE} — Directorio de servicios locales en Bogotá`;
  }, [title]);
}

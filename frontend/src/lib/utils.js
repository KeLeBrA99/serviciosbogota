import { DAYS } from "./constants";

/** Convierte cualquier error de la API en un mensaje legible. */
export function errorMessage(err, fallback = "Ocurrió un error. Intenta de nuevo.") {
  if (!err?.response) {
    return err?.code === "ECONNABORTED"
      ? "El servidor tardó demasiado en responder."
      : "No pudimos conectar con el servidor. Revisa tu conexión.";
  }
  const detail = err.response.data?.detail;
  if (Array.isArray(detail)) {
    // Errores de validación (422) de FastAPI
    const msg = detail[0]?.msg || fallback;
    return msg.replace(/^Value error, /, "");
  }
  return typeof detail === "string" ? detail : fallback;
}

export const formatCOP = (value) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(value);

/** La API guarda las fechas en UTC sin zona; se interpreta como UTC. */
export function parseDate(value) {
  if (!value) return null;
  const iso = /[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`;
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value) {
  const date = parseDate(value);
  return date
    ? date.toLocaleDateString("es-CO", { day: "numeric", month: "short", year: "numeric", timeZone: "America/Bogota" })
    : "—";
}

export function daysUntil(value) {
  const date = parseDate(value);
  return date ? Math.ceil((date.getTime() - Date.now()) / 86400000) : null;
}

/** Enlace de WhatsApp con indicativo de Colombia cuando el número es local. */
export function whatsappLink(number, text = "") {
  let digits = String(number || "").replace(/\D/g, "");
  if (digits.length === 10) digits = `57${digits}`;
  const query = text ? `?text=${encodeURIComponent(text)}` : "";
  return `https://wa.me/${digits}${query}`;
}

export const telLink = (number) => `tel:${String(number || "").replace(/[^\d+]/g, "")}`;

function bogotaNow() {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Bogota", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(new Date());
  const get = (type) => parts.find((p) => p.type === type)?.value;
  const index = { Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6 }[get("weekday")];
  return { day: DAYS[index].key, time: `${get("hour")}:${get("minute")}` };
}

/**
 * Abierto/cerrado: el interruptor manual del negocio manda cuando está en
 * "cerrado"; si hay horario, se calcula con la hora actual de Bogotá.
 */
export function isOpenNow(business) {
  if (!business?.is_open_now) return false;
  const schedule = business.schedule;
  if (!schedule || Object.keys(schedule).length === 0) return true;
  const { day, time } = bogotaNow();
  const today = schedule[day];
  if (!today || today.closed) return false;
  if (today.close <= today.open) return time >= today.open || time < today.close; // cruza medianoche
  return time >= today.open && time < today.close;
}

export function emptySchedule() {
  return Object.fromEntries(
    DAYS.map(({ key }) => [key, { open: "08:00", close: "18:00", closed: key === "domingo" }])
  );
}

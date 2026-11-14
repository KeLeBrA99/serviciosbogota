import { useEffect, useState } from "react";
import { categoriesAPI } from "../../services/api";
import { DAYS, LOCALIDADES } from "../../lib/constants";
import { emptySchedule } from "../../lib/utils";

const EMPTY = {
  name: "", category_id: "", description: "", short_description: "",
  phone: "", whatsapp: "", email: "", website: "",
  localidad: "", neighborhood: "", address: "", tags: "",
};

function toFormState(business) {
  if (!business) return EMPTY;
  return {
    ...Object.fromEntries(Object.keys(EMPTY).map((k) => [k, business[k] ?? ""])),
    category_id: business.category?.id ?? "",
    tags: (business.tags || []).join(", "),
  };
}

/**
 * Formulario compartido para crear y editar un negocio.
 * onSubmit recibe el payload listo para la API.
 */
export default function BusinessForm({ business, submitLabel, onSubmit }) {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(() => toFormState(business));
  const [useSchedule, setUseSchedule] = useState(Boolean(business?.schedule));
  const [schedule, setSchedule] = useState(() => ({ ...emptySchedule(), ...(business?.schedule || {}) }));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    categoriesAPI.list().then(({ data }) => setCategories(data)).catch(() => {});
  }, []);

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));
  const setDay = (day, patch) => setSchedule((s) => ({ ...s, [day]: { ...s[day], ...patch } }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSubmit({
        ...form,
        category_id: Number(form.category_id),
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
        schedule: useSchedule ? schedule : null,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <section className="card p-6 space-y-4">
        <h2 className="font-display font-700 text-white">Información básica</h2>
        <div>
          <label className="label" htmlFor="bf-name">Nombre del negocio *</label>
          <input id="bf-name" value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Ej: Taller El Rápido" className="input" required minLength={3} maxLength={150} />
        </div>
        <div>
          <label className="label" htmlFor="bf-category">Categoría *</label>
          <select id="bf-category" value={form.category_id} onChange={(e) => set("category_id", e.target.value)} className="input" required>
            <option value="">Seleccionar categoría</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="bf-short">Descripción corta</label>
          <input id="bf-short" value={form.short_description} onChange={(e) => set("short_description", e.target.value)} placeholder="Una línea que resume tu negocio" className="input" maxLength={300} />
          <p className="text-zinc-600 text-xs mt-1">Es lo que se ve en los resultados de búsqueda.</p>
        </div>
        <div>
          <label className="label" htmlFor="bf-description">Descripción completa *</label>
          <textarea id="bf-description" value={form.description} onChange={(e) => set("description", e.target.value)} placeholder="Describe tus servicios, experiencia, zonas que cubres..." className="input h-32 resize-y" required minLength={20} maxLength={5000} />
        </div>
        <div>
          <label className="label" htmlFor="bf-tags">Etiquetas (separadas por coma)</label>
          <input id="bf-tags" value={form.tags} onChange={(e) => set("tags", e.target.value)} placeholder="Ej: Domicilio, 24h, Garantía" className="input" />
        </div>
      </section>

      <section className="card p-6 space-y-4">
        <h2 className="font-display font-700 text-white">Contacto</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label" htmlFor="bf-phone">Teléfono *</label>
            <input id="bf-phone" type="tel" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="300 123 4567" className="input" required />
          </div>
          <div>
            <label className="label" htmlFor="bf-whatsapp">WhatsApp</label>
            <input id="bf-whatsapp" type="tel" value={form.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} placeholder="300 123 4567" className="input" />
          </div>
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label" htmlFor="bf-email">Correo de contacto</label>
            <input id="bf-email" type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="negocio@correo.com" className="input" />
          </div>
          <div>
            <label className="label" htmlFor="bf-website">Sitio web o red social</label>
            <input id="bf-website" value={form.website} onChange={(e) => set("website", e.target.value)} placeholder="instagram.com/minegocio" className="input" />
          </div>
        </div>
      </section>

      <section className="card p-6 space-y-4">
        <h2 className="font-display font-700 text-white">Ubicación</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="label" htmlFor="bf-localidad">Localidad *</label>
            <select id="bf-localidad" value={form.localidad} onChange={(e) => set("localidad", e.target.value)} className="input" required>
              <option value="">Seleccionar localidad</option>
              {LOCALIDADES.map((l) => <option key={l}>{l}</option>)}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="bf-neighborhood">Barrio</label>
            <input id="bf-neighborhood" value={form.neighborhood} onChange={(e) => set("neighborhood", e.target.value)} placeholder="Ej: Prado Veraniego" className="input" maxLength={150} />
          </div>
        </div>
        <div>
          <label className="label" htmlFor="bf-address">Dirección</label>
          <input id="bf-address" value={form.address} onChange={(e) => set("address", e.target.value)} placeholder="Cra 15 # 93-47" className="input" maxLength={300} />
        </div>
      </section>

      <section className="card p-6 space-y-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="font-display font-700 text-white">Horario de atención</h2>
            <p className="text-zinc-500 text-xs mt-1">Con horario, tu perfil muestra solo si estás abierto o cerrado.</p>
          </div>
          <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
            <input type="checkbox" checked={useSchedule} onChange={(e) => setUseSchedule(e.target.checked)} className="accent-amber-500 w-4 h-4" />
            Definir horario
          </label>
        </div>
        {useSchedule && (
          <div className="space-y-2">
            {DAYS.map(({ key, label }) => (
              <div key={key} className="flex flex-wrap items-center gap-3 text-sm">
                <span className="w-24 text-zinc-300">{label}</span>
                <input type="time" aria-label={`${label}: abre`} value={schedule[key].open} disabled={schedule[key].closed} onChange={(e) => setDay(key, { open: e.target.value })} className="input !w-32 disabled:opacity-40" required={!schedule[key].closed} />
                <span className="text-zinc-500">a</span>
                <input type="time" aria-label={`${label}: cierra`} value={schedule[key].close} disabled={schedule[key].closed} onChange={(e) => setDay(key, { close: e.target.value })} className="input !w-32 disabled:opacity-40" required={!schedule[key].closed} />
                <label className="flex items-center gap-1.5 text-zinc-400 cursor-pointer">
                  <input type="checkbox" checked={schedule[key].closed} onChange={(e) => setDay(key, { closed: e.target.checked })} className="accent-amber-500" />
                  Cerrado
                </label>
              </div>
            ))}
          </div>
        )}
      </section>

      <button type="submit" disabled={saving} className="btn-primary w-full py-3 text-base">
        {saving ? "Guardando..." : submitLabel}
      </button>
    </form>
  );
}

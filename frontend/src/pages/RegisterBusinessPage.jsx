import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { businessAPI, categoriesAPI } from "../services/api";
import Navbar from "../components/ui/Navbar";
import toast from "react-hot-toast";

const LOCALIDADES = [
  "Usaquén","Chapinero","Santa Fe","San Cristóbal","Usme","Tunjuelito",
  "Bosa","Kennedy","Fontibón","Engativá","Suba","Barrios Unidos",
  "Teusaquillo","Los Mártires","Antonio Nariño","Puente Aranda",
  "La Candelaria","Rafael Uribe Uribe","Ciudad Bolívar",
];

export default function RegisterBusinessPage() {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    name: "", category_id: "", description: "", short_description: "",
    phone: "", whatsapp: "", email: "", localidad: "", address: "",
    tags: "",
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    categoriesAPI.list().then(({ data }) => setCategories(data));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        category_id: Number(form.category_id),
        tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean),
      };
      await businessAPI.create(payload);
      toast.success("¡Negocio registrado! Activa tu plan para aparecer en el directorio.");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Error al registrar el negocio");
    } finally {
      setLoading(false);
    }
  };

  const set = (key, val) => setForm((f) => ({ ...f, [key]: val }));

  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-10">
        <div className="mb-8">
          <h1 className="font-display font-800 text-2xl text-white">Registrar mi negocio</h1>
          <p className="text-zinc-400 text-sm mt-1">Completa la información para aparecer en el directorio.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Info básica */}
          <div className="card p-6 space-y-4">
            <h2 className="font-display font-700 text-white">Información básica</h2>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Nombre del negocio *</label>
              <input value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Ej: Taller El Rápido" className="input" required />
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Categoría *</label>
              <select value={form.category_id} onChange={(e) => set("category_id", e.target.value)} className="input" required>
                <option value="">Seleccionar categoría</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Descripción corta</label>
              <input value={form.short_description} onChange={(e) => set("short_description", e.target.value)} placeholder="Una línea que resume tu negocio" className="input" maxLength={300} />
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Descripción completa *</label>
              <textarea value={form.description} onChange={(e) => set("description", e.target.value)} placeholder="Describe tus servicios, experiencia, horarios..." className="input h-28 resize-none" required />
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Etiquetas (separadas por coma)</label>
              <input value={form.tags} onChange={(e) => set("tags", e.target.value)} placeholder="Ej: Domicilio, 24h, Garantía" className="input" />
            </div>
          </div>

          {/* Contacto */}
          <div className="card p-6 space-y-4">
            <h2 className="font-display font-700 text-white">Contacto</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Teléfono *</label>
                <input value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="300 123 4567" className="input" required />
              </div>
              <div>
                <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">WhatsApp</label>
                <input value={form.whatsapp} onChange={(e) => set("whatsapp", e.target.value)} placeholder="300 123 4567" className="input" />
              </div>
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Correo de contacto</label>
              <input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="negocio@correo.com" className="input" />
            </div>
          </div>

          {/* Ubicación */}
          <div className="card p-6 space-y-4">
            <h2 className="font-display font-700 text-white">Ubicación</h2>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Localidad *</label>
              <select value={form.localidad} onChange={(e) => set("localidad", e.target.value)} className="input" required>
                <option value="">Seleccionar localidad</option>
                {LOCALIDADES.map((l) => <option key={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Dirección</label>
              <input value={form.address} onChange={(e) => set("address", e.target.value)} placeholder="Cra 15 # 93-47" className="input" />
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3 text-base disabled:opacity-50">
            {loading ? "Registrando..." : "Registrar negocio"}
          </button>
        </form>
      </div>
    </div>
  );
}

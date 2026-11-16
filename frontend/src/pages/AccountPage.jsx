import { useState } from "react";
import toast from "react-hot-toast";
import { authAPI } from "../services/api";
import useAuthStore from "../store/authStore";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage, formatDate } from "../lib/utils";

export default function AccountPage() {
  usePageTitle("Mi cuenta");
  const user = useAuthStore((s) => s.user);
  const [form, setForm] = useState({ current_password: "", new_password: "", confirm: "" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.new_password !== form.confirm) return toast.error("Las contraseñas nuevas no coinciden");
    setSaving(true);
    try {
      await authAPI.changePassword({ current_password: form.current_password, new_password: form.new_password });
      toast.success("Contraseña actualizada");
      setForm({ current_password: "", new_password: "", confirm: "" });
    } catch (err) {
      toast.error(errorMessage(err, "No se pudo cambiar la contraseña"));
    } finally {
      setSaving(false);
    }
  };

  const field = (key, label, autoComplete) => (
    <div>
      <label className="label" htmlFor={`acc-${key}`}>{label}</label>
      <input id={`acc-${key}`} type="password" autoComplete={autoComplete} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} className="input" required minLength={key === "current_password" ? undefined : 8} />
    </div>
  );

  return (
    <div className="max-w-xl mx-auto px-4 py-10 space-y-5">
      <h1 className="font-display font-800 text-2xl text-white">Mi cuenta</h1>

      <section className="card p-6">
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-3 text-sm">
          <dt className="text-zinc-500">Nombre</dt><dd className="text-white">{user?.full_name}</dd>
          <dt className="text-zinc-500">Correo</dt><dd className="text-white break-all">{user?.email}</dd>
          <dt className="text-zinc-500">Teléfono</dt><dd className="text-white">{user?.phone || "—"}</dd>
          <dt className="text-zinc-500">Miembro desde</dt><dd className="text-white">{formatDate(user?.created_at)}</dd>
        </dl>
      </section>

      <section className="card p-6">
        <h2 className="font-display font-700 text-white mb-4">Cambiar contraseña</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {field("current_password", "Contraseña actual", "current-password")}
          {field("new_password", "Nueva contraseña (mínimo 8 caracteres)", "new-password")}
          {field("confirm", "Repite la nueva contraseña", "new-password")}
          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? "Guardando..." : "Actualizar contraseña"}
          </button>
        </form>
      </section>
    </div>
  );
}

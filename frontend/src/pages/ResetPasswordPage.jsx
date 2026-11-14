import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { authAPI } from "../services/api";
import AuthShell from "../components/layout/AuthShell";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

export default function ResetPasswordPage() {
  usePageTitle("Nueva contraseña");
  const [params] = useSearchParams();
  const token = params.get("token");
  const navigate = useNavigate();
  const [form, setForm] = useState({ password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [expired, setExpired] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) return toast.error("Las contraseñas no coinciden");
    setLoading(true);
    try {
      await authAPI.resetPassword(token, form.password);
      toast.success("Contraseña actualizada. Ya puedes ingresar.");
      navigate("/login", { replace: true });
    } catch (err) {
      if (err.response?.status === 400) setExpired(true);
      else toast.error(errorMessage(err, "No se pudo cambiar la contraseña"));
      setLoading(false);
    }
  };

  if (!token || expired) {
    return (
      <AuthShell subtitle="Enlace no válido">
        <div className="text-center">
          <p className="text-4xl mb-3">⌛</p>
          <p className="text-zinc-300 text-sm mb-5">Este enlace no es válido o ya venció. Los enlaces duran 30 minutos y solo se pueden usar una vez.</p>
          <Link to="/recuperar" className="btn-primary w-full">Pedir un enlace nuevo</Link>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell subtitle="Crea tu nueva contraseña">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label" htmlFor="reset-password">Nueva contraseña (mínimo 8 caracteres)</label>
          <input id="reset-password" type="password" autoComplete="new-password" autoFocus value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="input" required minLength={8} />
        </div>
        <div>
          <label className="label" htmlFor="reset-confirm">Repite la contraseña</label>
          <input id="reset-confirm" type="password" autoComplete="new-password" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} className="input" required minLength={8} />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Guardando..." : "Guardar contraseña"}
        </button>
      </form>
    </AuthShell>
  );
}

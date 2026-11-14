import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { authAPI } from "../services/api";
import AuthShell from "../components/layout/AuthShell";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

export default function ForgotPasswordPage() {
  usePageTitle("Recuperar contraseña");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authAPI.forgotPassword(email);
      setSent(true);
    } catch (err) {
      toast.error(errorMessage(err, "No pudimos procesar la solicitud"));
    } finally {
      setLoading(false);
    }
  };

  const back = <Link to="/login" className="text-brand-400 hover:text-brand-300">← Volver a ingresar</Link>;

  if (sent) {
    return (
      <AuthShell subtitle="Revisa tu correo" footer={back}>
        <div className="text-center">
          <p className="text-4xl mb-3">📬</p>
          <p className="text-zinc-300 text-sm">
            Si <strong className="text-white break-all">{email}</strong> tiene una cuenta, te enviamos un enlace para crear una contraseña nueva.
          </p>
          <p className="text-zinc-500 text-xs mt-3">El enlace vence en 30 minutos. Si no lo ves, revisa la carpeta de spam.</p>
          <button onClick={() => setSent(false)} className="text-brand-400 hover:text-brand-300 text-xs mt-4">Usar otro correo</button>
        </div>
      </AuthShell>
    );
  }

  return (
    <AuthShell subtitle="Te enviaremos un enlace para crear una contraseña nueva" footer={back}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label" htmlFor="forgot-email">Correo de tu cuenta</label>
          <input id="forgot-email" type="email" autoComplete="email" autoFocus value={email} onChange={(e) => setEmail(e.target.value)} placeholder="tu@correo.com" className="input" required />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Enviando..." : "Enviar enlace"}
        </button>
      </form>
    </AuthShell>
  );
}

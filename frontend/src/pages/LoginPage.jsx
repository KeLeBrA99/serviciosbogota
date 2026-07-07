import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import toast from "react-hot-toast";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast.success("¡Bienvenido!");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Correo o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="font-display font-800 text-2xl text-white">
            Servicios<span className="text-brand-500">Bogotá</span>
          </Link>
          <p className="text-zinc-400 mt-2 text-sm">Ingresa a tu cuenta</p>
        </div>
        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Correo electrónico</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="tu@correo.com" className="input" required />
            </div>
            <div>
              <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">Contraseña</label>
              <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="••••••••" className="input" required />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
              {loading ? "Ingresando..." : "Ingresar"}
            </button>
          </form>
        </div>
        <p className="text-center text-zinc-500 text-sm mt-4">
          ¿No tienes cuenta?{" "}
          <Link to="/registro" className="text-brand-400 hover:text-brand-300">Regístrate gratis</Link>
        </p>
      </div>
    </div>
  );
}

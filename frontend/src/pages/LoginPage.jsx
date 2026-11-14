import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

export default function LoginPage() {
  usePageTitle("Ingresar");
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const { login, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const from = location.state?.from || "/dashboard";

  useEffect(() => {
    if (params.get("expirada")) toast("Tu sesión expiró. Ingresa de nuevo.", { id: "expirada" });
  }, [params]);

  if (isAuthenticated && !loading) return <Navigate to={from} replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(form.email, form.password);
      toast.success(`¡Hola, ${user.full_name.split(" ")[0]}!`);
      navigate(from, { replace: true });
    } catch (err) {
      toast.error(errorMessage(err, "Correo o contraseña incorrectos"));
      setLoading(false); // en caso de éxito no se reactiva: la página ya está navegando
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
              <label className="label" htmlFor="login-email">Correo electrónico</label>
              <input id="login-email" type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="tu@correo.com" className="input" required />
            </div>
            <div>
              <label className="label" htmlFor="login-password">Contraseña</label>
              <input id="login-password" type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="••••••••" className="input" required />
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Ingresando..." : "Ingresar"}
            </button>
          </form>
        </div>
        <p className="text-center text-zinc-500 text-sm mt-4">
          ¿No tienes cuenta?{" "}
          <Link to="/registro" state={location.state} className="text-brand-400 hover:text-brand-300">Regístrate gratis</Link>
        </p>
      </div>
    </div>
  );
}

import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

const FIELDS = [
  { key: "full_name", label: "Nombre completo", type: "text", placeholder: "Tu nombre", autoComplete: "name" },
  { key: "email", label: "Correo electrónico", type: "email", placeholder: "tu@correo.com", autoComplete: "email" },
  { key: "phone", label: "Teléfono (opcional)", type: "tel", placeholder: "300 123 4567", autoComplete: "tel" },
  { key: "password", label: "Contraseña", type: "password", placeholder: "Mínimo 8 caracteres", autoComplete: "new-password" },
];

export default function RegisterPage() {
  usePageTitle("Crear cuenta");
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "" });
  const [loading, setLoading] = useState(false);
  const { register, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  if (isAuthenticated && !loading) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      toast.success("¡Cuenta creada! Ahora registra tu negocio.");
      navigate("/registrar-negocio", { replace: true });
    } catch (err) {
      toast.error(errorMessage(err, "Error al crear la cuenta"));
      setLoading(false); // en caso de éxito no se reactiva: la página ya está navegando
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="font-display font-800 text-2xl text-white">
            Servicios<span className="text-brand-500">Bogotá</span>
          </Link>
          <p className="text-zinc-400 mt-2 text-sm">Crea tu cuenta y publica tu negocio</p>
        </div>
        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {FIELDS.map(({ key, label, ...input }) => (
              <div key={key}>
                <label className="label" htmlFor={`reg-${key}`}>{label}</label>
                <input
                  id={`reg-${key}`}
                  {...input}
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  className="input"
                  required={key !== "phone"}
                  minLength={key === "password" ? 8 : undefined}
                />
              </div>
            ))}
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? "Creando cuenta..." : "Crear cuenta"}
            </button>
          </form>
        </div>
        <p className="text-center text-zinc-500 text-sm mt-4">
          ¿Ya tienes cuenta?{" "}
          <Link to="/login" className="text-brand-400 hover:text-brand-300">Ingresar</Link>
        </p>
      </div>
    </div>
  );
}

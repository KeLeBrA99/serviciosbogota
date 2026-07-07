import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "" });
  const [loading, setLoading] = useState(false);
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      toast.success("¡Cuenta creada exitosamente!");
      navigate("/registrar-negocio");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Error al crear la cuenta");
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
          <p className="text-zinc-400 mt-2 text-sm">Crea tu cuenta gratis</p>
        </div>
        <div className="card p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { key: "full_name", label: "Nombre completo", type: "text", placeholder: "Tu nombre" },
              { key: "email", label: "Correo electrónico", type: "email", placeholder: "tu@correo.com" },
              { key: "phone", label: "Teléfono (opcional)", type: "tel", placeholder: "300 123 4567" },
              { key: "password", label: "Contraseña", type: "password", placeholder: "Mínimo 8 caracteres" },
            ].map(({ key, label, type, placeholder }) => (
              <div key={key}>
                <label className="text-zinc-400 text-xs font-display font-600 block mb-1.5">{label}</label>
                <input type={type} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} placeholder={placeholder} className="input" required={key !== "phone"} />
              </div>
            ))}
            <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
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

import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../../store/authStore";
import toast from "react-hot-toast";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success("Sesión cerrada");
    navigate("/");
  };

  return (
    <nav className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur border-b border-zinc-800">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-display font-800 text-lg text-white">
          Servicios<span className="text-brand-500">Bogotá</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link to="/planes" className="text-zinc-400 hover:text-white text-sm font-body transition-colors">
            Planes
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-zinc-400 hover:text-white text-sm transition-colors">
                Dashboard
              </Link>
              <button onClick={handleLogout} className="btn-outline text-sm py-1.5 px-3">
                Salir
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-zinc-400 hover:text-white text-sm transition-colors">
                Ingresar
              </Link>
              <Link to="/registro" className="btn-primary text-sm py-1.5 px-4">
                Registrarse
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

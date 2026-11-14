import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../../store/authStore";

const linkClass = ({ isActive }) =>
  `text-sm transition-colors ${isActive ? "text-white" : "text-zinc-400 hover:text-white"}`;

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const close = () => setOpen(false);

  const handleLogout = () => {
    logout();
    close();
    toast.success("Sesión cerrada");
    navigate("/");
  };

  const links = (
    <>
      <NavLink to="/planes" className={linkClass} onClick={close}>Planes</NavLink>
      {isAuthenticated ? (
        <>
          <NavLink to="/dashboard" className={linkClass} onClick={close}>Mi negocio</NavLink>
          {user?.role === "admin" && <NavLink to="/admin" className={linkClass} onClick={close}>Admin</NavLink>}
          <NavLink to="/cuenta" className={linkClass} onClick={close}>
            {user?.full_name?.split(" ")[0] || "Mi cuenta"}
          </NavLink>
          <button onClick={handleLogout} className="btn-ghost py-1.5 px-3">Salir</button>
        </>
      ) : (
        <>
          <NavLink to="/login" className={linkClass} onClick={close}>Ingresar</NavLink>
          <Link to="/registro" className="btn-primary text-sm py-1.5 px-4" onClick={close}>Publicar mi negocio</Link>
        </>
      )}
    </>
  );

  return (
    <nav className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur border-b border-zinc-800">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-display font-800 text-lg text-white" onClick={close}>
          Servicios<span className="text-brand-500">Bogotá</span>
        </Link>
        <div className="hidden md:flex items-center gap-5">{links}</div>
        <button
          className="md:hidden text-zinc-300 text-2xl leading-none px-2 py-1"
          onClick={() => setOpen((v) => !v)}
          aria-label="Abrir menú"
          aria-expanded={open}
        >
          {open ? "✕" : "☰"}
        </button>
      </div>
      {open && (
        <div className="md:hidden border-t border-zinc-800 px-4 py-4 flex flex-col items-start gap-4 bg-zinc-950">
          {links}
        </div>
      )}
    </nav>
  );
}

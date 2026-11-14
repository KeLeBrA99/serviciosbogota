import { Link, Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import { SUPPORT_EMAIL } from "../../lib/constants";

function Footer() {
  return (
    <footer className="border-t border-zinc-800 mt-16">
      <div className="max-w-6xl mx-auto px-4 py-8 flex flex-col md:flex-row gap-4 md:items-center md:justify-between text-sm">
        <div>
          <p className="font-display font-800 text-white">
            Servicios<span className="text-brand-500">Bogotá</span>
          </p>
          <p className="text-zinc-500 text-xs mt-1">Directorio de servicios locales por localidad.</p>
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-2 text-zinc-400">
          <Link to="/" className="hover:text-white transition-colors">Buscar servicios</Link>
          <Link to="/planes" className="hover:text-white transition-colors">Planes para negocios</Link>
          <Link to="/registro" className="hover:text-white transition-colors">Publicar mi negocio</Link>
          <a href={`mailto:${SUPPORT_EMAIL}`} className="hover:text-white transition-colors">{SUPPORT_EMAIL}</a>
        </div>
      </div>
    </footer>
  );
}

export default function Layout() {
  return (
    <div className="min-h-screen bg-zinc-950 flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

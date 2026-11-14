import { Link } from "react-router-dom";

/** Marco de las páginas de acceso: logo centrado y tarjeta. */
export default function AuthShell({ subtitle, children, footer }) {
  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link to="/" className="font-display font-800 text-2xl text-white">
            Servicios<span className="text-brand-500">Bogotá</span>
          </Link>
          <p className="text-zinc-400 mt-2 text-sm">{subtitle}</p>
        </div>
        <div className="card p-6">{children}</div>
        {footer && <p className="text-center text-zinc-500 text-sm mt-4">{footer}</p>}
      </div>
    </div>
  );
}

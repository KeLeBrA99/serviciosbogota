import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center gap-4 px-4">
      <p className="text-6xl">🔍</p>
      <h1 className="font-display font-800 text-2xl text-white">Página no encontrada</h1>
      <p className="text-zinc-400 text-center">La página que buscas no existe o fue movida.</p>
      <Link to="/" className="btn-primary mt-2">Volver al inicio</Link>
    </div>
  );
}

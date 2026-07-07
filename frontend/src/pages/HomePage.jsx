import { useState, useEffect, useCallback } from "react";
import { businessAPI, categoriesAPI } from "../services/api";
import Navbar from "../components/ui/Navbar";
import BusinessCard from "../components/ui/BusinessCard";

const LOCALIDADES = [
  "Todas", "Usaquén", "Chapinero", "Santa Fe", "Bosa", "Kennedy",
  "Fontibón", "Engativá", "Suba", "Teusaquillo", "Barrios Unidos",
  "Antonio Nariño", "Puente Aranda", "Rafael Uribe Uribe", "Ciudad Bolívar",
];

export default function HomePage() {
  const [businesses, setBusinesses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [localidad, setLocalidad] = useState("");

  useEffect(() => {
    categoriesAPI.list().then(({ data }) => setCategories(data));
  }, []);

  const fetchBusinesses = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 12 };
      if (search) params.search = search;
      if (category) params.category = category;
      if (localidad && localidad !== "Todas") params.localidad = localidad;
      const { data } = await businessAPI.list(params);
      setBusinesses(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [page, search, category, localidad]);

  useEffect(() => {
    const t = setTimeout(fetchBusinesses, 300);
    return () => clearTimeout(t);
  }, [fetchBusinesses]);

  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />

      {/* Hero */}
      <div className="relative overflow-hidden bg-gradient-to-br from-zinc-900 to-zinc-950 border-b border-zinc-800 py-12 px-4">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="max-w-3xl mx-auto relative">
          <span className="inline-block bg-brand-500/10 text-brand-400 border border-brand-500/20 rounded-full text-xs font-display font-700 px-3 py-1 mb-4 tracking-widest">
            📍 BOGOTÁ · SERVICIOS LOCALES
          </span>
          <h1 className="font-display font-800 text-4xl md:text-5xl text-white leading-tight mb-3">
            Encuentra el servicio<br />
            <span className="text-brand-500">que necesitas hoy.</span>
          </h1>
          <p className="text-zinc-400 text-lg mb-8">Profesionales verificados en tu ciudad, listos para ayudarte.</p>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="🔍 Buscar servicio o negocio..."
              className="input flex-1"
            />
            <select
              value={localidad}
              onChange={(e) => { setLocalidad(e.target.value); setPage(1); }}
              className="input sm:w-44"
            >
              {LOCALIDADES.map((l) => <option key={l} value={l === "Todas" ? "" : l}>{l}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Categorías */}
        <div className="flex gap-2 overflow-x-auto pb-2 mb-6 no-scrollbar">
          <button
            onClick={() => { setCategory(""); setPage(1); }}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-display font-600 border transition-all ${
              !category ? "bg-brand-500 text-black border-brand-500" : "bg-zinc-900 text-zinc-400 border-zinc-700 hover:border-brand-500/50"
            }`}
          >
            ⚡ Todos
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => { setCategory(cat.slug); setPage(1); }}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-display font-600 border transition-all ${
                category === cat.slug ? "bg-brand-500 text-black border-brand-500" : "bg-zinc-900 text-zinc-400 border-zinc-700 hover:border-brand-500/50"
              }`}
            >
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>

        {/* Contador */}
        <p className="text-zinc-500 text-sm mb-5">{total} servicios encontrados</p>

        {/* Grid */}
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="card p-5 animate-pulse">
                <div className="flex gap-3 mb-3">
                  <div className="w-12 h-12 bg-zinc-800 rounded-lg" />
                  <div className="flex-1">
                    <div className="h-4 bg-zinc-800 rounded mb-2" />
                    <div className="h-3 bg-zinc-800 rounded w-2/3" />
                  </div>
                </div>
                <div className="h-3 bg-zinc-800 rounded mb-2" />
                <div className="h-3 bg-zinc-800 rounded w-4/5" />
              </div>
            ))}
          </div>
        ) : businesses.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-3">🔍</p>
            <p className="text-zinc-400 font-body">No encontramos resultados para tu búsqueda.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {businesses.map((b) => <BusinessCard key={b.id} business={b} />)}
          </div>
        )}

        {/* Paginación */}
        {pages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            {[...Array(pages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setPage(i + 1)}
                className={`w-9 h-9 rounded-lg font-display font-700 text-sm transition-all ${
                  page === i + 1 ? "bg-brand-500 text-black" : "bg-zinc-900 text-zinc-400 hover:bg-zinc-800"
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

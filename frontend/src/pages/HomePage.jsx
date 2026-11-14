import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { businessAPI, categoriesAPI } from "../services/api";
import BusinessCard from "../components/ui/BusinessCard";
import usePageTitle from "../hooks/usePageTitle";
import { LOCALIDADES } from "../lib/constants";
import { errorMessage } from "../lib/utils";

const PER_PAGE = 12;

function pageWindow(page, pages) {
  const set = new Set([1, pages, page - 1, page, page + 1].filter((p) => p >= 1 && p <= pages));
  const sorted = [...set].sort((a, b) => a - b);
  return sorted.flatMap((p, i) => (i > 0 && p - sorted[i - 1] > 1 ? ["…", p] : [p]));
}

export default function HomePage() {
  usePageTitle();
  // Los filtros viven en la URL: se pueden compartir y sobreviven al botón "atrás".
  const [params, setParams] = useSearchParams();
  const search = params.get("q") || "";
  const category = params.get("categoria") || "";
  const localidad = params.get("localidad") || "";
  const sort = params.get("orden") || "relevance";
  const page = Math.max(1, Number(params.get("pagina")) || 1);

  const [searchInput, setSearchInput] = useState(search);
  const [categories, setCategories] = useState([]);
  const [reload, setReload] = useState(0);
  // Cada respuesta se guarda con la consulta que la originó; mientras no
  // coincida con la consulta actual, la página está cargando.
  const queryKey = [page, search, category, localidad, sort, reload].join("|");
  const [response, setResponse] = useState({ key: null, data: null, error: "" });
  const loading = response.key !== queryKey;
  const result = response.data || { items: [], total: 0, pages: 1 };
  const error = loading ? "" : response.error;

  const setFilter = (key, value) => {
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value) next.set(key, value); else next.delete(key);
      if (key !== "pagina") next.delete("pagina");
      return next;
    }, { replace: key === "q" });
  };

  useEffect(() => {
    categoriesAPI.list().then(({ data }) => setCategories(data)).catch(() => {});
  }, []);

  // Espera a que el usuario deje de escribir antes de buscar
  useEffect(() => {
    if (searchInput === search) return;
    const t = setTimeout(() => setFilter("q", searchInput.trim()), 350);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  useEffect(() => {
    let cancelled = false;
    const query = { page, per_page: PER_PAGE, sort };
    if (search) query.search = search;
    if (category) query.category = category;
    if (localidad) query.localidad = localidad;
    businessAPI.list(query)
      .then(({ data }) => { if (!cancelled) setResponse({ key: queryKey, data, error: "" }); })
      .catch((err) => { if (!cancelled) setResponse({ key: queryKey, data: null, error: errorMessage(err) }); });
    return () => { cancelled = true; };
  }, [page, search, category, localidad, sort, queryKey]);

  const hasFilters = Boolean(search || category || localidad);
  const clearFilters = () => { setSearchInput(""); setParams({}); };

  const chip = (active) =>
    `flex-shrink-0 px-4 py-2 rounded-full text-sm font-display font-600 border transition-all ${
      active ? "bg-brand-500 text-black border-brand-500" : "bg-zinc-900 text-zinc-400 border-zinc-700 hover:border-brand-500/50"
    }`;

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-br from-zinc-900 to-zinc-950 border-b border-zinc-800 py-12 px-4">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="max-w-3xl mx-auto relative">
          <span className="inline-block bg-brand-500/10 text-brand-400 border border-brand-500/20 rounded-full text-xs font-display font-700 px-3 py-1 mb-4 tracking-widest">
            📍 BOGOTÁ · SERVICIOS LOCALES
          </span>
          <h1 className="font-display font-800 text-4xl md:text-5xl text-white leading-tight mb-3">
            Encuentra el servicio<br />
            <span className="text-brand-500">que necesitas hoy.</span>
          </h1>
          <p className="text-zinc-400 text-lg mb-8">Negocios y profesionales de tu localidad, con reseñas de otros vecinos.</p>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="search"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="🔍 ¿Qué buscas? Ej: plomero, peluquería..."
              aria-label="Buscar servicio o negocio"
              className="input flex-1"
            />
            <select value={localidad} onChange={(e) => setFilter("localidad", e.target.value)} aria-label="Localidad" className="input sm:w-48">
              <option value="">Toda Bogotá</option>
              {LOCALIDADES.map((l) => <option key={l} value={l}>{l}</option>)}
            </select>
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex gap-2 overflow-x-auto pb-2 mb-6 no-scrollbar">
          <button onClick={() => setFilter("categoria", "")} className={chip(!category)}>⚡ Todos</button>
          {categories.map((cat) => (
            <button key={cat.id} onClick={() => setFilter("categoria", cat.slug)} className={chip(category === cat.slug)}>
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between gap-3 mb-5">
          <p className="text-zinc-500 text-sm">
            {loading ? "Buscando..." : `${result.total} ${result.total === 1 ? "servicio encontrado" : "servicios encontrados"}`}
            {hasFilters && !loading && (
              <button onClick={clearFilters} className="ml-3 text-brand-400 hover:text-brand-300">Limpiar filtros</button>
            )}
          </p>
          <select value={sort} onChange={(e) => setFilter("orden", e.target.value === "relevance" ? "" : e.target.value)} aria-label="Ordenar por" className="input !w-auto !py-1.5 text-xs">
            <option value="relevance">Más relevantes</option>
            <option value="rating">Mejor calificados</option>
            <option value="recent">Más recientes</option>
          </select>
        </div>

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
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-3">⚠️</p>
            <p className="text-zinc-400 mb-4">{error}</p>
            <button onClick={() => setReload((n) => n + 1)} className="btn-outline">Reintentar</button>
          </div>
        ) : result.items.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-3">🔍</p>
            {hasFilters ? (
              <>
                <p className="text-zinc-400 mb-4">No encontramos resultados para tu búsqueda.</p>
                <button onClick={clearFilters} className="btn-outline">Ver todos los servicios</button>
              </>
            ) : (
              <>
                <p className="text-zinc-400 mb-4">Aún no hay negocios publicados. ¡Sé el primero!</p>
                <Link to="/registro" className="btn-primary">Publicar mi negocio</Link>
              </>
            )}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {result.items.map((b) => <BusinessCard key={b.id} business={b} />)}
          </div>
        )}

        {!loading && result.pages > 1 && (
          <nav className="flex justify-center items-center gap-2 mt-8" aria-label="Paginación">
            <button disabled={page <= 1} onClick={() => setFilter("pagina", String(page - 1))} className="btn-ghost !px-3">←</button>
            {pageWindow(page, result.pages).map((p, i) =>
              p === "…" ? (
                <span key={`gap-${i}`} className="text-zinc-600 px-1">…</span>
              ) : (
                <button
                  key={p}
                  onClick={() => setFilter("pagina", p === 1 ? "" : String(p))}
                  aria-current={page === p ? "page" : undefined}
                  className={`w-9 h-9 rounded-lg font-display font-700 text-sm transition-all ${
                    page === p ? "bg-brand-500 text-black" : "bg-zinc-900 text-zinc-400 hover:bg-zinc-800"
                  }`}
                >
                  {p}
                </button>
              )
            )}
            <button disabled={page >= result.pages} onClick={() => setFilter("pagina", String(page + 1))} className="btn-ghost !px-3">→</button>
          </nav>
        )}

        <section className="card mt-12 p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-5 bg-gradient-to-r from-brand-500/10 to-transparent border-brand-500/20">
          <div>
            <h2 className="font-display font-800 text-xl text-white">¿Tienes un negocio en Bogotá?</h2>
            <p className="text-zinc-400 text-sm mt-1">Publica tu perfil, recibe solicitudes de clientes y responde reseñas desde un solo lugar.</p>
          </div>
          <Link to="/registro" className="btn-primary flex-shrink-0">Publicar mi negocio</Link>
        </section>
      </div>
    </>
  );
}

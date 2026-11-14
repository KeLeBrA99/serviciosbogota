import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { adminAPI } from "../services/api";
import Badge from "../components/ui/Badge";
import Spinner from "../components/ui/Spinner";
import StarRating from "../components/ui/StarRating";
import usePageTitle from "../hooks/usePageTitle";
import { BUSINESS_STATUS, PLANS } from "../lib/constants";
import { errorMessage, formatCOP, formatDate } from "../lib/utils";

function Businesses({ onChange }) {
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);

  const load = useCallback(() => {
    const params = { page, per_page: 20 };
    if (status) params.status = status;
    if (search.trim()) params.search = search.trim();
    return adminAPI.businesses(params)
      .then(({ data }) => setData(data))
      .catch((err) => toast.error(errorMessage(err)));
  }, [page, status, search]);

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [load]);

  const act = async (request, message) => {
    try {
      await request();
      toast.success(message);
      await load();
      onChange();
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  const activatePlan = (b, plan) => {
    if (!plan) return;
    if (!window.confirm(`¿Activar el plan ${PLANS[plan].name} por 30 días para "${b.name}" sin pago en línea?`)) return;
    act(() => adminAPI.activatePlan(b.id, plan), "Plan activado");
  };

  return (
    <div>
      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <input type="search" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder="Buscar por nombre o teléfono" aria-label="Buscar negocio" className="input flex-1" />
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} aria-label="Estado" className="input sm:w-44">
          <option value="">Todos los estados</option>
          {Object.entries(BUSINESS_STATUS).map(([key, { label }]) => <option key={key} value={key}>{label}</option>)}
        </select>
      </div>

      {!data ? <Spinner /> : data.items.length === 0 ? (
        <p className="text-zinc-500 text-sm py-8 text-center">No hay negocios con esos filtros.</p>
      ) : (
        <div className="space-y-3">
          {data.items.map((b) => {
            const sub = b.subscription?.status === "active" ? b.subscription : null;
            return (
              <div key={b.id} className="p-4 bg-zinc-800/50 rounded-lg">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <Link to={`/negocio/${b.slug}`} className="font-display font-700 text-white hover:text-brand-400">{b.name}</Link>
                    <p className="text-zinc-500 text-xs mt-0.5">{b.category?.name} · {b.localidad} · {b.phone}</p>
                    <p className="text-zinc-500 text-xs">Dueño: {b.owner_name} ({b.owner_email}) · Registrado el {formatDate(b.created_at)}</p>
                    <p className="text-zinc-500 text-xs">
                      {sub ? `Plan ${PLANS[sub.plan]?.name} hasta el ${formatDate(sub.expires_at)}` : "Sin plan activo"} · 👁 {b.view_count} · 📞 {b.contact_count}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                    <Badge color={BUSINESS_STATUS[b.status]?.color}>{BUSINESS_STATUS[b.status]?.label}</Badge>
                    {b.is_featured && <Badge color="amber">Destacado</Badge>}
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2 mt-3">
                  {b.status !== "active" && <button className="btn-ghost !py-1 !px-3 !text-xs !text-green-400" onClick={() => act(() => adminAPI.approve(b.id), "Negocio aprobado")}>Aprobar</button>}
                  {b.status === "active" && <button className="btn-ghost !py-1 !px-3 !text-xs" onClick={() => act(() => adminAPI.suspend(b.id), "Negocio suspendido")}>Suspender</button>}
                  {b.status === "pending" && <button className="btn-ghost !py-1 !px-3 !text-xs !text-red-400" onClick={() => act(() => adminAPI.reject(b.id), "Negocio rechazado")}>Rechazar</button>}
                  {b.status === "active" && (
                    <button className="btn-ghost !py-1 !px-3 !text-xs" onClick={() => act(() => adminAPI.setFeatured(b.id, !b.is_featured), "Destacado actualizado")}>
                      {b.is_featured ? "Quitar destacado" : "Destacar"}
                    </button>
                  )}
                  <select value="" onChange={(e) => activatePlan(b, e.target.value)} aria-label="Activar plan manualmente" className="input !w-auto !py-1 !text-xs">
                    <option value="">Activar plan manual…</option>
                    {Object.values(PLANS).map((p) => <option key={p.key} value={p.key}>{p.name} · 30 días</option>)}
                  </select>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-3 mt-5 text-sm text-zinc-400">
          <button className="btn-ghost !px-3" disabled={page <= 1} onClick={() => setPage(page - 1)}>←</button>
          Página {data.page} de {data.pages}
          <button className="btn-ghost !px-3" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>→</button>
        </div>
      )}
    </div>
  );
}

function Reviews() {
  const [reviews, setReviews] = useState(null);

  useEffect(() => {
    adminAPI.reviews().then(({ data }) => setReviews(data)).catch((err) => { toast.error(errorMessage(err)); setReviews([]); });
  }, []);

  const toggle = async (review) => {
    try {
      await adminAPI.setReviewVisible(review.id, !review.is_approved);
      setReviews((list) => list.map((r) => (r.id === review.id ? { ...r, is_approved: !r.is_approved } : r)));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  if (!reviews) return <Spinner />;
  if (reviews.length === 0) return <p className="text-zinc-500 text-sm py-8 text-center">Aún no hay reseñas.</p>;

  return (
    <div className="space-y-3">
      {reviews.map((r) => (
        <div key={r.id} className={`p-4 rounded-lg flex items-start justify-between gap-3 ${r.is_approved ? "bg-zinc-800/50" : "bg-red-500/5 border border-red-500/20"}`}>
          <div className="min-w-0">
            <p className="text-sm text-white">
              <span className="font-display font-600">{r.author_name}</span>
              <span className="text-zinc-500"> sobre {r.business_name} · {formatDate(r.created_at)}</span>
            </p>
            <StarRating rating={r.rating} />
            {r.comment && <p className="text-zinc-300 text-sm mt-1 whitespace-pre-line break-words">{r.comment}</p>}
          </div>
          <button className="btn-ghost !py-1 !px-3 !text-xs flex-shrink-0" onClick={() => toggle(r)}>
            {r.is_approved ? "Ocultar" : "Mostrar"}
          </button>
        </div>
      ))}
    </div>
  );
}

function Users() {
  const [users, setUsers] = useState(null);

  useEffect(() => {
    adminAPI.users().then(({ data }) => setUsers(data)).catch((err) => { toast.error(errorMessage(err)); setUsers([]); });
  }, []);

  if (!users) return <Spinner />;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-zinc-500 text-xs">
          <tr><th className="py-2 pr-4 font-normal">Nombre</th><th className="py-2 pr-4 font-normal">Correo</th><th className="py-2 pr-4 font-normal">Teléfono</th><th className="py-2 pr-4 font-normal">Rol</th><th className="py-2 font-normal">Registro</th></tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-t border-zinc-800 text-zinc-300">
              <td className="py-2 pr-4 text-white">{u.full_name}</td>
              <td className="py-2 pr-4">{u.email}</td>
              <td className="py-2 pr-4">{u.phone || "—"}</td>
              <td className="py-2 pr-4">{u.role === "admin" ? <Badge>Admin</Badge> : "Dueño"}</td>
              <td className="py-2 whitespace-nowrap">{formatDate(u.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const TABS = [["businesses", "Negocios"], ["reviews", "Reseñas"], ["users", "Usuarios"]];

export default function AdminPage() {
  usePageTitle("Administración");
  const [stats, setStats] = useState(null);
  const [tab, setTab] = useState("businesses");

  const loadStats = useCallback(() => {
    adminAPI.stats().then(({ data }) => setStats(data)).catch((err) => toast.error(errorMessage(err)));
  }, []);
  useEffect(loadStats, [loadStats]);

  const cards = stats && [
    [stats.active_businesses, "Negocios activos", `${stats.pending_businesses} pendientes · ${stats.suspended_businesses} suspendidos`],
    [stats.active_subscriptions, "Planes activos", `${stats.premium_subscriptions} Premium`],
    [formatCOP(stats.monthly_revenue_cop), "Ingreso mensual", "Suma de planes activos"],
    [stats.total_users, "Usuarios", `${stats.total_contacts} solicitudes · ${stats.total_reviews} reseñas`],
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="font-display font-800 text-2xl text-white mb-6">Administración</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {(cards || [...Array(4)]).map((card, i) => (
          <div key={i} className="card p-4">
            {card ? (
              <>
                <div className="font-display font-800 text-2xl text-white">{card[0]}</div>
                <div className="text-zinc-300 text-sm mt-1">{card[1]}</div>
                <div className="text-zinc-500 text-xs mt-0.5">{card[2]}</div>
              </>
            ) : <div className="h-16 animate-pulse bg-zinc-800 rounded" />}
          </div>
        ))}
      </div>

      <section className="card p-6">
        <div className="flex gap-1 mb-5 border-b border-zinc-800 overflow-x-auto no-scrollbar">
          {TABS.map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)} className={`px-4 py-2 text-sm font-display font-600 border-b-2 -mb-px transition-colors ${tab === key ? "border-brand-500 text-white" : "border-transparent text-zinc-500 hover:text-zinc-300"}`}>
              {label}
            </button>
          ))}
        </div>
        {tab === "businesses" && <Businesses onChange={loadStats} />}
        {tab === "reviews" && <Reviews />}
        {tab === "users" && <Users />}
      </section>
    </div>
  );
}

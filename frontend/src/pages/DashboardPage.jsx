import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { businessAPI, contactAPI, reviewsAPI } from "../services/api";
import Badge from "../components/ui/Badge";
import Spinner from "../components/ui/Spinner";
import StarRating from "../components/ui/StarRating";
import usePageTitle from "../hooks/usePageTitle";
import { BUSINESS_STATUS, CONTACT_STATUS, PLANS } from "../lib/constants";
import { daysUntil, errorMessage, formatDate, telLink, whatsappLink } from "../lib/utils";

function PlanSummary({ business }) {
  const sub = business.subscription;
  const active = sub?.status === "active";
  const days = active ? daysUntil(sub.expires_at) : null;

  let text = "Sin plan activo. Con un plan tu negocio gana visibilidad en el directorio.";
  if (active) {
    text = `Plan ${PLANS[sub.plan]?.name} activo hasta el ${formatDate(sub.expires_at)}`;
    if (days !== null && days <= 5) text += ` (vence en ${Math.max(days, 0)} ${days === 1 ? "día" : "días"})`;
  } else if (sub?.status === "expired") {
    text = `Tu plan ${PLANS[sub.plan]?.name} venció el ${formatDate(sub.expires_at)}.`;
  }
  const needsAction = !active || (days !== null && days <= 5);

  return (
    <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-lg border ${needsAction ? "border-brand-500/30 bg-brand-500/5" : "border-zinc-800 bg-zinc-800/40"}`}>
      <p className="text-sm text-zinc-300">{text}</p>
      <Link to={`/planes?negocio=${business.id}`} className={`${needsAction ? "btn-primary" : "btn-ghost"} text-sm !py-1.5 flex-shrink-0`}>
        {active ? (sub.plan === "basic" ? "Renovar o mejorar" : "Renovar") : "Activar plan"}
      </Link>
    </div>
  );
}

function Contacts({ business }) {
  const [contacts, setContacts] = useState(null);

  useEffect(() => {
    contactAPI.list(business.id)
      .then(({ data }) => setContacts(data))
      .catch((err) => { toast.error(errorMessage(err)); setContacts([]); });
  }, [business.id]);

  const setStatus = async (contact, status) => {
    try {
      const { data } = await contactAPI.setStatus(business.id, contact.id, status);
      setContacts((list) => list.map((c) => (c.id === data.id ? data : c)));
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  if (!contacts) return <p className="text-zinc-500 text-sm">Cargando solicitudes...</p>;
  if (contacts.length === 0) return <p className="text-zinc-500 text-sm">Aún no has recibido solicitudes. Comparte tu perfil para empezar a recibir clientes.</p>;

  return (
    <div className="space-y-3">
      {contacts.map((c) => (
        <div key={c.id} className="p-4 bg-zinc-800/50 rounded-lg">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="font-display font-600 text-white text-sm">{c.client_name} <span className="text-zinc-500 font-body font-normal text-xs ml-1">{formatDate(c.created_at)}</span></p>
              <p className="text-zinc-300 text-sm mt-1 whitespace-pre-line break-words">{c.message}</p>
            </div>
            <Badge color={CONTACT_STATUS[c.status]?.color}>{CONTACT_STATUS[c.status]?.label || c.status}</Badge>
          </div>
          <div className="flex flex-wrap items-center gap-2 mt-3">
            {c.client_phone && (
              <>
                <a href={whatsappLink(c.client_phone, `Hola ${c.client_name}, te escribo de ${business.name}.`)} target="_blank" rel="noreferrer" onClick={() => c.status !== "replied" && setStatus(c, "replied")} className="btn-ghost !py-1 !px-3 !text-xs !text-green-400 !border-green-500/30">💬 WhatsApp</a>
                <a href={telLink(c.client_phone)} className="btn-ghost !py-1 !px-3 !text-xs">📞 {c.client_phone}</a>
              </>
            )}
            {c.client_email && <a href={`mailto:${c.client_email}`} className="btn-ghost !py-1 !px-3 !text-xs">✉️ {c.client_email}</a>}
            {c.status === "new" && <button onClick={() => setStatus(c, "seen")} className="text-zinc-400 hover:text-white text-xs ml-auto">Marcar como visto</button>}
            {c.status !== "replied" && <button onClick={() => setStatus(c, "replied")} className={`text-zinc-400 hover:text-white text-xs ${c.status === "new" ? "" : "ml-auto"}`}>Marcar como respondido</button>}
          </div>
        </div>
      ))}
    </div>
  );
}

function Reviews({ business }) {
  const [reviews, setReviews] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    reviewsAPI.list(business.id)
      .then(({ data }) => setReviews(data))
      .catch((err) => { toast.error(errorMessage(err)); setReviews([]); });
  }, [business.id]);

  const respond = async (review) => {
    try {
      const { data } = await reviewsAPI.respond(business.id, review.id, drafts[review.id] ?? review.response ?? "");
      setReviews((list) => list.map((r) => (r.id === data.id ? data : r)));
      setEditing(null);
      toast.success("Respuesta publicada");
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  if (!reviews) return <p className="text-zinc-500 text-sm">Cargando reseñas...</p>;
  if (reviews.length === 0) return <p className="text-zinc-500 text-sm">Aún no tienes reseñas. Pídele a tus clientes que te califiquen desde tu perfil público.</p>;

  return (
    <div className="space-y-3">
      {reviews.map((r) => (
        <div key={r.id} className="p-4 bg-zinc-800/50 rounded-lg">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-display font-600 text-white text-sm">{r.author_name}</span>
            <StarRating rating={r.rating} />
            <span className="text-zinc-500 text-xs">{formatDate(r.created_at)}</span>
          </div>
          {r.comment && <p className="text-zinc-300 text-sm mt-1 whitespace-pre-line">{r.comment}</p>}
          {editing === r.id ? (
            <div className="mt-3 space-y-2">
              <textarea autoFocus value={drafts[r.id] ?? r.response ?? ""} onChange={(e) => setDrafts({ ...drafts, [r.id]: e.target.value })} placeholder="Escribe una respuesta pública..." className="input h-20 resize-none" maxLength={2000} />
              <div className="flex gap-2">
                <button onClick={() => respond(r)} className="btn-primary text-sm !py-1.5">Publicar</button>
                <button onClick={() => setEditing(null)} className="btn-ghost">Cancelar</button>
              </div>
            </div>
          ) : (
            <>
              {r.response && <p className="text-zinc-400 text-sm mt-2 pl-3 border-l-2 border-brand-500/40 whitespace-pre-line">{r.response}</p>}
              <button onClick={() => setEditing(r.id)} className="text-brand-400 hover:text-brand-300 text-xs mt-2">
                {r.response ? "Editar respuesta" : "Responder"}
              </button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  usePageTitle("Mi negocio");
  const [businesses, setBusinesses] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [tab, setTab] = useState("contacts");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    businessAPI.myBusinesses()
      .then(({ data }) => { setBusinesses(data); setSelectedId(data[0]?.id ?? null); })
      .catch((err) => toast.error(errorMessage(err, "Error cargando datos")))
      .finally(() => setLoading(false));
  }, []);

  const business = businesses.find((b) => b.id === selectedId);

  const toggleOpen = async () => {
    try {
      const { data } = await businessAPI.update(business.id, { is_open_now: !business.is_open_now });
      setBusinesses((list) => list.map((b) => (b.id === data.id ? data : b)));
      toast.success(data.is_open_now ? "Tu negocio aparece como abierto" : "Tu negocio aparece como cerrado");
    } catch (err) {
      toast.error(errorMessage(err));
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display font-800 text-2xl text-white">Mi negocio</h1>
          <p className="text-zinc-500 text-sm mt-1">Gestiona tu presencia en ServiciosBogotá</p>
        </div>
        <Link to="/registrar-negocio" className="btn-ghost flex-shrink-0">+ Nuevo negocio</Link>
      </div>

      {!business ? (
        <div className="card p-12 text-center">
          <p className="text-4xl mb-4">🏪</p>
          <h2 className="font-display font-700 text-white text-lg mb-2">Aún no tienes negocios registrados</h2>
          <p className="text-zinc-400 text-sm mb-6">Registra tu negocio y empieza a recibir clientes hoy.</p>
          <Link to="/registrar-negocio" className="btn-primary">Registrar mi negocio</Link>
        </div>
      ) : (
        <div className="space-y-5">
          {businesses.length > 1 && (
            <div className="flex gap-2 overflow-x-auto no-scrollbar">
              {businesses.map((b) => (
                <button key={b.id} onClick={() => setSelectedId(b.id)} className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm border transition-all ${b.id === selectedId ? "bg-brand-500 text-black border-brand-500 font-bold" : "bg-zinc-900 text-zinc-400 border-zinc-700 hover:border-zinc-500"}`}>
                  {b.name}
                </button>
              ))}
            </div>
          )}

          <section className="card p-6 space-y-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="font-display font-700 text-white text-lg truncate">{business.name}</h2>
                <p className="text-zinc-500 text-sm">📍 {business.localidad} · {business.category?.name}</p>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <Badge color={BUSINESS_STATUS[business.status]?.color}>{BUSINESS_STATUS[business.status]?.label}</Badge>
                {business.subscription?.status === "active" && (
                  <Badge color={business.subscription.plan === "premium" ? "amber" : "gray"}>{PLANS[business.subscription.plan]?.name.toUpperCase()}</Badge>
                )}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 p-4 bg-zinc-800/50 rounded-lg">
              {[
                ["👁", business.view_count, "Visitas al perfil"],
                ["📞", business.contact_count, "Solicitudes"],
                ["⭐", business.rating_count > 0 ? business.rating_avg.toFixed(1) : "—", `${business.rating_count} ${business.rating_count === 1 ? "reseña" : "reseñas"}`],
              ].map(([icon, val, label]) => (
                <div key={label} className="text-center">
                  <div className="text-lg mb-0.5">{icon}</div>
                  <div className="font-display font-700 text-white text-xl">{val}</div>
                  <div className="text-zinc-500 text-xs">{label}</div>
                </div>
              ))}
            </div>

            <PlanSummary business={business} />

            <div className="flex flex-wrap gap-2">
              <Link to={`/negocio/${business.slug}`} className="btn-outline text-sm !py-1.5">Ver perfil público</Link>
              <Link to={`/negocio/${business.id}/editar`} className="btn-ghost">✏️ Editar información y fotos</Link>
              <button onClick={toggleOpen} className="btn-ghost">
                {business.is_open_now ? "🔴 Marcar como cerrado" : "🟢 Marcar como abierto"}
              </button>
            </div>
          </section>

          <section className="card p-6">
            <div className="flex gap-1 mb-5 border-b border-zinc-800">
              {[["contacts", "Solicitudes de clientes"], ["reviews", "Reseñas"]].map(([key, label]) => (
                <button key={key} onClick={() => setTab(key)} className={`px-4 py-2 text-sm font-display font-600 border-b-2 -mb-px transition-colors ${tab === key ? "border-brand-500 text-white" : "border-transparent text-zinc-500 hover:text-zinc-300"}`}>
                  {label}
                </button>
              ))}
            </div>
            {/* key: al cambiar de negocio el panel se monta de nuevo y recarga sus datos */}
            {tab === "contacts" ? <Contacts key={business.id} business={business} /> : <Reviews key={business.id} business={business} />}
          </section>
        </div>
      )}
    </div>
  );
}

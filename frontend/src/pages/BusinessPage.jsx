import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { businessAPI, contactAPI, reviewsAPI } from "../services/api";
import useAuthStore from "../store/authStore";
import StarRating from "../components/ui/StarRating";
import Badge from "../components/ui/Badge";
import Spinner from "../components/ui/Spinner";
import usePageTitle from "../hooks/usePageTitle";
import { BUSINESS_STATUS, DAYS } from "../lib/constants";
import { errorMessage, formatDate, isOpenNow, telLink, whatsappLink } from "../lib/utils";

const EMPTY_CONTACT = { client_name: "", client_phone: "", message: "" };
const EMPTY_REVIEW = { author_name: "", rating: 5, comment: "" };

export default function BusinessPage() {
  const { slug } = useParams();
  // key: al navegar a otro negocio la página se monta de nuevo con estado limpio
  return <BusinessDetail key={slug} slug={slug} />;
}

function BusinessDetail({ slug }) {
  const user = useAuthStore((s) => s.user);
  const [business, setBusiness] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [photo, setPhoto] = useState(null);
  const [contactForm, setContactForm] = useState(EMPTY_CONTACT);
  const [reviewForm, setReviewForm] = useState(EMPTY_REVIEW);
  const [sending, setSending] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  usePageTitle(business ? `${business.name} en ${business.localidad}` : undefined);

  useEffect(() => {
    let cancelled = false;
    businessAPI.getBySlug(slug)
      .then(({ data }) => {
        if (cancelled) return null;
        setBusiness(data);
        return reviewsAPI.list(data.id);
      })
      .then((res) => { if (res && !cancelled) setReviews(res.data); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [slug]);

  const sendContact = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await contactAPI.send(business.id, contactForm);
      toast.success("¡Mensaje enviado! El negocio te contactará pronto.");
      setContactForm(EMPTY_CONTACT);
    } catch (err) {
      toast.error(errorMessage(err, "Error al enviar el mensaje"));
    } finally {
      setSending(false);
    }
  };

  const sendReview = async (e) => {
    e.preventDefault();
    setReviewing(true);
    try {
      const { data } = await reviewsAPI.create(business.id, reviewForm);
      const next = [data, ...reviews];
      setReviews(next);
      setBusiness((b) => ({
        ...b,
        rating_count: next.length,
        rating_avg: Math.round((next.reduce((sum, r) => sum + r.rating, 0) / next.length) * 10) / 10,
      }));
      toast.success("¡Reseña publicada!");
      setReviewForm(EMPTY_REVIEW);
    } catch (err) {
      toast.error(errorMessage(err, "Error al publicar la reseña"));
    } finally {
      setReviewing(false);
    }
  };

  const share = async () => {
    const data = { title: business.name, text: `${business.name} en ServiciosBogotá`, url: window.location.href };
    try {
      if (navigator.share) await navigator.share(data);
      else {
        await navigator.clipboard.writeText(data.url);
        toast.success("Enlace copiado");
      }
    } catch {
      // el usuario canceló el diálogo de compartir
    }
  };

  if (loading) return <Spinner />;

  if (!business) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24 px-4">
        <p className="text-5xl">🏪</p>
        <p className="text-zinc-400">No encontramos este negocio.</p>
        <Link to="/" className="btn-primary">Volver al inicio</Link>
      </div>
    );
  }

  const open = isOpenNow(business);
  const isPremium = business.subscription?.plan === "premium" && business.subscription?.status === "active";
  const isOwner = user && business.status !== "active"; // solo el dueño o un admin ven un negocio no activo
  const location = [business.address, business.neighborhood, business.localidad].filter(Boolean).join(", ");
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${location}, Bogotá`)}`;

  return (
    <>
      {business.cover_url && (
        <div className="h-48 relative">
          <img src={business.cover_url} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/80 to-transparent" />
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-8">
        {isOwner && (
          <div className="card border-brand-500/30 bg-brand-500/5 p-4 mb-5 text-sm text-zinc-300">
            Este negocio está <strong>{BUSINESS_STATUS[business.status]?.label.toLowerCase()}</strong> y no es visible para el público.
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1 min-w-0 space-y-5">
            <section className="card p-6">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-zinc-800 flex items-center justify-center text-3xl flex-shrink-0 border border-zinc-700 overflow-hidden">
                  {business.logo_url
                    ? <img src={business.logo_url} alt={`Logo de ${business.name}`} className="w-full h-full object-cover" />
                    : business.category?.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h1 className="font-display font-800 text-2xl text-white break-words">{business.name}</h1>
                    {isPremium && <span className="bg-brand-500 text-black text-xs font-bold px-2 py-0.5 rounded">PREMIUM</span>}
                    <Badge color={open ? "green" : "red"}>{open ? "Abierto" : "Cerrado"}</Badge>
                  </div>
                  <p className="text-zinc-500 text-sm mt-1">
                    📍 {business.localidad} ·{" "}
                    <Link to={`/?categoria=${business.category?.slug}`} className="hover:text-brand-400">{business.category?.name}</Link>
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <StarRating rating={business.rating_avg} size="lg" />
                    <span className="text-zinc-400 text-sm">
                      {business.rating_count > 0
                        ? `${business.rating_avg.toFixed(1)} (${business.rating_count} ${business.rating_count === 1 ? "reseña" : "reseñas"})`
                        : "Sin reseñas todavía"}
                    </span>
                  </div>
                </div>
                <button onClick={share} className="btn-ghost !px-3 flex-shrink-0" aria-label="Compartir">↗ <span className="hidden sm:inline">Compartir</span></button>
              </div>

              <p className="text-zinc-300 leading-relaxed whitespace-pre-line mb-4">{business.description}</p>

              {business.tags?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {business.tags.map((tag) => <Badge key={tag} color="gray">{tag}</Badge>)}
                </div>
              )}
            </section>

            {business.photos?.length > 0 && (
              <section className="card p-6">
                <h2 className="font-semibold text-white text-lg mb-4">Fotos</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {business.photos.map((url, i) => (
                    <button key={url} onClick={() => setPhoto(url)} className="aspect-square rounded-lg overflow-hidden">
                      <img src={url} alt={`Foto ${i + 1} de ${business.name}`} loading="lazy" className="w-full h-full object-cover hover:scale-105 transition-transform duration-300" />
                    </button>
                  ))}
                </div>
              </section>
            )}

            <section className="card p-6">
              <h2 className="font-semibold text-white text-lg mb-4">Reseñas</h2>
              {reviews.length === 0 ? (
                <p className="text-zinc-500 text-sm">Aún no hay reseñas. ¡Sé el primero en opinar!</p>
              ) : (
                <div className="space-y-4">
                  {reviews.map((r) => (
                    <div key={r.id} className="border-b border-zinc-800 pb-4 last:border-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="font-semibold text-white text-sm">{r.author_name}</span>
                        <StarRating rating={r.rating} />
                        <span className="text-zinc-600 text-xs">{formatDate(r.created_at)}</span>
                      </div>
                      {r.comment && <p className="text-zinc-400 text-sm whitespace-pre-line">{r.comment}</p>}
                      {r.response && (
                        <div className="mt-2 ml-3 pl-3 border-l-2 border-brand-500/40">
                          <p className="text-brand-400 text-xs font-semibold mb-0.5">Respuesta de {business.name}</p>
                          <p className="text-zinc-400 text-sm whitespace-pre-line">{r.response}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {business.status === "active" && (
                <form onSubmit={sendReview} className="mt-5 pt-5 border-t border-zinc-800 space-y-3">
                  <h3 className="font-semibold text-white text-sm">Dejar una reseña</h3>
                  <div className="flex items-center gap-3">
                    <StarRating rating={reviewForm.rating} size="xl" onChange={(rating) => setReviewForm({ ...reviewForm, rating })} />
                    <span className="text-zinc-500 text-sm">{reviewForm.rating} de 5</span>
                  </div>
                  <input value={reviewForm.author_name} onChange={(e) => setReviewForm({ ...reviewForm, author_name: e.target.value })} placeholder="Tu nombre" aria-label="Tu nombre" className="input" required minLength={2} maxLength={100} />
                  <textarea value={reviewForm.comment} onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })} placeholder="Cuéntanos cómo te fue (opcional)" aria-label="Comentario" className="input h-20 resize-none" maxLength={2000} />
                  <button type="submit" disabled={reviewing} className="btn-primary w-full">
                    {reviewing ? "Publicando..." : "Publicar reseña"}
                  </button>
                </form>
              )}
            </section>
          </div>

          <aside className="md:w-72 flex-shrink-0 space-y-4">
            <section className="card p-5">
              <h2 className="font-semibold text-white mb-4">Contactar</h2>
              <div className="space-y-2 mb-4">
                {business.whatsapp && (
                  <a
                    href={whatsappLink(business.whatsapp, `Hola, vi ${business.name} en ServiciosBogotá y quisiera más información.`)}
                    target="_blank" rel="noreferrer"
                    onClick={() => businessAPI.track(business.id, "whatsapp")}
                    className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 text-white font-semibold text-sm rounded-lg py-2.5 transition-colors"
                  >
                    💬 Escribir por WhatsApp
                  </a>
                )}
                <a href={telLink(business.phone)} onClick={() => businessAPI.track(business.id, "call")} className="btn-outline w-full text-sm">📞 {business.phone}</a>
              </div>
              <div className="space-y-2 text-sm">
                {business.email && (
                  <a href={`mailto:${business.email}`} className="flex items-center gap-2 text-zinc-300 hover:text-brand-400 transition-colors break-all">✉️ {business.email}</a>
                )}
                {business.website && (
                  <a href={business.website} target="_blank" rel="noreferrer nofollow" className="flex items-center gap-2 text-zinc-300 hover:text-brand-400 transition-colors break-all">
                    🌐 {business.website.replace(/^https?:\/\//, "").replace(/\/$/, "")}
                  </a>
                )}
                <a href={mapsUrl} target="_blank" rel="noreferrer" className="flex items-start gap-2 text-zinc-300 hover:text-brand-400 transition-colors">
                  <span>📍</span><span>{location}</span>
                </a>
              </div>

              {business.status === "active" && (
                <form onSubmit={sendContact} className="space-y-3 pt-4 mt-4 border-t border-zinc-800">
                  <p className="text-zinc-400 text-xs">O déjale tus datos para que te contacte:</p>
                  <input value={contactForm.client_name} onChange={(e) => setContactForm({ ...contactForm, client_name: e.target.value })} placeholder="Tu nombre" aria-label="Tu nombre" className="input" required minLength={2} />
                  <input type="tel" value={contactForm.client_phone} onChange={(e) => setContactForm({ ...contactForm, client_phone: e.target.value })} placeholder="Tu teléfono" aria-label="Tu teléfono" className="input" required minLength={7} />
                  <textarea value={contactForm.message} onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })} placeholder="¿Qué necesitas?" aria-label="Mensaje" className="input h-20 resize-none" required minLength={5} />
                  <button type="submit" disabled={sending} className="btn-primary w-full">
                    {sending ? "Enviando..." : "Enviar mensaje"}
                  </button>
                </form>
              )}
            </section>

            {business.schedule && (
              <section className="card p-5">
                <h2 className="font-semibold text-white mb-3">Horario</h2>
                <dl className="space-y-1.5 text-sm">
                  {DAYS.map(({ key, label }) => {
                    const day = business.schedule[key];
                    return (
                      <div key={key} className="flex justify-between">
                        <dt className="text-zinc-400">{label}</dt>
                        <dd className={!day || day.closed ? "text-zinc-600" : "text-zinc-200"}>
                          {!day || day.closed ? "Cerrado" : `${day.open} – ${day.close}`}
                        </dd>
                      </div>
                    );
                  })}
                </dl>
              </section>
            )}
          </aside>
        </div>
      </div>

      {photo && (
        <div className="fixed inset-0 z-[60] bg-black/90 flex items-center justify-center p-4" onClick={() => setPhoto(null)} role="dialog" aria-label="Foto ampliada">
          <img src={photo} alt="" className="max-w-full max-h-full rounded-lg" />
          <button className="absolute top-4 right-4 text-white text-2xl" aria-label="Cerrar">✕</button>
        </div>
      )}
    </>
  );
}

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { businessAPI, reviewsAPI, contactAPI } from "../services/api";
import Navbar from "../components/ui/Navbar";
import StarRating from "../components/ui/StarRating";
import Badge from "../components/ui/Badge";
import toast from "react-hot-toast";

export default function BusinessPage() {
  const { slug } = useParams();
  const [business, setBusiness] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [contactForm, setContactForm] = useState({ client_name: "", client_phone: "", message: "" });
  const [reviewForm, setReviewForm] = useState({ author_name: "", rating: 5, comment: "" });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    Promise.all([
      businessAPI.getBySlug(slug),
    ]).then(([{ data }]) => {
      setBusiness(data);
      return reviewsAPI.list(data.id);
    }).then(({ data }) => {
      setReviews(data);
    }).catch(() => {
      toast.error("Negocio no encontrado");
    }).finally(() => setLoading(false));
  }, [slug]);

  const sendContact = async (e) => {
    e.preventDefault();
    setSending(true);
    try {
      await contactAPI.send(business.id, contactForm);
      toast.success("¡Mensaje enviado! El negocio te contactará pronto.");
      setContactForm({ client_name: "", client_phone: "", message: "" });
    } catch {
      toast.error("Error al enviar el mensaje");
    } finally {
      setSending(false);
    }
  };

  const sendReview = async (e) => {
    e.preventDefault();
    try {
      const { data } = await reviewsAPI.create(business.id, reviewForm);
      setReviews([data, ...reviews]);
      toast.success("¡Reseña publicada!");
      setReviewForm({ author_name: "", rating: 5, comment: "" });
    } catch {
      toast.error("Error al publicar la reseña");
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
      <div className="text-zinc-400">Cargando...</div>
    </div>
  );

  if (!business) return (
    <div className="min-h-screen bg-zinc-950 flex flex-col items-center justify-center gap-4">
      <p className="text-zinc-400">Negocio no encontrado</p>
      <Link to="/" className="btn-primary">Volver al inicio</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />

      {/* Cover solo si tiene imagen */}
      {business.cover_url && (
        <div className="h-48 relative">
          <img src={business.cover_url} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-zinc-950/80 to-transparent" />
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-8 pb-16">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Main */}
          <div className="flex-1">
            <div className="card p-6 mb-5">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-zinc-800 flex items-center justify-center text-3xl flex-shrink-0 border border-zinc-700">
                  {business.logo_url
                    ? <img src={business.logo_url} className="w-full h-full rounded-xl object-cover" />
                    : business.category?.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h1 className="font-display font-800 text-2xl text-white">{business.name}</h1>
                    {business.subscription?.plan === "premium" && (
                      <span className="bg-amber-500 text-black text-xs font-bold px-2 py-0.5 rounded">PREMIUM</span>
                    )}
                    <Badge color={business.is_open_now ? "green" : "red"}>
                      {business.is_open_now ? "Abierto" : "Cerrado"}
                    </Badge>
                  </div>
                  <p className="text-zinc-500 text-sm mt-1">📍 {business.localidad} · {business.category?.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <StarRating rating={business.rating_avg} size="lg" />
                    <span className="text-zinc-400 text-sm">{business.rating_avg.toFixed(1)} ({business.rating_count} reseñas)</span>
                  </div>
                </div>
              </div>

              <p className="text-zinc-300 leading-relaxed mb-4">{business.description}</p>

              <div className="flex flex-wrap gap-2">
                {business.tags?.map((tag) => <Badge key={tag} color="gray">{tag}</Badge>)}
              </div>
            </div>

            {/* Reseñas */}
            <div className="card p-6 mb-5">
              <h2 className="font-semibold text-white text-lg mb-4">Reseñas</h2>
              {reviews.length === 0 ? (
                <p className="text-zinc-500 text-sm">Aún no hay reseñas. ¡Sé el primero!</p>
              ) : (
                <div className="space-y-4">
                  {reviews.map((r) => (
                    <div key={r.id} className="border-b border-zinc-800 pb-4 last:border-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-white text-sm">{r.author_name}</span>
                        <StarRating rating={r.rating} />
                      </div>
                      {r.comment && <p className="text-zinc-400 text-sm">{r.comment}</p>}
                    </div>
                  ))}
                </div>
              )}

              <form onSubmit={sendReview} className="mt-5 pt-5 border-t border-zinc-800 space-y-3">
                <h3 className="font-semibold text-white text-sm">Dejar una reseña</h3>
                <input value={reviewForm.author_name} onChange={(e) => setReviewForm({ ...reviewForm, author_name: e.target.value })} placeholder="Tu nombre" className="input" required />
                <select value={reviewForm.rating} onChange={(e) => setReviewForm({ ...reviewForm, rating: Number(e.target.value) })} className="input">
                  {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{"★".repeat(n)} {n} estrellas</option>)}
                </select>
                <textarea value={reviewForm.comment} onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })} placeholder="Tu comentario (opcional)" className="input h-20 resize-none" />
                <button type="submit" className="btn-primary w-full">Publicar reseña</button>
              </form>
            </div>
          </div>

          {/* Sidebar contacto */}
          <div className="md:w-72 space-y-4">
            <div className="card p-5">
              <h2 className="font-semibold text-white mb-4">Contactar</h2>
              <div className="space-y-3 mb-4">
                <a href={`tel:${business.phone}`} className="flex items-center gap-2 text-sm text-zinc-300 hover:text-amber-400 transition-colors">
                  📞 {business.phone}
                </a>
                {business.whatsapp && (
                  <a href={`https://wa.me/57${business.whatsapp}`} target="_blank" rel="noreferrer" className="flex items-center gap-2 text-sm text-green-400 hover:text-green-300 transition-colors">
                    💬 WhatsApp
                  </a>
                )}
                {business.email && (
                  <a href={`mailto:${business.email}`} className="flex items-center gap-2 text-sm text-zinc-300 hover:text-amber-400 transition-colors">
                    ✉️ {business.email}
                  </a>
                )}
              </div>

              <form onSubmit={sendContact} className="space-y-3 pt-4 border-t border-zinc-800">
                <p className="text-zinc-400 text-xs">O envíale un mensaje directo:</p>
                <input value={contactForm.client_name} onChange={(e) => setContactForm({ ...contactForm, client_name: e.target.value })} placeholder="Tu nombre" className="input" required />
                <input value={contactForm.client_phone} onChange={(e) => setContactForm({ ...contactForm, client_phone: e.target.value })} placeholder="Tu teléfono" className="input" />
                <textarea value={contactForm.message} onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })} placeholder="¿En qué te puede ayudar?" className="input h-20 resize-none" required />
                <button type="submit" disabled={sending} className="btn-primary w-full disabled:opacity-50">
                  {sending ? "Enviando..." : "Enviar mensaje"}
                </button>
              </form>
            </div>

            {/* Stats */}
            <div className="card p-5 grid grid-cols-2 gap-3">
              {[
                ["👁", business.view_count, "Visitas"],
                ["📞", business.contact_count, "Contactos"],
              ].map(([icon, val, label]) => (
                <div key={label} className="text-center">
                  <div className="text-xl mb-1">{icon}</div>
                  <div className="font-bold text-white text-lg">{val}</div>
                  <div className="text-zinc-500 text-xs">{label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
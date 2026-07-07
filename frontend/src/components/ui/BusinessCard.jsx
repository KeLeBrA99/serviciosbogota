import { Link } from "react-router-dom";
import StarRating from "./StarRating";
import Badge from "./Badge";

export default function BusinessCard({ business }) {
  const isPremium = business.subscription?.plan === "premium";

  return (
    <Link to={`/negocio/${business.slug}`} className="block">
      <div className={`card p-5 hover:border-brand-500/40 hover:-translate-y-0.5 transition-all duration-200 hover:shadow-lg hover:shadow-brand-500/10 relative overflow-hidden`}>
        {isPremium && (
          <div className="absolute top-0 right-0 bg-brand-500 text-black text-xs font-display font-800 px-3 py-0.5 rounded-bl-lg tracking-wider">
            PREMIUM
          </div>
        )}
        <div className="flex items-start gap-3 mb-3">
          {business.logo_url ? (
            <img src={business.logo_url} alt={business.name} className="w-12 h-12 rounded-lg object-cover flex-shrink-0" />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center text-xl flex-shrink-0">
              {business.category?.icon}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-display font-700 text-white text-base leading-tight truncate">{business.name}</h3>
            <p className="text-zinc-500 text-xs mt-0.5">📍 {business.localidad} · {business.category?.name}</p>
          </div>
          <Badge color={business.is_open_now ? "green" : "red"}>
            {business.is_open_now ? "Abierto" : "Cerrado"}
          </Badge>
        </div>

        {business.short_description && (
          <p className="text-zinc-400 text-sm leading-relaxed mb-3 line-clamp-2">{business.short_description}</p>
        )}

        <div className="flex flex-wrap gap-1.5 mb-3">
          {business.tags?.slice(0, 3).map((tag) => (
            <Badge key={tag} color="gray">{tag}</Badge>
          ))}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <StarRating rating={business.rating_avg} />
            <span className="text-zinc-500 text-xs">{business.rating_count} reseñas</span>
          </div>
          <span className="text-brand-500 font-display font-700 text-sm">{business.phone}</span>
        </div>
      </div>
    </Link>
  );
}

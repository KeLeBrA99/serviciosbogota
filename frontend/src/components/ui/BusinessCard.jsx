import { Link } from "react-router-dom";
import StarRating from "./StarRating";
import Badge from "./Badge";
import { isOpenNow } from "../../lib/utils";

export default function BusinessCard({ business }) {
  const isPremium = business.subscription?.plan === "premium" && business.subscription?.status === "active";
  const open = isOpenNow(business);

  return (
    <Link to={`/negocio/${business.slug}`} className="block h-full rounded-xl">
      <article className={`card h-full p-5 hover:border-brand-500/40 hover:-translate-y-0.5 transition-all duration-200 hover:shadow-lg hover:shadow-brand-500/10 relative overflow-hidden flex flex-col ${isPremium ? "border-brand-500/30" : ""}`}>
        {isPremium && (
          <div className="absolute top-0 right-0 bg-brand-500 text-black text-[10px] font-display font-800 px-3 py-0.5 rounded-bl-lg tracking-wider">
            PREMIUM
          </div>
        )}
        <div className={`flex items-start gap-3 mb-3 ${isPremium ? "mt-2" : ""}`}>
          {business.logo_url ? (
            <img src={business.logo_url} alt="" loading="lazy" className="w-12 h-12 rounded-lg object-cover flex-shrink-0" />
          ) : (
            <div className="w-12 h-12 rounded-lg bg-zinc-800 flex items-center justify-center text-xl flex-shrink-0">
              {business.category?.icon}
            </div>
          )}
          <div className="flex-1 min-w-0">
            <h3 className="font-display font-700 text-white text-base leading-tight truncate">{business.name}</h3>
            <p className="text-zinc-500 text-xs mt-0.5 truncate">📍 {business.localidad} · {business.category?.name}</p>
          </div>
          <Badge color={open ? "green" : "red"}>{open ? "Abierto" : "Cerrado"}</Badge>
        </div>

        {business.short_description && (
          <p className="text-zinc-400 text-sm leading-relaxed mb-3 line-clamp-2">{business.short_description}</p>
        )}

        {business.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {business.tags.slice(0, 3).map((tag) => <Badge key={tag} color="gray">{tag}</Badge>)}
          </div>
        )}

        <div className="flex items-center justify-between mt-auto pt-1">
          <div className="flex items-center gap-2">
            <StarRating rating={business.rating_avg} />
            <span className="text-zinc-500 text-xs">
              {business.rating_count > 0
                ? `${business.rating_avg.toFixed(1)} (${business.rating_count})`
                : "Sin reseñas"}
            </span>
          </div>
          <span className="text-brand-500 font-display font-700 text-sm">{business.phone}</span>
        </div>
      </article>
    </Link>
  );
}

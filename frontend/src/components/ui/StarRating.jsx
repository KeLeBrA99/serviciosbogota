export default function StarRating({ rating, size = "sm" }) {
  const stars = [];
  for (let i = 1; i <= 5; i++) {
    stars.push(
      <span key={i} className={`${i <= Math.round(rating) ? "text-brand-500" : "text-zinc-600"} ${size === "lg" ? "text-xl" : "text-sm"}`}>
        ★
      </span>
    );
  }
  return <span className="inline-flex gap-0.5">{stars}</span>;
}

/** Estrellas de solo lectura, o seleccionables si se pasa onChange. */
export default function StarRating({ rating = 0, size = "sm", onChange }) {
  const sizeClass = size === "lg" ? "text-xl" : size === "xl" ? "text-3xl" : "text-sm";
  const stars = [1, 2, 3, 4, 5].map((i) => {
    const className = `${i <= Math.round(rating) ? "text-brand-500" : "text-zinc-600"} ${sizeClass}`;
    return onChange ? (
      <button
        key={i}
        type="button"
        onClick={() => onChange(i)}
        aria-label={`${i} ${i === 1 ? "estrella" : "estrellas"}`}
        className={`${className} hover:scale-110 transition-transform`}
      >
        ★
      </button>
    ) : (
      <span key={i} className={className} aria-hidden="true">★</span>
    );
  });
  return (
    <span className="inline-flex gap-0.5" role={onChange ? "radiogroup" : "img"} aria-label={`Calificación: ${rating} de 5`}>
      {stars}
    </span>
  );
}

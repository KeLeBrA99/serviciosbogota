export default function Spinner({ label = "Cargando..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-20" role="status">
      <div className="w-8 h-8 border-2 border-zinc-700 border-t-brand-500 rounded-full animate-spin" />
      <p className="text-zinc-500 text-sm">{label}</p>
    </div>
  );
}

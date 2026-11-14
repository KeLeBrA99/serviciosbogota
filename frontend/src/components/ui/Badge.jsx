const COLORS = {
  amber: "bg-brand-500/10 text-brand-400 border-brand-500/20",
  green: "bg-green-500/10 text-green-400 border-green-500/20",
  red: "bg-red-500/10 text-red-400 border-red-500/20",
  gray: "bg-zinc-700/30 text-zinc-400 border-zinc-600/20",
  blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export default function Badge({ children, color = "amber" }) {
  return (
    <span className={`inline-block whitespace-nowrap border rounded text-xs font-display font-600 px-2 py-0.5 ${COLORS[color] || COLORS.gray}`}>
      {children}
    </span>
  );
}

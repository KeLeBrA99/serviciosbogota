import { Link } from "react-router-dom";
import Navbar from "../components/ui/Navbar";

const plans = [
  {
    name: "Básico", price: "$25.000", period: "/mes", color: "border-zinc-700",
    badge: null,
    features: [
      "✅ Perfil en el directorio",
      "✅ Hasta 3 fotos",
      "✅ Teléfono visible",
      "✅ Horarios de atención",
      "✅ Botón de WhatsApp",
      "❌ Posición destacada",
      "❌ Estadísticas",
      "❌ Agenda online",
    ],
    cta: "Comenzar básico", ctaStyle: "btn-outline",
  },
  {
    name: "Premium", price: "$65.000", period: "/mes", color: "border-brand-500",
    badge: "MÁS POPULAR",
    features: [
      "✅ Todo lo del Básico",
      "✅ Posición destacada en resultados",
      "✅ Hasta 10 fotos",
      "✅ Badge PREMIUM visible",
      "✅ Estadísticas de visitas",
      "✅ Agenda online de citas",
      "✅ Soporte prioritario",
      "✅ Aparece en home destacado",
    ],
    cta: "Comenzar Premium", ctaStyle: "btn-primary",
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="font-display font-800 text-4xl text-white mb-3">
            Planes simples, <span className="text-brand-500">resultados reales</span>
          </h1>
          <p className="text-zinc-400">Sin contratos. Cancela cuando quieras.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {plans.map((plan) => (
            <div key={plan.name} className={`card p-7 border-2 ${plan.color} relative`}>
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-brand-500 text-black text-xs font-display font-800 px-4 py-1 rounded-full tracking-wider">
                  {plan.badge}
                </div>
              )}
              <h2 className="font-display font-800 text-xl text-white mb-2">{plan.name}</h2>
              <div className="mb-6">
                <span className="font-display font-800 text-4xl text-white">{plan.price}</span>
                <span className="text-zinc-500 text-sm">{plan.period}</span>
              </div>
              <ul className="space-y-2.5 mb-7">
                {plan.features.map((f) => (
                  <li key={f} className="text-zinc-300 text-sm font-body">{f}</li>
                ))}
              </ul>
              <Link to="/registro" className={`${plan.ctaStyle} block text-center w-full`}>
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="card p-6 grid grid-cols-3 gap-6 text-center">
          {[["180+", "Negocios activos"], ["2.400+", "Búsquedas/día"], ["4.8★", "Calificación media"]].map(([num, label]) => (
            <div key={label}>
              <div className="font-display font-800 text-2xl text-brand-500">{num}</div>
              <div className="text-zinc-500 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>

        <p className="text-center text-zinc-500 text-sm mt-8">
          ¿Tienes preguntas?{" "}
          <a href="mailto:hola@serviciosbogota.co" className="text-brand-400 hover:text-brand-300">
            hola@serviciosbogota.co
          </a>
        </p>
      </div>
    </div>
  );
}

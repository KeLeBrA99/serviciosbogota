import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { businessAPI, paymentsAPI, statsAPI } from "../services/api";
import useAuthStore from "../store/authStore";
import usePageTitle from "../hooks/usePageTitle";
import { PLANS, SUPPORT_EMAIL } from "../lib/constants";
import { errorMessage, formatCOP } from "../lib/utils";

const PLAN_DETAILS = [
  {
    ...PLANS.basic,
    color: "border-zinc-700",
    badge: null,
    features: [
      [true, "Perfil completo en el directorio"],
      [true, "Hasta 3 fotos"],
      [true, "Botón de WhatsApp y llamada"],
      [true, "Horarios de atención"],
      [true, "Solicitudes de clientes y reseñas"],
      [false, "Posición destacada en resultados"],
      [false, "Insignia PREMIUM"],
    ],
    cta: "Elegir Básico",
    ctaStyle: "btn-outline",
  },
  {
    ...PLANS.premium,
    color: "border-brand-500",
    badge: "MÁS POPULAR",
    features: [
      [true, "Todo lo del plan Básico"],
      [true, "Apareces primero en los resultados"],
      [true, "Insignia PREMIUM en tu perfil"],
      [true, "Hasta 10 fotos"],
      [true, "Soporte prioritario"],
      [null, "Agenda online de citas (próximamente)"],
    ],
    cta: "Elegir Premium",
    ctaStyle: "btn-primary",
  },
];

export default function PricingPage() {
  usePageTitle("Planes para negocios");
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [businesses, setBusinesses] = useState([]);
  const [businessId, setBusinessId] = useState(params.get("negocio") || "");
  const [stats, setStats] = useState(null);
  const [paying, setPaying] = useState("");

  useEffect(() => {
    statsAPI.public().then(({ data }) => setStats(data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isAuthenticated) return;
    businessAPI.myBusinesses()
      .then(({ data }) => {
        setBusinesses(data);
        setBusinessId((current) => (data.some((b) => String(b.id) === current) ? current : String(data[0]?.id ?? "")));
      })
      .catch(() => {});
  }, [isAuthenticated]);

  const choose = async (plan) => {
    if (!isAuthenticated) return navigate("/registro");
    if (!businessId) {
      toast("Primero registra tu negocio para activar un plan.");
      return navigate("/registrar-negocio");
    }
    setPaying(plan);
    try {
      const { data } = await paymentsAPI.checkout(Number(businessId), plan);
      window.location.assign(data.checkout_url); // pasarela segura de Wompi
    } catch (err) {
      toast.error(errorMessage(err, "No se pudo iniciar el pago"), { duration: 6000 });
      setPaying("");
    }
  };

  const selected = businesses.find((b) => String(b.id) === businessId);
  const activePlan = selected?.subscription?.status === "active" ? selected.subscription.plan : null;

  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <div className="text-center mb-10">
        <h1 className="font-display font-800 text-4xl text-white mb-3">
          Planes simples, <span className="text-brand-500">sin letra pequeña</span>
        </h1>
        <p className="text-zinc-400">Pago mensual con Wompi. Sin contratos ni renovación automática.</p>
      </div>

      {businesses.length > 0 && (
        <div className="card p-4 mb-8 flex flex-col sm:flex-row sm:items-center gap-3">
          <label htmlFor="plan-business" className="text-sm text-zinc-400 flex-shrink-0">Plan para:</label>
          <select id="plan-business" value={businessId} onChange={(e) => setBusinessId(e.target.value)} className="input">
            {businesses.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {PLAN_DETAILS.map((plan) => (
          <div key={plan.key} className={`card p-7 border-2 ${plan.color} relative flex flex-col`}>
            {plan.badge && (
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-brand-500 text-black text-xs font-display font-800 px-4 py-1 rounded-full tracking-wider whitespace-nowrap">
                {plan.badge}
              </div>
            )}
            <h2 className="font-display font-800 text-xl text-white mb-2">{plan.name}</h2>
            <div className="mb-6">
              <span className="font-display font-800 text-4xl text-white">{formatCOP(plan.price)}</span>
              <span className="text-zinc-500 text-sm"> /mes</span>
            </div>
            <ul className="space-y-2.5 mb-7 flex-1">
              {plan.features.map(([included, text]) => (
                <li key={text} className={`text-sm flex gap-2 ${included === false ? "text-zinc-600" : "text-zinc-300"}`}>
                  <span aria-hidden="true">{included === true ? "✅" : included === false ? "—" : "🕓"}</span>{text}
                </li>
              ))}
            </ul>
            <button onClick={() => choose(plan.key)} disabled={Boolean(paying)} className={`${plan.ctaStyle} w-full`}>
              {paying === plan.key ? "Abriendo Wompi..." : activePlan === plan.key ? "Renovar 30 días" : plan.cta}
            </button>
          </div>
        ))}
      </div>

      {stats && stats.businesses > 0 && (
        <div className="card p-6 grid grid-cols-3 gap-6 text-center">
          {[[stats.businesses, "Negocios publicados"], [stats.localidades, "Localidades cubiertas"], [stats.reviews, "Reseñas de clientes"]].map(([num, label]) => (
            <div key={label}>
              <div className="font-display font-800 text-2xl text-brand-500">{num}</div>
              <div className="text-zinc-500 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      <p className="text-center text-zinc-500 text-sm mt-8">
        ¿Prefieres pagar por transferencia o tienes preguntas?{" "}
        <a href={`mailto:${SUPPORT_EMAIL}`} className="text-brand-400 hover:text-brand-300">{SUPPORT_EMAIL}</a>
        {!isAuthenticated && <> · <Link to="/login" className="text-brand-400 hover:text-brand-300">Ya tengo cuenta</Link></>}
      </p>
    </div>
  );
}

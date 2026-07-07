import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { businessAPI, contactAPI } from "../services/api";
import Navbar from "../components/ui/Navbar";
import Badge from "../components/ui/Badge";
import toast from "react-hot-toast";

export default function DashboardPage() {
  const [businesses, setBusinesses] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    businessAPI.myBusinesses()
      .then(({ data }) => {
        setBusinesses(data);
        if (data.length > 0) return contactAPI.list(data[0].id);
      })
      .then((res) => { if (res) setContacts(res.data); })
      .catch(() => toast.error("Error cargando datos"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
      <p className="text-zinc-400">Cargando...</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-zinc-950">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-display font-800 text-2xl text-white">Mi Dashboard</h1>
            <p className="text-zinc-500 text-sm mt-1">Gestiona tu negocio en ServiciosBogotá</p>
          </div>
          <Link to="/registrar-negocio" className="btn-primary text-sm">
            + Nuevo negocio
          </Link>
        </div>

        {businesses.length === 0 ? (
          <div className="card p-12 text-center">
            <p className="text-4xl mb-4">🏪</p>
            <h2 className="font-display font-700 text-white text-lg mb-2">Aún no tienes negocios registrados</h2>
            <p className="text-zinc-400 text-sm mb-6">Registra tu negocio y empieza a recibir clientes hoy.</p>
            <Link to="/registrar-negocio" className="btn-primary">Registrar mi negocio</Link>
          </div>
        ) : (
          <div className="space-y-6">
            {businesses.map((b) => (
              <div key={b.id} className="card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="font-display font-700 text-white text-lg">{b.name}</h2>
                    <p className="text-zinc-500 text-sm">📍 {b.localidad} · {b.category?.name}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge color={b.status === "active" ? "green" : b.status === "pending" ? "amber" : "red"}>
                      {b.status === "active" ? "Activo" : b.status === "pending" ? "Pendiente" : "Suspendido"}
                    </Badge>
                    <Badge color={b.subscription?.plan === "premium" ? "amber" : "gray"}>
                      {b.subscription?.plan?.toUpperCase() || "SIN PLAN"}
                    </Badge>
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-zinc-800/50 rounded-lg">
                  {[
                    ["👁", b.view_count, "Visitas"],
                    ["📞", b.contact_count, "Contactos"],
                    ["⭐", b.rating_avg?.toFixed(1) || "—", "Calificación"],
                  ].map(([icon, val, label]) => (
                    <div key={label} className="text-center">
                      <div className="text-lg mb-0.5">{icon}</div>
                      <div className="font-display font-700 text-white text-xl">{val}</div>
                      <div className="text-zinc-500 text-xs">{label}</div>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <Link to={`/negocio/${b.slug}`} className="btn-outline text-sm py-1.5 flex-1 text-center">
                    Ver perfil público
                  </Link>
                  {(!b.subscription || b.subscription.status !== "active") && (
                    <Link to="/planes" className="btn-primary text-sm py-1.5 flex-1 text-center">
                      Activar plan
                    </Link>
                  )}
                </div>
              </div>
            ))}

            {/* Solicitudes recientes */}
            {contacts.length > 0 && (
              <div className="card p-6">
                <h2 className="font-display font-700 text-white mb-4">Últimas solicitudes</h2>
                <div className="space-y-3">
                  {contacts.slice(0, 5).map((c) => (
                    <div key={c.id} className="flex items-start justify-between p-3 bg-zinc-800/50 rounded-lg">
                      <div>
                        <p className="font-display font-600 text-white text-sm">{c.client_name}</p>
                        <p className="text-zinc-400 text-xs mt-0.5">{c.message.slice(0, 80)}...</p>
                        {c.client_phone && <p className="text-brand-400 text-xs mt-1">📞 {c.client_phone}</p>}
                      </div>
                      <Badge color={c.status === "new" ? "amber" : "gray"}>
                        {c.status === "new" ? "Nuevo" : c.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { businessAPI } from "../services/api";
import BusinessForm from "../components/business/BusinessForm";
import Spinner from "../components/ui/Spinner";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

function ImageManager({ business, onChange }) {
  const [busy, setBusy] = useState("");
  const logoInput = useRef(null);
  const photoInput = useRef(null);
  const isPremium = business.subscription?.plan === "premium" && business.subscription?.status === "active";
  const limit = isPremium ? 10 : 3;
  const photos = business.photos || [];

  const run = async (key, request, okMessage) => {
    setBusy(key);
    try {
      const { data } = await request();
      onChange(data);
      toast.success(okMessage);
    } catch (err) {
      toast.error(errorMessage(err, "No se pudo completar la acción"));
    } finally {
      setBusy("");
    }
  };

  const pick = (e, handler) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) return toast.error("La imagen supera el máximo de 5 MB.");
    handler(file);
  };

  return (
    <section className="card p-6 space-y-5">
      <h2 className="font-display font-700 text-white">Logo y fotos</h2>

      <div className="flex items-center gap-4">
        <div className="w-20 h-20 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center text-3xl overflow-hidden flex-shrink-0">
          {business.logo_url ? <img src={business.logo_url} alt="Logo" className="w-full h-full object-cover" /> : business.category?.icon}
        </div>
        <div>
          <input ref={logoInput} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={(e) => pick(e, (f) => run("logo", () => businessAPI.uploadLogo(business.id, f), "Logo actualizado"))} />
          <button type="button" className="btn-ghost" disabled={busy === "logo"} onClick={() => logoInput.current.click()}>
            {busy === "logo" ? "Subiendo..." : business.logo_url ? "Cambiar logo" : "Subir logo"}
          </button>
          <p className="text-zinc-600 text-xs mt-1.5">JPG, PNG o WEBP · máximo 5 MB</p>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-zinc-300">Fotos del negocio <span className="text-zinc-500">({photos.length}/{limit})</span></p>
          <input ref={photoInput} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={(e) => pick(e, (f) => run("photo", () => businessAPI.uploadPhoto(business.id, f), "Foto agregada"))} />
          <button type="button" className="btn-ghost" disabled={busy === "photo" || photos.length >= limit} onClick={() => photoInput.current.click()}>
            {busy === "photo" ? "Subiendo..." : "+ Agregar foto"}
          </button>
        </div>
        {photos.length === 0 ? (
          <p className="text-zinc-500 text-sm">Aún no hay fotos. Los perfiles con fotos reciben más contactos.</p>
        ) : (
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
            {photos.map((url) => (
              <div key={url} className="relative group aspect-square">
                <img src={url} alt="" className="w-full h-full object-cover rounded-lg" />
                <button
                  type="button"
                  aria-label="Eliminar foto"
                  disabled={busy === url}
                  onClick={() => run(url, () => businessAPI.deletePhoto(business.id, url), "Foto eliminada")}
                  className="absolute top-1 right-1 bg-black/70 hover:bg-red-600 text-white w-7 h-7 rounded-full text-sm transition-colors"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
        {!isPremium && photos.length >= limit && (
          <p className="text-zinc-500 text-xs mt-3">
            Llegaste al límite de tu plan. <Link to={`/planes?negocio=${business.id}`} className="text-brand-400 hover:text-brand-300">Con Premium subes hasta 10 fotos.</Link>
          </p>
        )}
      </div>
    </section>
  );
}

export default function EditBusinessPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [loading, setLoading] = useState(true);
  usePageTitle(business ? `Editar ${business.name}` : "Editar negocio");

  useEffect(() => {
    businessAPI.myBusinesses()
      .then(({ data }) => setBusiness(data.find((b) => String(b.id) === id) || null))
      .catch((err) => toast.error(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (payload) => {
    try {
      const { data } = await businessAPI.update(business.id, payload);
      setBusiness(data);
      toast.success("Cambios guardados");
    } catch (err) {
      toast.error(errorMessage(err, "No se pudieron guardar los cambios"));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`¿Eliminar "${business.name}" definitivamente? Se borrarán sus reseñas y solicitudes.`)) return;
    try {
      await businessAPI.remove(business.id);
      toast.success("Negocio eliminado");
      navigate("/dashboard");
    } catch (err) {
      toast.error(errorMessage(err, "No se pudo eliminar el negocio"));
    }
  };

  if (loading) return <Spinner />;
  if (!business) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <p className="text-zinc-400 mb-4">No encontramos este negocio en tu cuenta.</p>
        <Link to="/dashboard" className="btn-primary">Volver a mi negocio</Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to="/dashboard" className="text-zinc-500 hover:text-white text-sm">← Mi negocio</Link>
          <h1 className="font-display font-800 text-2xl text-white mt-2">Editar {business.name}</h1>
        </div>
        <Link to={`/negocio/${business.slug}`} className="btn-ghost flex-shrink-0">Ver perfil</Link>
      </div>

      <ImageManager business={business} onChange={setBusiness} />
      <BusinessForm key={business.id} business={business} submitLabel="Guardar cambios" onSubmit={handleSubmit} />

      <section className="card p-6 border-red-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="font-display font-700 text-white">Eliminar negocio</h2>
          <p className="text-zinc-500 text-sm mt-1">Esta acción no se puede deshacer.</p>
        </div>
        <button type="button" className="btn-danger" onClick={handleDelete}>Eliminar</button>
      </section>
    </div>
  );
}

import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { businessAPI } from "../services/api";
import BusinessForm from "../components/business/BusinessForm";
import usePageTitle from "../hooks/usePageTitle";
import { errorMessage } from "../lib/utils";

export default function RegisterBusinessPage() {
  usePageTitle("Registrar negocio");
  const navigate = useNavigate();

  const handleSubmit = async (payload) => {
    try {
      const { data } = await businessAPI.create(payload);
      toast.success("¡Negocio registrado! Ahora agrega tu logo y fotos.");
      navigate(`/negocio/${data.id}/editar`);
    } catch (err) {
      toast.error(errorMessage(err, "Error al registrar el negocio"));
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="font-display font-800 text-2xl text-white">Registrar mi negocio</h1>
        <p className="text-zinc-400 text-sm mt-1">Completa la información para aparecer en el directorio.</p>
      </div>
      <BusinessForm submitLabel="Registrar negocio" onSubmit={handleSubmit} />
    </div>
  );
}

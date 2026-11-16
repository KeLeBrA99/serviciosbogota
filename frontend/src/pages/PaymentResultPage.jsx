import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { paymentsAPI } from "../services/api";
import Spinner from "../components/ui/Spinner";
import usePageTitle from "../hooks/usePageTitle";
import { PLANS, SUPPORT_EMAIL } from "../lib/constants";
import { errorMessage } from "../lib/utils";

const MAX_ATTEMPTS = 8; // los pagos por PSE o Nequi pueden tardar unos segundos en confirmarse

export default function PaymentResultPage() {
  usePageTitle("Resultado del pago");
  const [params] = useSearchParams();
  const transactionId = params.get("id");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!transactionId) return;
    let cancelled = false;
    let timer;
    const check = async (attempt) => {
      try {
        const { data } = await paymentsAPI.verify(transactionId);
        if (cancelled) return;
        setResult(data);
        if (data.status === "PENDING" && attempt < MAX_ATTEMPTS) timer = setTimeout(() => check(attempt + 1), 4000);
      } catch (err) {
        if (!cancelled) setError(errorMessage(err, "No pudimos confirmar el pago"));
      }
    };
    check(1);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [transactionId]);

  let icon, title, text;
  if (!transactionId) {
    [icon, title, text] = ["❓", "No hay ningún pago que confirmar", "Abre esta página desde el enlace de confirmación de Wompi."];
  } else if (error) {
    [icon, title, text] = ["⚠️", "No pudimos confirmar tu pago", `${error} Si el cobro se realizó, tu plan se activará automáticamente en unos minutos.`];
  } else if (!result) {
    return <Spinner label="Confirmando tu pago con Wompi..." />;
  } else if (result.status === "APPROVED" && result.activated) {
    [icon, title, text] = ["🎉", "¡Pago aprobado!", `Tu plan ${PLANS[result.plan]?.name || ""} ya está activo por 30 días.`];
  } else if (result.status === "APPROVED") {
    [icon, title, text] = ["⚠️", "Pago aprobado, pero no pudimos activar el plan", `Escríbenos a ${SUPPORT_EMAIL} con la referencia de abajo y lo resolvemos.`];
  } else if (result.status === "PENDING") {
    [icon, title, text] = ["⏳", "Tu pago está en proceso", "El banco aún no lo confirma. Tu plan se activará automáticamente cuando se apruebe; no necesitas pagar de nuevo."];
  } else {
    [icon, title, text] = ["❌", "El pago no fue aprobado", "No se realizó ningún cobro. Puedes intentarlo de nuevo con otro medio de pago."];
  }

  const approved = result?.status === "APPROVED" && result.activated;

  return (
    <div className="max-w-md mx-auto px-4 py-20 text-center">
      <p className="text-6xl mb-4">{icon}</p>
      <h1 className="font-display font-800 text-2xl text-white mb-3">{title}</h1>
      <p className="text-zinc-400 mb-2">{text}</p>
      {transactionId && <p className="text-zinc-600 text-xs mb-8 break-all">Referencia Wompi: {transactionId}</p>}
      <div className="flex flex-col sm:flex-row gap-3 justify-center mt-6">
        <Link to="/dashboard" className="btn-primary">Ir a mi negocio</Link>
        {!approved && result?.status !== "PENDING" && <Link to="/planes" className="btn-outline">Ver planes</Link>}
      </div>
    </div>
  );
}

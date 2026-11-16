export const LOCALIDADES = [
  "Usaquén", "Chapinero", "Santa Fe", "San Cristóbal", "Usme",
  "Tunjuelito", "Bosa", "Kennedy", "Fontibón", "Engativá",
  "Suba", "Barrios Unidos", "Teusaquillo", "Los Mártires",
  "Antonio Nariño", "Puente Aranda", "La Candelaria",
  "Rafael Uribe Uribe", "Ciudad Bolívar", "Sumapaz",
];

export const DAYS = [
  { key: "lunes", label: "Lunes" },
  { key: "martes", label: "Martes" },
  { key: "miercoles", label: "Miércoles" },
  { key: "jueves", label: "Jueves" },
  { key: "viernes", label: "Viernes" },
  { key: "sabado", label: "Sábado" },
  { key: "domingo", label: "Domingo" },
];

export const PLANS = {
  basic: { key: "basic", name: "Básico", price: 25000 },
  premium: { key: "premium", name: "Premium", price: 65000 },
};

export const BUSINESS_STATUS = {
  active: { label: "Activo", color: "green" },
  pending: { label: "Pendiente", color: "amber" },
  suspended: { label: "Suspendido", color: "red" },
  rejected: { label: "Rechazado", color: "red" },
};

export const CONTACT_STATUS = {
  new: { label: "Nuevo", color: "amber" },
  seen: { label: "Visto", color: "blue" },
  replied: { label: "Respondido", color: "green" },
};

export const SUPPORT_EMAIL = "hola@serviciosbogota.co";

import axios from "axios";

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, ""),
  timeout: 15000,
});

const AUTH_KEYS = ["access_token", "refresh_token", "user"];
export const clearSession = () => AUTH_KEYS.forEach((k) => localStorage.removeItem(k));

// Añade el token JWT a cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Si el token expira se refresca una sola vez; las peticiones simultáneas
// comparten el mismo intento de refresco.
let refreshing = null;

function refreshTokens() {
  if (!refreshing) {
    refreshing = axios
      .post(`${api.defaults.baseURL}/auth/refresh`, { refresh_token: localStorage.getItem("refresh_token") })
      .then(({ data }) => {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        return data.access_token;
      })
      .finally(() => { refreshing = null; });
  }
  return refreshing;
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isAuthCall = original?.url?.startsWith("/auth/login") || original?.url?.startsWith("/auth/register");
    if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      if (localStorage.getItem("refresh_token")) {
        try {
          const token = await refreshTokens();
          original.headers.Authorization = `Bearer ${token}`;
          return api(original);
        } catch {
          // el refresh token también venció: se cierra la sesión abajo
        }
      }
      clearSession();
      if (!["/login", "/registro"].includes(window.location.pathname)) {
        window.location.assign("/login?expirada=1");
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──
export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  changePassword: (data) => api.post("/auth/change-password", data),
};

// ── Negocios ──
const upload = (url, file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post(url, form, { timeout: 60000 });
};

export const businessAPI = {
  list: (params) => api.get("/businesses", { params }),
  getBySlug: (slug) => api.get(`/businesses/${slug}`),
  create: (data) => api.post("/businesses", data),
  update: (id, data) => api.put(`/businesses/${id}`, data),
  remove: (id) => api.delete(`/businesses/${id}`),
  myBusinesses: () => api.get("/businesses/my"),
  uploadLogo: (id, file) => upload(`/businesses/${id}/logo`, file),
  uploadCover: (id, file) => upload(`/businesses/${id}/cover`, file),
  uploadPhoto: (id, file) => upload(`/businesses/${id}/photos`, file),
  deletePhoto: (id, url) => api.delete(`/businesses/${id}/photos`, { data: { url } }),
};

// ── Catálogos ──
export const categoriesAPI = {
  list: () => api.get("/categories"),
};
export const statsAPI = {
  public: () => api.get("/stats"),
};

// ── Reseñas ──
export const reviewsAPI = {
  list: (businessId) => api.get(`/businesses/${businessId}/reviews`),
  create: (businessId, data) => api.post(`/businesses/${businessId}/reviews`, data),
  respond: (businessId, reviewId, response) =>
    api.put(`/businesses/${businessId}/reviews/${reviewId}/response`, { response }),
};

// ── Contactos ──
export const contactAPI = {
  send: (businessId, data) => api.post(`/businesses/${businessId}/contact`, data),
  list: (businessId) => api.get(`/my-businesses/${businessId}/contacts`),
  setStatus: (businessId, contactId, status) =>
    api.patch(`/my-businesses/${businessId}/contacts/${contactId}`, { status }),
};

// ── Pagos ──
export const paymentsAPI = {
  checkout: (businessId, plan) => api.post("/payments/checkout", { business_id: businessId, plan }),
  verify: (transactionId) => api.get(`/payments/verify/${encodeURIComponent(transactionId)}`),
};

// ── Admin ──
export const adminAPI = {
  stats: () => api.get("/admin/stats"),
  businesses: (params) => api.get("/admin/businesses", { params }),
  approve: (id) => api.patch(`/admin/businesses/${id}/approve`),
  suspend: (id) => api.patch(`/admin/businesses/${id}/suspend`),
  reject: (id) => api.patch(`/admin/businesses/${id}/reject`),
  setFeatured: (id, featured) => api.patch(`/admin/businesses/${id}/featured`, null, { params: { featured } }),
  activatePlan: (id, plan, days = 30) => api.post(`/admin/businesses/${id}/subscription`, { plan, days }),
  reviews: () => api.get("/admin/reviews"),
  setReviewVisible: (id, visible) => api.patch(`/admin/reviews/${id}/visibility`, null, { params: { visible } }),
  users: () => api.get("/admin/users"),
};

export default api;

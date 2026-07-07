import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
});

// Añade el token JWT a cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Si el token expira, intenta refrescarlo
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh_token: refresh }
          );
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api(error.config);
        } catch {
          localStorage.clear();
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──
export const authAPI = {
  register: (data) => api.post("/auth/register", data),
  login: (data) => api.post("/auth/login", data),
};

// ── Negocios ──
export const businessAPI = {
  list: (params) => api.get("/businesses", { params }),
  getBySlug: (slug) => api.get(`/businesses/${slug}`),
  create: (data) => api.post("/businesses", data),
  update: (id, data) => api.put(`/businesses/${id}`, data),
  myBusinesses: () => api.get("/businesses/my"),
};

// ── Categorías ──
export const categoriesAPI = {
  list: () => api.get("/categories"),
};

// ── Reseñas ──
export const reviewsAPI = {
  list: (businessId) => api.get(`/businesses/${businessId}/reviews`),
  create: (businessId, data) => api.post(`/businesses/${businessId}/reviews`, data),
};

// ── Contactos ──
export const contactAPI = {
  send: (businessId, data) => api.post(`/businesses/${businessId}/contact`, data),
  list: (businessId) => api.get(`/my-businesses/${businessId}/contacts`),
};

// ── Pagos ──
export const paymentsAPI = {
  checkout: (businessId, plan) =>
    api.post("/payments/checkout", null, { params: { business_id: businessId, plan } }),
};

// ── Admin ──
export const adminAPI = {
  stats: () => api.get("/admin/stats"),
  approve: (id) => api.patch(`/admin/businesses/${id}/approve`),
  suspend: (id) => api.patch(`/admin/businesses/${id}/suspend`),
};

export default api;

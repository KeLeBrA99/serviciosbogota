import { create } from "zustand";
import { authAPI, clearSession } from "../services/api";

function storedUser() {
  try {
    const token = localStorage.getItem("access_token");
    const user = JSON.parse(localStorage.getItem("user") || "null");
    return token && user ? user : null;
  } catch {
    return null;
  }
}

async function startSession(tokens, set) {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
  const { data: user } = await authAPI.me();
  localStorage.setItem("user", JSON.stringify(user));
  set({ isAuthenticated: true, user });
  return user;
}

// El estado inicial se lee de localStorage de forma síncrona para que las
// rutas privadas no redirijan a /login al recargar la página.
const initial = storedUser();

const useAuthStore = create((set) => ({
  user: initial,
  isAuthenticated: Boolean(initial),

  /** Revalida la sesión guardada contra la API (rol, nombre, cuenta activa). */
  init: async () => {
    if (!localStorage.getItem("access_token")) return;
    try {
      const { data: user } = await authAPI.me();
      localStorage.setItem("user", JSON.stringify(user));
      set({ isAuthenticated: true, user });
    } catch (err) {
      if (err.response?.status === 401) {
        clearSession();
        set({ isAuthenticated: false, user: null });
      }
    }
  },

  login: async (email, password) => {
    const { data } = await authAPI.login({ email, password });
    return startSession(data, set);
  },

  register: async (formData) => {
    const { data } = await authAPI.register(formData);
    return startSession(data, set);
  },

  logout: () => {
    clearSession();
    set({ isAuthenticated: false, user: null });
  },
}));

export default useAuthStore;

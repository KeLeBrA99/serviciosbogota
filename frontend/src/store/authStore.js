import { create } from "zustand";
import { authAPI } from "../services/api";

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,

  init: () => {
    const token = localStorage.getItem("access_token");
    const user = localStorage.getItem("user");
    if (token && user) {
      set({ isAuthenticated: true, user: JSON.parse(user) });
    }
  },

  login: async (email, password) => {
    const { data } = await authAPI.login({ email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    // Decodificar payload del token para obtener rol
    const payload = JSON.parse(atob(data.access_token.split(".")[1]));
    const user = { id: payload.sub, role: payload.role };
    localStorage.setItem("user", JSON.stringify(user));
    set({ isAuthenticated: true, user });
    return user;
  },

  register: async (formData) => {
    const { data } = await authAPI.register(formData);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    const payload = JSON.parse(atob(data.access_token.split(".")[1]));
    const user = { id: payload.sub, role: payload.role };
    localStorage.setItem("user", JSON.stringify(user));
    set({ isAuthenticated: true, user });
    return user;
  },

  logout: () => {
    localStorage.clear();
    set({ isAuthenticated: false, user: null });
  },
}));

export default useAuthStore;

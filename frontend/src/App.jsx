import { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import useAuthStore from "./store/authStore";
import Layout from "./components/layout/Layout";

import HomePage from "./pages/HomePage";
import BusinessPage from "./pages/BusinessPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import RegisterBusinessPage from "./pages/RegisterBusinessPage";
import EditBusinessPage from "./pages/EditBusinessPage";
import PricingPage from "./pages/PricingPage";
import PaymentResultPage from "./pages/PaymentResultPage";
import AccountPage from "./pages/AccountPage";
import AdminPage from "./pages/AdminPage";
import NotFoundPage from "./pages/NotFoundPage";

function PrivateRoute({ children, adminOnly = false }) {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  if (adminOnly && user?.role !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return null;
}

export default function App() {
  const init = useAuthStore((s) => s.init);
  useEffect(() => { init(); }, [init]);

  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/negocio/:slug" element={<BusinessPage />} />
          <Route path="/planes" element={<PricingPage />} />
          <Route path="/pago/confirmacion" element={<PaymentResultPage />} />
          <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
          <Route path="/registrar-negocio" element={<PrivateRoute><RegisterBusinessPage /></PrivateRoute>} />
          <Route path="/negocio/:id/editar" element={<PrivateRoute><EditBusinessPage /></PrivateRoute>} />
          <Route path="/cuenta" element={<PrivateRoute><AccountPage /></PrivateRoute>} />
          <Route path="/admin" element={<PrivateRoute adminOnly><AdminPage /></PrivateRoute>} />
        </Route>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<RegisterPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}

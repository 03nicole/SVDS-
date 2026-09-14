import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { AlertsProvider } from "./context/AlertsContext";
import ProtectedRoute from "./components/ProtectedRoute";
import NotificationToast from "./components/NotificationToast";
import Login           from "./pages/Login";
import Register        from "./pages/Register";
import ReporteeHome    from "./pages/reportee/ReporteeHome";
import ReportVehicle   from "./pages/reportee/ReportVehicle";
import MyReports       from "./pages/reportee/MyReports";
import Profile         from "./pages/reportee/Profile";
import PoliceHome      from "./pages/police/PoliceHome";
import Alerts          from "./pages/police/Alerts";
import Cameras         from "./pages/police/Cameras";
import Analytics       from "./pages/police/Analytics";
import AdminHome       from "./pages/admin/AdminHome";
import UserManagement  from "./pages/admin/UserManagement";
import SystemHealth    from "./pages/admin/SystemHealth";
import AuditLog        from "./pages/admin/AuditLog";

const Guard = ({ roles, children }) => (
    <ProtectedRoute allowedRoles={roles}>{children}</ProtectedRoute>
);

export default function App() {
    return (
        <AuthProvider>
            <AlertsProvider>
                <BrowserRouter>
                    <NotificationToast />
                    <Routes>
                        <Route path="/"         element={<Navigate to="/login" replace />} />
                        <Route path="/login"    element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/my"              element={<Guard roles={["reportee","police","admin"]}><ReporteeHome /></Guard>} />
                        <Route path="/my/report"       element={<Guard roles={["reportee","police","admin"]}><ReportVehicle /></Guard>} />
                        <Route path="/my/reports"      element={<Guard roles={["reportee","police","admin"]}><MyReports /></Guard>} />
                        <Route path="/my/profile"      element={<Guard roles={["reportee","police","admin"]}><Profile /></Guard>} />
                        <Route path="/police"           element={<Guard roles={["police","admin"]}><PoliceHome /></Guard>} />
                        <Route path="/police/alerts"    element={<Guard roles={["police","admin"]}><Alerts /></Guard>} />
                        <Route path="/police/cameras"   element={<Guard roles={["police","admin"]}><Cameras /></Guard>} />
                        <Route path="/police/analytics" element={<Guard roles={["police","admin"]}><Analytics /></Guard>} />
                        <Route path="/admin"            element={<Guard roles={["admin"]}><AdminHome /></Guard>} />
                        <Route path="/admin/users"      element={<Guard roles={["admin"]}><UserManagement /></Guard>} />
                        <Route path="/admin/health"     element={<Guard roles={["admin"]}><SystemHealth /></Guard>} />
                        <Route path="/admin/audit"      element={<Guard roles={["admin"]}><AuditLog /></Guard>} />
                    </Routes>
                </BrowserRouter>
            </AlertsProvider>
        </AuthProvider>
    );
}

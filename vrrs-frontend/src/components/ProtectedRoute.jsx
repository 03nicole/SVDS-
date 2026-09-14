import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roleHomeMap = {
    reportee: "/my",
    police: "/police",
    admin: "/admin",
};

export default function ProtectedRoute({ children, allowedRoles }) {
    const { user, loading } = useAuth();
    if (loading) return <div style={{padding:"2rem"}}>Loading...</div>;
    if (!user)   return <Navigate to="/login" replace />;
    if (allowedRoles && !allowedRoles.includes(user.role)) {
        return <Navigate to={roleHomeMap[user.role] || "/login"} replace />;
    }
    return children;
}

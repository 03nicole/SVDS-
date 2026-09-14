import { createContext, useContext, useState, useEffect } from "react";
import { usersAPI } from "../services/api";

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user,    setUser]    = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const saved = localStorage.getItem("vrrs_user");
        const token = localStorage.getItem("vrrs_token");
        if (saved && token) {
            setUser(JSON.parse(saved));
            usersAPI.getMe()
                .then(res => setUser(res.data))
                .catch(() => logout())
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = (userData, token) => {
        localStorage.setItem("vrrs_user",  JSON.stringify(userData));
        localStorage.setItem("vrrs_token", token);
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem("vrrs_user");
        localStorage.removeItem("vrrs_token");
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);

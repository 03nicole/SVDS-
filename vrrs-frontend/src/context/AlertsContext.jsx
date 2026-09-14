import { createContext, useContext, useEffect, useState } from "react";
import { alertsAPI, createAlertSocket } from "../services/api";
import { useAuth } from "./AuthContext";

const AlertsContext = createContext();

export function AlertsProvider({ children }) {
    const { user } = useAuth();
    const [unread, setUnread] = useState(0);
    const [notification, setNotification] = useState(null);
    const [lastEvent, setLastEvent] = useState(null);

    const canSeeAlerts = user && (user.role === "police" || user.role === "admin");

    useEffect(() => {
        if (!canSeeAlerts) return;

        alertsAPI.unreadCount().then(r => setUnread(r.data.unread)).catch(() => {});

        const ws = createAlertSocket((data) => {
            if (data.type === "STOLEN_DETECTED") {
                setUnread(prev => prev + 1);
                setNotification(data);
                setLastEvent(data);
            }
        });
        return () => ws.close();
    }, [canSeeAlerts]);

    const dismissNotification = () => setNotification(null);
    const decrementUnread = (by = 1) => setUnread(prev => Math.max(0, prev - by));

    return (
        <AlertsContext.Provider value={{ unread, setUnread, decrementUnread, notification, dismissNotification, lastEvent }}>
            {children}
        </AlertsContext.Provider>
    );
}

export const useAlerts = () => useContext(AlertsContext);

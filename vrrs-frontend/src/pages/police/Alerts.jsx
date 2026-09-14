import { useEffect, useState } from "react";
import { alertsAPI } from "../../services/api";
import { useAlerts } from "../../context/AlertsContext";
import { getPoliceNav } from "../../config/policeNav";
import PortalLayout from "../../components/PortalLayout";

export default function Alerts() {
    const { unread, setUnread, decrementUnread, lastEvent } = useAlerts();
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [view, setView] = useState("unread");
    const [limit, setLimit] = useState(25);

    const load = () => {
        setLoading(true);
        const params = { limit };
        if (view === "unread") params.is_read = false;
        alertsAPI.getAll(params).then(r => { setAlerts(r.data); setLoading(false); });
    };

    useEffect(load, [view, limit]);

    useEffect(() => {
        if (lastEvent && view === "unread") setAlerts(prev => [lastEvent, ...prev]);
    }, [lastEvent]);

    const markResolved = (id) => {
        setAlerts(prev => view === "unread"
            ? prev.filter(a => (a.id || a.alert_id) !== id)
            : prev.map(a => (a.id || a.alert_id) === id ? { ...a, is_read: true } : a));
        decrementUnread();
    };

    const handleMarkRead = async (id) => {
        await alertsAPI.markRead(id);
        markResolved(id);
    };

    const handleMarkAllRead = async () => {
        await alertsAPI.markAllRead();
        setAlerts(prev => view === "unread" ? [] : prev.map(a => ({ ...a, is_read: true })));
        setUnread(0);
    };

    const handleFalsePositive = async (id) => {
        await alertsAPI.falsePositive(id);
        markResolved(id);
    };

    return (
        <PortalLayout portal="Police Portal" navItems={getPoliceNav(unread)}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Live alerts</h2>
                    <p className="rd-page-subtitle">Real-time camera detections - updates via WebSocket</p>
                </div>
            </div>

            <div className="rd-grid-2">
                <article className="rd-card"><div className="rd-stat-label">Unread alerts</div><strong className="rd-stat-value">{unread}</strong><span className="rd-stat-note danger">Live</span></article>
                <article className="rd-card"><div className="rd-stat-label">Alerts today</div><strong className="rd-stat-value">{alerts.length}</strong><span className="rd-stat-note">Across {new Set(alerts.map(a => a.camera_id).filter(Boolean)).size || 0} nodes</span></article>
            </div>

            <section className="rd-section rd-card">
                <div className="rd-section-head">
                    <h3 className="rd-section-title">Alert feed</h3>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <select className="rd-select" value={limit} onChange={e => setLimit(Number(e.target.value))}>
                            <option value={10}>Show 10</option>
                            <option value={25}>Show 25</option>
                            <option value={50}>Show 50</option>
                            <option value={100}>Show 100</option>
                        </select>
                        {view === "unread" && unread > 0 && (
                            <button className="rd-button small" onClick={handleMarkAllRead}>Clear all</button>
                        )}
                    </div>
                </div>

                <div className="rd-tabs" style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                    <button
                        className={`rd-button small${view === "unread" ? " primary" : ""}`}
                        onClick={() => setView("unread")}
                    >Unread{unread > 0 ? ` (${unread})` : ""}</button>
                    <button
                        className={`rd-button small${view === "all" ? " primary" : ""}`}
                        onClick={() => setView("all")}
                    >History</button>
                </div>

                {loading ? <p className="rd-empty">Loading alerts...</p> : null}
                {!loading && alerts.length === 0 ? (
                    <p className="rd-empty">{view === "unread" ? "No unread alerts." : "No alerts yet."}</p>
                ) : null}
                {alerts.map((alert, i) => {
                    const id = alert.id || alert.alert_id;
                    const plate = alert.plate || alert.license_plate;
                    const location = alert.location || alert.location_spotted;
                    return (
                        <div className="rd-alert-row" key={id || i}>
                            <span className="rd-alert-marker" />
                            <div>
                                <strong>{plate}</strong> - {alert.confidence || alert.confidence_score || 90}% confidence
                                <div className="rd-muted">{location || "Camera node"} - {alert.camera_id || "NODE-001"}</div>
                                {!alert.is_read && (
                                    <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
                                        <button className="rd-button small" onClick={() => handleMarkRead(id)}>Mark read</button>
                                        <button className="rd-button small" onClick={() => handleFalsePositive(id)}>Flag false positive</button>
                                    </div>
                                )}
                            </div>
                            <span className="rd-muted">{alert.detected_at?.slice(11, 16) || "2 min ago"}</span>
                        </div>
                    );
                })}
            </section>
        </PortalLayout>
    );
}

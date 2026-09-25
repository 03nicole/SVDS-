import PortalLayout from "../../components/PortalLayout";
import { useEffect, useState } from "react";
import { systemAPI } from "../../services/api";

const adminNav = [
    { to: "/admin", label: "Overview", icon: "grid", end: true },
    { to: "/admin/users", label: "User management", icon: "users" },
    { to: "/admin/health", label: "System health", icon: "clock" },
    { to: "/admin/audit", label: "Audit log", icon: "list" },
];

export default function SystemHealth() {
    const [health, setHealth] = useState(null);
    const [nodes, setNodes] = useState([]);

    useEffect(() => {
        systemAPI.health().then(r => setHealth(r.data));
        systemAPI.cameraNodes().then(r => setNodes(r.data));
    }, []);

    const metrics = health?.metrics || {};
    const services = health?.services || [];

    return (
        <PortalLayout portal="Admin Portal" navItems={adminNav}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">System health</h2>
                    <p className="rd-page-subtitle">Monitor service status, camera nodes, and platform performance</p>
                </div>
            </div>

            <div className="rd-grid-4">
                <article className="rd-card"><div className="rd-stat-label">API response time</div><strong className="rd-stat-value">{metrics.api_response_ms || 0}ms</strong><span className="rd-stat-note success">Normal</span></article>
                <article className="rd-card"><div className="rd-stat-label">DB connections</div><strong className="rd-stat-value">{metrics.db_connections_used != null && metrics.db_connections_max != null ? `${metrics.db_connections_used}/${metrics.db_connections_max}` : "—"}</strong>{metrics.db_connections_used != null && metrics.db_connections_max != null && <span className="rd-stat-note success">Healthy</span>}</article>
                <article className="rd-card"><div className="rd-stat-label">Disk usage</div><strong className="rd-stat-value">{metrics.disk_usage_percent || 0}%</strong><span className="rd-stat-note success">{metrics.disk_free_gb || 0} GB free</span></article>
                <article className="rd-card"><div className="rd-stat-label">Active sessions</div><strong className="rd-stat-value">{metrics.active_sessions || 0}</strong><span className="rd-stat-note">Right now</span></article>
            </div>

            <section className="rd-section rd-grid-2">
                <article className="rd-card">
                    <h3 className="rd-section-title">Core services</h3>
                    {services.map(service => (
                        <div className="rd-service-row" key={service.name}>
                            <div><strong>{service.name}</strong><div className="rd-muted">{service.detail}</div></div>
                            <div>{service.status}<span className="rd-status-dot" /></div>
                        </div>
                    ))}
                </article>

                <article className="rd-card">
                    <h3 className="rd-section-title">Camera nodes</h3>
                    {nodes.map(node => (
                        <div className="rd-service-row" key={node.camera_id}>
                            <div><strong>{node.camera_id} - {node.location}</strong><div className="rd-muted">{node.status === "online" ? `Last ping: ${node.last_ping_seconds}s ago` : "Offline"}</div></div>
                            <div>{node.status}<span className={`rd-status-dot ${node.status === "offline" ? "red" : ""}`} /></div>
                        </div>
                    ))}
                </article>
            </section>
        </PortalLayout>
    );
}

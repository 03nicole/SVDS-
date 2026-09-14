import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { analyticsAPI, systemAPI } from "../../services/api";
import PortalLayout from "../../components/PortalLayout";

function formatUptime(seconds) {
    if (!seconds) return "0m";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

const adminNav = [
    { to: "/admin", label: "Overview", icon: "grid", end: true },
    { to: "/admin/users", label: "User management", icon: "users" },
    { to: "/admin/health", label: "System health", icon: "clock" },
    { to: "/admin/audit", label: "Audit log", icon: "list" },
];

export default function AdminHome() {
    const [summary, setSummary] = useState(null);
    const [health, setHealth] = useState(null);

    useEffect(() => {
        analyticsAPI.summary().then(r => setSummary(r.data));
        systemAPI.health().then(r => setHealth(r.data));
    }, []);

    const users = summary?.users || {};
    const metrics = health?.metrics || {};
    const publicUsers = Math.max((users.total || 0) - (users.police || 0) - (users.admin || 0), 0);
    const totalUsers = users.total || 0;

    return (
        <PortalLayout portal="Admin Portal" navItems={adminNav}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">System overview</h2>
                    <p className="rd-page-subtitle">SVDS platform - Zambia Police Service</p>
                </div>
            </div>

            <div className="rd-grid-4">
                <article className="rd-card">
                    <div className="rd-stat-label">Total users</div>
                    <strong className="rd-stat-value">{totalUsers}</strong>
                    <span className="rd-stat-note danger">+{users.new_this_week || 0} this week</span>
                </article>
                <article className="rd-card">
                    <div className="rd-stat-label">Police accounts</div>
                    <strong className="rd-stat-value">{users.police || 0}</strong>
                    <span className={`rd-stat-note ${users.police_active === users.police ? "success" : "danger"}`}>{users.police_active || 0}/{users.police || 0} active</span>
                </article>
                <article className="rd-card">
                    <div className="rd-stat-label">Camera nodes</div>
                    <strong className="rd-stat-value">{metrics.camera_nodes_online || 0}/{metrics.camera_nodes_total || 0}</strong>
                    <span className="rd-stat-note danger">{metrics.camera_nodes_offline || 0} offline</span>
                </article>
                <article className="rd-card">
                    <div className="rd-stat-label">Server uptime</div>
                    <strong className="rd-stat-value">{formatUptime(metrics.uptime_seconds)}</strong>
                    <span className="rd-stat-note success">Since last restart</span>
                </article>
            </div>

            <section className="rd-section rd-grid-2">
                <article className="rd-card">
                    <h3 className="rd-section-title">User breakdown</h3>
                    <div style={{ marginTop: 28 }}>
                        {[
                            ["Public (Reportee)", "Can file vehicle reports", publicUsers, totalUsers ? Math.round((publicUsers / totalUsers) * 100) : 0],
                            ["Police officers", "Registry and alert access", users.police || 0, totalUsers ? Math.round(((users.police || 0) / totalUsers) * 100) : 0],
                            ["Administrators", "Full system control", users.admin || 0, totalUsers ? Math.round(((users.admin || 0) / totalUsers) * 100) : 0],
                        ].map(([title, copy, value, pct]) => (
                            <div className="rd-progress-row" key={title}>
                                <div>
                                    <div className="rd-progress-title">{title}</div>
                                    <div className="rd-progress-copy">{copy}</div>
                                </div>
                                <div className="rd-progress-value">{value}</div>
                                <div className="rd-progress-track"><div className="rd-progress-bar" style={{ width: `${pct}%` }} /></div>
                            </div>
                        ))}
                    </div>
                </article>

                <article className="rd-card">
                    <h3 className="rd-section-title">Quick actions</h3>
                    <div className="rd-action-stack" style={{ marginTop: 28 }}>
                        <Link className="rd-button" to="/admin/users">Manage user accounts -&gt;</Link>
                        <Link className="rd-button" to="/admin/health">View system health -&gt;</Link>
                        <Link className="rd-button" to="/register?role=police">Invite new police officer -&gt;</Link>
                        <Link className="rd-button" to="/admin/audit">Review audit log -&gt;</Link>
                    </div>
                </article>
            </section>
        </PortalLayout>
    );
}

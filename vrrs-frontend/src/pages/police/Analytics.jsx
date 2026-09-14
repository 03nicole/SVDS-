import { useEffect, useState } from "react";
import { analyticsAPI } from "../../services/api";
import { useAlerts } from "../../context/AlertsContext";
import { getPoliceNav } from "../../config/policeNav";
import PortalLayout from "../../components/PortalLayout";

export default function Analytics() {
    const { unread } = useAlerts();
    const [summary, setSummary] = useState(null);
    const [monthly, setMonthly] = useState([]);
    const [breakdown, setBreakdown] = useState([]);
    const [nodes, setNodes] = useState([]);
    const [recovery, setRecovery] = useState(null);
    const [error, setError] = useState("");
    const [reloadKey, setReloadKey] = useState(0);

    useEffect(() => {
        setError("");
        Promise.all([
            analyticsAPI.summary(),
            analyticsAPI.reportsPerMonth(),
            analyticsAPI.statusBreakdown(),
            analyticsAPI.detectionsPerNode(),
            analyticsAPI.recoveryTime(),
        ]).then(([s, m, b, n, r]) => {
            setSummary(s.data);
            setMonthly(m.data);
            setBreakdown(b.data);
            setNodes(n.data);
            setRecovery(r.data);
        }).catch(() => {
            setError("Failed to load analytics. The backend may be unreachable.");
        });
    }, [reloadKey]);

    const reports = summary?.reports || {};
    const alertStats = summary?.alerts || {};
    const totalBreakdown = breakdown.reduce((sum, item) => sum + item.count, 0);
    const missingPct = totalBreakdown ? Math.round(((breakdown.find(i => i.status === "missing")?.count || 0) / totalBreakdown) * 100) : 0;
    const foundPct = totalBreakdown ? Math.round(((breakdown.find(i => i.status === "found")?.count || 0) / totalBreakdown) * 100) : 0;

    return (
        <PortalLayout portal="Police Portal" navItems={getPoliceNav(unread)}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Analytics</h2>
                    <p className="rd-page-subtitle">Vehicle recovery statistics and detection trends</p>
                </div>
            </div>

            {error ? (
                <div className="rd-alert error" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16 }}>
                    <span>{error}</span>
                    <button className="rd-button small" onClick={() => setReloadKey(k => k + 1)}>Retry</button>
                </div>
            ) : !summary ? <p className="rd-empty">Loading analytics...</p> : (
                <>
                    <div className="rd-grid-4">
                        <article className="rd-card"><div className="rd-stat-label">Total reports</div><strong className="rd-stat-value">{reports.total || 0}</strong><span className="rd-stat-note danger">+{reports.new_this_week || 0} this week</span></article>
                        <article className="rd-card"><div className="rd-stat-label">Avg. recovery time</div><strong className="rd-stat-value">{recovery?.avg_days || 0}d</strong><span className="rd-stat-note success">{recovery?.total_recovered || 0} vehicles recovered</span></article>
                        <article className="rd-card"><div className="rd-stat-label">Avg. detection confidence</div><strong className="rd-stat-value">{alertStats.avg_confidence || 0}%</strong><span className="rd-stat-note">Camera nodes</span></article>
                        <article className="rd-card"><div className="rd-stat-label">False positives</div><strong className="rd-stat-value">{alertStats.false_positives || 0}</strong><span className="rd-stat-note">Flagged by officers</span></article>
                    </div>

                    <section className="rd-section rd-grid-2">
                        <article className="rd-card">
                            <h3 className="rd-section-title">Reports per month</h3>
                            {monthly.length ? (
                                <div className="rd-bars">
                                    {monthly.slice(-6).map(m => (
                                        <div className="rd-bar" key={`${m.label}-${m.year}`}>
                                            <div className="rd-bar-fill" style={{ height: `${Math.max(20, Math.min((m.count || 1) * 10, 170))}px` }} />
                                            <span>{m.label}</span>
                                        </div>
                                    ))}
                                </div>
                            ) : <p className="rd-empty">No report history yet.</p>}
                        </article>

                        <article className="rd-card">
                            <h3 className="rd-section-title">Status breakdown</h3>
                            <div className="rd-donut" style={{ background: `conic-gradient(#62a420 0 ${foundPct}%, #e64646 ${foundPct}% ${foundPct + missingPct}%, #f0a52b ${foundPct + missingPct}% 100%)` }} />
                            <div className="rd-grid-3" style={{ fontSize: 16 }}>
                                <span><span className="rd-status-dot red" /> Missing</span>
                                <span><span className="rd-status-dot" /> Found</span>
                                <span><span className="rd-status-dot" style={{ background: "#f0a52b" }} /> Under review</span>
                            </div>
                        </article>
                    </section>

                    <section className="rd-section rd-card">
                        <h3 className="rd-section-title">Top detection locations</h3>
                        {nodes.length ? (
                            <table className="rd-table" style={{ marginTop: 20 }}>
                                <thead><tr><th>Location</th><th>Node ID</th><th>Detections</th><th>Avg. confidence</th></tr></thead>
                                <tbody>
                                    {nodes.map(n => (
                                        <tr key={n.camera_id}>
                                            <td>{n.location}</td>
                                            <td>{n.camera_id}</td>
                                            <td>{n.total_detections}</td>
                                            <td>{n.avg_confidence || 0}%</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : <p className="rd-empty">No detections yet.</p>}
                    </section>
                </>
            )}
        </PortalLayout>
    );
}

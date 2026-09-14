import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { reportsAPI, analyticsAPI } from "../../services/api";
import { useAlerts } from "../../context/AlertsContext";
import { getPoliceNav } from "../../config/policeNav";
import PortalLayout from "../../components/PortalLayout";

function statusClass(status) {
    if (status === "found") return "found";
    if (status === "missing") return "missing";
    return "review";
}

function statusLabel(status) {
    return (status || "under_review").replaceAll("_", " ");
}

export default function PoliceHome() {
    const { unread } = useAlerts();
    const [reports, setReports] = useState([]);
    const [summary, setSummary] = useState(null);
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");

    useEffect(() => {
        reportsAPI.getAll().then(r => setReports(r.data));
        analyticsAPI.summary().then(r => setSummary(r.data));
    }, []);

    const reload = (params = {}) => reportsAPI.getAll(params).then(r => setReports(r.data));

    const handleSearch = e => {
        const next = e.target.value;
        setSearch(next);
        reload({ search: next, status: status || undefined });
    };

    const handleStatus = e => {
        const next = e.target.value;
        setStatus(next);
        reload({ search: search || undefined, status: next || undefined });
    };

    const handleMarkFound = async (id) => {
        await reportsAPI.markFound(id);
        reload({ search: search || undefined, status: status || undefined });
    };

    const handleActivate = async (id) => {
        await reportsAPI.activate(id);
        reload({ search: search || undefined, status: status || undefined });
    };

    const reportStats = summary?.reports || {};

    return (
        <PortalLayout portal="Police Portal" navItems={getPoliceNav(unread)}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Vehicle registry</h2>
                    <p className="rd-page-subtitle">Manage stolen and recovered vehicle reports</p>
                </div>
            </div>

            <div className="rd-grid-4">
                <article className="rd-card"><div className="rd-stat-label">Total reports</div><strong className="rd-stat-value">{reportStats.total || 0}</strong><span className="rd-stat-note danger">+{reportStats.new_this_week || 0} this week</span></article>
                <article className="rd-card"><div className="rd-stat-label">Missing</div><strong className="rd-stat-value">{reportStats.missing || 0}</strong><span className="rd-stat-note danger">Open cases</span></article>
                <article className="rd-card"><div className="rd-stat-label">Recovered</div><strong className="rd-stat-value">{reportStats.found || 0}</strong><span className="rd-stat-note success">All time</span></article>
                <article className="rd-card"><div className="rd-stat-label">Recovery rate</div><strong className="rd-stat-value">{reportStats.recovery_rate || 0}%</strong><span className="rd-stat-note">All time</span></article>
            </div>

            <section className="rd-section rd-card">
                <div className="rd-toolbar">
                    <div className="rd-toolbar-title">All reports</div>
                    <input className="rd-input" placeholder="Search plate or owner" value={search} onChange={handleSearch} />
                    <select className="rd-select" value={status} onChange={handleStatus}>
                        <option value="">All statuses</option>
                        <option value="missing">Missing</option>
                        <option value="found">Found</option>
                        <option value="under_review">Under review</option>
                    </select>
                    <Link className="rd-button small" to="/my/report">+ Add vehicle</Link>
                </div>

                <table className="rd-table">
                    <thead>
                        <tr>
                            <th>Plate</th>
                            <th>Vehicle</th>
                            <th>Reported</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reports.map(r => (
                            <tr key={r.id}>
                                <td><strong>{r.license_plate}</strong></td>
                                <td>{r.vehicle_make || "Vehicle"} {r.vehicle_model || ""}{r.vehicle_color ? ` - ${r.vehicle_color}` : ""}</td>
                                <td>{r.report_date?.slice(0, 10)}</td>
                                <td><span className={`rd-pill ${statusClass(r.status)}`}>{statusLabel(r.status)}</span></td>
                                <td>
                                    {r.status === "under_review" && <button className="rd-button small" onClick={() => handleActivate(r.id)}>Activate</button>}
                                    {r.status === "missing" && <button className="rd-button small" onClick={() => handleMarkFound(r.id)}>Mark found</button>}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>
        </PortalLayout>
    );
}

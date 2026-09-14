import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { reportsAPI } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import ReporteeLayout from "../../components/ReporteeLayout";

function statusClass(status) {
    if (status === "found") return "found";
    if (status === "missing") return "missing";
    return "review";
}

function statusLabel(status) {
    return (status || "under_review").replaceAll("_", " ");
}

export default function ReporteeHome() {
    const [reports, setReports] = useState([]);
    const { user } = useAuth();
    const location = useLocation();
    const isFirstLogin = location.state?.newlyRegistered;

    useEffect(() => {
        reportsAPI.getAll().then(r => setReports(r.data));
    }, []);

    const missing = reports.filter(r => r.status === "missing").length;
    const found = reports.filter(r => r.status === "found").length;

    return (
        <ReporteeLayout>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">{isFirstLogin ? "Welcome" : "Welcome back"}, {user?.first_name}</h2>
                    <p className="rd-page-subtitle">Track your vehicle reports and their current status</p>
                </div>
            </div>

            <div className="rd-grid-3">
                <article className="rd-card">
                    <div className="rd-stat-label">Total reports filed</div>
                    <strong className="rd-stat-value">{reports.length}</strong>
                    <span className="rd-stat-note">Since Jan 2026</span>
                </article>
                <article className="rd-card">
                    <div className="rd-stat-label">Currently missing</div>
                    <strong className="rd-stat-value">{missing}</strong>
                    <span className="rd-stat-note danger">Active cases</span>
                </article>
                <article className="rd-card">
                    <div className="rd-stat-label">Recovered</div>
                    <strong className="rd-stat-value">{found}</strong>
                    <span className="rd-stat-note success">Vehicle returned</span>
                </article>
            </div>

            <section className="rd-section rd-card">
                <div className="rd-section-head">
                    <h3 className="rd-section-title">Recent reports</h3>
                    <Link className="rd-button small" to="/my/report">+ New report</Link>
                </div>

                {reports.length === 0 ? (
                    <p className="rd-empty">No reports filed yet. Start by creating your first vehicle report.</p>
                ) : (
                    <table className="rd-table">
                        <thead>
                            <tr>
                                <th>Plate</th>
                                <th>Vehicle</th>
                                <th>Reported</th>
                                <th>Status</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {reports.slice(0, 5).map(r => (
                                <tr key={r.id}>
                                    <td><strong>{r.license_plate}</strong></td>
                                    <td>{r.vehicle_make || "Vehicle"} {r.vehicle_model || ""}{r.vehicle_color ? ` - ${r.vehicle_color}` : ""}</td>
                                    <td>{r.report_date?.slice(0, 10)}</td>
                                    <td><span className={`rd-pill ${statusClass(r.status)}`}>{statusLabel(r.status)}</span></td>
                                    <td><Link className="rd-button small" to="/my/reports">View</Link></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </section>
        </ReporteeLayout>
    );
}

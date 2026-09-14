import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { reportsAPI } from "../../services/api";
import ReporteeLayout from "../../components/ReporteeLayout";

function statusClass(status) {
    if (status === "found") return "found";
    if (status === "missing") return "missing";
    return "review";
}

function statusLabel(status) {
    return (status || "under_review").replaceAll("_", " ");
}

export default function MyReports() {
    const [reports, setReports] = useState([]);

    useEffect(() => {
        reportsAPI.getAll().then(r => setReports(r.data));
    }, []);

    return (
        <ReporteeLayout>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">My reports</h2>
                    <p className="rd-page-subtitle">Review every vehicle report connected to your account.</p>
                </div>
                <Link className="rd-button small" to="/my/report">+ New report</Link>
            </div>

            {reports.length === 0 ? (
                <section className="rd-card">
                    <p className="rd-empty">No reports filed yet. <Link to="/my/report">File one now</Link>.</p>
                </section>
            ) : (
                <section className="rd-report-list">
                    {reports.map(r => (
                        <article className="rd-report-card" key={r.id}>
                            <div>
                                <h3 className="rd-report-title">{r.license_plate} - {r.vehicle_make || "Vehicle"} {r.vehicle_model || ""}</h3>
                                <p className="rd-report-meta">Filed: {r.report_date?.slice(0, 10)} - Last seen: {r.last_seen_location || "Not provided"}</p>
                                {r.description && <p className="rd-report-meta">{r.description}</p>}
                            </div>
                            <span className={`rd-pill ${statusClass(r.status)}`}>{statusLabel(r.status)}</span>
                        </article>
                    ))}
                </section>
            )}
        </ReporteeLayout>
    );
}

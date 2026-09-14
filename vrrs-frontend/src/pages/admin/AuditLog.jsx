import PortalLayout from "../../components/PortalLayout";
import { useEffect, useState } from "react";
import { systemAPI } from "../../services/api";

const adminNav = [
    { to: "/admin", label: "Overview", icon: "grid", end: true },
    { to: "/admin/users", label: "User management", icon: "users" },
    { to: "/admin/health", label: "System health", icon: "clock" },
    { to: "/admin/audit", label: "Audit log", icon: "list" },
];

export default function AuditLog() {
    const [rows, setRows] = useState([]);
    const [filter, setFilter] = useState("");

    useEffect(() => {
        systemAPI.audit(filter ? { action: filter } : undefined).then(r => setRows(r.data));
    }, [filter]);

    const exportCsv = () => {
        const header = "Timestamp,Action,Target Table,Target ID";
        const body = rows.map(row => [
            new Date(row.timestamp).toLocaleString(),
            row.action,
            row.target_table || "system",
            row.target_id || "",
        ].map(value => `"${String(value).replaceAll('"', '""')}"`).join(","));
        const blob = new Blob([[header, ...body].join("\n")], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "svds-audit-log.csv";
        link.click();
        URL.revokeObjectURL(url);
    };

    return (
        <PortalLayout portal="Admin Portal" navItems={adminNav}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Audit log</h2>
                    <p className="rd-page-subtitle">Full record of all system actions</p>
                </div>
            </div>

            <section className="rd-card">
                <div className="rd-toolbar" style={{ gridTemplateColumns: "auto minmax(220px, 1fr) auto" }}>
                    <div className="rd-toolbar-title">Activity log</div>
                    <select className="rd-select" value={filter} onChange={e => setFilter(e.target.value)}>
                        <option value="">All actions</option>
                        <option value="account">User actions</option>
                        <option value="report">Report updates</option>
                        <option value="alert">Alert events</option>
                    </select>
                    <button className="rd-button small" onClick={exportCsv}>Export CSV</button>
                </div>

                {rows.map(row => (
                    <div className="rd-audit-row" key={row.id}>
                        <div className="rd-muted">{new Date(row.timestamp).toLocaleString()}</div>
                        <div><strong>{row.action}</strong><br />{row.target_table || "system"} #{row.target_id || "-"}</div>
                    </div>
                ))}
                {rows.length === 0 && <p className="rd-empty">No audit events match this filter.</p>}
            </section>
        </PortalLayout>
    );
}

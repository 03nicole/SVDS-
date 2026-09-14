import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { usersAPI } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import PortalLayout from "../../components/PortalLayout";

const adminNav = [
    { to: "/admin", label: "Overview", icon: "grid", end: true },
    { to: "/admin/users", label: "User management", icon: "users" },
    { to: "/admin/health", label: "System health", icon: "clock" },
    { to: "/admin/audit", label: "Audit log", icon: "list" },
];

function initials(user) {
    return `${user.first_name?.[0] || "U"}${user.last_name?.[0] || ""}`.toUpperCase();
}

export default function UserManagement() {
    const { user: currentUser } = useAuth();
    const [users, setUsers] = useState([]);
    const [search, setSearch] = useState("");
    const [role, setRole] = useState("");
    const [loading, setLoading] = useState(true);
    const [msg, setMsg] = useState("");
    const [error, setError] = useState("");

    const load = (params = {}) => usersAPI.getAll(params).then(r => {
        setUsers(r.data);
        setLoading(false);
    });

    useEffect(() => {
        load();
    }, []);

    const handleSearch = e => {
        const next = e.target.value;
        setSearch(next);
        load({ search: next, role: role || undefined });
    };

    const handleRoleFilter = e => {
        const next = e.target.value;
        setRole(next);
        load({ search: search || undefined, role: next || undefined });
    };

    const handleToggleActive = async (id) => {
        setError("");
        try {
            await usersAPI.toggleActive(id);
            load({ search: search || undefined, role: role || undefined });
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to update user.");
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Permanently delete this user?")) return;
        setError("");
        try {
            await usersAPI.delete(id);
            load({ search: search || undefined, role: role || undefined });
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to delete user.");
        }
    };

    return (
        <PortalLayout portal="Admin Portal" navItems={adminNav}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">User management</h2>
                    <p className="rd-page-subtitle">Manage accounts, roles, and access</p>
                </div>
            </div>

            {msg && <div className="rd-alert success">{msg}</div>}
            {error && <div className="rd-alert error">{error}</div>}

            <section className="rd-card rd-user-management">
                <div className="rd-toolbar">
                    <div className="rd-toolbar-title">All users</div>
                    <input className="rd-input" placeholder="Search name or email" value={search} onChange={handleSearch} />
                    <select className="rd-select" value={role} onChange={handleRoleFilter}>
                        <option value="">All roles</option>
                        <option value="reportee">Reportee</option>
                        <option value="police">Police</option>
                        <option value="admin">Admin</option>
                    </select>
                    <Link className="rd-button small" to="/register?role=police">+ Invite officer</Link>
                </div>

                {loading ? (
                    <p className="rd-empty">Loading users...</p>
                ) : (
                    <div className="rd-table-wrap">
                    <table className="rd-table rd-user-table">
                        <thead>
                            <tr>
                                <th className="user-col">User</th>
                                <th className="email-col">Email</th>
                                <th className="role-col">Role</th>
                                <th className="status-col">Status</th>
                                <th className="actions-col">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(u => (
                                <tr key={u.id}>
                                    <td className="user-col">
                                        <div className="rd-user-cell">
                                            <span className="rd-avatar small">{initials(u)}</span>
                                            <strong>{u.first_name} {u.last_name}</strong>
                                        </div>
                                    </td>
                                    <td className="email-col" title={u.email}>{u.email}</td>
                                    <td className="role-col">
                                        <span className={`rd-role-label ${u.role}`}>{u.role}</span>
                                    </td>
                                    <td className="status-col"><span className={`rd-status-chip ${u.is_active ? "" : "inactive"}`}>{u.is_active ? "Active" : "Inactive"}</span></td>
                                    <td className="actions-col">
                                        {u.id === currentUser?.id ? (
                                            <span className="rd-muted">This is you</span>
                                        ) : (
                                            <div className="rd-user-actions">
                                                <button className="rd-button small" onClick={() => handleToggleActive(u.id)}>{u.is_active ? "Deactivate" : "Reactivate"}</button>
                                                <button className="rd-button small" onClick={() => handleDelete(u.id)}>Delete</button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    </div>
                )}
            </section>
        </PortalLayout>
    );
}

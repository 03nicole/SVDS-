import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const icons = {
    home: "M3 11.5 12 4l9 7.5V21h-6v-6H9v6H3v-9.5z",
    report: "M12 8v5m0 4h.01M21 12A9 9 0 1 1 3 12a9 9 0 0 1 18 0z",
    list: "M4 6h16M4 12h11M4 18h7",
    clipboard: "M9 5h6a2 2 0 0 1 2 2v13H7V7a2 2 0 0 1 2-2zm1-2h4a1 1 0 0 1 1 1v1h-6V4a1 1 0 0 1 1-1zM10 11h4M10 15h4",
    user: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm-7 9a7 7 0 0 1 14 0",
};

function Icon({ name }) {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
            <path d={icons[name]} />
        </svg>
    );
}

function initials(user) {
    const first = user?.first_name?.[0] || "U";
    const last = user?.last_name?.[0] || "";
    return `${first}${last}`.toUpperCase();
}

export default function ReporteeLayout({ children }) {
    const { user, logout } = useAuth();

    return (
        <main className="rd-shell">
            <div className="rd-frame">
                <aside className="rd-sidebar">
                    <div className="rd-brand">
                        <h1 className="rd-brand-title">SVDS</h1>
                        <div className="rd-brand-subtitle">My Account</div>
                    </div>

                    <nav className="rd-nav" aria-label="Reportee navigation">
                        <NavLink to="/my" end className={({ isActive }) => `rd-nav-link${isActive ? " active" : ""}`}>
                            <Icon name="home" />
                            <span>Home</span>
                        </NavLink>
                        <NavLink to="/my/report" className={({ isActive }) => `rd-nav-link${isActive ? " active" : ""}`}>
                            <Icon name="report" />
                            <span>Report vehicle</span>
                        </NavLink>
                        <NavLink to="/my/reports" className={({ isActive }) => `rd-nav-link${isActive ? " active" : ""}`}>
                            <Icon name="clipboard" />
                            <span>My reports</span>
                        </NavLink>
                        <NavLink to="/my/profile" className={({ isActive }) => `rd-nav-link${isActive ? " active" : ""}`}>
                            <Icon name="user" />
                            <span>My profile</span>
                        </NavLink>
                    </nav>

                    <div className="rd-account">
                        <div className="rd-avatar">{initials(user)}</div>
                        <div>
                            <div className="rd-account-name">{user?.first_name} {user?.last_name}</div>
                            <div className="rd-account-role">Public user</div>
                        </div>
                    </div>
                    <button type="button" className="rd-logout" onClick={logout}>Logout</button>
                </aside>

                <section className="rd-content">
                    {children}
                </section>
            </div>
        </main>
    );
}

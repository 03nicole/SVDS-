import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const icons = {
    grid: "M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z",
    users: "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm6 1a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM2 21a7 7 0 0 1 14 0H2zm12.5 0a7.8 7.8 0 0 0-1.7-4.8A5.5 5.5 0 0 1 22 21h-7.5z",
    clock: "M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm1-10.4V7h-2v6l5 3 .9-1.7-3.9-2.7z",
    list: "M4 6h16M4 12h16M4 18h12",
    bell: "M18 16v-5a6 6 0 0 0-12 0v5l-2 2h16l-2-2zm-8 4h4",
    bars: "M5 20V10h3v10H5zm6 0V4h3v16h-3zm6 0v-7h3v7h-3z",
    camera: "M9 3l-1.5 2H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3.5L15 3H9zm3 6a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6z",
};

function Icon({ name }) {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">
            <path d={icons[name]} />
        </svg>
    );
}

export default function PortalLayout({ portal, kicker, navItems, children }) {
    const { logout } = useAuth();

    return (
        <main className="rd-shell">
            {kicker && <div className="rd-kicker">{kicker} &gt;</div>}
            <div className="rd-frame">
                <aside className="rd-sidebar">
                    <div className="rd-brand">
                        <h1 className="rd-brand-title">SVDS</h1>
                        <div className="rd-brand-subtitle">{portal}</div>
                    </div>

                    <nav className="rd-nav" aria-label={`${portal} navigation`}>
                        {navItems.map(item => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                end={item.end}
                                className={({ isActive }) => `rd-nav-link${isActive ? " active" : ""}`}
                            >
                                <Icon name={item.icon} />
                                <span>{item.label}</span>
                                {item.badge ? <span className="rd-nav-badge">{item.badge}</span> : null}
                            </NavLink>
                        ))}
                    </nav>

                    <div className="rd-account">
                        <div className="rd-avatar">VR</div>
                        <div>
                            <div className="rd-account-name">Zambia Police</div>
                            <div className="rd-account-role">{portal}</div>
                        </div>
                    </div>
                    <button className="rd-logout" onClick={logout}>Logout</button>
                </aside>

                <section className="rd-content">
                    {children}
                </section>
            </div>
        </main>
    );
}

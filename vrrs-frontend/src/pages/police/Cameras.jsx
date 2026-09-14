import { useEffect, useState } from "react";
import { systemAPI } from "../../services/api";
import { useAlerts } from "../../context/AlertsContext";
import { getPoliceNav } from "../../config/policeNav";
import PortalLayout from "../../components/PortalLayout";

export default function Cameras() {
    const { unread } = useAlerts();
    const [nodes, setNodes] = useState([]);
    const [feedError, setFeedError] = useState(false);

    useEffect(() => {
        systemAPI.cameraNodes().then(r => setNodes(r.data));
    }, []);

    const online = nodes.filter(n => n.status === "online").length;
    const offline = nodes.filter(n => n.status === "offline").length;

    return (
        <PortalLayout portal="Police Portal" navItems={getPoliceNav(unread)}>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Cameras</h2>
                    <p className="rd-page-subtitle">Live feed and connected camera nodes</p>
                </div>
            </div>

            <div className="rd-grid-2">
                <article className="rd-card"><div className="rd-stat-label">Active cameras</div><strong className="rd-stat-value">{online}/{nodes.length}</strong><span className="rd-stat-note">Live</span></article>
                <article className="rd-card"><div className="rd-stat-label">Offline nodes</div><strong className="rd-stat-value">{offline}</strong><span className="rd-stat-note danger">Needs attention</span></article>
            </div>

            <section className="rd-section rd-card">
                <h3 className="rd-section-title">Live camera feed</h3>
                {feedError ? (
                    <p className="rd-empty">Camera feed unavailable - check the camera node is running and reachable.</p>
                ) : (
                    <img
                        className="rd-live-feed"
                        src={systemAPI.liveFeedUrl()}
                        alt="Live camera feed"
                        onError={() => setFeedError(true)}
                    />
                )}
            </section>

            <section className="rd-section rd-card">
                <h3 className="rd-section-title">Camera nodes</h3>
                <table className="rd-node-list" style={{ marginTop: 24 }}>
                    <thead><tr><th>Node ID</th><th>Location</th></tr></thead>
                    <tbody>
                        {nodes.map(node => <tr key={node.camera_id}><td>{node.camera_id}</td><td>{node.location}<br /><span className="rd-muted">{node.status}</span></td></tr>)}
                    </tbody>
                </table>
            </section>
        </PortalLayout>
    );
}

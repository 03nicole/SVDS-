import { useState } from "react";
import { reportsAPI } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useAlerts } from "../../context/AlertsContext";
import { getPoliceNav } from "../../config/policeNav";
import PortalLayout from "../../components/PortalLayout";
import ReporteeLayout from "../../components/ReporteeLayout";

const emptyForm = {
    license_plate: "",
    vehicle_make: "",
    vehicle_model: "",
    vehicle_color: "",
    vehicle_year: "",
    incident_date: "",
    last_seen_location: "",
    description: "",
};

export default function ReportVehicle() {
    const [form, setForm] = useState(emptyForm);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const { user } = useAuth();
    const { unread } = useAlerts();
    const isPolice = user?.role === "police";

    const handleChange = e => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));

    const handleClear = () => {
        setForm(emptyForm);
        setSuccess(false);
        setError("");
    };

    const handleSubmit = async () => {
        setError("");
        setSuccess(false);
        setLoading(true);
        try {
            await reportsAPI.create({
                ...form,
                license_plate: form.license_plate.toUpperCase().trim(),
                incident_date: form.incident_date || null,
            });
            setSuccess(true);
            setForm(emptyForm);
        } catch (err) {
            setError(err.response?.data?.detail || "Submission failed.");
        } finally {
            setLoading(false);
        }
    };

    const content = (
        <>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">Report vehicle</h2>
                    <p className="rd-page-subtitle">Tell us what was stolen so police can verify and activate the case.</p>
                </div>
            </div>

            {success && <div className="rd-alert success">Report submitted successfully.</div>}
            {error && <div className="rd-alert error">{error}</div>}

            <section className="rd-form-card">
                <h3 className="rd-form-title">Vehicle details</h3>
                <div className="rd-form-grid">
                    <div className="rd-field">
                        <label>License plate *</label>
                        <input name="license_plate" value={form.license_plate} onChange={handleChange} placeholder="e.g. BAA 1234" />
                    </div>
                    <div className="rd-field">
                        <label>Color</label>
                        <input name="vehicle_color" value={form.vehicle_color} onChange={handleChange} placeholder="e.g. White" />
                    </div>
                </div>

                <div className="rd-form-grid three" style={{ marginTop: 26 }}>
                    <div className="rd-field">
                        <label>Make *</label>
                        <input name="vehicle_make" value={form.vehicle_make} onChange={handleChange} placeholder="e.g. Toyota" />
                    </div>
                    <div className="rd-field">
                        <label>Model *</label>
                        <input name="vehicle_model" value={form.vehicle_model} onChange={handleChange} placeholder="e.g. Land Cruiser" />
                    </div>
                    <div className="rd-field">
                        <label>Year</label>
                        <input name="vehicle_year" value={form.vehicle_year} onChange={handleChange} placeholder="e.g. 2019" />
                    </div>
                </div>

            </section>

            <section className="rd-form-card">
                <h3 className="rd-form-title">Incident details</h3>
                <div className="rd-form-grid">
                    <div className="rd-field">
                        <label>Date stolen</label>
                        <input type="date" name="incident_date" value={form.incident_date} onChange={handleChange} />
                    </div>
                    <div className="rd-field">
                        <label>Last seen location *</label>
                        <input name="last_seen_location" value={form.last_seen_location} onChange={handleChange} placeholder="e.g. Lusaka CBD, Cairo Road" />
                    </div>
                    <div className="rd-field full">
                        <label>Description</label>
                        <textarea name="description" value={form.description} onChange={handleChange} placeholder="Add anything useful: markings, stickers, circumstances, or contact notes." />
                    </div>
                </div>
            </section>

            <section className="rd-form-card">
                <h3 className="rd-form-title">What happens after you report?</h3>
                <div className="rd-timeline">
                    <div className="rd-timeline-item">
                        <span className="rd-timeline-dot" />
                        <div>
                            <div className="rd-timeline-title">Report submitted</div>
                            <div className="rd-timeline-copy">Your vehicle details are saved and tagged to your account</div>
                        </div>
                    </div>
                    <div className="rd-timeline-item">
                        <span className="rd-timeline-dot" />
                        <div>
                            <div className="rd-timeline-title">Police review</div>
                            <div className="rd-timeline-copy">A ZPS officer verifies and activates the report in the system</div>
                        </div>
                    </div>
                    <div className="rd-timeline-item">
                        <span className="rd-timeline-dot" />
                        <div>
                            <div className="rd-timeline-title">Camera network scanning</div>
                            <div className="rd-timeline-copy">Your plate is cross-referenced at active road nodes across Zambia</div>
                        </div>
                    </div>
                    <div className="rd-timeline-item muted">
                        <span className="rd-timeline-dot" />
                        <div>
                            <div className="rd-timeline-title">Detection alert</div>
                            <div className="rd-timeline-copy">If spotted, law enforcement is notified immediately and your report is updated</div>
                        </div>
                    </div>
                </div>
            </section>

            <div className="rd-form-actions">
                <button className="rd-button" onClick={handleClear}>Clear form</button>
                <button className="rd-button primary" onClick={handleSubmit} disabled={loading}>
                    {loading ? "Submitting..." : "Submit report"}
                </button>
            </div>
            </>
    );

    return isPolice ? (
        <PortalLayout portal="Police Portal" navItems={getPoliceNav(unread)}>{content}</PortalLayout>
    ) : (
        <ReporteeLayout>{content}</ReporteeLayout>
    );
}

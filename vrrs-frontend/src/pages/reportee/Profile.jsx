import { useEffect, useState } from "react";
import { usersAPI } from "../../services/api";
import ReporteeLayout from "../../components/ReporteeLayout";

export default function Profile() {
    const [profile, setProfile] = useState(null);
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState({});
    const [pwForm, setPwForm] = useState({ current_password: "", new_password: "" });
    const [msg, setMsg] = useState("");

    useEffect(() => {
        usersAPI.getMe().then(r => {
            setProfile(r.data);
            setForm(r.data);
        });
    }, []);

    const handleSave = async () => {
        await usersAPI.updateMe({
            first_name: form.first_name,
            last_name: form.last_name,
            phone: form.phone,
        });
        setProfile(form);
        setEditing(false);
        setMsg("Profile updated.");
    };

    const handlePasswordChange = async () => {
        try {
            await usersAPI.changePassword(pwForm);
            setMsg("Password updated successfully.");
            setPwForm({ current_password: "", new_password: "" });
        } catch (err) {
            setMsg(err.response?.data?.detail || "Failed.");
        }
    };

    if (!profile) {
        return (
            <ReporteeLayout>
                <p className="rd-empty">Loading profile...</p>
            </ReporteeLayout>
        );
    }

    return (
        <ReporteeLayout>
            <div className="rd-topbar">
                <div>
                    <h2 className="rd-page-title">My profile</h2>
                    <p className="rd-page-subtitle">Keep your contact information current for report updates.</p>
                </div>
            </div>

            {msg && <div className="rd-alert success">{msg}</div>}

            <section className="rd-form-card">
                <div className="rd-section-head">
                    <h3 className="rd-form-title" style={{ margin: 0 }}>Account details</h3>
                    {!editing && <button className="rd-button small" onClick={() => setEditing(true)}>Edit profile</button>}
                </div>

                {!editing ? (
                    <div className="rd-profile-grid">
                        {[
                            ["Full name", `${profile.first_name} ${profile.last_name}`],
                            ["Email address", profile.email],
                            ["Phone number", profile.phone || "Not provided"],
                            ["Account role", profile.role],
                        ].map(([label, value]) => (
                            <div className="rd-profile-row" key={label}>
                                <div className="rd-profile-label">{label}</div>
                                <div className="rd-profile-value">{value}</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <>
                        <div className="rd-form-grid">
                            <div className="rd-field">
                                <label>First name</label>
                                <input value={form.first_name || ""} onChange={e => setForm(p => ({ ...p, first_name: e.target.value }))} />
                            </div>
                            <div className="rd-field">
                                <label>Last name</label>
                                <input value={form.last_name || ""} onChange={e => setForm(p => ({ ...p, last_name: e.target.value }))} />
                            </div>
                            <div className="rd-field full">
                                <label>Phone number</label>
                                <input value={form.phone || ""} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} placeholder="+260 97 123 4567" />
                            </div>
                        </div>
                        <div className="rd-form-actions">
                            <button className="rd-button" onClick={() => setEditing(false)}>Cancel</button>
                            <button className="rd-button primary" onClick={handleSave}>Save profile</button>
                        </div>
                    </>
                )}
            </section>

            <section className="rd-form-card">
                <h3 className="rd-form-title">Change password</h3>
                <div className="rd-form-grid">
                    <div className="rd-field">
                        <label>Current password</label>
                        <input type="password" value={pwForm.current_password} onChange={e => setPwForm(p => ({ ...p, current_password: e.target.value }))} />
                    </div>
                    <div className="rd-field">
                        <label>New password</label>
                        <input type="password" value={pwForm.new_password} onChange={e => setPwForm(p => ({ ...p, new_password: e.target.value }))} />
                    </div>
                </div>
                <div className="rd-form-actions">
                    <button className="rd-button primary" onClick={handlePasswordChange}>Update password</button>
                </div>
            </section>
        </ReporteeLayout>
    );
}

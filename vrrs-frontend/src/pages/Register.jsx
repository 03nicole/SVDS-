import { useState } from "react";
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { authAPI, usersAPI } from "../services/api";

export default function Register() {
    const [form, setForm] = useState({ first_name:"",last_name:"",email:"",phone:"",password:"",confirm_password:"",role:"reportee",national_id:"",badge_number:"" });
    const [errors, setErrors] = useState({});
    const [error, setError]     = useState("");
    const [loading, setLoading] = useState(false);
    const navigate  = useNavigate();
    const [searchParams] = useSearchParams();
    const isPoliceInvite = searchParams.get("role") === "police";

    const handleChange = e => {
        const { name, value } = e.target;
        setForm(prev => ({...prev, [name]: value}));
        setErrors(prev => ({...prev, [name]: ""}));
        setError("");
    };

    const validate = () => {
        const nextErrors = {};
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phonePattern = /^\+260[\s-]?\d{2}[\s-]?\d{7}$/;
        const firstName = form.first_name.trim();
        const lastName = form.last_name.trim();
        const email = form.email.trim();
        const phone = form.phone.trim();
        const nationalId = form.national_id.trim();
        const badgeNumber = form.badge_number.trim();

        if (!firstName) nextErrors.first_name = "First name is required.";
        if (!lastName) nextErrors.last_name = "Last name is required.";
        if (!email) nextErrors.email = "Email is required.";
        else if (!emailPattern.test(email)) nextErrors.email = "Enter a valid email address.";
        if (!phone) nextErrors.phone = "Phone number is required.";
        else if (!phonePattern.test(phone)) nextErrors.phone = "Use a Zambian number starting with +260, for example +260 97 1234567.";
        if (form.password.length < 6) nextErrors.password = "Password must be at least 6 characters.";
        if (!form.confirm_password) nextErrors.confirm_password = "Please confirm your password.";
        else if (form.password !== form.confirm_password) nextErrors.confirm_password = "Passwords do not match.";
        if (isPoliceInvite) {
            if (!badgeNumber) nextErrors.badge_number = "Badge number is required.";
        } else {
            if (!nationalId) nextErrors.national_id = "National ID is required.";
            else if (!/^\d{6}\/\d{2}\/\d$/.test(nationalId)) nextErrors.national_id = "Use the format 123456/78/1.";
        }

        setErrors(nextErrors);
        return { valid: Object.keys(nextErrors).length === 0, firstName, lastName, email, phone, nationalId, badgeNumber };
    };

    const handleRegister = async e => {
        e.preventDefault();
        const validation = validate();
        if (!validation.valid) return;
        setError(""); setLoading(true);
        try {
            const { firstName, lastName, email, phone, nationalId, badgeNumber } = validation;
            if (isPoliceInvite) {
                await usersAPI.invite({ first_name: firstName, last_name: lastName, email, phone, password: form.password, badge_number: badgeNumber });
                navigate("/admin/users");
            } else {
                await authAPI.register({ ...form, first_name: firstName, last_name: lastName, email, phone, national_id: nationalId, role: "reportee" });
                navigate("/login", { state: { message: "Account created successfully. Please sign in with your new details.", newlyRegistered: true } });
            }
        } catch (err) {
            setError(err.response?.data?.detail || "Registration failed.");
        } finally { setLoading(false); }
    };

    return (
        <form onSubmit={handleRegister} noValidate style={{maxWidth:480,margin:"4rem auto",padding:"2rem",border:"1px solid #ddd",borderRadius:8}}>
            <h2>{isPoliceInvite ? "SVDS — Create police account" : "SVDS — Create account"}</h2>
            {error && <p style={{color:"red"}}>{error}</p>}
            {["first_name","last_name","email","phone"].map(field => (
                <div key={field} style={{marginBottom:"0.75rem"}}>
                    <label htmlFor={field}>{field.replace("_"," ")}{" *"}</label><br/>
                    <input id={field} type={field === "email" ? "email" : "text"} name={field} value={form[field]} onChange={handleChange} placeholder={field === "phone" ? "+260 97 1234567" : undefined} pattern={field === "phone" ? "\\+260[\\s-]?\\d{2}[\\s-]?\\d{7}" : undefined} aria-invalid={Boolean(errors[field])} aria-describedby={errors[field] ? `${field}-error` : undefined} style={{width:"100%",padding:8}} />
                    {errors[field] && <p id={`${field}-error`} style={{color:"red",fontSize:"0.85rem",margin:"0.25rem 0 0"}}>{errors[field]}</p>}
                </div>
            ))}
            <div style={{marginBottom:"0.75rem"}}>
                <label>Account type</label><br/>
                <select value={isPoliceInvite ? "police" : "reportee"} disabled style={{width:"100%",padding:8,backgroundColor:"#f5f5f5",color:"#666"}}>
                    <option>{isPoliceInvite ? "Police Officer" : "Public Reportee"}</option>
                </select>
                <p style={{fontSize:"0.85rem",color:"#666",marginTop:"0.25rem"}}>{isPoliceInvite ? "This account will have police portal access." : "Police and admin accounts are created by administrators."}</p>
            </div>
            {isPoliceInvite ? (
                <div style={{marginBottom:"0.75rem"}}>
                    <label htmlFor="badge_number">Badge number *</label><br/>
                    <input id="badge_number" name="badge_number" value={form.badge_number} onChange={handleChange} aria-invalid={Boolean(errors.badge_number)} aria-describedby={errors.badge_number ? "badge_number-error" : undefined} style={{width:"100%",padding:8}} />
                    {errors.badge_number && <p id="badge_number-error" style={{color:"red",fontSize:"0.85rem",margin:"0.25rem 0 0"}}>{errors.badge_number}</p>}
                </div>
            ) : (
            <div style={{marginBottom:"0.75rem"}}>
                <label htmlFor="national_id">National ID *</label><br/>
                <input id="national_id" name="national_id" value={form.national_id} onChange={handleChange} placeholder="123456/78/1" pattern="\d{6}/\d{2}/\d" aria-invalid={Boolean(errors.national_id)} aria-describedby={errors.national_id ? "national_id-error" : undefined} style={{width:"100%",padding:8}} />
                {errors.national_id && <p id="national_id-error" style={{color:"red",fontSize:"0.85rem",margin:"0.25rem 0 0"}}>{errors.national_id}</p>}
            </div>
            )}
            <div style={{marginBottom:"0.75rem"}}>
                <label>Password</label><br/>
                <input id="password" type="password" name="password" value={form.password} onChange={handleChange} aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? "password-error" : undefined} style={{width:"100%",padding:8}} />
                {errors.password && <p id="password-error" style={{color:"red",fontSize:"0.85rem",margin:"0.25rem 0 0"}}>{errors.password}</p>}
            </div>
            <div style={{marginBottom:"0.75rem"}}>
                <label htmlFor="confirm_password">Confirm password</label><br/>
                <input id="confirm_password" type="password" name="confirm_password" value={form.confirm_password} onChange={handleChange} aria-invalid={Boolean(errors.confirm_password)} aria-describedby={errors.confirm_password ? "confirm_password-error" : undefined} style={{width:"100%",padding:8}} />
                {errors.confirm_password && <p id="confirm_password-error" style={{color:"red",fontSize:"0.85rem",margin:"0.25rem 0 0"}}>{errors.confirm_password}</p>}
            </div>
            <button type="submit" disabled={loading} style={{width:"100%",padding:10}}>
                {loading ? "Creating account..." : "Create account"}
            </button>
            {!isPoliceInvite && <p style={{marginTop:"1rem",textAlign:"center"}}>Have an account? <Link to="/login">Sign in</Link></p>}
        </form>
    );
}

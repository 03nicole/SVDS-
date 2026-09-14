import { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { authAPI } from "../services/api";

export default function Login() {
    const [email, setEmail]       = useState("");
    const [password, setPassword] = useState("");
    const [error, setError]       = useState("");
    const [loading, setLoading]   = useState(false);
    const { login } = useAuth();
    const navigate  = useNavigate();
    const location  = useLocation();
    const successMessage = location.state?.message;
    const newlyRegistered = location.state?.newlyRegistered;

    const handleLogin = async () => {
        setError(""); setLoading(true);
        try {
            const res = await authAPI.login({ email, password });
            login(res.data.user, res.data.token);
            navigate(res.data.redirect, { state: { newlyRegistered } });
        } catch (err) {
            setError(err.response?.data?.detail || "Login failed.");
        } finally { setLoading(false); }
    };

    return (
        <div style={{maxWidth:400,margin:"4rem auto",padding:"2rem",border:"1px solid #ddd",borderRadius:8}}>
            <h2>SVDS — Sign in</h2>
            {successMessage && <p style={{color:"green"}}>{successMessage}</p>}
            {error && <p style={{color:"red"}}>{error}</p>}
            <div style={{marginBottom:"1rem"}}>
                <label>Email</label><br/>
                <input type="email" value={email} onChange={e=>setEmail(e.target.value)} style={{width:"100%",padding:8}} />
            </div>
            <div style={{marginBottom:"1rem"}}>
                <label>Password</label><br/>
                <input type="password" value={password} onChange={e=>setPassword(e.target.value)} style={{width:"100%",padding:8}} />
            </div>
            <button onClick={handleLogin} disabled={loading} style={{width:"100%",padding:10}}>
                {loading ? "Signing in..." : "Sign in"}
            </button>
            <p style={{marginTop:"1rem",textAlign:"center"}}>No account? <Link to="/register">Register</Link></p>
        </div>
    );
}

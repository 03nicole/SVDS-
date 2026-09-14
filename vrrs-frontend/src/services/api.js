import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("vrrs_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.clear();
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    register: (data) => api.post("/auth/register", data),
    login:    (data) => api.post("/auth/login",    data),
    logout:   ()     => api.post("/auth/logout"),
};

export const reportsAPI = {
    create:    (data)       => api.post("/reports/",              data),
    getAll:    (params)     => api.get("/reports/",               { params }),
    getOne:    (id)         => api.get(`/reports/${id}`),
    update:    (id, data)   => api.patch(`/reports/${id}`,        data),
    activate:  (id)         => api.patch(`/reports/${id}/activate`),
    markFound: (id)         => api.patch(`/reports/${id}/found`),
    delete:    (id)         => api.delete(`/reports/${id}`),
};

export const alertsAPI = {
    getAll:      (params) => api.get("/alerts/",           { params }),
    getOne:      (id)     => api.get(`/alerts/${id}`),
    markRead:    (id)     => api.patch(`/alerts/${id}/read`),
    falsePositive: (id)   => api.patch(`/alerts/${id}/false-positive`),
    markAllRead: ()       => api.patch("/alerts/read-all"),
    unreadCount: ()       => api.get("/alerts/unread/count"),
};

export const usersAPI = {
    invite:         (data)      => api.post("/users/invite", data),
    getMe:          ()          => api.get("/users/me"),
    updateMe:       (data)      => api.patch("/users/me",             data),
    changePassword: (data)      => api.patch("/users/me/password",    data),
    getAll:         (params)    => api.get("/users/",                 { params }),
    getOne:         (id)        => api.get(`/users/${id}`),
    changeRole:     (id, role)  => api.patch(`/users/${id}/role`,     { role }),
    toggleActive:   (id)        => api.patch(`/users/${id}/toggle-active`),
    delete:         (id)        => api.delete(`/users/${id}`),
};

export const analyticsAPI = {
    summary:           ()          => api.get("/analytics/summary"),
    reportsPerMonth:   (months=6)  => api.get("/analytics/reports-per-month",  { params: { months } }),
    statusBreakdown:   ()          => api.get("/analytics/status-breakdown"),
    detectionsPerNode: ()          => api.get("/analytics/detections-per-node"),
    alertsOverTime:    (days=30)   => api.get("/analytics/alerts-over-time",   { params: { days } }),
    recoveryTime:      ()          => api.get("/analytics/recovery-time"),
    userGrowth:        (months=6)  => api.get("/analytics/user-growth",        { params: { months } }),
};

export const systemAPI = {
    audit:       (params) => api.get("/system/audit",        { params }),
    health:      ()       => api.get("/system/health"),
    cameraNodes: ()       => api.get("/system/camera-nodes"),
    liveFeedUrl: ()       => `${BASE_URL}/system/live-feed?token=${localStorage.getItem("vrrs_token")}`,
};

export const createAlertSocket = (onMessage) => {
    const token = localStorage.getItem("vrrs_token");
    const ws = new WebSocket(`${WS_BASE_URL}/alerts/ws?token=${token}`);
    ws.onopen    = () => { setInterval(() => ws.readyState === 1 && ws.send("ping"), 30000); };
    ws.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.onclose   = () => console.log("[WS] Disconnected");
    ws.onerror   = (e) => console.error("[WS] Error:", e);
    return ws;
};

export default api;

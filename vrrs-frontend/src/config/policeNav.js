export const getPoliceNav = (unread) => [
    { to: "/police", label: "Vehicle registry", icon: "list", end: true },
    { to: "/police/alerts", label: "Live alerts", icon: "bell", badge: unread || undefined },
    { to: "/police/cameras", label: "Cameras", icon: "camera" },
    { to: "/police/analytics", label: "Analytics", icon: "bars" },
];

import { useAlerts } from "../context/AlertsContext";

export default function NotificationToast() {
    const { notification, dismissNotification } = useAlerts();
    if (!notification) return null;

    return (
        <div className="rd-detection-notification rd-toast" role="alert">
            <div>
                <strong>Vehicle detected</strong>
                <span>
                    {notification.plate} spotted at {notification.location || "an active camera"}
                    {notification.camera_id ? ` - ${notification.camera_id}` : ""}
                    {notification.confidence ? ` (${notification.confidence}% confidence)` : ""}
                </span>
            </div>
            <button type="button" onClick={dismissNotification} aria-label="Dismiss detection notification">Dismiss</button>
        </div>
    );
}

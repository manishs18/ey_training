export default function NotificationBanner({ notifications = [], onClose = () => {} }) {
  if (!notifications || !notifications.length) return null
  return (
    <div className="notification-banner">
      <div className="notification-content">
        {notifications.map((msg, i) => (
          <div className="notification-item" key={i}>
            <p>{msg}</p>
          </div>
        ))}
      </div>
      <button className="notification-close" onClick={onClose} aria-label="Dismiss notifications">×</button>
    </div>
  )
}

// //새 알림이 들어오면 자동 팝업
// import React, { useEffect } from "react";
// import { useNotifications } from "../context/NotificationContext";

// export default function NotificationToast() {
//   const { lastAdded, setLastAdded, markRead } = useNotifications();

//   useEffect(() => {
//     if (!lastAdded) return;
//     const t = setTimeout(() => setLastAdded(null), 4000); // 4초 후 자동 닫힘
//     return () => clearTimeout(t);
//   }, [lastAdded, setLastAdded]);

//   if (!lastAdded) return null;

//   const n = lastAdded;
//   const tone =
//     n.type === "critical" ? "#fee2e2" : n.type === "warning" ? "#fef3c7" : "#e0f2fe";
//   const border =
//     n.type === "critical" ? "#ef4444" : n.type === "warning" ? "#f59e0b" : "#0284c7";

//   return (
//     <div
//       role="alert"
//       style={{
//         position: "fixed",
//         top: 20,
//         left: "50%",
//         transform: "translateX(-50%)",
//         zIndex: 2000,
//         background: "#fff",
//         border: `2px solid ${border}`,
//         boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
//         borderRadius: 12,
//         minWidth: 340,
//         maxWidth: 520,
//         padding: 14,
//       }}
//       onClick={() => {
//         markRead(n.id);
//         setLastAdded(null);
//       }}
//       title="클릭하면 읽음 처리"
//     >
//       <div style={{ fontWeight: 800, marginBottom: 6 }}>
//         {n.type === "critical" ? "🚨 긴급" : n.type === "warning" ? "⚠️ 주의" : "ℹ️ 알림"} — {n.title}
//       </div>
//       <div style={{ whiteSpace: "pre-wrap" }}>{n.message}</div>
//       <div style={{ height: 6, background: tone, borderRadius: 6, marginTop: 10 }} />
//     </div>
//   );
// }

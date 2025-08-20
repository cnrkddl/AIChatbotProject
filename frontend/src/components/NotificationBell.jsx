// //헤더에 붙일 알림창 아이콘//
// import React, { useEffect, useRef, useState } from "react";
// import { useNotifications } from "../context/NotificationContext";
// import NotificationCenter from "./NotificationCenter";

// export default function NotificationBell() {
//   const { unreadCount } = useNotifications();
//   const [open, setOpen] = useState(false);
//   const ref = useRef(null);

//   useEffect(() => {
//     const onClick = (e) => {
//       if (ref.current && !ref.current.contains(e.target)) setOpen(false);
//     };
//     document.addEventListener("click", onClick);
//     return () => document.removeEventListener("click", onClick);
//   }, []);

//   return (
//     <div ref={ref} style={{ position: "relative" }}>
//       <button
//         aria-label="알림"
//         onClick={() => setOpen((v) => !v)}
//         style={{
//           position: "relative",
//           width: 40,
//           height: 40,
//           borderRadius: 12,
//           border: "1px solid #e5e7eb",
//           background: "#fff",
//           cursor: "pointer",
//           fontSize: 20,
//         }}
//         title="알림"
//       >
//         🔔
//         {unreadCount > 0 && (
//           <span
//             style={{
//               position: "absolute",
//               top: -6,
//               right: -6,
//               minWidth: 18,
//               height: 18,
//               padding: "0 4px",
//               borderRadius: 999,
//               background: "#ef4444",
//               color: "#fff",
//               fontSize: 11,
//               lineHeight: "18px",
//               textAlign: "center",
//               fontWeight: 700,
//               boxShadow: "0 0 0 2px #fff",
//             }}
//           >
//             {unreadCount}
//           </span>
//         )}
//       </button>

//       {open && <NotificationCenter onClose={() => setOpen(false)} />}
//     </div>
//   );
// }

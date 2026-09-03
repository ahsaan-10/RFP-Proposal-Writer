export const metadata = { title: "RFP Proposal Writer" };
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#f7f7f8", color: "#1a1a1a" }}>
        {children}
      </body>
    </html>
  );
}

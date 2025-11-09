export const metadata = {
  title: "AI Forex Bot",
  description: "Gemini-driven MT5 trading orchestrator"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system', background: '#0b1020', color: '#eef2ff' }}>
        <div style={{ maxWidth: 1000, margin: '0 auto', padding: 24 }}>
          <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
            <h1 style={{ fontSize: 22, fontWeight: 700 }}>AI Forex Bot</h1>
            <a href="/" style={{ color: '#93c5fd' }}>Dashboard</a>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}

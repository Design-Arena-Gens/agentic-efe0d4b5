import Link from 'next/link';

export default async function Page() {
  const res = await fetch(`${process.env.VERCEL_URL ? 'https://' + process.env.VERCEL_URL : ''}/api/agent/status`, { cache: 'no-store' }).catch(() => undefined);
  const status = res?.ok ? await res.json() : { agents: 0, lastHeartbeat: null };

  return (
    <main>
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Connected Agents</h2>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{status.agents}</div>
          <div style={{ color: '#94a3b8', marginTop: 6 }}>Last heartbeat: {status.lastHeartbeat ?? '?'}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Signal API</h2>
          <div style={{ color: '#94a3b8' }}>POST <code>/api/signal</code> with OHLCV to get a trade signal.</div>
          <Link href="/api-docs" style={{ color: '#93c5fd', marginTop: 8, display: 'inline-block' }}>API Docs</Link>
        </div>
      </section>
    </main>
  );
}

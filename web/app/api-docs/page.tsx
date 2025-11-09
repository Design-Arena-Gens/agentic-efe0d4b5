export default function ApiDocs() {
  return (
    <main>
      <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Signal API</h2>
      <pre style={{ background: '#0f172a', border: '1px solid #1e293b', padding: 16, borderRadius: 8, overflowX: 'auto' }}>
{`POST /api/signal
Content-Type: application/json

{
  "symbol": "EURUSD",
  "timeframe": "M5",
  "candles": [
    { "time": 1690000000, "open": 1.1010, "high": 1.1020, "low": 1.1000, "close": 1.1015, "volume": 1200 }
    // ... >= 50 items, most-recent last
  ]
}

Response 200
{
  "symbol": "EURUSD",
  "timeframe": "M5",
  "signal": "buy|sell|none",
  "confidence": 0.0-1.0,
  "entry": 1.1015,
  "stopLoss": 1.0990,
  "takeProfit": 1.1050,
  "rationale": "..."
}`}
      </pre>
    </main>
  );
}

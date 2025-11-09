import { NextRequest, NextResponse } from "next/server";
import { analyzeWithGemini, SignalSchema, type OHLCV } from "@/lib/gemini";
import { computeATR, defaultStops } from "@/lib/strategy";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const symbol: string = body.symbol;
    const timeframe: string = body.timeframe ?? "M5";
    const candles: OHLCV[] = body.candles;
    if (!symbol || !Array.isArray(candles) || candles.length < 50) {
      return NextResponse.json({ error: "symbol and candles[50+] required" }, { status: 400 });
    }

    const ai = await analyzeWithGemini(symbol, timeframe, candles);

    if (ai.signal === "none") return NextResponse.json(ai);

    const last = candles.at(-1)!;
    const entry = ai.entry ?? last.close;
    const atr = computeATR(candles);
    const stops = defaultStops(entry, atr, ai.signal);

    const merged = SignalSchema.parse({
      symbol,
      timeframe,
      signal: ai.signal,
      confidence: ai.confidence,
      entry,
      stopLoss: ai.stopLoss ?? stops.sl,
      takeProfit: ai.takeProfit ?? stops.tp,
      rationale: ai.rationale
    });

    return NextResponse.json(merged);
  } catch (e: any) {
    return NextResponse.json({ error: e?.message ?? "unknown" }, { status: 500 });
  }
}

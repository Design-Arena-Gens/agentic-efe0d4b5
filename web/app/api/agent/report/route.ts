import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const secret = process.env.WEBHOOK_SECRET;
  const header = req.headers.get("x-webhook-secret");
  if (!secret || header !== secret) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const body = await req.json();
  console.log("Agent report:", JSON.stringify(body).slice(0, 500));
  return NextResponse.json({ ok: true });
}

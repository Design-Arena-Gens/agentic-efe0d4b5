import { NextRequest, NextResponse } from "next/server";
import { getStore } from "../store";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const secret = process.env.WEBHOOK_SECRET;
  const header = req.headers.get("x-webhook-secret");
  if (!secret || header !== secret) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await req.json();
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 });
  const store = getStore();
  if (!store.agents[id]) store.agents[id] = { id, lastHeartbeat: null };
  store.agents[id].lastHeartbeat = Date.now();
  return NextResponse.json({ ok: true });
}

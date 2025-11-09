import { NextResponse } from "next/server";
import { getStore } from "../store";

export const dynamic = "force-dynamic";

export async function GET() {
  const store = getStore();
  const agents = Object.values(store.agents);
  const lastHeartbeat = agents.sort((a, b) => (b.lastHeartbeat ?? 0) - (a.lastHeartbeat ?? 0))[0]?.lastHeartbeat ?? null;
  return NextResponse.json({ agents: agents.length, lastHeartbeat });
}

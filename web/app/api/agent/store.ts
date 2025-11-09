type AgentInfo = { id: string; lastHeartbeat: number | null };

type Store = { agents: Record<string, AgentInfo> };

const globalForStore = global as unknown as { __AGENT_STORE__?: Store };

function init(): Store { return { agents: {} }; }

export function getStore(): Store {
  if (!globalForStore.__AGENT_STORE__) globalForStore.__AGENT_STORE__ = init();
  return globalForStore.__AGENT_STORE__;
}

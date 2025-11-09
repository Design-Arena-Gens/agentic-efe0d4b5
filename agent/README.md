# Local MT5 Agent

Runs on your Windows PC alongside MetaTrader 5 to execute trades from the web orchestrator.

## Setup

1. Install Python 3.11+
2. Copy `config.example.json` to `config.json` and fill values:
   - `terminal_path`: e.g. `G:\\Program Files\\terminal64\\terminal64.exe`
   - `mt5.login`, `mt5.password`, `mt5.server`: your broker credentials (optional if terminal is already logged in)
   - `webhook_secret`: must match the web app `WEBHOOK_SECRET`
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the agent:

```bash
set BOT_CONFIG=%cd%\config.json
python main.py
```

The agent:
- Launches MT5 terminal if not running
- Fetches candles from MT5
- Calls the web `/api/signal` to get AI-generated trade signals
- Applies risk management and places orders
- Reports executions back to the web app

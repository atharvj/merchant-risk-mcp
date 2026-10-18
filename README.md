# Merchant Risk Evaluation MCP

A tiny learning project using the **official Python MCP SDK 2.3.0**.
It exposes exactly one tool, `evaluate_merchant_risk(merchant_name, website_url=None)`.

| Exact merchant name | Result |
| --- | --- |
| Demo Safe Store | LOW |
| Demo Review Store | MEDIUM |
| Demo Risk Store | HIGH |
| Any other name (including different capitalization) | UNKNOWN |

Every result contains `merchant_name`, `risk_level`, `reason`, and `demo_only: true`.
These are fictional examples, never real assessments. The website is ignored.
The tool performs no network requests, research, AI inference, or external actions.
Its only write is a local invocation log; it does not modify merchant/customer data.
No API key or authentication is needed for this demo.

## 1. Install (macOS Terminal)

Use Python 3.10 or newer; Python 3.12 is installed on this laptop.

```bash
cd /Users/atharvjoshi/Downloads/coding/merchant-risk-mcp
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

A **virtual environment** (`.venv`) keeps this project's Python dependencies separate.
If this environment was already created and installed by Codex, skip this step.

## 2. Start the server

```bash
cd /Users/atharvjoshi/Downloads/coding/merchant-risk-mcp
.venv/bin/python server.py
```

Leave this Terminal open. The endpoint is `http://127.0.0.1:8000/mcp`.
`127.0.0.1` means this laptop. An **endpoint** is the address clients use to talk
to the server. **Streamable HTTP** is MCP's method for exchanging messages over HTTP.
Press **Control+C** to stop it. If port 8000 is occupied, stop your earlier copy.

## 3. Test locally (a second Terminal)

```bash
cd /Users/atharvjoshi/Downloads/coding/merchant-risk-mcp
.venv/bin/python test_mcp.py
tail -n 8 invocations.log
```

Expect four printed JSON results and `OK`. The test uses an actual MCP client
over HTTP: it discovers the tool, checks its schemas and read-only annotation,
calls all four cases, confirms URLs do not affect results, and checks missing-name
validation. Eight timestamped log entries show the Python handler ran.
The log records the name and result, never the optional URL.

**MCP** is a standard way for an AI app to discover and call functions in another
program. `@mcp.tool()` makes this Python function discoverable. Its parameter types
describe the accepted inputs; `RiskResult` describes the output structure
(these descriptions are called **schemas**). The SDK handles MCP messages.

## 4. Temporary HTTPS tunnel (after the local test)

A **tunnel** gives your local server a temporary public HTTPS address that
ChatGPT can reach. Anyone with the address can call this unauthenticated demo;
use fictional names and stop the tunnel after your demonstration.

Install Cloudflare's tunnel program once using Homebrew (installed on this laptop):

```bash
brew install cloudflared
```

In a third Terminal, leaving the server running:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Copy the printed `https://...trycloudflare.com` address. Keep the tunnel running.
In the server Terminal, press Control+C and restart with the **exact hostname**
(replace the example below; omit `https://` and `/mcp` in this variable):

```bash
MCP_PUBLIC_HOST=your-actual-host.trycloudflare.com .venv/bin/python server.py
```

This explicitly allows your tunnel's HTTP Host header while keeping the SDK's
host validation enabled. The MCP address is `https://your-actual-host.trycloudflare.com/mcp`.
Check it with the same client test from the second Terminal:

```bash
MCP_TEST_URL=https://your-actual-host.trycloudflare.com/mcp .venv/bin/python test_mcp.py
```

That verifies the tunnel, not a ChatGPT or Grok connection. A new tunnel may have
a new hostname; update the variable and connection URL when that happens.

## 5. Connect to ChatGPT Work (your account)

According to [OpenAI's current connection guide](https://developers.openai.com/plugins/deploy/connect-chatgpt),
account and workspace policies control access to custom MCP servers.

1. Open [ChatGPT Plugins](https://chatgpt.com/plugins).
2. Select **+**, then **Add custom MCP server**.
3. Name it `Merchant Risk Demo`; describe it as fictional hardcoded demo results.
4. Choose the public URL connection and enter your full HTTPS URL ending in `/mcp`.
5. Choose no authentication for this demo if the form offers it; review the warning
   and select **I understand and want to continue**, then **Create as a plugin**.
6. Check that `evaluate_merchant_risk` was discovered, and install/enable the plugin.
7. In a new Work conversation, type `@` and select your plugin. Ask:
   `Call evaluate_merchant_risk for Demo Safe Store. Show its returned demo data.`
8. Confirm a real tool call appears in ChatGPT and a **new** `Demo Safe Store`
   entry appears in `invocations.log`. Expect LOW and `demo_only: true`.

If your account lacks that menu or option, pause and report what you see.
Do not claim ChatGPT success from an answer alone: confirm the tool call and log.
The endpoint also uses standard MCP transport for a compatible Grok client;
Grok's account-specific setup and real tool calling have not been verified here.

Stop the tunnel and server with Control+C in their respective Terminals when done.

## Official references

- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [SDK HTTP server configuration](https://py.sdk.modelcontextprotocol.io/run/)
- [Cloudflare temporary tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

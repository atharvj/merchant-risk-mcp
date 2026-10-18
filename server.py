"""A fictional merchant-risk demonstration using the official MCP SDK."""

import json
import logging
import os
from pathlib import Path
from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

mcp = MCPServer("Merchant Risk Evaluation Demo", version="0.1.0")

# A separate local log proves that the Python function executed.
logger = logging.getLogger("merchant_risk.invocations")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.FileHandler(
    Path(__file__).with_name("invocations.log"), encoding="utf-8", delay=True
)
handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(handler)

DEMO_RISKS = {
    "Demo Safe Store": "LOW",
    "Demo Review Store": "MEDIUM",
    "Demo Risk Store": "HIGH",
}


class RiskResult(BaseModel):
    merchant_name: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"]
    reason: str
    demo_only: Literal[True] = True


@mcp.tool(
    annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False),
)
def evaluate_merchant_risk(
    merchant_name: Annotated[str, Field(description="Merchant name to look up.")],
    website_url: Annotated[
        str | None, Field(description="Optional website URL; never visited or assessed.")
    ] = None,
) -> RiskResult:
    """Call when the user asks to evaluate merchant risk.

    Returns fictional, hardcoded demonstration results only: Demo Safe Store
    is LOW, Demo Review Store is MEDIUM, and Demo Risk Store is HIGH.
    Names must match exactly; all other names return UNKNOWN.
    The optional website URL is ignored. No research or real risk assessment
    takes place. Never present these results as evidence of safety or fraud.
    """
    risk_level = DEMO_RISKS.get(merchant_name, "UNKNOWN")
    reason = (
        f"Fictional demo: this example merchant is hardcoded as {risk_level}. "
        "No real risk assessment was performed."
        if risk_level != "UNKNOWN"
        else "No fictional demo entry exists for this name. "
        "No real risk assessment was performed."
    )
    result = RiskResult(merchant_name=merchant_name, risk_level=risk_level, reason=reason)
    logger.info(json.dumps({"tool": "evaluate_merchant_risk", **result.model_dump()}))
    return result


if __name__ == "__main__":
    # Permit localhost, this exact ngrok host, and an optional configured tunnel host.
    allowed_hosts = ["127.0.0.1:*", "localhost:*"]
    allowed_origins = ["http://127.0.0.1:*", "http://localhost:*"]
    allowed_hosts.extend([
        "stooge-slinging-divisible.ngrok-free.dev",
        "stooge-slinging-divisible.ngrok-free.dev:443",
    ])
    allowed_origins.append("https://stooge-slinging-divisible.ngrok-free.dev")
    public_host = os.environ.get("MCP_PUBLIC_HOST", "").strip()
    if public_host:
        allowed_hosts.append(public_host)
        allowed_origins.append(f"https://{public_host}")
    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8000,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=allowed_hosts, allowed_origins=allowed_origins
        ),
    )

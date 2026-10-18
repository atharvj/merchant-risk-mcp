# Merchant Risk MCP

A Python MCP server I built to experiment with connecting custom tools to AI agents.

The server exposes an `evaluate_merchant_risk` tool that returns mock risk assessments for fictional merchants. It supports different risk levels and returns structured results that an AI agent can use.

I built it using the Python MCP SDK and Streamable HTTP, then connected it to ChatGPT Work through an HTTPS tunnel. I also wrote a test script and used server logs to verify that the agent was actually calling my Python code.

This was mainly a project to get some hands-on experience with MCP, HTTP debugging, and AI tool integration.

The risk evaluations use synthetic data, not real merchant information.

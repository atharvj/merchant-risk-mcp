"""Run against a running server: .venv/bin/python test_mcp.py"""

import json
import os
import unittest

from mcp import Client

MCP_URL = os.environ.get("MCP_TEST_URL", "http://127.0.0.1:8000/mcp")


class MerchantRiskMCPTest(unittest.IsolatedAsyncioTestCase):
    async def test_tool_over_http(self):
        async with Client(MCP_URL, read_timeout_seconds=10) as client:
            tools = (await client.list_tools()).tools
            self.assertEqual([tool.name for tool in tools], ["evaluate_merchant_risk"])
            tool = tools[0]
            self.assertEqual(tool.input_schema["required"], ["merchant_name"])
            self.assertIn("website_url", tool.input_schema["properties"])
            self.assertIsNotNone(tool.output_schema)
            self.assertTrue(tool.annotations.read_only_hint)
            self.assertFalse(tool.annotations.open_world_hint)

            for name, level in (
                ("Demo Safe Store", "LOW"),
                ("Demo Review Store", "MEDIUM"),
                ("Demo Risk Store", "HIGH"),
                ("Unlisted Example Store", "UNKNOWN"),
            ):
                with self.subTest(merchant=name):
                    arguments = {"merchant_name": name}
                    result = await client.call_tool("evaluate_merchant_risk", arguments)
                    self.assertFalse(result.is_error)
                    data = result.structured_content
                    self.assertEqual(
                        set(data), {"merchant_name", "risk_level", "reason", "demo_only"}
                    )
                    self.assertEqual(data["merchant_name"], name)
                    self.assertEqual(data["risk_level"], level)
                    self.assertIs(data["demo_only"], True)
                    self.assertIn("No real risk assessment", data["reason"])
                    print(json.dumps(data, indent=2))

                    # Adding a URL cannot change the result, even for UNKNOWN.
                    arguments["website_url"] = "https://unused.example"
                    repeated = await client.call_tool("evaluate_merchant_risk", arguments)
                    self.assertFalse(repeated.is_error)
                    self.assertEqual(repeated.structured_content, data)

            invalid = await client.call_tool("evaluate_merchant_risk", {})
            self.assertTrue(invalid.is_error)  # SDK rejects a missing required name.


if __name__ == "__main__":
    unittest.main(verbosity=2)

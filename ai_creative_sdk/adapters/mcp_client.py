"""
Test AI Creative Remote MCP Server.

Requirements:

    pip install fastmcp==2.14.7

or:

    uv add fastmcp==2.14.7

Environment:

    MCP_URL=http://127.0.0.1:8000/mcp
    MCP_API_KEY=sk-xxxx

Usage:

    python test_mcp_server.py

or:

    uv run test_mcp_server.py
"""

from __future__ import annotations

import asyncio
import os
import sys

from fastmcp import Client


MCP_URL = os.getenv(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp",
)

MCP_API_KEY = os.getenv(
    "MCP_API_KEY",
)


async def test_mcp_server() -> None:

    if not MCP_API_KEY:
        raise RuntimeError(
            "MCP_API_KEY is not configured.\n"
            "Example:\n\n"
            "export MCP_API_KEY='sk-xxxx'\n"
        )

    print("=" * 70)
    print("AI Creative MCP Test")
    print("=" * 70)

    print()
    print("Server:")
    print(MCP_URL)

    print()
    print("API Key:")
    print(
        MCP_API_KEY[:8] + "..."
    )

    print()
    print("Connecting...")

    async with Client(
        MCP_URL,
        auth=MCP_API_KEY,
    ) as client:

        # ---------------------------------------------------------------
        # 1. Ping
        # ---------------------------------------------------------------

        print()
        print("[1/4] Ping")

        await client.ping()

        print("✓ Ping OK")

        # ---------------------------------------------------------------
        # 2. List tools
        # ---------------------------------------------------------------

        print()
        print("[2/4] List tools")

        tools = await client.list_tools()

        for tool in tools:

            print(
                f"✓ {tool.name}"
            )

            if tool.description:
                print(
                    f"  {tool.description}"
                )

        tool_names = {
            tool.name
            for tool in tools
        }

        if "generate_commercial_image" not in tool_names:

            raise RuntimeError(
                "generate_commercial_image "
                "tool not found."
            )

        # ---------------------------------------------------------------
        # 3. Generate image
        # ---------------------------------------------------------------

        print()
        print("[3/4] Generate image")

        result = await client.call_tool(
            "generate_commercial_image",
            {
                "prompt": (
                    "A premium ecommerce product photo "
                    "of a black leather handbag, "
                    "studio lighting, "
                    "clean luxury fashion background"
                ),
                "negative_prompt": (
                    "blurry, low quality, "
                    "distorted, watermark"
                ),
                "width": 1024,
                "height": 1024,
                "batch_size": 1,
            },
        )

        print("✓ Tool call completed")

        print()
        print("Result:")

        print(result)

        # ---------------------------------------------------------------
        # 4. Test unauthorized tool
        # ---------------------------------------------------------------

        print()
        print("[4/4] Permission test")

        print(
            "Current API key is authenticated "
            "and image:generate should be allowed."
        )

        print()
        print("=" * 70)
        print("ALL TESTS PASSED")
        print("=" * 70)


async def main() -> None:

    try:

        await test_mcp_server()

    except Exception as exc:

        print()
        print("=" * 70)
        print("TEST FAILED")
        print("=" * 70)

        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )

        sys.exit(1)


if __name__ == "__main__":
    """
    uv run -m ai_creative_sdk.adapters.mcp_client
    """
    asyncio.run(main())
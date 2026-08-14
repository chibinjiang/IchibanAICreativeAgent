"""Minimal stdio MCP server exposing AI Creative SDK image generation tools.

Run with:
    uv run -m ai_creative_sdk.adapters.mcp_server
"""

import asyncio
import json
import os
import sys
from typing import Any

from ai_creative_sdk.providers.comfyui.provider import TOKEN, ComfyUIProvider
from ai_creative_sdk.skills.commercial_image import CommercialImageSkill

DEFAULT_WORKFLOW_PATH = "workflows/zimage_txt2img_api.json"
SERVER_NAME = "ai-creative-sdk"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"

TOOL_SCHEMA: dict[str, Any] = {
    "name": "generate_commercial_image",
    "description": "Generate a commercial image through the configured ComfyUI workflow.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Positive prompt describing the desired image."},
            "negative_prompt": {
                "type": "string",
                "description": "Negative prompt to avoid unwanted content when supported by the workflow.",
                "default": "",
            },
            "width": {"type": "integer", "description": "Target image width in pixels.", "default": 1024},
            "height": {"type": "integer", "description": "Target image height in pixels.", "default": 1024},
            "batch_size": {
                "type": "integer",
                "description": "Number of images to generate when supported by the workflow.",
                "default": 1,
            },
            "seed": {
                "type": ["integer", "null"],
                "description": "Optional random seed for reproducible results.",
                "default": None,
            },
            "workflow_path": {
                "type": ["string", "null"],
                "description": "Optional workflow JSON path. Defaults to AI_CREATIVE_WORKFLOW_PATH or z-image workflow.",
                "default": None,
            },
        },
        "required": ["prompt"],
    },
}


def _write_message(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _success(message_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}
    if data is not None:
        payload["error"]["data"] = data
    return payload


def _get_provider(workflow_path: str | None = None) -> ComfyUIProvider:
    """Create a ComfyUI provider from MCP tool input and environment config."""
    return ComfyUIProvider(
        workflow_path=workflow_path or os.getenv("AI_CREATIVE_WORKFLOW_PATH", DEFAULT_WORKFLOW_PATH),
        host=os.getenv("COMFYUI_HOST", "115.190.131.64"),
        port=int(os.getenv("COMFYUI_PORT", "7188")),
        token=os.getenv("COMFYUI_TOKEN", TOKEN),
        timeout=int(os.getenv("COMFYUI_TIMEOUT", "300")),
    )


async def generate_commercial_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    batch_size: int = 1,
    seed: int | None = None,
    workflow_path: str | None = None,
) -> dict[str, Any]:
    """Generate a commercial image through the configured ComfyUI workflow."""
    provider = _get_provider(workflow_path)
    skill = CommercialImageSkill(provider)
    try:
        result = await skill.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            batch_size=batch_size,
            seed=seed,
        )
        return result.model_dump()
    finally:
        await provider.close()


async def _handle_tool_call(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name != TOOL_SCHEMA["name"]:
        raise ValueError(f"Unknown tool: {name}")
    result = await generate_commercial_image(**arguments)
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False),
            }
        ],
        "isError": not result.get("success", False),
    }


async def _handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    message_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if message_id is None:
        return None

    try:
        if method == "initialize":
            return _success(
                message_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            )
        if method == "tools/list":
            return _success(message_id, {"tools": [TOOL_SCHEMA]})
        if method == "tools/call":
            return _success(message_id, await _handle_tool_call(params))
        if method == "ping":
            return _success(message_id, {})
        return _error(message_id, -32601, f"Method not found: {method}")
    except Exception as exc:
        return _error(message_id, -32000, str(exc), {"type": exc.__class__.__name__})


async def _run_stdio() -> None:
    while line := await asyncio.to_thread(sys.stdin.readline):
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_message(_error(None, -32700, "Parse error", str(exc)))
            continue
        response = await _handle_request(message)
        if response is not None:
            _write_message(response)


def main() -> None:
    """Run the MCP server over stdio for local Agent integrations."""
    asyncio.run(_run_stdio())


if __name__ == "__main__":
    main()

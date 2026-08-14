"""FastMCP stdio server exposing AI Creative SDK image generation tools.

Run with:
    uv run -m ai_creative_sdk.adapters.mcp_server
"""

import os
from typing import Any

from fastmcp import FastMCP

from ai_creative_sdk.providers.comfyui.provider import TOKEN, ComfyUIProvider
from ai_creative_sdk.skills.commercial_image import CommercialImageSkill

DEFAULT_WORKFLOW_PATH = "workflows/zimage_txt2img_api.json"
SERVER_NAME = "ai-creative-sdk"
SERVER_VERSION = "0.1.0"

mcp = FastMCP(name=SERVER_NAME)


def _get_provider(workflow_path: str | None = None) -> ComfyUIProvider:
    """Create a ComfyUI provider from MCP tool input and environment config."""
    return ComfyUIProvider(
        workflow_path=workflow_path or os.getenv("AI_CREATIVE_WORKFLOW_PATH", DEFAULT_WORKFLOW_PATH),
        host=os.getenv("COMFYUI_HOST", "115.190.131.64"),
        port=int(os.getenv("COMFYUI_PORT", "7188")),
        token=os.getenv("COMFYUI_TOKEN", TOKEN),
        timeout=int(os.getenv("COMFYUI_TIMEOUT", "300")),
    )


@mcp.tool(
    name="generate_commercial_image",
    description="Generate a commercial image through the configured ComfyUI workflow.",
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
    """Generate a commercial image through the configured ComfyUI workflow.

    Args:
        prompt: Positive prompt describing the desired image.
        negative_prompt: Negative prompt to avoid unwanted content when supported by the workflow.
        width: Target image width in pixels.
        height: Target image height in pixels.
        batch_size: Number of images to generate when supported by the workflow.
        seed: Optional random seed for reproducible results.
        workflow_path: Optional workflow JSON path. Defaults to AI_CREATIVE_WORKFLOW_PATH or z-image workflow.
    """
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


def main() -> None:
    """Run the MCP server over FastMCP's default stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()

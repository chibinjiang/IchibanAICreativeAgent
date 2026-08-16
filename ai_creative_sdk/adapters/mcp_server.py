"""
AI Creative SDK - Remote MCP Server

FastMCP 2.14.7
Python 3.12+

Run locally:

    uv run -m ai_creative_sdk.adapters.mcp_server

Server endpoint:

    http://127.0.0.1:8000/mcp

Production:

    https://mcp.example.com/mcp

Authentication:

    Authorization: Bearer <API_KEY>

Environment variables:

    MCP_HOST
    MCP_PORT
    MCP_PATH

    MCP_BASE_URL

    AI_CREATIVE_API_KEYS_JSON

    COMFYUI_HOST
    COMFYUI_PORT
    COMFYUI_TOKEN
    COMFYUI_TIMEOUT

    AI_CREATIVE_WORKFLOW_PATH

Example API key configuration:

    export AI_CREATIVE_API_KEYS_JSON='[
      {
        "user_id": "alice",
        "name": "Alice",
        "key_hash": "sha256...",
        "scopes": ["image:generate"],
        "enabled": true
      },
      {
        "user_id": "admin",
        "name": "Admin",
        "key_hash": "sha256...",
        "scopes": ["image:generate", "admin"],
        "enabled": true
      }
    ]'
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.tools.tool import ToolResult
from fastmcp.utilities.types import Image

from ai_creative_sdk.providers.comfyui.provider import TOKEN, ComfyUIProvider
from ai_creative_sdk.skills.commercial_image import CommercialImageSkill


# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
)

logger = logging.getLogger("ai-creative-mcp")


# ============================================================================
# Configuration
# ============================================================================

SERVER_NAME = "ai-creative-sdk"
SERVER_VERSION = "0.1.0"

DEFAULT_WORKFLOW_PATH = "workflows/zimage_txt2img_api.json"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_MCP_PATH = "/mcp"

IMAGE_GENERATE_SCOPE = "image:generate"
ADMIN_SCOPE = "admin"


# ============================================================================
# API Key
# ============================================================================


@dataclass(frozen=True)
class APIKey:
    """
    Server-side representation of one API key.

    IMPORTANT:
        key_hash is SHA-256(key), not the plaintext API key.
    """

    user_id: str
    name: str
    key_hash: str
    scopes: frozenset[str]
    enabled: bool = True
    expires_at: int | None = None

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False

        return time.time() >= self.expires_at


def hash_api_key(api_key: str) -> str:
    """
    SHA-256 hash of an API key.

    The plaintext key should never be stored in the server configuration.
    """

    return hashlib.sha256(
        api_key.encode("utf-8")
    ).hexdigest()


def load_api_keys() -> dict[str, APIKey]:
    """
    Load API keys from AI_CREATIVE_API_KEYS_JSON.

    Example:

    [
      {
        "user_id": "alice",
        "name": "Alice",
        "key_hash": "...",
        "scopes": ["image:generate"],
        "enabled": true
      }
    ]
    """

    raw = os.getenv("AI_CREATIVE_API_KEYS_JSON")

    if not raw:
        raise RuntimeError(
            "AI_CREATIVE_API_KEYS_JSON is not configured. "
            "Generate API keys before starting the MCP server."
        )

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AI_CREATIVE_API_KEYS_JSON is not valid JSON."
        ) from exc

    if not isinstance(items, list):
        raise RuntimeError(
            "AI_CREATIVE_API_KEYS_JSON must be a JSON array."
        )

    result: dict[str, APIKey] = {}

    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError(
                "Each API key configuration must be an object."
            )

        user_id = str(item["user_id"])
        name = str(item.get("name", user_id))
        key_hash = str(item["key_hash"]).lower()

        scopes = frozenset(
            str(scope)
            for scope in item.get("scopes", [])
        )

        enabled = bool(
            item.get("enabled", True)
        )

        expires_at = item.get("expires_at")

        if expires_at is not None:
            expires_at = int(expires_at)

        if len(key_hash) != 64:
            raise RuntimeError(
                f"Invalid SHA-256 key_hash for user '{user_id}'."
            )

        api_key = APIKey(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            scopes=scopes,
            enabled=enabled,
            expires_at=expires_at,
        )

        if key_hash in result:
            raise RuntimeError(
                f"Duplicate API key hash for user '{user_id}'."
            )

        result[key_hash] = api_key

    if not result:
        raise RuntimeError(
            "AI_CREATIVE_API_KEYS_JSON contains no API keys."
        )

    logger.info(
        "Loaded %d MCP API key(s).",
        len(result),
    )

    for item in result.values():
        logger.info(
            "API user=%s scopes=%s enabled=%s",
            item.user_id,
            sorted(item.scopes),
            item.enabled,
        )

    return result


# ============================================================================
# Authentication
# ============================================================================


class APIKeyTokenVerifier(TokenVerifier):
    """
    FastMCP TokenVerifier using static API keys.

    Client sends:

        Authorization: Bearer sk-xxxx

    Server:

        SHA256(sk-xxxx)
              ↓
        lookup API key
              ↓
        AccessToken
    """

    def __init__(
        self,
        api_keys: dict[str, APIKey],
    ):
        super().__init__(
            required_scopes=[],
        )

        self.api_keys = api_keys

    async def verify_token(
        self,
        token: str,
    ) -> AccessToken | None:

        if not token:
            return None

        token_hash = hash_api_key(token)

        matched_key: APIKey | None = None

        # Constant-time comparison.
        for stored_hash, api_key in self.api_keys.items():
            if hmac.compare_digest(
                token_hash,
                stored_hash,
            ):
                matched_key = api_key
                break

        if matched_key is None:
            logger.warning(
                "Rejected unknown MCP API key."
            )
            return None

        if not matched_key.enabled:
            logger.warning(
                "Rejected disabled API key user=%s",
                matched_key.user_id,
            )
            return None

        if matched_key.expired:
            logger.warning(
                "Rejected expired API key user=%s",
                matched_key.user_id,
            )
            return None

        logger.info(
            "Authenticated MCP user=%s scopes=%s",
            matched_key.user_id,
            sorted(matched_key.scopes),
        )

        return AccessToken(
            token=token,
            client_id=matched_key.user_id,
            scopes=sorted(matched_key.scopes),
            expires_at=matched_key.expires_at,
            claims={
                "user_id": matched_key.user_id,
                "name": matched_key.name,
                "scopes": sorted(matched_key.scopes),
            },
        )


# ============================================================================
# Authorization
# ============================================================================


def get_current_user() -> AccessToken:
    """
    Get authenticated user.

    FastMCP has already authenticated the HTTP request before
    the MCP tool is executed.
    """

    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()

    if token is None:
        raise PermissionError(
            "Authentication required."
        )

    return token


# def require_scope(scope: str):
#     """
#     Decorator used for application-level authorization.
#
#     FastMCP 2.14.7 supports authentication providers, while newer
#     FastMCP authorization helpers should not be assumed to exist
#     in this exact version.
#
#     Therefore we enforce tool permissions explicitly here.
#     """
#
#     def decorator(func):
#
#         async def wrapper(*args, **kwargs):
#             token = get_current_user()
#
#             scopes = set(
#                 token.scopes or []
#             )
#
#             if ADMIN_SCOPE in scopes:
#                 return await func(
#                     *args,
#                     **kwargs,
#                 )
#
#             if scope not in scopes:
#                 user_id = token.client_id or "unknown"
#
#                 logger.warning(
#                     "Permission denied user=%s required_scope=%s",
#                     user_id,
#                     scope,
#                 )
#
#                 raise PermissionError(
#                     f"Permission denied. "
#                     f"Required scope: {scope}"
#                 )
#
#             return await func(
#                 *args,
#                 **kwargs,
#             )
#
#         wrapper.__name__ = func.__name__
#         wrapper.__doc__ = func.__doc__
#         wrapper.__annotations__ = getattr(
#             func,
#             "__annotations__",
#             {},
#         )
#
#         return wrapper
#
#     return decorator


# ============================================================================
# ComfyUI Provider
# ============================================================================


def _get_provider(
    workflow_path: str | None = None,
) -> ComfyUIProvider:

    resolved_workflow = (
        workflow_path
        or os.getenv(
            "AI_CREATIVE_WORKFLOW_PATH",
            DEFAULT_WORKFLOW_PATH,
        )
    )

    return ComfyUIProvider(
        workflow_path=resolved_workflow,
        host=os.getenv(
            "COMFYUI_HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "COMFYUI_PORT",
                "7188",
            )
        ),
        token=os.getenv(
            "COMFYUI_TOKEN",
            TOKEN,
        ),
        timeout=int(
            os.getenv(
                "COMFYUI_TIMEOUT",
                "300",
            ),
        ),
    )


# ============================================================================
# MCP Server
# ============================================================================


API_KEYS = load_api_keys()

auth = APIKeyTokenVerifier(
    API_KEYS,
)

mcp = FastMCP(
    name=SERVER_NAME,
    version=SERVER_VERSION,
    instructions=(
        "AI Creative image generation server. "
        "Use generate_commercial_image to generate commercial images."
    ),
    auth=auth,
)


# ============================================================================
# MCP Tools
# ============================================================================


@mcp.tool(
    name="generate_commercial_image",
    description=(
        "Generate a commercial image through the configured "
        "ComfyUI workflow."
    ),
)
async def generate_commercial_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    batch_size: int = 1,
    seed: int | None = None,
    workflow_path: str | None = None,
):

    user = get_current_user()

    scopes = set(user.scopes or [])

    if (
        IMAGE_GENERATE_SCOPE not in scopes
        and ADMIN_SCOPE not in scopes
    ):
        raise PermissionError(
            "Permission denied. "
            f"Required scope: {IMAGE_GENERATE_SCOPE}"
        )

    logger.info(
        "Image generation requested "
        "user=%s prompt_length=%d size=%dx%d batch=%d",
        user.client_id,
        len(prompt),
        width,
        height,
        batch_size,
    )

    provider = _get_provider(
        workflow_path,
    )

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
        images = []
        for image_url in result.images:
            if image_url.startswith("http"):
                image_bytes = await skill.provider.client.url_to_image_content(image_url)
            else:
                image_bytes = image_url
            images.append(Image(data=image_bytes, format='png'))
        print(images)
        return images
        return ToolResult(
            content=content,
            meta=result.metadata,
            # structured_content={
            #     "success": result.success,
            #     "duration": result.duration,
            #     "images": result.images,
            #     "prompt_id": result.prompt_id,
            # },
        )
    finally:
        await provider.close()

# ============================================================================
# Server
# ============================================================================


def main() -> None:

    host = os.getenv(
        "MCP_HOST",
        DEFAULT_HOST,
    )

    port = int(
        os.getenv(
            "MCP_PORT",
            str(DEFAULT_PORT),
        )
    )

    path = os.getenv(
        "MCP_PATH",
        DEFAULT_MCP_PATH,
    )

    logger.info(
        "Starting AI Creative MCP server"
    )

    logger.info(
        "Transport: Streamable HTTP"
    )

    logger.info(
        "Endpoint: http://%s:%d%s",
        host,
        port,
        path,
    )

    # FastMCP 2.14.7 supports both "http" and
    # "streamable-http". We explicitly use streamable-http.
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        path=path,
        show_banner=True,
    )


if __name__ == "__main__":
    """
    API key: sk-vMIjcpKC5lRNITPbofRk6Ukbx1PZw7zJwANjAGKkymM
    uv run -m ai_creative_sdk.adapters.mcp_server
    """
    main()
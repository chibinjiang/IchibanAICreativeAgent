import asyncio
import uuid
from typing import Optional

import httpx


class ComfyUIClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8188, token: Optional[str] = None, timeout: int = 300):
        self.base_url = f"http://{host}:{port}"
        self.token = token
        self.client = httpx.AsyncClient(timeout=timeout)

    def _build_url(self, path: str):
        """拼接 ComfyUI API URL,带 token 时追加 ?token=xxx。"""
        url = f"{self.base_url}{path}"
        if self.token:
            url += f"?token={self.token}"
        return url

    async def submit_prompt(self, prompt: dict) -> str:
        """POST /prompt?token=xxx 提交 ComfyUI 任务。"""
        payload = {"prompt": prompt, "client_id": str(uuid.uuid4())}
        response = await self.client.post(self._build_url("/prompt"), json=payload)
        response.raise_for_status()
        data = response.json()
        return data["prompt_id"]

    async def convert_workflow(self, workflow: dict) -> dict:
        resp = await self.client.post(self._build_url("/workflow/convert"), json=workflow)
        resp.raise_for_status()
        data = resp.json()
        # 插件一般直接返回 Prompt JSON;若返回 {"prompt": ...} 则统一展开
        return data.get("prompt", data)

    async def get_history(self, prompt_id: str):
        """GET /history/{prompt_id}?token=xxx"""
        response = await self.client.get(self._build_url(f"/history/{prompt_id}"))
        response.raise_for_status()
        return response.json()

    async def wait_result(self, prompt_id: str, interval: int = 2):
        """轮询等待任务完成。"""
        while True:
            history = await self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            await asyncio.sleep(interval)

    async def close(self):
        await self.client.aclose()

    def get_asset_url(self, filename):
        """
        http://115.190.131.64:7188/api/view?filename=z-image-turbo_00005_.png&type=output&subfolder=
        :return:
        """
        asset_url = f"{self.base_url}/api/view?filename={filename}&type=output"
        return asset_url

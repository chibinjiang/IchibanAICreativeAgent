import time
from uuid import uuid4

from ai_creative_sdk.providers.base import BaseImageProvider
from ai_creative_sdk.types import ImageGenerateRequest, ImageGenerateResult

from .client import ComfyUIClient
from .prompt_modifier import PromptModifier
from .workflow_loader import WorkflowLoader
from ai_creative_sdk.log_config import logger

TOKEN = '$2b$12$v7wbbMyMM671Wqht6UdWW.68naNFjnjT2ZrhsQv26zL0M6cTSHXOG'


class ComfyUIProvider(BaseImageProvider):
    def __init__(
        self,
        workflow_path,
        host: str = '115.190.131.64',
        port: int = 7188,
        token: str | None = TOKEN,
        timeout: int = 300,
    ):
        self.client = ComfyUIClient(host=host, port=port, token=token, timeout=timeout)
        self.workflow_loader = WorkflowLoader(workflow_path)

    async def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        start_time = time.time()
        workflow = self.workflow_loader.load()  # 加载
        logger.info(f"workflow init: {workflow}")
        workflow = PromptModifier.set_prompt(workflow, request.prompt)  # Customize
        # workflow = PromptModifier.set_filename_prefix(workflow, f"comfy_{str(uuid4())}")  # Customize
        # workflow = await self.workflow_loader.convert_for_api(workflow, self.client)
        logger.info(f"workflow convert to: {workflow}")
        prompt_id = await self.client.submit_prompt(workflow)
        logger.info(f"Prompt ID: {prompt_id}")
        result = await self.client.wait_result(prompt_id)
        logger.info(f"It took {time.time() - start_time:.2f} Seconds, Prompt result: {result}")
        images = []
        for key in result.get('outputs') or []:
            for img_d in result['outputs'][key]['images']:
                images.append(self.client.get_asset_url(img_d['filename']))
        return ImageGenerateResult(
            success=True,
            images=images,
            prompt_id=prompt_id,
            metadata=result,
        )

    async def close(self):
        await self.client.close()


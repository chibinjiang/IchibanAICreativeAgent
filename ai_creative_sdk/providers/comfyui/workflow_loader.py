import json
from enum import Enum

from ai_creative_sdk.providers.comfyui.client import ComfyUIClient


class WorkflowType(Enum):
    UI = "ui"
    PROMPT = "prompt"


class WorkflowLoader:
    def __init__(self, workflow_path):
        self.workflow_path = workflow_path

    @classmethod
    def detect(cls, workflow: dict) -> WorkflowType | None:
        if "nodes" in workflow:
            return WorkflowType.UI
        first = next(iter(workflow.values()))
        if isinstance(first, dict) and "class_type" in first:
            return WorkflowType.PROMPT

    def load(self) -> dict:
        with open(self.workflow_path) as f:
            return json.load(f)

    async def convert_for_api(self, workflow: dict, client: ComfyUIClient) -> dict:
        if self.detect(workflow) == WorkflowType.UI:
            workflow = await client.convert_workflow(workflow)
        return workflow

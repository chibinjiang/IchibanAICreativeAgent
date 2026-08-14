class PromptModifier:
    @classmethod
    def set_prompt(cls, workflow: dict, prompt: str):
        # /57:27/inputs/text
        workflow['57:27']['inputs']['text'] = prompt
        return workflow

    @classmethod
    def set_filename_prefix(cls, workflow: dict, prefix: str):
        # /nodes/1/inputs/1/widget/name
        for node in workflow['nodes']:
            for inp in node['inputs']:
                if inp['name'] == 'filename_prefix':
                    inp['widget']['name'] = prefix
        return workflow

    @classmethod
    def set_seed(cls, workflow, seed):
        for node in workflow['nodes']:
            if "widgets_values" in node and isinstance(node["widgets_values"], list):
                node["widgets_values"][3] = seed
        return workflow

    @classmethod
    def set_size(cls, workflow, width: int = 1024, height: int = 1024):
        for node in workflow['nodes']:
            if "widgets_values" in node and isinstance(node["widgets_values"], list):
                node["widgets_values"][1], node["widgets_values"][2] = width, height
        return workflow

    def set_batch(self):
        raise NotImplementedError

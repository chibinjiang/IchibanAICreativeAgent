"""Run with: uv run -m examples.generate_image."""

import asyncio

from ai_creative_sdk.providers.comfyui.provider import ComfyUIProvider
from ai_creative_sdk.skills.commercial_image import CommercialImageSkill


async def main():
    provider = ComfyUIProvider(workflow_path="workflows/zimage_txt2img_api.json")
    skill = CommercialImageSkill(provider)
    pos_prompt = """
    luxury perfume product photography,
    marble table,
    cinematic lighting
    """
    pos_prompt = "IMAX商业科幻大片，全景深空镜头，流浪的地球，巨型行星发动机喷射炽蓝色等离子焰流，冰封地表，厚重大气层光晕，浩瀚深邃宇宙星河，璀璨银河星云，前景精致绝美的东方女性，高级清冷氛围感，长款深空银灰色科幻风衣，柔顺长发，温柔坚毅眼神，精致高级五官，电影级侧逆光，体积光，尘埃丁达尔光束，8K超高清，超写实，超精细皮肤纹理，胶片颗粒，宽画幅2.39:1，史诗氛围感，景深极强，镜头畸变可控，hdr，顶级商拍质感，细节丰富，科幻电影光影，冷色调主基调，深蓝与冰金色配色，精致妆容，极简高级配饰，风吹动发丝与衣摆，宇宙远景壮阔震撼"
    result = await skill.generate(prompt=pos_prompt)
    print(result)


if __name__ == "__main__":
    """
    uv run -m examples.generate_image
    """
    asyncio.run(main())

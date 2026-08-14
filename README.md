# AI Creative SDK

> A lightweight AI Creative SDK for AI Agents.
> One unified interface for Commercial Image Generation, AI Video Generation, Image Editing and more.

---

# AI Creative SDK

AI Creative SDK 是一个面向 **AI Agent** 的创意内容生成 SDK。

它将 **ComfyUI、Stable Diffusion、Diffusers、Wan、HiDream、FLUX、OpenAI Image API** 等各种底层能力统一封装为 **Skill**，让 Agent（如 OpenClaw、Codex、Claude Code、WorkBuddy 等）可以通过统一接口调用，实现商业广告图、商品主图、营销海报、广告视频等内容的自动生成。

项目遵循 **Provider + Skill + Adapter** 架构，将模型调用、工作流管理、参数替换、结果解析等逻辑进行模块化设计，使整个 SDK 易于扩展、易于维护，并适合作为 AI Agent 的基础能力层。

---

# Why AI Creative SDK

当前 AI 生图、视频生态存在几个典型问题：

* 每种模型都有不同的调用方式
* ComfyUI Workflow 与 API Workflow 不统一
* Agent 很难直接调用 ComfyUI
* 不同模型参数格式完全不同
* 不方便统一接入多个 Agent

AI Creative SDK 希望解决这些问题。

统一之后：

```
Agent

↓

CommercialImageSkill

↓

Provider

↓

ComfyUI / Diffusers / OpenAI / Wan / FLUX
```

Agent 永远不需要关心底层模型。

---

# Features

当前版本

* Async ComfyUI Client
* ComfyUI Token Authentication（ComfyUI-Login）
* Workflow 自动加载
* UI Workflow 自动转换（workflow/convert）
* Prompt Workflow 自动识别
* Prompt 自动替换
* 图片自动下载
* 多图片生成
* Provider 抽象
* Skill 抽象

规划支持

* FLUX
* Wan 2.2
* HiDream
* Stable Diffusion XL
* Stable Diffusion WebUI
* Diffusers
* OpenAI Images API
* Kling
* Hunyuan Video
* Seedance
* 腾讯混元
* 字节即梦

---

# Architecture

整体采用 Provider + Skill + Adapter 架构。

```
                   AI Agent
(OpenClaw / Codex / Claude Code / WorkBuddy)

                         │

                         ▼

                CommercialImageSkill

                         │

                 CommercialVideoSkill

                         │

                    BaseSkill

                         │

                 Provider Interface

      ┌──────────────────┼────────────────────┐

      ▼                  ▼                    ▼

 ComfyUI Provider   Diffusers Provider   OpenAI Provider

      │

      ▼

ComfyUI HTTP Client

      │

      ▼

ComfyUI Server
```

Skill 负责业务能力。

Provider 负责底层模型。

Client 负责 HTTP 通信。

这样 Agent 永远只调用 Skill，而不会依赖具体模型。

---

# Project Structure

```
ai_creative_sdk/

├── providers/
│   ├── base.py
│   └── comfyui/
│       ├── client.py
│       ├── provider.py
│       ├── workflow_loader.py
│       ├── prompt_modifier.py
│       ├── output_parser.py
│       └── exceptions.py
│
├── skills/
│   ├── base.py
│   ├── commercial_image.py
│   └── commercial_video.py
│
├── workflows/
│
├── assets/
│
├── examples/
│
└── tests/
```

---

# Core Modules

## ComfyUI Client

负责：

* Async HTTP Client
* Token Authentication
* Workflow Convert
* Submit Prompt
* Query History
* Download Images

屏蔽 ComfyUI HTTP API 细节。

---

## Workflow Loader

负责：

* 加载 Workflow
* 自动识别 Workflow 类型
* 自动转换 UI Workflow
* Workflow Cache

SDK 支持直接使用 ComfyUI 导出的 Workflow，无需用户手工转换。

---

## Prompt Modifier

负责：

统一修改 Workflow 参数。

例如：

* Positive Prompt
* Negative Prompt
* Seed
* CFG
* Steps
* Width
* Height
* Batch Size

以后不同模型只需要修改这里。

---

## Output Parser

负责：

```
History

↓

Outputs

↓

Images

↓

Download

↓

ImageGenerateResult
```

统一返回 SDK 对象。

---

## Provider

Provider 负责模型调用。

目前：

* ComfyUI Provider

未来：

* Diffusers Provider
* OpenAI Provider
* InvokeAI Provider
* Stable Diffusion WebUI Provider

---

## Skill

Skill 面向 Agent。

例如：

CommercialImageSkill

负责：

* 商品主图
* 广告图
* 模特图
* Banner
* 电商海报

以后：

CommercialVideoSkill

负责：

* 商品广告视频
* Image To Video
* AI 短视频
* 营销视频

---

# Current Roadmap

第一阶段

* ComfyUI Provider
* Commercial Image Skill
* Workflow Convert
* Async Client

第二阶段

* Commercial Video Skill
* Wan 2.2
* HiDream
* FLUX
* SDXL

第三阶段

* Diffusers Provider
* Stable Diffusion WebUI Provider
* OpenAI Image Provider

第四阶段

* Multi-Agent Support
* Workflow Registry
* Plugin System

---

# Product Planning

AI Creative SDK 不只是一个 ComfyUI SDK。

未来定位为：

> AI Agent 的 Creative Capability Layer。

即：

所有 AI Agent 都可以调用统一的 Creative Skill。

支持：

* Text → Image
* Image → Image
* Image → Video
* Text → Video
* Background Remove
* Product Retouch
* Virtual Try-on
* Face Swap
* Upscale
* Inpainting
* Outpainting
* Image Caption
* OCR
* Visual QA

所有能力统一封装。

---

# Future Plans

未来重点方向包括：

### Multi Provider

支持多个模型后端。

例如：

* ComfyUI
* Diffusers
* Stable Diffusion WebUI
* InvokeAI
* OpenAI
* Wan
* HiDream

---

### Workflow Registry

Workflow 不再直接读取 JSON。

统一注册：

```
Commercial Product

↓

Workflow Registry

↓

Workflow Cache
```

支持版本管理。

---

### Skill Marketplace

所有 Skill 插件化。

例如：

```
CommercialImageSkill

CommercialVideoSkill

VirtualTryOnSkill

UpscaleSkill

RemoveBackgroundSkill

ProductPhotographySkill
```

Agent 可以按需安装。

---

### Agent Adapter

支持：

* OpenClaw
* Codex
* Claude Code
* WorkBuddy
* Cursor
* Goose
* RooCode

真正做到：

**Write Once, Use Everywhere.**

---

# Vision

AI Creative SDK 希望成为 AI Agent 时代的 Creative SDK。

开发者无需关注底层模型差异，只需要调用统一 Skill，即可完成商业图片、广告视频、营销素材等 AI 创意内容生成。

未来，本项目将持续完善 Provider、Skill、Workflow Registry、Plugin System 等能力，逐步构建一个面向 AI Agent 的统一创意内容基础设施。


参考: 
- Flux text2img skill: https://mcpmarket.com/zh/tools/skills/flux-txt2img-workflows
- Flux Workflow Convert: https://github.com/SethRobinson/comfyui-workflow-to-api-converter-endpoint
- 
---

# MCP Server

本项目提供轻量 stdio MCP Server，用于让 OpenClaw、Codex、Claude Code 等 Agent 通过标准工具协议调用生图能力。

## 启动方式

首次迁移到 FastMCP 后，建议先同步依赖：

```bash
uv sync --reinstall-package fastmcp
```

如果本地 `.venv` 中已经安装过 FastMCP 3.x 或升级过程中出现包文件混用，也可以先强制重装项目锁定的 FastMCP 2.x：

```bash
uv pip install --force-reinstall "fastmcp==2.14.7"
```

然后从项目根目录启动 stdio MCP Server：

```bash
uv run -m ai_creative_sdk.adapters.mcp_server
```

这是 stdio MCP Server，直接在终端运行时会等待 MCP Client 输入，通常不会像 HTTP 服务一样打印监听端口。

安装项目后也可以使用脚本入口：

```bash
ai-creative-mcp
```

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `AI_CREATIVE_WORKFLOW_PATH` | `workflows/zimage_txt2img_api.json` | 默认 ComfyUI workflow 路径 |
| `COMFYUI_HOST` | `115.190.131.64` | ComfyUI 服务 host |
| `COMFYUI_PORT` | `7188` | ComfyUI 服务端口 |
| `COMFYUI_TOKEN` | SDK Provider 默认 token | ComfyUI-Login token |
| `COMFYUI_TIMEOUT` | `300` | HTTP 请求超时时间，单位秒 |

## 暴露工具

### `generate_commercial_image`

输入参数：

* `prompt`: 正向提示词。
* `negative_prompt`: 负向提示词，当前 workflow 支持时生效。
* `width`: 图片宽度，默认 `1024`。
* `height`: 图片高度，默认 `1024`。
* `batch_size`: 生成数量，默认 `1`。
* `seed`: 可选随机种子。
* `workflow_path`: 可选 workflow JSON 路径；不传则使用 `AI_CREATIVE_WORKFLOW_PATH` 或默认 z-image workflow。

返回结构沿用 SDK 的 `ImageGenerateResult`：

```json
{
  "success": true,
  "images": ["http://.../api/view?filename=...&type=output"],
  "prompt_id": "...",
  "metadata": {}
}
```

## OpenClaw / Codex 接入示例

将 MCP server 配置为 stdio 命令：

```json
{
  "mcpServers": {
    "ai-creative-sdk": {
      "command": "uv",
      "args": ["run", "-m", "ai_creative_sdk.adapters.mcp_server"],
      "cwd": "/workspace/IchibanAICreativeAgent",
      "env": {
        "AI_CREATIVE_WORKFLOW_PATH": "workflows/zimage_txt2img_api.json",
        "COMFYUI_HOST": "115.190.131.64",
        "COMFYUI_PORT": "7188"
      }
    }
  }
}
```

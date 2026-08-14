#!/usr/bin/env bash
#
# setup_comfyui_minimax_h3_workflow.sh
# -------------------------------------------------------------
# 为 MiniMax-H3「加速视频流整合-Only-文生视频」ComfyUI workflow 安装依赖：
#   1. 克隆所需核心自定义节点 (custom_nodes)
#   2. 下载所需模型权重 (models/...)  — 使用 hf-mirror.com 国内镜像
#
# 用法：
#   chmod +x setup_comfyui_minimax_h3_workflow.sh
#   ./setup_comfyui_minimax_h3_workflow.sh
#
# 注意：
#   - 请先把下面 COMFYUI_ROOT 改成你本机 ComfyUI 的实际根目录
#   - 原生 MiniMax-H3 节点 (MiniMaxH3ImageToVideo / MiniMaxH3ReferenceToVideo 等)
#     已合入 ComfyUI >= 0.31.0 核心，无需 clone，只需更新 ComfyUI 本体
#   - MiniMax-H3 采用社区许可，开放权重不覆盖美国/欧盟/英国/韩国等地，
#     下载或商用前请核对许可条款
# -------------------------------------------------------------

set -euo pipefail

# ====================== 配置区 ======================
# 修改为你的 ComfyUI 根目录（包含 models/ 与 custom_nodes/）
COMFYUI_ROOT="${COMFYUI_ROOT:-/Users/ichiban/ComfyUI}"

# 国内无法访问 huggingface.co，统一走镜像
HF_HOST="https://hf-mirror.com"

CUSTOM_NODES="$COMFYUI_ROOT/custom_nodes"
MODELS="$COMFYUI_ROOT/models"
# ====================================================

echo "==> 目标 ComfyUI 目录: $COMFYUI_ROOT"
if [ ! -d "$COMFYUI_ROOT" ]; then
  echo "错误: ComfyUI 根目录不存在: $COMFYUI_ROOT"
  echo "请编辑脚本顶部的 COMFYUI_ROOT 变量。"
  exit 1
fi

mkdir -p "$CUSTOM_NODES"

# -------------------------------------------------------------
# 1. 克隆核心自定义节点
# -------------------------------------------------------------
clone_node() {
  local url="$1"
  local name
  name="$(basename "$url" .git)"
  local target="$CUSTOM_NODES/$name"
  if [ -d "$target" ]; then
    echo "==> [跳过] 已存在: $name"
  else
    echo "==> [克隆] $name"
    git clone --depth 1 "$url" "$target"
  fi
}

echo ""
echo "================ 1/2 安装自定义节点 ================"
clone_node "https://github.com/rgthree/rgthree-comfy.git"
clone_node "https://github.com/kijai/ComfyUI-KJNodes.git"
clone_node "https://github.com/city96/ComfyUI-GGUF.git"
clone_node "https://github.com/tl2012tl/comfyUI-llama-TE.git"
clone_node "https://github.com/tl2012tl/TE_MAN.git"

# -------------------------------------------------------------
# 2. 下载模型权重（hf-mirror.com 镜像）
# -------------------------------------------------------------
# 便捷函数：wget 下载并自动以指定文件名保存
dl() {
  local url="$1"
  local out="$2"
  if [ -f "$out" ]; then
    echo "==> [跳过] 已存在: $out"
  else
    echo "==> [下载] $out"
    echo "    $url"
    wget -c "$url" -O "$out"
  fi
}

echo ""
echo "================ 2/2 下载模型权重 ================"

# --- A. 官方原生权重 Comfy-Org/MiniMax-H3 ---
# 主扩散模型 (diffusion_models)
mkdir -p "$MODELS/diffusion_models"
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors" \
   "$MODELS/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors" \
   "$MODELS/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors"

# 文本编码器 (text_encoders)
mkdir -p "$MODELS/text_encoders"
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors" \
   "$MODELS/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
# 备选文本编码器变体（工作流 CLIPLoader 也引用此 INT8 版）
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors" \
   "$MODELS/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors"

# 视频 / 音频 VAE (vae)
mkdir -p "$MODELS/vae"
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors" \
   "$MODELS/vae/minimax_h3_video_vae_fp16.safetensors"
dl "$HF_HOST/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors" \
   "$MODELS/vae/minimax_h3_audio_vae_fp32.safetensors"

# --- B. GGUF 备用主模型 realrebelai/MiniMax-H3_GGUFs (unet) ---
mkdir -p "$MODELS/unet"
dl "$HF_HOST/realrebelai/MiniMax-H3_GGUFs/resolve/main/MiniMax-H3-FL2VA-Q4_K_M.gguf" \
   "$MODELS/unet/MiniMax-H3-FL2VA-Q4_K_M.gguf"
# 备选 GGUF 仓库(量化更全 Q3–Q5): Abiray/MiniMax-H3-GGUF

# --- C. Turbo 4-step LoRA (Kijai/MiniMax-H3_comfy) (loras) ---
mkdir -p "$MODELS/loras"
dl "$HF_HOST/Kijai/MiniMax-H3_comfy/resolve/main/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors" \
   "$MODELS/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors"

# --- D. Qwen3.5-4B TE 模型 (llama-TE 用) (LLM) ---
mkdir -p "$MODELS/LLM"
dl "$HF_HOST/unsloth/Qwen3.5-4B-GGUF/resolve/main/Qwen3.5-4B-Q4_K_M.gguf" \
   "$MODELS/LLM/Qwen3.5-4B-Q4_K_M.gguf"
# 视觉投影 mmproj：HF 上无 “Qwen3.5-4B-mmproj-BF16.gguf” 这一精确拼写，
# 下载任意 Qwen3.5-4B mmproj 并用 -O 重命名即可（mmproj 仅与架构绑定）。
dl "$HF_HOST/prithivMLmods/Qwen3.5-4B-MTP-GGUF/resolve/main/Qwen3.5-4B.mmproj-bf16.gguf" \
   "$MODELS/LLM/Qwen3.5-4B-mmproj-BF16.gguf"

echo ""
echo "================ 完成 ================"
echo "自定义节点与模型已就绪。"
echo "提醒: 请将 ComfyUI 本体更新到 >= 0.31.0 以获得 MiniMax-H3 原生节点。"
echo "提醒: 模型目录切勿放错 —— diffusion_models/text_encoders/vae 与原生权重对应，"
echo "      GGUF 进 unet，TE 模型进 LLM（不是 text_encoders）。"

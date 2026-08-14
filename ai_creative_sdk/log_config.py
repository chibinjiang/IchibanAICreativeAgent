import os
import sys
from loguru import logger
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)
# 日志格式模板（标准工程格式，面试非常加分）
# 时间 | 级别 | 进程‑线程 | 文件.函数(行号) | 日志内容 | 额外结构化参数
LOG_FORMAT = (
    "<green>{time:YYYY‑MM‑DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{process.name}</cyan>‑<cyan>{thread.name}</cyan> | "
    "<magenta>{file.name}:{function}:{line}</magenta> | "
    "<level>{message}</level>"
)

# 文件日志格式(关闭ANSI颜色，方便日志查看工具读取)
LOG_FORMAT_FILE = (
    "{time:YYYY‑MM‑DD HH:mm:ss.SSS} | {level: <8} | "
    "{process.name}‑{thread.name} | {file.name}:{function}:{line} | {message}"
)

logger.remove()
ENV = 'dev'

if ENV == "dev":
    # 开发环境 DEBUG
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="DEBUG",
        enqueue=False,
        backtrace=True,  # 打印完整堆栈
        diagnose=True,    # 显示局部变量，调试神器
    )
else:
    # 生产环境 INFO
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="INFO",
        enqueue=True,
        backtrace=False,
        diagnose=False
    )

# ---------------------- 文件持久化日志
logger.add(
    sink=f"{LOG_DIR}/app_{{time:YYYY‑MM‑DD}}.log",
    format=LOG_FORMAT_FILE,
    level="INFO",
    rotation="00:00",        # 每日零点新建日志文件
    retention="30 days",     # 只保留30天日志
    compression="zip",        # 旧日志压缩zip节省磁盘
    enqueue=True,             # 多线程/多进程安全，你的批量绘图任务必开
    backtrace=True,
    diagnose=False
)

# ---------------------- 过滤第三方库嘈杂日志
# import logging
# # 屏蔽 fastapi、uvicorn、torch、comfyui 多余debug日志
# for noisy_lib in ["uvicorn", "uvicorn.access", "torch", "transformers"]:
#     logging.getLogger(noisy_lib).setLevel("WARNING")

# 预留日志工具 

import logging
import sys

# 创建logger
logger = logging.getLogger("BigDataOps")
logger.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 避免重复添加处理器
if not logger.hasHandlers():
    logger.addHandler(console_handler)

# 设置传播
logger.propagate = False

# 用法示例：
# from app.utils.logger import logger
# logger.info("info日志")
# logger.warning("warning日志")
# logger.error("error日志")
# logger.debug("debug日志") 
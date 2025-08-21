import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import settings

# 创建日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(log_level: str = "INFO"):
    """配置日志系统"""

    # 创建 logger
    logger = logging.getLogger("edu_feedback_analysis")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # 文件 handler (带轮转)
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 错误文件 handler
    error_handler = RotatingFileHandler(
        LOG_DIR / "error.log",
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 添加 handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)

    return logger


# 创建全局 logger 实例
app_logger = setup_logging()
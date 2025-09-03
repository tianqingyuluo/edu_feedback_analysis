from pathlib import Path

from app.core.config import settings


class ModelVersionManager:
    """模型版本管理器"""

    def __init__(self, model_dir=None):
        if model_dir is None:
            # 如果没有指定模型目录，则使用配置中的路径
            self.model_dir = Path(settings.machine_learning_models_path)
        else:
            self.model_dir = Path(model_dir)

        # 确保目录存在
        self.model_dir.mkdir(parents=True, exist_ok=True)

    async def get_next_version(self, model_name):
        """获取下一个版本号"""
        versions = []
        prefix = f"{model_name}_v"

        # 遍历目录中的所有文件
        for file_path in self.model_dir.glob(f"{prefix}*.pkl"):
            file_name = file_path.name
            # 提取版本号
            if "_" in file_name:
                parts = file_name.split("_")
                if len(parts) >= 2 and parts[1].startswith("v"):
                    try:
                        version_num = int(parts[1][1:])  # 去掉'v'前缀
                        versions.append(version_num)
                    except ValueError:
                        continue

        # 返回下一个版本号
        if not versions:
            return 1
        return max(versions) + 1
from pathlib import Path

from app.core.config import settings
from app.core.logging import app_logger


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
                if len(parts) >= 2 and parts[-1].startswith("v"):
                    try:
                        point_pos = parts[-1].find(".")
                        version_num = int(parts[-1][1:point_pos])  # 去掉'v'前缀
                        versions.append(version_num)
                    except ValueError:
                        continue

        # 返回下一个版本号
        if not versions:
            return 1
        return max(versions) + 1

    def get_model_path(self, model_name, version=None):
        """获取模型文件路径"""
        if version is None:
            # 获取最新版本
            versions = []
            prefix = f"{model_name}_v"
            
            # 遍历目录中的所有文件
            for file_path in self.model_dir.glob(f"{prefix}*.pkl"):
                file_name = file_path.name
                # 提取版本号
                if "_" in file_name:
                    parts = file_name.split("_")
                    if len(parts) >= 2 and parts[-1].startswith("v"):
                        try:
                            point_pos = parts[-1].find(".")
                            version_num = int(parts[-1][1:point_pos])  # 去掉'v'前缀
                            versions.append((version_num, file_path))
                        except ValueError:
                            continue
            
            if not versions:
                raise FileNotFoundError(f"No model files found for {model_name}")
            
            # 返回最高版本的文件路径
            latest_version_path = max(versions, key=lambda x: x[0])[1]
            return latest_version_path
        else:
            # 获取指定版本
            model_file = self.model_dir / f"{model_name}_v{version}.pkl"
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")
            return model_file

    def get_model_path_by_taskid(self, model_name, taskid: str, version=None):
        """获取用taskid路径存的模型文件的路径"""
        if version is None:
            # 获取最新版本
            directory = self.model_dir / taskid
            versions = []
            prefix = f"{model_name}_v"

            # 遍历目录中的所有文件
            for file_path in directory.glob(f"{prefix}*.pkl"):
                file_name = file_path.name
                # 提取版本号
                if "_" in file_name:
                    parts = file_name.split("_")
                    if len(parts) >= 2 and parts[-1].startswith("v"):
                        try:
                            point_pos = parts[-1].find(".")
                            version_num = int(parts[-1][1:point_pos])  # 去掉'v'前缀
                            versions.append((version_num, file_path))
                        except ValueError:
                            continue

            if not versions:
                raise FileNotFoundError(f"No model files found for {model_name}")

            # 返回最高版本的文件路径
            latest_version_path = max(versions, key=lambda x: x[0])[1]
            return latest_version_path
        else:
            # 获取指定版本
            model_file = self.model_dir / f"{model_name}_v{version}.pkl"
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_file}")
            return model_file

    def list_model_versions(self, model_name):
        """列出模型的所有版本"""
        versions = []
        prefix = f"{model_name}_v"
        
        # 遍历目录中的所有文件
        for file_path in self.model_dir.glob(f"{prefix}*.pkl"):
            file_name = file_path.name
            # 提取版本号
            if "_" in file_name:
                parts = file_name.split("_")
                if len(parts) >= 2 and parts[-1].startswith("v"):
                    try:
                        point_pos = parts[-1].find(".")
                        version_num = int(parts[-1][1:point_pos])  # 去掉'v'前缀
                        versions.append(version_num)
                    except ValueError:
                        continue
        
        return sorted(versions)

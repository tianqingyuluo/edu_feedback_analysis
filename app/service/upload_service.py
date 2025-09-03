import hashlib
import os.path

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, func

from app.core.config import settings
from app.db.models.upload import Upload
from app.exception.exceptions.upload import FileConflictError
from app.schemas import UploadResponse


class UploadService:
    """上传文件服务"""

    async def upload(self, file: UploadFile, db: AsyncSession) -> UploadResponse:
        """上传文件"""
        filename = file.filename
        file_path = f"{settings.analysis_file_path}{filename}"

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        content: bytes = await file.read()

        try:
            file_hash: str
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            file_hash = hashlib.sha256(content).hexdigest()

            upload = Upload(
                filename=filename,
                path=file_path,
                size=len(content),
                hash=file_hash,
            )
            db.add(upload)
            await db.commit()
            await db.refresh(upload)
            return UploadResponse(
                filename=upload.filename,
                id=str(upload.id),
                size=upload.size,
                uploaded_at=upload.uploaded_at,
            )
        except IntegrityError:
            await db.rollback()
            raise FileConflictError(filename)

    async def check_filename_conflict(self, filename: str, db: AsyncSession) -> bool:
        """检查文件名是否冲突"""
        res = await db.execute(select(Upload).where(Upload.filename == filename))
        upload = res.scalars().first()
        return upload is not None

    # async def delete(self, id: int, db: AsyncSession) -> bool:
    #     """删除文件"""
    #     try:
    #         upload = await db.get(Upload, id)
    #         if not upload:
    #             return False
    #         await db.delete(upload)
    #         await db.commit()
    #         return True
    #     except Exception:
    #         return False
    async def delete(self, id: int, db: AsyncSession) -> bool:
        """删除文件"""
        try:
            upload: Upload | None = await db.get(Upload, id)
            if not upload:
                return False

            # 获取文件路径
            file_path = upload.path

            # 先将文件移动到临时位置，确保可以恢复
            temp_path = file_path + ".deleting"
            if os.path.exists(file_path):
                os.rename(file_path, temp_path)

            try:
                # 删除数据库记录
                await db.delete(upload)
                await db.commit()
                # 如果数据库删除成功，再永久删除文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return True
            except Exception:
                # 如果数据库操作失败，恢复文件
                await db.rollback()
                if os.path.exists(temp_path):
                    os.rename(temp_path, file_path)
                return False

        except Exception:
            return False

    async def get_history_by_page(self, page: int, page_size: int, db: AsyncSession) -> list[UploadResponse]:
        """获取历史记录"""
        offset = (page - 1) * page_size
        uploads = await db.execute(
            select(Upload).offset(offset).limit(page_size)
        )
        upload_responses = [
            UploadResponse(
                filename=upload.filename,
                id=str(upload.id),
                size=upload.size,
                uploaded_at=upload.uploaded_at,
            )
            for upload in uploads.scalars().all()
        ]
        return upload_responses

    async def get_history_count(self, db: AsyncSession) -> int:
        """获取历史记录数量"""
        count = await db.execute(select(func.count()).select_from(Upload))
        return count.scalar()


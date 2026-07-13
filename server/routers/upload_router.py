"""通用文件上传路由 (Upload Router)

Sprint 6 — Task 6.4
依据 CODE_WIKI §15.8、Sprint 2 file_handler Frozen API。

GTMS 全局上传入口，业务无关设计。
本模块仅实现图片上传，后续模块可扩展其他文件类型。

职责:
    - 接收 UploadFile
    - MIME 校验（委托 Sprint 2 file_handler）
    - 扩展名校验（委托 Sprint 2 file_handler）
    - 文件大小校验（委托 Sprint 2 file_handler）
    - 文件命名（{task_no}_receipt_{timestamp}.{ext}）
    - 文件保存
    - URL 生成
    - 返回 Upload API Response

不得负责:
    - 业务逻辑
    - 数据库操作
    - ORM
    - Receipt / Grinding / Inspection
    - SystemLog
    - 状态流转

Upload API Response:
    {
        "filename": "20260701-1_receipt_20260708153020.jpg",
        "url": "http://host:port/uploads/images/20260701-1_receipt_20260708153020.jpg",
        "content_type": "image/jpeg",
        "size": 12345
    }
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    File,
    status,
)
from fastapi.responses import JSONResponse

from server.core.dependencies import get_current_active_user
from server.core.exceptions import BusinessLogicException
from server.enums.file_type import FileType
from server.models.user import User
from server.utils.file_handler import validate_file

logger = logging.getLogger("gtms.server")

# ============================================================
# 常量
# ============================================================

UPLOAD_DIR = "uploads/images"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

# ============================================================
# Router 定义
# ============================================================

router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"],
)


# ============================================================
# POST /api/upload/image — 图片上传
# ============================================================


@router.post(
    "/image",
    status_code=status.HTTP_201_CREATED,
    summary="上传图片",
    description=(
        "上传工件图片（jpg/jpeg/png）。"
        "校验 MIME 类型、扩展名、文件大小。"
        "返回 Upload API Response（filename / url / content_type / size）。"
    ),
)
async def upload_image(
    request: Request,
    file: UploadFile = File(..., description="图片文件"),
    task_no: str = File(..., description="任务编号"),
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:
    """上传图片接口。

    流程:
        ① 校验文件（委托 Sprint 2 file_handler.validate_file）
        ② 生成文件名（{task_no}_receipt_{timestamp}.{ext}）
        ③ 保存到 uploads/images/
        ④ 构造 URL
        ⑤ 返回 Upload API Response

    Args:
        request: FastAPI Request 对象（用于构造 URL）。
        file: 上传的图片文件。
        task_no: 任务编号（如 "20260701-1"）。
        current_user: 当前登录用户（依赖注入）。

    Returns:
        JSONResponse: Upload API Response。

    Raises:
        HTTPException 400: 文件校验失败。
    """
    # ① 校验文件（委托 Sprint 2 frozen API）
    try:
        validate_file(file, FileType.IMAGE)
    except BusinessLogicException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # ② 生成文件名
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    ext = _get_extension(file.filename or "unknown")
    filename = f"{task_no}_receipt_{timestamp}.{ext}"

    # ③ 保存文件
    target_dir = Path(UPLOAD_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    file_size = 0
    try:
        content = await file.read()
        file_size = len(content)
        target_path.write_bytes(content)
        logger.info(
            "图片上传成功: filename=%s, size=%d, task_no=%s",
            filename, file_size, task_no,
        )
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {e}",
        ) from e

    # ④ 构造 URL
    file_url = f"{request.base_url}{UPLOAD_DIR}/{filename}"

    # ⑤ 返回 Upload API Response
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "filename": filename,
            "url": file_url,
            "content_type": file.content_type,
            "size": file_size,
        },
    )


# ============================================================
# 私有函数
# ============================================================


def _get_extension(filename: str) -> str:
    """从文件名中提取小写扩展名。

    Args:
        filename: 文件名。

    Returns:
        小写扩展名，如 "jpg"、"png"。
    """
    suffix = Path(filename).suffix.lower()
    return suffix.lstrip(".")


__all__ = [
    "router",
]

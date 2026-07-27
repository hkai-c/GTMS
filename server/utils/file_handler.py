"""统一文件处理工具 (File Handler)

Sprint 2 — Task 2.5
严格依据 CODE_WIKI.md §6.6.2、DB_DESIGN.md Attachment 表。

提供文件上传、校验、删除、命名等统一工具函数。
所有公开 API 为冻结接口，不允许后续 Sprint 修改函数签名。

公开 API:
    save_upload_file(file, task_no, file_type) -> str
    delete_file(file_path) -> None
    validate_file(file, file_type) -> None
    generate_filename(task_no, file_type, original_filename) -> str

使用方式:
    from server.utils.file_handler import save_upload_file, validate_file

    path = save_upload_file(upload_file, "20260701-1", FileType.IMAGE)
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from server.core.exceptions import BusinessLogicException
from server.enums.file_type import FileType

logger = logging.getLogger(__name__)

# ============================================================
# 目录映射 — 根据 FileType 自动选择保存目录
# ============================================================

_DIR_MAP: dict[FileType, str] = {
    FileType.IMAGE: "uploads/images",
    FileType.VIDEO: "uploads/videos",
    FileType.DOCUMENT: "uploads/reports",
    FileType.CAD: "uploads/files",
}

# ============================================================
# 文件格式白名单 — 每种 FileType 允许的扩展名
# ============================================================

_ALLOWED_EXTENSIONS: dict[FileType, set[str]] = {
    FileType.IMAGE:    {"jpg", "jpeg", "png"},
    FileType.VIDEO:    {"mp4", "mov"},
    FileType.DOCUMENT: {"pdf", "doc", "docx", "xls", "xlsx"},
    FileType.CAD:      {"zip", "rar", "7z"},
}

# ============================================================
# 文件大小限制（字节） — 每种 FileType 的最大允许大小
# ============================================================

_SIZE_LIMITS: dict[FileType, int] = {
    FileType.IMAGE:    20 * 1024 * 1024,   # 20 MB
    FileType.VIDEO:    200 * 1024 * 1024,  # 200 MB
    FileType.DOCUMENT: 50 * 1024 * 1024,   # 50 MB
    FileType.CAD:      100 * 1024 * 1024,  # 100 MB
}

# ============================================================
# MIME 类型映射 — 每种扩展名对应的 MIME 类型
# ============================================================

_MIME_MAP: dict[str, set[str]] = {
    "jpg":  {"image/jpeg"},
    "jpeg": {"image/jpeg"},
    "png":  {"image/png"},
    "mp4":  {"video/mp4"},
    "mov":  {"video/quicktime"},
    "pdf":  {"application/pdf"},
    "doc":  {"application/msword"},
    "docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    "xls":  {"application/vnd.ms-excel"},
    "xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "zip":  {"application/zip", "application/x-zip-compressed"},
    "rar":  {"application/x-rar-compressed", "application/vnd.rar"},
    "7z":   {"application/x-7z-compressed"},
}


# ============================================================
# 公开 API
# ============================================================


def save_upload_file(
    file: UploadFile,
    task_no: str,
    file_type: FileType,
) -> str:
    """保存上传文件到对应目录。

    流程:
        validate_file() → generate_filename() → 创建目录 → 保存文件 → 返回相对路径

    文件保存成功后，路径可写入 Attachment.file_path。

    Args:
        file: FastAPI UploadFile 对象。
        task_no: 任务编号（如 "20260701-1"）。
        file_type: 文件类型枚举。

    Returns:
        相对路径字符串（如 "uploads/images/20260701-1_image_20260704103015_a8f3b2.jpg"）。

    Raises:
        BusinessLogicException: 文件校验失败时抛出。
    """
    # ① 校验文件
    validate_file(file, file_type)

    # ② 生成文件名
    filename = generate_filename(task_no, file_type, file.filename or "unknown")

    # ③ 确定目标目录
    dir_name = _DIR_MAP[file_type]
    target_dir = Path(dir_name)
    target_dir.mkdir(parents=True, exist_ok=True)

    # ④ 保存文件
    target_path = target_dir / filename
    try:
        content = file.file.read()
        target_path.write_bytes(content)
        logger.info(
            "文件保存成功: path=%s, size=%d, type=%s",
            target_path, len(content), file_type.value,
        )
    except OSError as e:
        raise BusinessLogicException(
            f"文件保存失败: {e}",
            detail={"filename": filename, "error": str(e)},
        )

    # ⑤ 返回相对路径（使用正斜杠）
    return str(target_path).replace("\\", "/")


def delete_file(file_path: str) -> None:
    """删除指定文件。

    若文件不存在，直接返回，不抛异常。

    Args:
        file_path: 文件路径（相对或绝对路径均可）。
    """
    path = Path(file_path)
    if not path.exists():
        return

    try:
        path.unlink()
        logger.info("文件删除成功: path=%s", file_path)
    except OSError as e:
        logger.warning("文件删除失败: path=%s, error=%s", file_path, e)


def validate_file(file: UploadFile, file_type: FileType) -> None:
    """校验上传文件的类型、大小和 MIME。

    仅负责校验，不保存文件。校验失败时抛出 BusinessLogicException。

    校验规则:
        1. 扩展名必须在 file_type 对应的白名单中
        2. 文件大小不得超过 file_type 对应的限制
        3. MIME 类型必须与扩展名匹配

    Args:
        file: FastAPI UploadFile 对象。
        file_type: 文件类型枚举。

    Raises:
        BusinessLogicException: 文件类型不合法、大小超限或 MIME 不匹配。
    """
    # 获取原始文件名和扩展名
    original_filename = file.filename or "unknown"
    ext = _get_extension(original_filename)

    # 获取文件大小（seek 到末尾再回到开头）
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    allowed = _ALLOWED_EXTENSIONS[file_type]
    size_limit = _SIZE_LIMITS[file_type]

    # ① 检查扩展名
    if ext not in allowed:
        raise BusinessLogicException(
            f"不支持的文件格式: .{ext}，{file_type.display_name}允许的格式: {', '.join(sorted(allowed))}",
            detail={
                "file_type": file_type.value,
                "extension": ext,
                "allowed": sorted(allowed),
            },
        )

    # BUG-UPLOAD-001 修复: 检查空文件（0 字节）
    if file_size == 0:
        raise BusinessLogicException(
            "文件不能为空（0 字节）",
            detail={
                "file_type": file_type.value,
                "file_size": file_size,
            },
        )

    # ② 检查文件大小
    if file_size > size_limit:
        limit_mb = size_limit / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise BusinessLogicException(
            f"文件大小超限: {actual_mb:.1f}MB（最大允许 {limit_mb:.0f}MB）",
            detail={
                "file_type": file_type.value,
                "file_size": file_size,
                "size_limit": size_limit,
            },
        )

    # BUG-UPLOAD-002 修复: 检查 content_type 必须存在
    if file.content_type is None:
        raise BusinessLogicException(
            "文件 MIME 类型不能为空",
            detail={
                "file_type": file_type.value,
                "filename": original_filename,
            },
        )

    # ③ 检查 MIME 类型
    allowed_mimes = _MIME_MAP.get(ext, set())
    if allowed_mimes and file.content_type not in allowed_mimes:
        raise BusinessLogicException(
            f"MIME 类型不匹配: {file.content_type}，期望: {', '.join(sorted(allowed_mimes))}",
            detail={
                "file_type": file_type.value,
                "extension": ext,
                "content_type": file.content_type,
                "expected_mimes": sorted(allowed_mimes),
            },
        )

    logger.debug(
        "文件校验通过: name=%s, ext=%s, size=%d, type=%s",
        original_filename, ext, file_size, file_type.value,
    )


def generate_filename(
    task_no: str,
    file_type: FileType,
    original_filename: str,
) -> str:
    """生成唯一文件名。

    格式: {task_no}_{file_type}_{YYYYMMDDHHMMSS}_{uuid}.{ext}

    示例: 20260701-1_image_20260704103015_a8f3b2.jpg

    Args:
        task_no: 任务编号。
        file_type: 文件类型枚举。
        original_filename: 原始文件名（用于提取扩展名）。

    Returns:
        唯一文件名（不含路径）。
    """
    ext = _get_extension(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]

    return f"{task_no}_{file_type.value}_{timestamp}_{unique_id}.{ext}"


# ============================================================
# 私有函数
# ============================================================


def _get_extension(filename: str) -> str:
    """从文件名中提取小写扩展名（不含点号）。

    Args:
        filename: 文件名。

    Returns:
        小写扩展名，如 "jpg"、"pdf"。无扩展名时返回空字符串。
    """
    suffix = Path(filename).suffix.lower()
    return suffix.lstrip(".")


__all__ = [
    "save_upload_file",
    "delete_file",
    "validate_file",
    "generate_filename",
]
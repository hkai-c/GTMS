"""Sprint 2 — Task 2.5 File Handler 自检脚本

验证项:
    1.  py_compile
    2.  import
    3.  generate_filename — 基本格式 (IMAGE)
    4.  generate_filename — VIDEO
    5.  generate_filename — DOCUMENT
    6.  generate_filename — CAD
    7.  generate_filename — 唯一性
    8.  generate_filename — 扩展名保留
    9.  validate_file — 图片 jpg 通过
    10. validate_file — 图片 png 通过
    11. validate_file — 图片 jpeg 通过
    12. validate_file — 图片格式错误
    13. validate_file — 视频 mp4 通过
    14. validate_file — 视频 mov 通过
    15. validate_file — 视频格式错误
    16. validate_file — 文档 pdf 通过
    17. validate_file — 文档 docx 通过
    18. validate_file — 文档格式错误
    19. validate_file — CAD zip 通过
    20. validate_file — CAD 7z 通过
    21. validate_file — 文件大小超限
    22. validate_file — MIME 类型错误
    23. validate_file — 无扩展名
    24. save_upload_file — 完整流程
    25. save_upload_file — 返回相对路径
    26. save_upload_file — 目录自动创建
    27. save_upload_file — 文件内容正确
    28. delete_file — 删除文件
    29. delete_file — 删除不存在文件（不抛异常）
    30. delete_file — 路径清理
    31. 禁止命名
    32. 循环导入
"""

import io
import sys
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.utils.file_handler import (
    save_upload_file,
    delete_file,
    validate_file,
    generate_filename,
)
from server.core.exceptions import (
    BusinessLogicException,
)
from server.enums.file_type import FileType

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {name}")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}  -- {detail}")


class MockUploadFile:
    """模拟 FastAPI UploadFile 对象。"""

    def __init__(self, filename: str, content: bytes, content_type: str = "application/octet-stream"):
        self.filename = filename
        self.content_type = content_type
        self.file = io.BytesIO(content)

    @property
    def size(self) -> int:
        return len(self.file.getvalue())


print("=" * 60)
print("  Task 2.5 — File Handler Self Test")
print("=" * 60)

# ============================================================
# 1. py_compile
# ============================================================
print("\n[1] py_compile")
import py_compile
try:
    py_compile.compile(
        str(Path(__file__).parent.parent / "server" / "utils" / "file_handler.py"),
        doraise=True,
    )
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False, str(e))

# ============================================================
# 2. import
# ============================================================
print("\n[2] import")
check("save_upload_file", save_upload_file is not None)
check("delete_file", delete_file is not None)
check("validate_file", validate_file is not None)
check("generate_filename", generate_filename is not None)

# ============================================================
# 3. generate_filename — 基本格式 (IMAGE)
# ============================================================
print("\n[3] generate_filename — IMAGE")
name = generate_filename("20260701-1", FileType.IMAGE, "photo.jpg")
check("包含 task_no", "20260701-1" in name)
check("包含 file_type", "image" in name)
check("以 .jpg 结尾", name.endswith(".jpg"))
check("长度为 42", len(name) == 42)  # 20260701-1_image_YYYYMMDDHHMMSS_xxxxxx.jpg

# ============================================================
# 4. generate_filename — VIDEO
# ============================================================
print("\n[4] generate_filename — VIDEO")
name2 = generate_filename("20260702-5", FileType.VIDEO, "clip.mp4")
check("包含 video", "video" in name2)
check("以 .mp4 结尾", name2.endswith(".mp4"))

# ============================================================
# 5. generate_filename — DOCUMENT
# ============================================================
print("\n[5] generate_filename — DOCUMENT")
name3 = generate_filename("20260703-10", FileType.DOCUMENT, "report.pdf")
check("包含 document", "document" in name3)
check("以 .pdf 结尾", name3.endswith(".pdf"))

# ============================================================
# 6. generate_filename — CAD
# ============================================================
print("\n[6] generate_filename — CAD")
name4 = generate_filename("20260704-3", FileType.CAD, "drawing.zip")
check("包含 cad", "cad" in name4)
check("以 .zip 结尾", name4.endswith(".zip"))

# ============================================================
# 7. generate_filename — 唯一性
# ============================================================
print("\n[7] generate_filename — 唯一性")
import time
name_a = generate_filename("20260701-1", FileType.IMAGE, "test.jpg")
time.sleep(1.1)  # 确保时间戳不同
name_b = generate_filename("20260701-1", FileType.IMAGE, "test.jpg")
check("两次调用不同", name_a != name_b)

# ============================================================
# 8. generate_filename — 扩展名保留
# ============================================================
print("\n[8] generate_filename — 扩展名保留")
name_caps = generate_filename("20260701-1", FileType.IMAGE, "PHOTO.JPG")
check("大写扩展名转小写", name_caps.endswith(".jpg"))
name_ddots = generate_filename("20260701-1", FileType.DOCUMENT, "file.tar.gz")
check("多段扩展名保留最后一段", name_ddots.endswith(".gz"))

# ============================================================
# 9. validate_file — 图片 jpg 通过
# ============================================================
print("\n[9] validate_file — 图片 jpg")
f = MockUploadFile("test.jpg", b"fake_jpeg_data", "image/jpeg")
try:
    validate_file(f, FileType.IMAGE)
    check("jpg 通过", True)
except BusinessLogicException:
    check("jpg 通过", False)

# ============================================================
# 10. validate_file — 图片 png 通过
# ============================================================
print("\n[10] validate_file — 图片 png")
f = MockUploadFile("test.png", b"fake_png_data", "image/png")
try:
    validate_file(f, FileType.IMAGE)
    check("png 通过", True)
except BusinessLogicException:
    check("png 通过", False)

# ============================================================
# 11. validate_file — 图片 jpeg 通过
# ============================================================
print("\n[11] validate_file — 图片 jpeg")
f = MockUploadFile("test.jpeg", b"fake_jpeg_data", "image/jpeg")
try:
    validate_file(f, FileType.IMAGE)
    check("jpeg 通过", True)
except BusinessLogicException:
    check("jpeg 通过", False)

# ============================================================
# 12. validate_file — 图片格式错误
# ============================================================
print("\n[12] validate_file — 图片格式错误")
f = MockUploadFile("test.gif", b"fake_gif", "image/gif")
try:
    validate_file(f, FileType.IMAGE)
    check("应抛异常", False)
except BusinessLogicException:
    check("gif→BusinessLogicException", True)

# ============================================================
# 13. validate_file — 视频 mp4 通过
# ============================================================
print("\n[13] validate_file — 视频 mp4")
f = MockUploadFile("video.mp4", b"fake_mp4", "video/mp4")
try:
    validate_file(f, FileType.VIDEO)
    check("mp4 通过", True)
except BusinessLogicException:
    check("mp4 通过", False)

# ============================================================
# 14. validate_file — 视频 mov 通过
# ============================================================
print("\n[14] validate_file — 视频 mov")
f = MockUploadFile("video.mov", b"fake_mov", "video/quicktime")
try:
    validate_file(f, FileType.VIDEO)
    check("mov 通过", True)
except BusinessLogicException:
    check("mov 通过", False)

# ============================================================
# 15. validate_file — 视频格式错误
# ============================================================
print("\n[15] validate_file — 视频格式错误")
f = MockUploadFile("video.avi", b"fake_avi", "video/x-msvideo")
try:
    validate_file(f, FileType.VIDEO)
    check("应抛异常", False)
except BusinessLogicException:
    check("avi→BusinessLogicException", True)

# ============================================================
# 16. validate_file — 文档 pdf 通过
# ============================================================
print("\n[16] validate_file — 文档 pdf")
f = MockUploadFile("report.pdf", b"fake_pdf", "application/pdf")
try:
    validate_file(f, FileType.DOCUMENT)
    check("pdf 通过", True)
except BusinessLogicException:
    check("pdf 通过", False)

# ============================================================
# 17. validate_file — 文档 docx 通过
# ============================================================
print("\n[17] validate_file — 文档 docx")
f = MockUploadFile("report.docx", b"fake_docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
try:
    validate_file(f, FileType.DOCUMENT)
    check("docx 通过", True)
except BusinessLogicException:
    check("docx 通过", False)

# ============================================================
# 18. validate_file — 文档格式错误
# ============================================================
print("\n[18] validate_file — 文档格式错误")
f = MockUploadFile("report.txt", b"fake_txt", "text/plain")
try:
    validate_file(f, FileType.DOCUMENT)
    check("应抛异常", False)
except BusinessLogicException:
    check("txt→BusinessLogicException", True)

# ============================================================
# 19. validate_file — CAD zip 通过
# ============================================================
print("\n[19] validate_file — CAD zip")
f = MockUploadFile("archive.zip", b"fake_zip", "application/zip")
try:
    validate_file(f, FileType.CAD)
    check("zip 通过", True)
except BusinessLogicException:
    check("zip 通过", False)

# ============================================================
# 20. validate_file — CAD 7z 通过
# ============================================================
print("\n[20] validate_file — CAD 7z")
f = MockUploadFile("archive.7z", b"fake_7z", "application/x-7z-compressed")
try:
    validate_file(f, FileType.CAD)
    check("7z 通过", True)
except BusinessLogicException:
    check("7z 通过", False)

# ============================================================
# 21. validate_file — 文件大小超限
# ============================================================
print("\n[21] validate_file — 文件大小超限")
# 创建 21MB 的假数据（超过 IMAGE 的 20MB 限制）
big_data = b"x" * (21 * 1024 * 1024)
f = MockUploadFile("big.jpg", big_data, "image/jpeg")
try:
    validate_file(f, FileType.IMAGE)
    check("应抛异常", False)
except BusinessLogicException:
    check("超限→BusinessLogicException", True)

# ============================================================
# 22. validate_file — MIME 类型错误
# ============================================================
print("\n[22] validate_file — MIME 类型错误")
f = MockUploadFile("test.jpg", b"fake_data", "text/html")
try:
    validate_file(f, FileType.IMAGE)
    check("应抛异常", False)
except BusinessLogicException:
    check("MIME不匹配→BusinessLogicException", True)

# ============================================================
# 23. validate_file — 无扩展名
# ============================================================
print("\n[23] validate_file — 无扩展名")
f = MockUploadFile("noextension", b"fake_data", "image/jpeg")
try:
    validate_file(f, FileType.IMAGE)
    check("应抛异常", False)
except BusinessLogicException:
    check("无扩展名→BusinessLogicException", True)

# ============================================================
# 24. save_upload_file — 完整流程
# ============================================================
print("\n[24] save_upload_file — 完整流程")
f = MockUploadFile("test_photo.jpg", b"hello world test content", "image/jpeg")
path = save_upload_file(f, "20260701-1", FileType.IMAGE)
check("路径非空", path is not None)
check("路径以 uploads/images/ 开头", path.startswith("uploads/images/"))

# ============================================================
# 25. save_upload_file — 返回相对路径
# ============================================================
print("\n[25] save_upload_file — 返回相对路径")
check("使用正斜杠", "\\" not in path)
check("扩展名 jpg", path.endswith(".jpg"))

# ============================================================
# 26. save_upload_file — 目录自动创建
# ============================================================
print("\n[26] save_upload_file — 目录自动创建")
check("上传目录存在", Path("uploads/images").exists())

# ============================================================
# 27. save_upload_file — 文件内容正确
# ============================================================
print("\n[27] save_upload_file — 文件内容正确")
full_path = Path(path)
check("文件存在", full_path.exists())
content = full_path.read_bytes()
check("内容正确", content == b"hello world test content")

# ============================================================
# 28. delete_file — 删除文件
# ============================================================
print("\n[28] delete_file — 删除文件")
delete_file(path)
check("文件已删除", not Path(path).exists())

# ============================================================
# 29. delete_file — 删除不存在文件（不抛异常）
# ============================================================
print("\n[29] delete_file — 删除不存在文件")
try:
    delete_file("uploads/nonexistent/file.jpg")
    check("不抛异常", True)
except Exception:
    check("不抛异常", False)

# ============================================================
# 30. delete_file — 路径清理
# ============================================================
print("\n[30] delete_file — 路径清理")
# 使用 save_upload_file 再删除进行验证
f2 = MockUploadFile("test_del.png", b"delete me", "image/png")
path2 = save_upload_file(f2, "20260701-1", FileType.IMAGE)
check("创建成功", Path(path2).exists())
delete_file(path2)
check("删除成功", not Path(path2).exists())

# ============================================================
# 31. 禁止命名
# ============================================================
print("\n[31] 禁止命名")
try:
    from server.utils.file_handler import ValidationException  # type: ignore
    check("ValidationException 不应存在", False)
except ImportError:
    check("ValidationException 未使用", True)
try:
    from server.utils.file_handler import AuthorizationException  # type: ignore
    check("AuthorizationException 不应存在", False)
except ImportError:
    check("AuthorizationException 未使用", True)
try:
    from server.utils.file_handler import ConflictException  # type: ignore
    check("ConflictException 不应存在", False)
except ImportError:
    check("ConflictException 未使用", True)

# ============================================================
# 32. 循环导入
# ============================================================
print("\n[32] 循环导入")
from server.utils import file_handler as fh
check("无循环导入", True)

# ============================================================
# 清理
# ============================================================
# 清理 uploads 测试目录
uploads_dir = Path("uploads")
if uploads_dir.exists():
    shutil.rmtree(uploads_dir)

# ============================================================
# 结果
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  结果: ALL PASSED")
else:
    print(f"  结果: {FAILED} FAILED")
print("=" * 60)

sys.exit(0 if FAILED == 0 else 1)
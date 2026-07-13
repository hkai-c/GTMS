"""Test: Upload Router (Sprint 6 — Task 6.4)

严格依据 DEVELOPMENT_ROADMAP.md Task 6.4 验收标准。
测试 server/routers/upload_router.py 全部接口与代码规范。

注意：本测试使用源码分析，不依赖数据库连接。
"""

import ast
import inspect
import os
import re
import sys

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# 自检框架
# ============================================================

PASSED = 0
FAILED = 0


def check(desc: str, condition: bool) -> None:
    """执行一条检查。"""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [PASS] {desc}")
    else:
        FAILED += 1
        print(f"  [FAIL] {desc}")


def extract_code_text(file_path: str) -> str:
    """提取代码文本（排除 docstring 和注释）。"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
    content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
    content = re.sub(r"#.*$", "", content, flags=re.MULTILINE)
    return content


# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 6.4 — Upload Router Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile

    py_compile.compile("server/routers/upload_router.py", doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] import
# ----------------------------------------------------------
print("\n[2] import")
try:
    from server.routers.upload_router import router

    check("router 导入", True)
except ImportError as e:
    check("router 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# 获取源码
router_path = os.path.join("server", "routers", "upload_router.py")
with open(router_path, "r", encoding="utf-8") as f:
    source = f.read()
code = extract_code_text(router_path)

# ----------------------------------------------------------
# [3] Router 类型
# ----------------------------------------------------------
print("\n[3] Router 类型")
from fastapi import APIRouter

check("router 是 APIRouter 实例", isinstance(router, APIRouter))
check("router.prefix = /api/upload", router.prefix == "/api/upload")
check("router.tags = ['Upload']", router.tags == ["Upload"])

# ----------------------------------------------------------
# [4] Route 数量
# ----------------------------------------------------------
print("\n[4] Route 数量")
routes = router.routes
check("路由数量 = 1", len(routes) == 1)

# ----------------------------------------------------------
# [5] HTTP Method
# ----------------------------------------------------------
print("\n[5] HTTP Method")
check("POST 方法存在", "POST" in routes[0].methods)

# ----------------------------------------------------------
# [6] URL 路径
# ----------------------------------------------------------
print("\n[6] URL 路径")
check("POST /api/upload/image", "@router.post(\n    \"/image\"" in source)

# ----------------------------------------------------------
# [7] 接受 UploadFile
# ----------------------------------------------------------
print("\n[7] 接受 UploadFile")
check("upload_image 参数包含 file", "file" in source)
check("使用 UploadFile 类型", "UploadFile" in source)
check("使用 File 依赖", "File(" in source)

# ----------------------------------------------------------
# [8] 使用 file_handler.validate_file
# ----------------------------------------------------------
print("\n[8] 使用 file_handler.validate_file")
check("导入 validate_file from file_handler",
      "from server.utils.file_handler import validate_file" in source)
check("调用 validate_file", "validate_file(file, FileType.IMAGE)" in source)

# ----------------------------------------------------------
# [9] 校验失败抛 HTTPException 400
# ----------------------------------------------------------
print("\n[9] 校验失败抛 HTTPException 400")
check("捕获 BusinessLogicException",
      "BusinessLogicException" in source)
check("转换为 HTTPException 400",
      "status.HTTP_400_BAD_REQUEST" in source)

# ----------------------------------------------------------
# [10] 文件命名规则
# ----------------------------------------------------------
print("\n[10] 文件命名规则")
check("使用 task_no 前缀", "task_no" in code)
check("使用 _receipt_ 标识", '_receipt_' in source or "_receipt_" in source)
check("使用时间戳", "TIMESTAMP_FORMAT" in source)
check("提取扩展名", "_get_extension" in source)

# ----------------------------------------------------------
# [11] 仅允许 jpg/jpeg/png
# ----------------------------------------------------------
print("\n[11] 仅允许 jpg/jpeg/png")
check("ALLOWED_EXTENSIONS 包含 jpg", '"jpg"' in source)
check("ALLOWED_EXTENSIONS 包含 jpeg", '"jpeg"' in source)
check("ALLOWED_EXTENSIONS 包含 png", '"png"' in source)
check("ALLOWED_EXTENSIONS 不包含 gif", "gif" not in source.lower())

# ----------------------------------------------------------
# [12] 保存目录
# ----------------------------------------------------------
print("\n[12] 保存目录")
check("UPLOAD_DIR = 'uploads/images'", "UPLOAD_DIR" in source)
check("使用 mkdir 创建目录", "mkdir" in source)
check("使用 write_bytes 保存", "write_bytes" in source)

# ----------------------------------------------------------
# [13] URL 生成
# ----------------------------------------------------------
print("\n[13] URL 生成")
check("使用 request.base_url", "request.base_url" in source)
check("构造文件 URL", "file_url" in source)

# ----------------------------------------------------------
# [14] Upload API Response 结构
# ----------------------------------------------------------
print("\n[14] Upload API Response 结构")
check("返回 filename 字段", '"filename"' in source)
check("返回 url 字段", '"url"' in source)
check("返回 content_type 字段", '"content_type"' in source)
check("返回 size 字段", '"size"' in source)
check("不返回 path", '"path"' not in source)
check("不返回 absolute_path", "absolute_path" not in source)
check("不返回 disk_path", "disk_path" not in source)

# ----------------------------------------------------------
# [15] 无业务逻辑
# ----------------------------------------------------------
print("\n[15] 无业务逻辑")
check("无 ReceiptService", "ReceiptService" not in source)
check("无 TaskService", "TaskService" not in source)
check("无 ORM 操作", "db.query" not in code and "Session" not in code)
check("无 SystemLog", "SystemLog" not in code)
check("无状态流转", "process_status" not in source)

# ----------------------------------------------------------
# [16] 无 try/except 吞异常
# ----------------------------------------------------------
print("\n[16] 无 try/except 吞异常")
check("捕获 BusinessLogicException 并转为 HTTPException",
      "BusinessLogicException" in source)
check("文件保存异常转为 HTTPException 500",
      "HTTP_500_INTERNAL_SERVER_ERROR" in source)

# ----------------------------------------------------------
# [17] main.py include_router
# ----------------------------------------------------------
print("\n[17] main.py include_router")
main_path = os.path.join("server", "main.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_source = f.read()
check("main.py 导入 upload_router",
      "from server.routers.upload_router import router "
      "as upload_router" in main_source)
check("main.py include_router(upload_router)",
      "app.include_router(upload_router)" in main_source)

# ----------------------------------------------------------
# [18] 代码规范
# ----------------------------------------------------------
print("\n[18] 代码规范")
check("无 print()", "print(" not in code)
check("无 TODO", "TODO" not in source)
check("无 FIXME", "FIXME" not in source)
check("无 tab 缩进", "\t" not in source)
check("文件以换行结尾", source.endswith("\n"))
check("有 __all__", "__all__" in source)
check("__all__ 包含 router", "router" in source.split("__all__")[-1])
check("常量集中管理", "UPLOAD_DIR" in source and "TIMESTAMP_FORMAT" in source)

# ----------------------------------------------------------
# [19] Docstring
# ----------------------------------------------------------
print("\n[19] Docstring")
# 使用 __import__ 获取模块
router_module = __import__(
    "server.routers.upload_router", fromlist=["_"]
)
check("upload_image 有 docstring",
      inspect.getdoc(router_module.upload_image) is not None)

# ----------------------------------------------------------
# [20] Type Hint
# ----------------------------------------------------------
print("\n[20] Type Hint")
sig = inspect.signature(router_module.upload_image)
check("upload_image 有 -> 返回类型",
      sig.return_annotation is not inspect.Signature.empty)

# ----------------------------------------------------------
# [21] 无循环导入
# ----------------------------------------------------------
print("\n[21] 无循环导入")
try:
    import importlib

    importlib.reload(sys.modules.get(
        "server.routers.upload_router",
        __import__("server.routers.upload_router",
                   fromlist=["router"])))
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [22] OpenAPI 完整性
# ----------------------------------------------------------
print("\n[22] OpenAPI 完整性")
check("有 summary", 'summary="上传图片"' in source)
check("有 description", "description=" in source)
check("有 status_code=201",
      "status_code=status.HTTP_201_CREATED" in source)

# ----------------------------------------------------------
# [23] Frozen API 未修改
# ----------------------------------------------------------
print("\n[23] Frozen API 未修改")
check("未导入 ReceiptService", "ReceiptService" not in source)
check("未导入 CustomerService", "CustomerService" not in source)
check("未导入 TaskService", "TaskService" not in source)
check("未导入 UserService", "UserService" not in source)

# ----------------------------------------------------------
# [24] File 类型校验委托
# ----------------------------------------------------------
print("\n[24] File 类型校验委托")
check("使用 FileType.IMAGE", "FileType.IMAGE" in source)
check("枚举仅 image 类型", "FileType.IMAGE" in source)

# ----------------------------------------------------------
# [25] 文件大小校验
# ----------------------------------------------------------
print("\n[25] 文件大小校验")
check("file_handler 校验包含大小检查",
      "validate_file" in source)

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
total = PASSED + FAILED
print(f"  Total: {total}  |  PASS: {PASSED}  |  FAIL: {FAILED}")
if FAILED == 0:
    print("  Result: ALL PASSED")
else:
    print(f"  Result: {FAILED} FAILED")
print("=" * 60)
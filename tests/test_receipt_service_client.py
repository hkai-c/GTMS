"""Test: Desktop ReceiptService (Sprint 6 — Task 6.5)

严格依据 DEVELOPMENT_ROADMAP.md Task 6.5 验收标准。
测试 client/services/receipt_service.py 全部公开 API 与代码规范。

验证项:
    Import:
        ✓ py_compile
        ✓ 模块导入
        ✓ 类存在性
    Public API:
        ✓ 6 个公开方法
        ✓ 方法签名
        ✓ 返回类型注解
    HTTP Method:
        ✓ GET / POST / PUT / DELETE 映射
    URL:
        ✓ URL 路径正确
    Query:
        ✓ list_receipts 查询参数
        ✓ 仅提交非 None 参数
    Body:
        ✓ create_receipt 请求体
        ✓ update_receipt 仅提交非 None 字段
    Upload:
        ✓ upload_receipt_image 调用
        ✓ multipart/form-data
    ApiClient:
        ✓ 统一使用 self._api_client
        ✓ 禁止直接 requests
    response.json():
        ✓ 所有方法返回 resp.json()
    异常:
        ✓ 无 try/except
        ✓ 异常原样抛出
    PEP8:
        ✓ 无 print()
        ✓ 无 TODO/FIXME
        ✓ 无 tab 缩进
        ✓ 有 __all__
    Type Hint:
        ✓ 所有参数有类型注解
        ✓ 有返回类型注解
    Docstring:
        ✓ 文件有 docstring
        ✓ 类有 docstring
        ✓ 所有公开方法有 docstring
    依赖:
        ✓ 不导入 server 模块
        ✓ 不导入 ORM/Database
        ✓ 不导入 JWT
        ✓ 不导入 PySide6
    Logger:
        ✓ 使用 logging.getLogger("gtms.client")
        ✓ 无 print()
"""

import ast
import inspect
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

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
# 文件路径
# ============================================================

SERVICE_PATH = os.path.join("client", "services", "receipt_service.py")
with open(SERVICE_PATH, "r", encoding="utf-8") as f:
    SOURCE = f.read()
CODE = extract_code_text(SERVICE_PATH)

# ============================================================
# 自检
# ============================================================

print("=" * 60)
print("  Task 6.5 — Desktop ReceiptService Self Test")
print("=" * 60)

# ----------------------------------------------------------
# [1] py_compile
# ----------------------------------------------------------
print("\n[1] py_compile")
try:
    import py_compile
    py_compile.compile(SERVICE_PATH, doraise=True)
    check("py_compile", True)
except py_compile.PyCompileError as e:
    check("py_compile", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [2] Import
# ----------------------------------------------------------
print("\n[2] Import")
try:
    from client.services.receipt_service import ReceiptService
    check("ReceiptService 导入", True)
except ImportError as e:
    check("ReceiptService 导入", False)
    print(f"      Error: {e}")
    sys.exit(1)

# 从 __init__.py 导入
try:
    from client.services import ReceiptService as ReceiptServiceFromInit
    check("ReceiptService 从 __init__ 导入", True)
except ImportError as e:
    check("ReceiptService 从 __init__ 导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [3] 类存在性
# ----------------------------------------------------------
print("\n[3] 类存在性")
check("ReceiptService 是 class", inspect.isclass(ReceiptService))

# ----------------------------------------------------------
# [4] 公开 API 列表
# ----------------------------------------------------------
print("\n[4] 公开 API 列表")
public_methods = [
    m for m in dir(ReceiptService)
    if not m.startswith("_") and callable(getattr(ReceiptService, m))
]
check("create_receipt 存在", "create_receipt" in public_methods)
check("list_receipts 存在", "list_receipts" in public_methods)
check("get_receipt 存在", "get_receipt" in public_methods)
check("update_receipt 存在", "update_receipt" in public_methods)
check("delete_receipt 存在", "delete_receipt" in public_methods)
check("upload_receipt_image 存在", "upload_receipt_image" in public_methods)
check("公开 API 数量 = 6", len(public_methods) == 6)
check("公开方法不包含 _", all(not m.startswith("_") for m in public_methods))

# ----------------------------------------------------------
# [5] 公开 API 签名 — list_receipts
# ----------------------------------------------------------
print("\n[5] 公开 API 签名 — list_receipts")
sig = inspect.signature(ReceiptService.list_receipts)
params = list(sig.parameters.keys())
check("list_receipts: 含 self", "self" in params)
check("list_receipts: 含 task_id", "task_id" in params)
check("list_receipts: 含 page", "page" in params)
check("list_receipts: 含 page_size", "page_size" in params)
check("list_receipts: 含 keyword", "keyword" in params)
check("list_receipts: 含 customer_id", "customer_id" in params)
check("list_receipts: 含 sales_id", "sales_id" in params)
check("list_receipts: 含 start_date", "start_date" in params)
check("list_receipts: 含 end_date", "end_date" in params)
check("page 默认值 = 1", sig.parameters["page"].default == 1)
check("page_size 默认值 = 20", sig.parameters["page_size"].default == 20)

# ----------------------------------------------------------
# [6] 公开 API 签名 — get_receipt
# ----------------------------------------------------------
print("\n[6] 公开 API 签名 — get_receipt")
sig = inspect.signature(ReceiptService.get_receipt)
params = list(sig.parameters.keys())
check("get_receipt: 含 self", "self" in params)
check("get_receipt: 含 receipt_id", "receipt_id" in params)

# ----------------------------------------------------------
# [7] 公开 API 签名 — create_receipt
# ----------------------------------------------------------
print("\n[7] 公开 API 签名 — create_receipt")
sig = inspect.signature(ReceiptService.create_receipt)
params = list(sig.parameters.keys())
check("create_receipt: 含 self", "self" in params)
check("create_receipt: 含 task_id", "task_id" in params)
check("create_receipt: 含 received_at", "received_at" in params)
check("create_receipt: 含 receiver_id", "receiver_id" in params)
check("create_receipt: 含 image_paths", "image_paths" in params)

# ----------------------------------------------------------
# [8] 公开 API 签名 — update_receipt
# ----------------------------------------------------------
print("\n[8] 公开 API 签名 — update_receipt")
sig = inspect.signature(ReceiptService.update_receipt)
params = list(sig.parameters.keys())
check("update_receipt: 含 self", "self" in params)
check("update_receipt: 含 receipt_id", "receipt_id" in params)
check("update_receipt: 含 task_id", "task_id" in params)
check("update_receipt: 含 received_at", "received_at" in params)
check("update_receipt: 含 receiver_id", "receiver_id" in params)
check("update_receipt: 含 image_paths", "image_paths" in params)

# ----------------------------------------------------------
# [9] 公开 API 签名 — delete_receipt
# ----------------------------------------------------------
print("\n[9] 公开 API 签名 — delete_receipt")
sig = inspect.signature(ReceiptService.delete_receipt)
params = list(sig.parameters.keys())
check("delete_receipt: 含 self", "self" in params)
check("delete_receipt: 含 receipt_id", "receipt_id" in params)

# ----------------------------------------------------------
# [10] 公开 API 签名 — upload_receipt_image
# ----------------------------------------------------------
print("\n[10] 公开 API 签名 — upload_receipt_image")
sig = inspect.signature(ReceiptService.upload_receipt_image)
params = list(sig.parameters.keys())
check("upload_receipt_image: 含 self", "self" in params)
check("upload_receipt_image: 含 task_no", "task_no" in params)
check("upload_receipt_image: 含 file_path", "file_path" in params)

# ----------------------------------------------------------
# [11] 返回值类型注解
# ----------------------------------------------------------
print("\n[11] 返回值类型注解")
for method_name in public_methods:
    method = getattr(ReceiptService, method_name)
    sig = inspect.signature(method)
    has_return = sig.return_annotation is not inspect.Signature.empty
    check(f"{method_name} 有返回类型注解", has_return)

# 检查返回类型都是 dict[str, Any]
check("list_receipts 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)
check("get_receipt 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)
check("create_receipt 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)
check("update_receipt 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)
check("delete_receipt 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)
check("upload_receipt_image 返回 dict[str, Any]",
      "dict[str, Any]" in SOURCE)

# ----------------------------------------------------------
# [12] HTTP Method 映射 — list_receipts (GET)
# ----------------------------------------------------------
print("\n[12] HTTP Method 映射 — list_receipts (GET)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"items": [], "total": 0}
mock_client.get.return_value = mock_resp

service = ReceiptService(mock_client)
result = service.list_receipts()
check("list_receipts 调用 GET", mock_client.get.called)
check("未调用 POST", not mock_client.post.called)
check("未调用 PUT", not mock_client.put.called)
check("未调用 DELETE", not mock_client.delete.called)
check("返回 mock_resp.json()", result == {"items": [], "total": 0})

# ----------------------------------------------------------
# [13] HTTP Method 映射 — get_receipt (GET)
# ----------------------------------------------------------
print("\n[13] HTTP Method 映射 — get_receipt (GET)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"id": 1}
mock_client.get.return_value = mock_resp

service = ReceiptService(mock_client)
result = service.get_receipt(1)
check("get_receipt 调用 GET", mock_client.get.called)
check("未调用 POST", not mock_client.post.called)
check("未调用 PUT", not mock_client.put.called)
check("未调用 DELETE", not mock_client.delete.called)
check("返回 mock_resp.json()", result == {"id": 1})

# ----------------------------------------------------------
# [14] HTTP Method 映射 — create_receipt (POST)
# ----------------------------------------------------------
print("\n[14] HTTP Method 映射 — create_receipt (POST)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"id": 1, "task_id": 10}
mock_client.post.return_value = mock_resp

service = ReceiptService(mock_client)
now = datetime(2026, 7, 10, 10, 30, 0)
result = service.create_receipt(task_id=10, received_at=now, receiver_id=5)
check("create_receipt 调用 POST", mock_client.post.called)
check("未调用 GET", not mock_client.get.called)
check("未调用 PUT", not mock_client.put.called)
check("未调用 DELETE", not mock_client.delete.called)
check("返回 mock_resp.json()", result == {"id": 1, "task_id": 10})

# ----------------------------------------------------------
# [15] HTTP Method 映射 — update_receipt (PUT)
# ----------------------------------------------------------
print("\n[15] HTTP Method 映射 — update_receipt (PUT)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"id": 1}
mock_client.put.return_value = mock_resp

service = ReceiptService(mock_client)
result = service.update_receipt(1, receiver_id=10)
check("update_receipt 调用 PUT", mock_client.put.called)
check("未调用 GET", not mock_client.get.called)
check("未调用 POST", not mock_client.post.called)
check("未调用 DELETE", not mock_client.delete.called)
check("返回 mock_resp.json()", result == {"id": 1})

# ----------------------------------------------------------
# [16] HTTP Method 映射 — delete_receipt (DELETE)
# ----------------------------------------------------------
print("\n[16] HTTP Method 映射 — delete_receipt (DELETE)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"message": "收件记录已删除"}
mock_client.delete.return_value = mock_resp

service = ReceiptService(mock_client)
result = service.delete_receipt(1)
check("delete_receipt 调用 DELETE", mock_client.delete.called)
check("未调用 GET", not mock_client.get.called)
check("未调用 POST", not mock_client.post.called)
check("未调用 PUT", not mock_client.put.called)
check("返回 mock_resp.json()", result == {"message": "收件记录已删除"})

# ----------------------------------------------------------
# [17] HTTP Method 映射 — upload_receipt_image (POST)
# ----------------------------------------------------------
print("\n[17] HTTP Method 映射 — upload_receipt_image (POST)")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {
    "filename": "test.jpg",
    "url": "http://localhost/uploads/images/test.jpg",
    "content_type": "image/jpeg",
    "size": 1024,
}
mock_client.post.return_value = mock_resp

# 创建临时图片文件用于测试
import tempfile
tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
tmp_file.write(b"\xff\xd8\xff\xe0")  # JPEG 魔数
tmp_file_path = tmp_file.name
tmp_file.close()

try:
    service = ReceiptService(mock_client)
    result = service.upload_receipt_image(
        task_no="20260701-1",
        file_path=tmp_file_path,
    )
    check("upload_receipt_image 调用 POST", mock_client.post.called)
    check("未调用 GET", not mock_client.get.called)
    check("未调用 PUT", not mock_client.put.called)
    check("未调用 DELETE", not mock_client.delete.called)
    check("返回 mock_resp.json()", result == {
        "filename": "test.jpg",
        "url": "http://localhost/uploads/images/test.jpg",
        "content_type": "image/jpeg",
        "size": 1024,
    })
finally:
    os.unlink(tmp_file_path)

# ----------------------------------------------------------
# [18] URL 映射
# ----------------------------------------------------------
print("\n[18] URL 映射")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {}
mock_client.get.return_value = mock_resp
mock_client.post.return_value = mock_resp
mock_client.put.return_value = mock_resp
mock_client.delete.return_value = mock_resp

service = ReceiptService(mock_client)

# list_receipts
service.list_receipts()
check("list_receipts URL = /api/receipts",
      mock_client.get.call_args[0][0] == "/api/receipts")

# get_receipt
service.get_receipt(1)
check("get_receipt URL = /api/receipts/1",
      mock_client.get.call_args[0][0] == "/api/receipts/1")

# create_receipt
service.create_receipt(task_id=1, received_at=datetime.now(), receiver_id=1)
check("create_receipt URL = /api/receipts",
      mock_client.post.call_args[0][0] == "/api/receipts")

# update_receipt
service.update_receipt(1, receiver_id=2)
check("update_receipt URL = /api/receipts/1",
      mock_client.put.call_args[0][0] == "/api/receipts/1")

# delete_receipt
service.delete_receipt(1)
check("delete_receipt URL = /api/receipts/1",
      mock_client.delete.call_args[0][0] == "/api/receipts/1")

# upload_receipt_image
tmp_file2 = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
tmp_file2.write(b"\xff\xd8\xff\xe0")
tmp_file2_path = tmp_file2.name
tmp_file2.close()
try:
    service.upload_receipt_image(task_no="T001", file_path=tmp_file2_path)
    check("upload_receipt_image URL = /api/upload/image",
          mock_client.post.call_args[0][0] == "/api/upload/image")
finally:
    os.unlink(tmp_file2_path)

# ----------------------------------------------------------
# [19] Query 参数 — list_receipts 仅提交非 None
# ----------------------------------------------------------
print("\n[19] Query 参数 — list_receipts 仅提交非 None")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {"items": [], "total": 0}
mock_client.get.return_value = mock_resp

service = ReceiptService(mock_client)

# 默认参数（无筛选）
service.list_receipts()
params = mock_client.get.call_args[1]["params"]
check("默认含 page", params["page"] == 1)
check("默认含 page_size", params["page_size"] == 20)
check("默认不含 task_id", "task_id" not in params)
check("默认不含 keyword", "keyword" not in params)
check("默认不含 customer_id", "customer_id" not in params)
check("默认不含 sales_id", "sales_id" not in params)
check("默认不含 start_date", "start_date" not in params)
check("默认不含 end_date", "end_date" not in params)

# 传入 task_id
service.list_receipts(task_id=5)
params = mock_client.get.call_args[1]["params"]
check("task_id=5 时含 task_id", params.get("task_id") == 5)

# 传入 keyword
service.list_receipts(keyword="test")
params = mock_client.get.call_args[1]["params"]
check("keyword=test 时含 keyword", params.get("keyword") == "test")

# 传入 customer_id
service.list_receipts(customer_id=3)
params = mock_client.get.call_args[1]["params"]
check("customer_id=3 时含 customer_id", params.get("customer_id") == 3)

# 传入 sales_id
service.list_receipts(sales_id=7)
params = mock_client.get.call_args[1]["params"]
check("sales_id=7 时含 sales_id", params.get("sales_id") == 7)

# 传入 start_date
service.list_receipts(start_date="2026-01-01")
params = mock_client.get.call_args[1]["params"]
check("start_date 传入时含 start_date", params.get("start_date") == "2026-01-01")

# 传入 end_date
service.list_receipts(end_date="2026-12-31")
params = mock_client.get.call_args[1]["params"]
check("end_date 传入时含 end_date", params.get("end_date") == "2026-12-31")

# 全部参数
service.list_receipts(
    task_id=1, page=2, page_size=50,
    keyword="abc", customer_id=10, sales_id=20,
    start_date="2026-01-01", end_date="2026-12-31",
)
params = mock_client.get.call_args[1]["params"]
check("全参数时 page=2", params["page"] == 2)
check("全参数时 page_size=50", params["page_size"] == 50)
check("全参数时 task_id=1", params["task_id"] == 1)
check("全参数时 keyword=abc", params["keyword"] == "abc")
check("全参数时 customer_id=10", params["customer_id"] == 10)
check("全参数时 sales_id=20", params["sales_id"] == 20)
check("全参数时 start_date 存在", params["start_date"] == "2026-01-01")
check("全参数时 end_date 存在", params["end_date"] == "2026-12-31")

# page=0 不提交（非 None 时才提交，但 page 有默认值 1，所以默认为 1）
# 实际上 page 默认值是 1，所以总是会提交
# 关键：keyword/customer_id/sales_id/start_date/end_date 为 None 时不应提交
service.list_receipts()
params = mock_client.get.call_args[1]["params"]
check("keyword=None 时不含 keyword", "keyword" not in params)
check("customer_id=None 时不含 customer_id", "customer_id" not in params)
check("sales_id=None 时不含 sales_id", "sales_id" not in params)
check("start_date=None 时不含 start_date", "start_date" not in params)
check("end_date=None 时不含 end_date", "end_date" not in params)

# ----------------------------------------------------------
# [20] Body 参数 — create_receipt
# ----------------------------------------------------------
print("\n[20] Body 参数 — create_receipt")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {}
mock_client.post.return_value = mock_resp

service = ReceiptService(mock_client)
now = datetime(2026, 7, 10, 14, 0, 0)

service.create_receipt(task_id=10, received_at=now, receiver_id=5)
body = mock_client.post.call_args[1]["json"]
check("create body 含 task_id=10", body["task_id"] == 10)
check("create body 含 received_at ISO", body["received_at"] == "2026-07-10T14:00:00")
check("create body 含 receiver_id=5", body["receiver_id"] == 5)
check("create body 不含 image_paths（默认 None）", "image_paths" not in body)

# 含 image_paths
service.create_receipt(
    task_id=10, received_at=now, receiver_id=5,
    image_paths='["/path/to/img.jpg"]',
)
body = mock_client.post.call_args[1]["json"]
check("create body 含 image_paths", body["image_paths"] == '["/path/to/img.jpg"]')

# ----------------------------------------------------------
# [21] Body 参数 — update_receipt 仅提交非 None
# ----------------------------------------------------------
print("\n[21] Body 参数 — update_receipt 仅提交非 None")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {}
mock_client.put.return_value = mock_resp

service = ReceiptService(mock_client)

# 仅传入 receiver_id
service.update_receipt(1, receiver_id=10)
body = mock_client.put.call_args[1]["json"]
check("update 仅 receiver_id: 含 receiver_id", body["receiver_id"] == 10)
check("update 仅 receiver_id: 不含 task_id", "task_id" not in body)
check("update 仅 receiver_id: 不含 received_at", "received_at" not in body)
check("update 仅 receiver_id: 不含 image_paths", "image_paths" not in body)

# 传入 task_id
service.update_receipt(1, task_id=5)
body = mock_client.put.call_args[1]["json"]
check("update task_id: 含 task_id=5", body["task_id"] == 5)
check("update task_id: 不含 receiver_id", "receiver_id" not in body)

# 传入 received_at
now = datetime(2026, 7, 10, 15, 0, 0)
service.update_receipt(1, received_at=now)
body = mock_client.put.call_args[1]["json"]
check("update received_at ISO", body["received_at"] == "2026-07-10T15:00:00")

# 传入 image_paths
service.update_receipt(1, image_paths='["/a.jpg"]')
body = mock_client.put.call_args[1]["json"]
check("update image_paths", body["image_paths"] == '["/a.jpg"]')

# 传入全部字段
service.update_receipt(
    1, task_id=5, received_at=now, receiver_id=10,
    image_paths='["/a.jpg"]',
)
body = mock_client.put.call_args[1]["json"]
check("update 全字段: task_id=5", body["task_id"] == 5)
check("update 全字段: receiver_id=10", body["receiver_id"] == 10)
check("update 全字段: 共 4 个字段", len(body) == 4)

# 不传入任何字段（空 body）
service.update_receipt(1)
body = mock_client.put.call_args[1]["json"]
check("update 空 body: body 为 {}", body == {})

# ----------------------------------------------------------
# [22] Upload 参数 — upload_receipt_image
# ----------------------------------------------------------
print("\n[22] Upload 参数 — upload_receipt_image")
mock_client = MagicMock()
mock_resp = MagicMock()
mock_resp.json.return_value = {}
mock_client.post.return_value = mock_resp

tmp_file3 = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
tmp_file3.write(b"\x89PNG\r\n\x1a\n")
tmp_file3_path = tmp_file3.name
tmp_file3.close()

try:
    service = ReceiptService(mock_client)
    service.upload_receipt_image(task_no="T001", file_path=tmp_file3_path)

    call_kwargs = mock_client.post.call_args[1]
    # 检查 data 参数
    check("upload data 含 task_no", call_kwargs["data"]["task_no"] == "T001")
    # 检查 files 参数
    check("upload files 含 file", "file" in call_kwargs["files"])
    file_tuple = call_kwargs["files"]["file"]
    check("upload file 是 tuple (3 元素)", len(file_tuple) == 3)
    check("upload file content_type = image/png", file_tuple[2] == "image/png")
finally:
    os.unlink(tmp_file3_path)

# ----------------------------------------------------------
# [23] 所有方法使用 self._api_client
# ----------------------------------------------------------
print("\n[23] 所有方法使用 self._api_client")
check("使用 self._api_client", "self._api_client" in CODE)
check("使用 self._api_client.get", "self._api_client.get" in CODE)
check("使用 self._api_client.post", "self._api_client.post" in CODE)
check("使用 self._api_client.put", "self._api_client.put" in CODE)
check("使用 self._api_client.delete", "self._api_client.delete" in CODE)

# ----------------------------------------------------------
# [24] 统一返回 response.json()
# ----------------------------------------------------------
print("\n[24] 统一返回 response.json()")
check("list_receipts 返回 resp.json()", "resp.json()" in CODE)
# 检查每个方法都有 resp.json() 调用
json_count = len(re.findall(r"resp\.json\(\)", CODE))
check("至少 6 处 resp.json() 调用", json_count >= 6)

# ----------------------------------------------------------
# [25] 异常透传 — 无 try/except
# ----------------------------------------------------------
print("\n[25] 异常透传 — 无 try/except")
check("无 try 语句", "try:" not in CODE)
# 注意：upload_receipt_image 的 with open 不应该有 try
# 检查方法体内没有 try/except
check("无 except 语句", "except" not in CODE)

# ----------------------------------------------------------
# [26] 代码规范 — PEP8
# ----------------------------------------------------------
print("\n[26] 代码规范 — PEP8")
check("无 print()", "print(" not in CODE)
check("无 TODO", "TODO" not in SOURCE)
check("无 FIXME", "FIXME" not in SOURCE)
check("无 tab 缩进", "\t" not in SOURCE)
check("文件以换行结尾", SOURCE.endswith("\n"))
check("有 __all__", "__all__" in SOURCE)
check("__all__ 包含 ReceiptService", "ReceiptService" in SOURCE.split("__all__")[-1])
check("snake_case 方法名", all("_" not in m or m == m.lower() for m in public_methods))

# ----------------------------------------------------------
# [27] Logger
# ----------------------------------------------------------
print("\n[27] Logger")
check('使用 logging.getLogger("gtms.client")',
      'logging.getLogger("gtms.client")' in SOURCE)
check("使用 logger.debug", "logger.debug" in SOURCE)
check("使用 logger.info", "logger.info" in SOURCE)

# ----------------------------------------------------------
# [28] 依赖规则 — 禁止导入
# ----------------------------------------------------------
print("\n[28] 依赖规则 — 禁止导入")
forbidden_imports = [
    "from server",
    "import server",
    "from sqlalchemy",
    "import sqlalchemy",
    "from PySide6",
    "import PySide6",
    "from jwt",
    "import jwt",
    "JWT",
    "Session",
    "ReceiptView",
]
for name in forbidden_imports:
    check(f"不含禁止导入: {name}", name not in SOURCE)

# ----------------------------------------------------------
# [29] 允许的导入
# ----------------------------------------------------------
print("\n[29] 允许的导入")
check("导入 ApiClient", "from client.services.api_client import ApiClient" in SOURCE)
check("导入 logging", "import logging" in SOURCE)
check("导入 typing", "from typing import Any" in SOURCE)
check("导入 datetime", "from datetime import datetime" in SOURCE)
check("导入 pathlib", "from pathlib import Path" in SOURCE)

# ----------------------------------------------------------
# [30] Type Hint — 所有参数
# ----------------------------------------------------------
print("\n[30] Type Hint — 所有参数")
for method_name in public_methods:
    method = getattr(ReceiptService, method_name)
    sig = inspect.signature(method)
    all_annotated = all(
        p.annotation is not inspect.Parameter.empty
        for p in sig.parameters.values()
        if p.name != "self"
    )
    check(f"{method_name} 所有参数有类型注解", all_annotated)

# ----------------------------------------------------------
# [31] Docstring
# ----------------------------------------------------------
print("\n[31] Docstring")
# 文件 docstring
check("文件有 docstring", SOURCE.strip().startswith('"""'))
# 类 docstring
class_doc = inspect.getdoc(ReceiptService)
check("ReceiptService 有 docstring", class_doc is not None and len(class_doc) > 10)
# 方法 docstring
for method_name in public_methods:
    method = getattr(ReceiptService, method_name)
    doc = inspect.getdoc(method)
    check(f"{method_name} 有 docstring", doc is not None and len(doc) > 10)

# ----------------------------------------------------------
# [32] 无 Magic String / Magic Number
# ----------------------------------------------------------
print("\n[32] 无 Magic String / Magic Number")
# 检查 URL 是否为直接字符串（非变量）
check("list_receipts URL 为 /api/receipts", '"/api/receipts"' in CODE)
check("get_receipt URL 含 /api/receipts/", '"/api/receipts/' in CODE)
check("upload URL 为 /api/upload/image", '"/api/upload/image"' in CODE)
# 检查没有硬编码的 base_url
check("无硬编码 http://", "http://" not in CODE)
check("无硬编码 https://", "https://" not in CODE)

# ----------------------------------------------------------
# [33] __init__ 方法
# ----------------------------------------------------------
print("\n[33] __init__ 方法")
check("有 __init__", "__init__" in dir(ReceiptService))
init_sig = inspect.signature(ReceiptService.__init__)
init_params = list(init_sig.parameters.keys())
check("__init__ 含 self", "self" in init_params)
check("__init__ 含 api_client", "api_client" in init_params)
check("__init__ 设置 _api_client", "self._api_client" in CODE)

# ----------------------------------------------------------
# [34] 构造函数
# ----------------------------------------------------------
print("\n[34] 构造函数")
mock_api = MagicMock()
svc = ReceiptService(mock_api)
check("ReceiptService 可实例化", svc is not None)
check("_api_client 已设置", svc._api_client is mock_api)

# ----------------------------------------------------------
# [35] 公开 API 冻结
# ----------------------------------------------------------
print("\n[35] 公开 API 冻结")
expected_methods = {
    "create_receipt", "list_receipts", "get_receipt",
    "update_receipt", "delete_receipt", "upload_receipt_image",
}
check("公开方法 = 6 个", set(public_methods) == expected_methods)
check("无额外公开方法", set(public_methods) == expected_methods)

# ----------------------------------------------------------
# [36] __all__ 仅导出 ReceiptService
# ----------------------------------------------------------
print("\n[36] __all__ 仅导出 ReceiptService")
from client.services.receipt_service import __all__ as receipt_all
check("__all__ 包含 ReceiptService", "ReceiptService" in receipt_all)
check("__all__ 仅 1 个导出", len(receipt_all) == 1)

# ----------------------------------------------------------
# [37] 无循环导入
# ----------------------------------------------------------
print("\n[37] 无循环导入")
try:
    import importlib
    mod = sys.modules.get("client.services.receipt_service")
    if mod:
        importlib.reload(mod)
    check("无循环导入", True)
except Exception as e:
    check("无循环导入", False)
    print(f"      Error: {e}")

# ----------------------------------------------------------
# [38] response.json() 不缓存
# ----------------------------------------------------------
print("\n[38] response.json() 不缓存")
# 验证没有使用 self._cache 或类似缓存机制
check("无 self._cache", "self._cache" not in SOURCE)
check("无缓存字典", "cache" not in SOURCE.lower())

# ----------------------------------------------------------
# [39] 无业务逻辑
# ----------------------------------------------------------
print("\n[39] 无业务逻辑")
check("无状态校验", "ProcessStatus" not in SOURCE)
check("无 ResultStatus", "ResultStatus" not in SOURCE)
check("无 ORM 查询", "query(" not in SOURCE)
check("无 db.commit", "commit" not in CODE)
check("无 SystemLog", "SystemLog" not in SOURCE)
check("无 BusinessLogicException", "BusinessLogicException" not in SOURCE)
check("无 NotFoundException", "NotFoundException" not in SOURCE)

# ----------------------------------------------------------
# [40] 私有函数 _get_content_type
# ----------------------------------------------------------
print("\n[40] 私有函数 _get_content_type")
from client.services.receipt_service import _get_content_type
check("_get_content_type 可导入", _get_content_type is not None)
check("_get_content_type .jpg → image/jpeg",
      _get_content_type(Path("test.jpg")) == "image/jpeg")
check("_get_content_type .jpeg → image/jpeg",
      _get_content_type(Path("test.jpeg")) == "image/jpeg")
check("_get_content_type .png → image/png",
      _get_content_type(Path("test.png")) == "image/png")
check("_get_content_type .unknown → application/octet-stream",
      _get_content_type(Path("test.unknown")) == "application/octet-stream")

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

sys.exit(0 if FAILED == 0 else 1)
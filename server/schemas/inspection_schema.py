"""检测记录 Schema (Inspection Schema)

Sprint 8 — Task 8.1
严格依据 Sprint 1 InspectionRecord ORM 模型、SRS §4.6、CODE_WIKI.md。
使用 Pydantic v2 ConfigDict(from_attributes=True)。

Schema 列表:
    - InspectionBase:          检测记录公共字段
    - InspectionCreate:        创建检测记录（上传检测报告）
    - InspectionUpdate:        更新检测记录
    - InspectionResponse:      检测记录响应
    - InspectionListResponse:  检测记录列表响应
    - InspectionQuery:         检测记录查询参数
    - InspectionFinishRequest: 完成检测请求
    - InspectionReport:        检测报告上传元数据
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from server.enums import InspectionResult


# ============================================================
# 检测记录公共字段
# ============================================================


class InspectionBase(BaseModel):
    """检测记录公共字段（创建和更新共用）。

    字段基于 Sprint 1 InspectionRecord ORM 模型。
    failure_reason 为 Schema 层校验字段，ORM 中不直接存储。

    Attributes:
        task_id: 关联试磨任务 ID（UNIQUE）。
        inspector_id: 检测人 ID（可选）。
        report_path: 检测报告文件路径（可选）。
        accuracy: 精度检测结果（可选）。
        roughness: 表面粗糙度检测结果（可选）。
        result: 检测结论（InspectionResult: pass / fail，可选）。
        failure_reason: 不合格原因（result=fail 时必填，可选）。
    """

    task_id: int = Field(
        ...,
        description="关联试磨任务 ID",
    )
    inspector_id: Optional[int] = Field(
        default=None,
        description="检测人 ID",
    )
    report_path: Optional[str] = Field(
        default=None,
        max_length=500,
        description="检测报告文件路径",
    )
    accuracy: Optional[str] = Field(
        default=None,
        max_length=100,
        description="精度检测结果",
    )
    roughness: Optional[str] = Field(
        default=None,
        max_length=100,
        description="表面粗糙度检测结果",
    )
    result: Optional[InspectionResult] = Field(
        default=None,
        description="检测结论",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="不合格原因（result=fail 时必填）",
    )


# ============================================================
# 创建检测记录（上传检测报告）
# ============================================================


class InspectionCreate(InspectionBase):
    """创建检测记录 Schema（上传检测报告）。

    继承 InspectionBase。
    必填: task_id。
    校验: result=fail 时 failure_reason 必填。
    """

    @model_validator(mode="after")
    def validate_failure_reason(self) -> "InspectionCreate":
        """校验：result=fail 时 failure_reason 必填。"""
        if self.result == InspectionResult.FAIL and not self.failure_reason:
            raise ValueError("检测结果为不合格时，必须填写不合格原因 (failure_reason)")
        return self


# ============================================================
# 更新检测记录
# ============================================================


class InspectionUpdate(BaseModel):
    """更新检测记录 Schema。

    所有字段均为可选，仅更新传入的非 None 字段。

    Attributes:
        inspector_id: 检测人 ID（可选）。
        report_path: 检测报告文件路径（可选）。
        accuracy: 精度检测结果（可选）。
        roughness: 表面粗糙度检测结果（可选）。
        result: 检测结论（可选）。
        failure_reason: 不合格原因（可选）。
    """

    inspector_id: Optional[int] = Field(
        default=None,
        description="检测人 ID",
    )
    report_path: Optional[str] = Field(
        default=None,
        max_length=500,
        description="检测报告文件路径",
    )
    accuracy: Optional[str] = Field(
        default=None,
        max_length=100,
        description="精度检测结果",
    )
    roughness: Optional[str] = Field(
        default=None,
        max_length=100,
        description="表面粗糙度检测结果",
    )
    result: Optional[InspectionResult] = Field(
        default=None,
        description="检测结论",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="不合格原因（result=fail 时必填）",
    )

    @model_validator(mode="after")
    def validate_failure_reason(self) -> "InspectionUpdate":
        """校验：result=fail 时 failure_reason 必填。"""
        if self.result == InspectionResult.FAIL and not self.failure_reason:
            raise ValueError("检测结果为不合格时，必须填写不合格原因 (failure_reason)")
        return self


# ============================================================
# 检测记录响应
# ============================================================


class InspectionResponse(BaseModel):
    """检测记录响应 Schema。

    包含 ORM 全部可读字段，不含 created_by、updated_by、is_deleted。
    使用 from_attributes=True 支持 ORM 实例直接转换。

    Attributes:
        id: 检测记录 ID。
        task_id: 关联试磨任务 ID。
        report_path: 检测报告文件路径。
        accuracy: 精度检测结果。
        roughness: 表面粗糙度检测结果。
        result: 检测结论。
        inspector_id: 检测人 ID。
        created_at: 创建时间。
        updated_at: 更新时间。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="检测记录 ID")
    task_id: int = Field(..., description="关联试磨任务 ID")
    report_path: Optional[str] = Field(
        default=None,
        description="检测报告文件路径",
    )
    accuracy: Optional[str] = Field(
        default=None,
        description="精度检测结果",
    )
    roughness: Optional[str] = Field(
        default=None,
        description="表面粗糙度检测结果",
    )
    result: Optional[InspectionResult] = Field(
        default=None,
        description="检测结论",
    )
    inspector_id: Optional[int] = Field(
        default=None,
        description="检测人 ID",
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# ============================================================
# 检测记录列表响应
# ============================================================


class InspectionListResponse(BaseModel):
    """检测记录列表响应 Schema。

    Attributes:
        items: 检测记录列表。
        total: 总数。
    """

    items: list[InspectionResponse] = Field(
        default_factory=list,
        description="检测记录列表",
    )
    total: int = Field(..., description="总数")


# ============================================================
# 检测记录查询参数
# ============================================================


class InspectionQuery(BaseModel):
    """检测记录查询参数 Schema。

    支持分页、关键词搜索、状态筛选、日期范围筛选、排序。
    符合 §15.9.20 Performance Standard。

    Attributes:
        page: 页码（从 1 开始）。
        page_size: 每页条数。
        keyword: 关键词搜索（任务编号）。
        inspection_result: 检测结果筛选。
        date_from: 开始日期筛选。
        date_to: 结束日期筛选。
        sort_by: 排序字段。
        sort_order: 排序方向（asc / desc）。
    """

    page: int = Field(
        default=1,
        ge=1,
        description="页码（从 1 开始）",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=200,
        description="每页条数",
    )
    keyword: Optional[str] = Field(
        default=None,
        description="关键词搜索（任务编号）",
    )
    inspection_result: Optional[InspectionResult] = Field(
        default=None,
        description="检测结果筛选",
    )
    date_from: Optional[datetime] = Field(
        default=None,
        description="开始日期筛选",
    )
    date_to: Optional[datetime] = Field(
        default=None,
        description="结束日期筛选",
    )
    sort_by: str = Field(
        default="created_at",
        description="排序字段",
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="排序方向（asc / desc）",
    )


# ============================================================
# 完成检测请求
# ============================================================


class InspectionFinishRequest(BaseModel):
    """完成检测请求 Schema。

    用于提交检测结论，完成检测流程。

    Attributes:
        result: 检测结论（必填）。
        failure_reason: 不合格原因（result=fail 时必填）。
    """

    result: InspectionResult = Field(
        ...,
        description="检测结论",
    )
    failure_reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="不合格原因（result=fail 时必填）",
    )

    @model_validator(mode="after")
    def validate_failure_reason(self) -> "InspectionFinishRequest":
        """校验：result=fail 时 failure_reason 必填。"""
        if self.result == InspectionResult.FAIL and not self.failure_reason:
            raise ValueError("检测结果为不合格时，必须填写不合格原因 (failure_reason)")
        return self


# ============================================================
# 检测报告上传元数据
# ============================================================


class InspectionReport(BaseModel):
    """检测报告上传元数据 Schema。

    仅保存 Upload API 返回的元数据，符合 §15.8 Upload API Standard。
    不保存 path / filepath / full_path / Windows Path / Linux Absolute Path。

    Attributes:
        filename: 文件名。
        url: 文件访问 URL。
        content_type: 文件 MIME 类型。
        size: 文件大小（字节）。
    """

    filename: str = Field(
        ...,
        description="文件名",
    )
    url: str = Field(
        ...,
        description="文件访问 URL",
    )
    content_type: str = Field(
        ...,
        description="文件 MIME 类型",
    )
    size: int = Field(
        ...,
        ge=0,
        description="文件大小（字节）",
    )


__all__ = [
    "InspectionBase",
    "InspectionCreate",
    "InspectionUpdate",
    "InspectionResponse",
    "InspectionListResponse",
    "InspectionQuery",
    "InspectionFinishRequest",
    "InspectionReport",
]

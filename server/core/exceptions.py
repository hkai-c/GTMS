"""
GTMS 统一异常体系

严格依据 CODE_WIKI.md §6.2.3，包含以下异常类：

    BaseAppException                 — 所有业务异常基类
    ├── BusinessLogicException      — 业务逻辑错误 (HTTP 400)
    ├── AuthenticationException     — 认证失败 (HTTP 401)
    ├── PermissionDeniedException   — 权限不足 (HTTP 403)
    ├── NotFoundException           — 资源不存在 (HTTP 404)
    └── DuplicateException          — 重复数据 (HTTP 409)

所有异常均为纯 Python Exception，不依赖 FastAPI / HTTPException。
可通过 to_dict() 转换为统一 JSON 格式，供 FastAPI Exception Handler 使用。

使用方式:
    from server.core.exceptions import NotFoundException

    raise NotFoundException("用户不存在", detail={"user_id": 123})
"""

from typing import Any


class BaseAppException(Exception):
    """所有业务异常的基类。

    提供统一的 code / message / detail / status_code 属性，
    以及 to_dict() 方法，支持 FastAPI 统一异常处理。

    Attributes:
        message: 异常消息（人类可读）。
        status_code: HTTP 状态码。
        code: 业务错误码（机器可读）。
        detail: 可选附加信息。
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str,
        detail: Any | None = None,
    ) -> None:
        """初始化业务异常。

        Args:
            message: 异常消息（人类可读）。
            status_code: HTTP 状态码。
            code: 业务错误码（机器可读，如 "NOT_FOUND"）。
            detail: 可选附加信息（如 dict / list）。
        """
        super().__init__(message)
        self.message: str = message
        self.status_code: int = status_code
        self.code: str = code
        self.detail: Any | None = detail

    def to_dict(self) -> dict[str, Any]:
        """将异常转换为统一 JSON 格式。

        Returns:
            dict: 包含 code、message、detail 的字典。
        """
        result: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.detail is not None:
            result["detail"] = self.detail
        return result

    def __str__(self) -> str:
        """返回异常描述字符串。"""
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        """返回异常可调试表示。"""
        return (
            f"<{self.__class__.__name__}("
            f"code={self.code!r}, "
            f"message={self.message!r}, "
            f"status_code={self.status_code})>"
        )


class BusinessLogicException(BaseAppException):
    """业务逻辑错误。

    用于参数校验失败、业务规则不满足等场景。
    默认 HTTP 400。

    使用方式:
        raise BusinessLogicException("任务状态不允许此操作")
    """

    def __init__(
        self,
        message: str = "Business logic error",
        *,
        code: str = "BUSINESS_ERROR",
        detail: Any | None = None,
    ) -> None:
        """初始化业务逻辑异常。

        Args:
            message: 异常消息。
            code: 错误码，默认 "BUSINESS_ERROR"。
            detail: 可选附加信息。
        """
        super().__init__(
            message=message,
            status_code=400,
            code=code,
            detail=detail,
        )


class AuthenticationException(BaseAppException):
    """认证失败。

    用于登录失败、Token 无效等场景。
    默认 HTTP 401。

    使用方式:
        raise AuthenticationException("用户名或密码错误")
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        *,
        code: str = "AUTHENTICATION_FAILED",
        detail: Any | None = None,
    ) -> None:
        """初始化认证异常。

        Args:
            message: 异常消息。
            code: 错误码，默认 "AUTHENTICATION_FAILED"。
            detail: 可选附加信息。
        """
        super().__init__(
            message=message,
            status_code=401,
            code=code,
            detail=detail,
        )


class PermissionDeniedException(BaseAppException):
    """权限不足。

    用于用户无权限访问资源等场景。
    默认 HTTP 403。

    使用方式:
        raise PermissionDeniedException("仅管理员可执行此操作")
    """

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        code: str = "PERMISSION_DENIED",
        detail: Any | None = None,
    ) -> None:
        """初始化权限不足异常。

        Args:
            message: 异常消息。
            code: 错误码，默认 "PERMISSION_DENIED"。
            detail: 可选附加信息。
        """
        super().__init__(
            message=message,
            status_code=403,
            code=code,
            detail=detail,
        )


class NotFoundException(BaseAppException):
    """资源不存在。

    用于查询不到指定资源等场景。
    默认 HTTP 404。

    使用方式:
        raise NotFoundException("任务不存在", detail={"task_id": 123})
    """

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        code: str = "NOT_FOUND",
        detail: Any | None = None,
    ) -> None:
        """初始化资源不存在异常。

        Args:
            message: 异常消息。
            code: 错误码，默认 "NOT_FOUND"。
            detail: 可选附加信息。
        """
        super().__init__(
            message=message,
            status_code=404,
            code=code,
            detail=detail,
        )


class DuplicateException(BaseAppException):
    """重复数据。

    用于唯一约束冲突等场景。
    默认 HTTP 409。

    使用方式:
        raise DuplicateException("任务编号已存在", detail={"task_no": "TM202600001"})
    """

    def __init__(
        self,
        message: str = "Duplicate data",
        *,
        code: str = "DUPLICATE_DATA",
        detail: Any | None = None,
    ) -> None:
        """初始化重复数据异常。

        Args:
            message: 异常消息。
            code: 错误码，默认 "DUPLICATE_DATA"。
            detail: 可选附加信息。
        """
        super().__init__(
            message=message,
            status_code=409,
            code=code,
            detail=detail,
        )


__all__ = [
    "BaseAppException",
    "BusinessLogicException",
    "AuthenticationException",
    "PermissionDeniedException",
    "NotFoundException",
    "DuplicateException",
]
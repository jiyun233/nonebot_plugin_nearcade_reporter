import re

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self


class InvalidRegexError(ValueError):
    def __init__(self, detail: str) -> None:
        super().__init__(f"无效的正则表达式: {detail}")


class MissingRegexGroupError(ValueError):
    def __init__(self, group_name: str, available: set[str]) -> None:
        super().__init__(
            f"分组 '{group_name}' 不存在于 regex 中，可用分组: {available}"
        )

class InvalidArcadeSourceError(ValueError):
    def __init__(self, source: str) -> None:
        super().__init__(f"无效的机厅来源: {source}")

class QueryAttendanceRegexConfig(BaseModel):
    enabled: bool = Field(description="是否启用查询机厅人数")
    pattern: str = Field(description="用于匹配的正则表达式")
    arcade_alias: str = Field(description="机厅名称/别名")

    @staticmethod
    def _extract_group_names(pattern: str) -> set[str]:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise InvalidRegexError(str(e)) from e

        return set(regex.groupindex.keys())

    @model_validator(mode="after")
    def validate_group_names(self) -> Self:
        groups = self._extract_group_names(self.pattern)

        if self.arcade_alias not in groups:
            raise MissingRegexGroupError(self.arcade_alias, groups)

        return self

class UpdateAttendanceRegexConfig(BaseModel):
    enabled: bool = Field(description="是否启用更新机厅人数")
    pattern: str = Field(description="用于匹配的正则表达式")
    arcade_alias: str = Field(description="机厅名称/别名")
    attendence_count: str = Field(description="当前人数")

    @staticmethod
    def _extract_group_names(pattern: str) -> set[str]:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise InvalidRegexError(str(e)) from e

        return set(regex.groupindex.keys())

    @model_validator(mode="after")
    def validate_group_names(self) -> Self:
        groups = self._extract_group_names(self.pattern)

        if self.arcade_alias not in groups:
            raise MissingRegexGroupError(self.arcade_alias, groups)

        if self.attendence_count not in groups:
            raise MissingRegexGroupError(self.attendence_count, groups)

        return self

class ArcadeConfig(BaseModel):
    arcade_source: str = Field(description="机厅来源")
    aliases: set[str] = Field(
        default_factory=set,
        description="机厅别名",
    )
    default_game_id: int = Field(description="默认游戏ID")

    @field_validator("arcade_source")
    @classmethod
    def validate_source_availability(cls, value: str) -> str:
        if value not in {"bemani", "ziv"}:
            raise InvalidArcadeSourceError(value)
        return value

class Config(BaseModel):
    api_token: str
    query_attendance_match: QueryAttendanceRegexConfig
    update_attendance_match: UpdateAttendanceRegexConfig
    arcades: dict[int, ArcadeConfig] = Field(
        default_factory=dict,
        description="机厅配置",
    )

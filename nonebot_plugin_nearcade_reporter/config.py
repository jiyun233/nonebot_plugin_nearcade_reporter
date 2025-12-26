import re

from errors import (
    ArcadeNotFoundError,
    InvalidArcadeSourceError,
    InvalidRegexError,
    MissingRegexGroupError,
)
from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self


class QueryAttendanceRegexConfig(BaseModel):
    enabled: bool = Field(description="是否启用查询机厅人数")
    pattern: str = Field(description="用于匹配的正则表达式")
    arcade_alias: str = Field(description="机厅名称/别名")
    reply_message: str = Field(description="回复消息")

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
    attendance_count: str = Field(description="当前人数")
    reply_message: str = Field(description="回复消息")

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

        if self.attendance_count not in groups:
            raise MissingRegexGroupError(self.attendance_count, groups)

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

    _alias_index: dict[str, int] = {}

    @model_validator(mode="after")
    def build_alias_index(self) -> Self:
        index: dict[str, int] = {}

        for arcade_id, arcade in self.arcades.items():
            for alias in arcade.aliases:
                key = alias.casefold()
                index[key] = arcade_id

        self._alias_index = index
        return self

    def find_arcade_by_alias(
        self, arcade_name: str
    ) -> tuple[int, ArcadeConfig]:
        key = arcade_name.casefold()

        arcade_id = self._alias_index.get(key)
        if arcade_id is None:
            raise ArcadeNotFoundError(arcade_name)

        return arcade_id, self.arcades[arcade_id]

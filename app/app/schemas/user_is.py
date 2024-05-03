"""
DTO schemes for User from IS entity.
Test variation
"""
from typing import Optional, List
from pydantic import BaseModel


class Organization(BaseModel):
    name: Optional[str]
    note: Optional[str]


class UserIS(BaseModel):
    country: str
    created_at: str
    email: str
    first_name: str
    id: int
    im: Optional[str]
    note: Optional[str]
    organization: Optional[Organization]
    phone: Optional[str]
    phone_vpn: Optional[str]
    photo_file: Optional[str]
    photo_file_small: Optional[str]
    state: str
    surname: str
    ui_language: Optional[str]
    ui_skin: str
    username: str
    usertype: str


class LimitObject(BaseModel):
    id: int
    name: str
    alias: str
    note: str


class Role(BaseModel):
    role: str
    name: str
    description: str
    limit: str
    limit_objects: list[LimitObject]


class RoleList(BaseModel):
    roles: list[Role]

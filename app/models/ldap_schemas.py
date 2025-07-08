from pydantic import BaseModel
from typing import List, Optional

class LdapUser(BaseModel):
    """
    LDAP 用户数据结构
    """
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    groups: List[str] = []

class LdapGroup(BaseModel):
    """
    LDAP 组数据结构
    """
    groupname: str
    members: List[str] = []

class CreateUserRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    email: Optional[str] = None

class CreateGroupRequest(BaseModel):
    groupname: str

class AddUserToGroupRequest(BaseModel):
    username: str
    groupname: str

class AlertMessage(BaseModel):
    """
    Alertmanager 告警消息结构
    """
    group_id: str
    message: str 
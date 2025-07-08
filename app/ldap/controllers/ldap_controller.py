# 迁移自ldap_api.py
# ... existing code ... 

from fastapi import APIRouter
import logging
from pydantic import BaseModel
from typing import Optional
# from app.models.ldap_schemas import LdapUser, LdapGroup, CreateUserRequest, CreateGroupRequest, AddUserToGroupRequest
from app.ldap.services.ldap_service import LdapManager
from app.models.alert_schemas import CommonResponse

router = APIRouter(prefix="/ldap", tags=["LDAP"])
logger = logging.getLogger("ldap_controller")

class EnvParam(BaseModel):
    env: Optional[str] = "prod"

class UserQueryParam(EnvParam):
    uid: str

class GroupQueryParam(EnvParam):
    groupname: str

class AllQueryParam(EnvParam):
    pass

class CreateUserParam(EnvParam):
    username: str
    email: Optional[str] = None
    gidNumber: Optional[str] = None
    homeDirectory: Optional[str] = None

class CreateGroupParam(EnvParam):
    groupname: str
    gidNumber: Optional[str] = None

class AddUserToGroupParam(EnvParam):
    username: str
    groupname: str

def get_ldap_mgr(env: str = "prod"):
    logger.info(f"当前环境: {env}")
    return LdapManager()

@router.post("/users", summary="查询所有用户及其组", response_model=CommonResponse[list])
def list_users(param: AllQueryParam):
    logger.info(f"调用接口：查询所有用户及其组，环境={param.env}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        users = ldap_mgr.get_all_users_with_groups()
        return {"code": 0, "data": users, "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询所有用户失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.post("/user/info", summary="查询指定用户信息", response_model=CommonResponse[dict])
def get_user_info(param: UserQueryParam):
    logger.info(f"调用接口：查询用户信息，uid={param.uid}，环境={param.env}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        user = ldap_mgr.get_user_with_groups(param.uid)
        if user:
            return {"code": 0, "data": user, "msg": "查询成功"}
        else:
            logger.warning(f"未找到用户: {param.uid}")
            return {"code": 1, "data": None, "msg": f"未找到用户: {param.uid}"}
    except Exception as e:
        logger.error(f"查询用户失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.post("/groups", summary="查询所有组及其成员", response_model=CommonResponse[list])
def list_groups(param: AllQueryParam):
    logger.info(f"调用接口：查询所有组及其成员，环境={param.env}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        groups = ldap_mgr.get_all_groups_with_members()
        return {"code": 0, "data": groups, "msg": "查询成功"}
    except Exception as e:
        logger.error(f"查询所有组失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.post("/group/info", summary="查询指定组信息", response_model=CommonResponse[dict])
def get_group_info(param: GroupQueryParam):
    logger.info(f"调用接口：查询组信息，组名={param.groupname}，环境={param.env}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        group = ldap_mgr.get_group_with_members(param.groupname)
        if group:
            return {"code": 0, "data": group, "msg": "查询成功"}
        else:
            logger.warning(f"未找到组: {param.groupname}")
            return {"code": 1, "data": None, "msg": f"未找到组: {param.groupname}"}
    except Exception as e:
        logger.error(f"查询组失败: {e}")
        return {"code": 1, "data": None, "msg": f"查询失败: {str(e)}"}

@router.post("/user/create", summary="创建用户", response_model=CommonResponse[dict])
def create_user(param: CreateUserParam):
    logger.info(f"调用接口：创建用户，参数={param}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        ok = ldap_mgr.create_user(
            username=param.username,
            email=param.email or "",
            gidNumber=param.gidNumber or '',
            homeDirectory=param.homeDirectory or ''
        )
        if ok:
            user = ldap_mgr.get_user_with_groups(param.username)
            logger.info(f"创建用户成功: {user}")
            return {"code": 0, "data": {"success": True, "user": user}, "msg": "创建用户成功"}
        else:
            logger.error(f"创建用户失败: {param.username}")
            return {"code": 1, "data": None, "msg": "创建用户失败"}
    except Exception as e:
        logger.error(f"创建用户异常: {e}")
        return {"code": 1, "data": None, "msg": f"创建用户失败: {str(e)}"}

@router.post("/group/create", summary="创建组", response_model=CommonResponse[dict])
def create_group(param: CreateGroupParam):
    logger.info(f"调用接口：创建组，参数={param}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        ok = ldap_mgr.create_group(
            groupname=param.groupname,
            gidNumber=param.gidNumber or ''
        )
        if ok:
            group = ldap_mgr.get_group_with_members(param.groupname)
            logger.info(f"创建组成功: {group}")
            return {"code": 0, "data": {"success": True, "group": group}, "msg": "创建组成功"}
        else:
            logger.error(f"创建组失败: {param.groupname}")
            return {"code": 1, "data": None, "msg": "创建组失败"}
    except Exception as e:
        logger.error(f"创建组异常: {e}")
        return {"code": 1, "data": None, "msg": f"创建组失败: {str(e)}"}

@router.post("/group/add", summary="添加用户到组", response_model=CommonResponse[dict])
def add_user_to_group(param: AddUserToGroupParam):
    logger.info(f"调用接口：添加用户到组，参数={param}")
    try:
        ldap_mgr = get_ldap_mgr(param.env)
        ok = ldap_mgr.add_user_to_group(param.username, param.groupname)
        if ok:
            return {"code": 0, "data": {"success": True}, "msg": "添加用户到组成功"}
        else:
            return {"code": 1, "data": None, "msg": "添加用户到组失败"}
    except Exception as e:
        logger.error(f"添加用户到组异常: {e}")
        return {"code": 1, "data": None, "msg": f"添加用户到组失败: {str(e)}"} 
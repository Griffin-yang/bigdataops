# 迁移自ldap_module.py
# ... existing code ... 

import logging
from ldap3 import Server, Connection, ALL, MODIFY_ADD, SUBTREE
from app.config import get_settings
from typing import List, Dict, Optional
import time

settings = get_settings()
logger = logging.getLogger("ldap_service")

class LdapManager:
    """
    LDAP 管理类，封装用户和组的相关操作，适配posixAccount/posixGroup结构
    """
    def __init__(self):
        self.server = Server(settings.ldap_server, get_info=ALL)
        self.conn = Connection(self.server, user=settings.ldap_user, password=settings.ldap_password, auto_bind=True)
        self.base_dn = settings.ldap_base_dn
        self.group_dn = settings.ldap_group_dn

    def get_all_users(self) -> List[Dict]:
        logger.info("查询所有用户及其所在组（posixAccount）")
        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=posixAccount)',
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            users = []
            for entry in self.conn.entries:
                user = {
                    "uid": str(entry.uid),
                    "username": str(entry.cn),
                    "email": str(entry.mail) if 'mail' in entry else "",
                    "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                    "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
                }
                users.append(user)
            logger.info(f"查询到用户数量: {len(users)}")
            return users
        except Exception as e:
            logger.error(f"查询所有用户失败: {e}")
            return []

    def get_user_by_name(self, username: str) -> Optional[Dict]:
        logger.info(f"查询用户信息: {username}")
        try:
            search_filter = f'(uid={username})'
            self.conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            if not self.conn.entries:
                logger.warning(f"未找到用户: {username}")
                return None
            entry = self.conn.entries[0]
            user = {
                "uid": str(entry.uid),
                "username": str(entry.cn),
                "email": str(entry.mail) if 'mail' in entry else "",
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
            }
            logger.info(f"用户信息: {user}")
            return user
        except Exception as e:
            logger.error(f"查询用户失败: {e}")
            return None

    def get_all_groups(self) -> List[Dict]:
        logger.info("查询所有组及其成员（posixGroup）")
        try:
            self.conn.search(
                search_base=self.group_dn,
                search_filter='(objectClass=posixGroup)',
                search_scope=SUBTREE,
                attributes=['cn', 'gidNumber', 'memberUid']
            )
            groups = []
            for entry in self.conn.entries:
                group = {
                    "groupname": str(entry.cn),
                    "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                    "members": [str(m) for m in entry.memberUid] if 'memberUid' in entry else []
                }
                groups.append(group)
            logger.info(f"查询到组数量: {len(groups)}")
            return groups
        except Exception as e:
            logger.error(f"查询所有组失败: {e}")
            return []

    def get_group_by_name(self, groupname: str) -> Optional[Dict]:
        logger.info(f"查询组信息: {groupname}")
        try:
            search_filter = f'(cn={groupname})'
            self.conn.search(
                search_base=self.group_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn', 'gidNumber', 'memberUid']
            )
            if not self.conn.entries:
                logger.warning(f"未找到组: {groupname}")
                return None
            entry = self.conn.entries[0]
            group = {
                "groupname": str(entry.cn),
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                "members": [str(m) for m in entry.memberUid] if 'memberUid' in entry else []
            }
            logger.info(f"组信息: {group}")
            return group
        except Exception as e:
            logger.error(f"查询组失败: {e}")
            return None

    @staticmethod
    def generate_user_id():
        timestamp = int(time.time() % 1000000)
        return timestamp

    def create_user(self, username: str, email: str = '', gidNumber: str = '', homeDirectory: str = '') -> bool:
        logger.info(f"创建用户: {username}, gidNumber: {gidNumber}, homeDirectory: {homeDirectory}, email: {email}")
        uid_num = str(LdapManager.generate_user_id())
        dn = f"uid={username},{self.base_dn}"
        attributes = {
            'objectClass': ['top', 'posixAccount', 'posixGroup'],
            'uid': username,
            'cn': username,
            'gidNumber': gidNumber or uid_num,
            'uidNumber': uid_num,
            'homeDirectory': homeDirectory or f"/home/{username}"
        }
        if email:
            attributes['mail'] = email
        try:
            result = self.conn.add(dn, attributes=attributes)
            logger.info(f"创建用户结果: {result}")
            return result
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return False

    def create_group(self, groupname: str, gidNumber: str = '') -> bool:
        logger.info(f"创建组: {groupname}, gidNumber: {gidNumber}")
        gid_num = str(LdapManager.generate_user_id())
        dn = f"cn={groupname},{self.group_dn}"
        attributes = {
            'objectClass': ['top', 'posixGroup'],
            'cn': groupname,
            'gidNumber': gidNumber or gid_num,
        }
        try:
            result = self.conn.add(dn, attributes=attributes)
            logger.info(f"创建组结果: {result}")
            return result
        except Exception as e:
            logger.error(f"创建组失败: {e}")
            return False

    def add_user_to_group(self, username: str, groupname: str) -> bool:
        logger.info(f"将用户 {username} 添加到组 {groupname}")
        group_dn = f"cn={groupname},{self.group_dn}"
        try:
            result = self.conn.modify(group_dn, {'memberUid': [(MODIFY_ADD, [username])]})
            logger.info(f"添加用户到组结果: {result}")
            return result
        except Exception as e:
            logger.error(f"添加用户到组失败: {e}")
            return False

    def get_all_users_with_groups(self) -> List[Dict]:
        logger.info("查询所有用户及其组（含组名列表）")
        try:
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=posixAccount)',
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            users = [
                {
                    "uid": str(entry.uid),
                    "username": str(entry.cn),
                    "email": str(entry.mail) if 'mail' in entry else "",
                    "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                    "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
                }
                for entry in self.conn.entries
            ]
            # 查所有组
            self.conn.search(
                search_base=self.group_dn,
                search_filter='(objectClass=posixGroup)',
                search_scope=SUBTREE,
                attributes=['cn', 'memberUid']
            )
            group_map = {}
            for entry in self.conn.entries:
                groupname = str(entry.cn)
                members = [str(m) for m in entry.memberUid] if 'memberUid' in entry else []
                for uid in members:
                    group_map.setdefault(uid, []).append(groupname)
            # 组装用户及其组
            for user in users:
                user["groups"] = group_map.get(user["uid"], [])
            logger.info(f"查询到用户数量: {len(users)}")
            return users
        except Exception as e:
            logger.error(f"查询所有用户及其组失败: {e}")
            return []

    def get_user_with_groups(self, uid: str) -> Optional[Dict]:
        logger.info(f"查询用户信息及其组: {uid}")
        try:
            # 查用户
            self.conn.search(
                search_base=self.base_dn,
                search_filter=f'(uid={uid})',
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            if not self.conn.entries:
                logger.warning(f"未找到用户: {uid}")
                return None
            entry = self.conn.entries[0]
            user = {
                "uid": str(entry.uid),
                "username": str(entry.cn),
                "email": str(entry.mail) if 'mail' in entry else "",
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
            }
            # 查所有组
            self.conn.search(
                search_base=self.group_dn,
                search_filter='(objectClass=posixGroup)',
                search_scope=SUBTREE,
                attributes=['cn', 'memberUid']
            )
            groups = []
            for entry in self.conn.entries:
                groupname = str(entry.cn)
                members = [str(m) for m in entry.memberUid] if 'memberUid' in entry else []
                if uid in members:
                    groups.append(groupname)
            user["groups"] = groups
            logger.info(f"用户信息: {user}")
            return user
        except Exception as e:
            logger.error(f"查询用户及其组失败: {e}")
            return None

    def get_all_groups_with_members(self) -> List[Dict]:
        logger.info("查询所有组及其成员（含成员详细信息）")
        try:
            # 查所有组
            self.conn.search(
                search_base=self.group_dn,
                search_filter='(objectClass=posixGroup)',
                search_scope=SUBTREE,
                attributes=['cn', 'gidNumber', 'memberUid']
            )
            groups = []
            group_entries = self.conn.entries[:]
            # 查所有用户，做成map
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=posixAccount)',
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            user_map = {str(entry.uid): {
                "uid": str(entry.uid),
                "username": str(entry.cn),
                "email": str(entry.mail) if 'mail' in entry else "",
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
            } for entry in self.conn.entries}
            for entry in group_entries:
                group = {
                    "groupname": str(entry.cn),
                    "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                    "members": [user_map[uid] for uid in entry.memberUid if uid in user_map] if 'memberUid' in entry else []
                }
                groups.append(group)
            logger.info(f"查询到组数量: {len(groups)}")
            return groups
        except Exception as e:
            logger.error(f"查询所有组及其成员失败: {e}")
            return []

    def get_group_with_members(self, groupname: str) -> Optional[Dict]:
        logger.info(f"查询组信息及其成员: {groupname}")
        try:
            # 查组
            self.conn.search(
                search_base=self.group_dn,
                search_filter=f'(cn={groupname})',
                search_scope=SUBTREE,
                attributes=['cn', 'gidNumber', 'memberUid']
            )
            if not self.conn.entries:
                logger.warning(f"未找到组: {groupname}")
                return None
            entry = self.conn.entries[0]
            group = {
                "groupname": str(entry.cn),
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
            }
            # 查所有用户，做成map
            self.conn.search(
                search_base=self.base_dn,
                search_filter='(objectClass=posixAccount)',
                search_scope=SUBTREE,
                attributes=['uid', 'cn', 'mail', 'gidNumber', 'homeDirectory']
            )
            user_map = {str(entry.uid): {
                "uid": str(entry.uid),
                "username": str(entry.cn),
                "email": str(entry.mail) if 'mail' in entry else "",
                "gidNumber": str(entry.gidNumber) if 'gidNumber' in entry else "",
                "homeDirectory": str(entry.homeDirectory) if 'homeDirectory' in entry else ""
            } for entry in self.conn.entries}
            group["members"] = [user_map[uid] for uid in entry.memberUid if uid in user_map] if 'memberUid' in entry else []
            logger.info(f"组信息: {group}")
            return group
        except Exception as e:
            logger.error(f"查询组及其成员失败: {e}")
            return None 
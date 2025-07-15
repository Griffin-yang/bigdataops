#!/bin/bash
# ======================================================
# 数据库重建脚本
# 删除旧表并创建增强版告警系统表结构
# ======================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 数据库配置（请根据实际情况修改）
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_NAME="${DB_NAME:-bigdataops}"
DB_USER="${DB_USER:-root}"

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}BigDataOps 告警系统数据库重建脚本 v2.0${NC}"
echo -e "${BLUE}======================================================${NC}"

# 检查是否提供了密码
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}请输入数据库密码:${NC}"
    read -s DB_PASSWORD
fi

# 构建 MySQL 连接命令
MYSQL_CMD="mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME}"

echo -e "\n${YELLOW}数据库配置:${NC}"
echo -e "  主机: ${DB_HOST}:${DB_PORT}"
echo -e "  数据库: ${DB_NAME}"
echo -e "  用户: ${DB_USER}"

# 检查数据库连接
echo -e "\n${BLUE}检查数据库连接...${NC}"
if ! $MYSQL_CMD -e "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${RED}❌ 数据库连接失败！请检查配置${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 数据库连接成功${NC}"

# 备份现有数据（可选）
echo -e "\n${YELLOW}是否需要备份现有数据？(y/N)${NC}"
read -n 1 -r backup_choice
echo
if [[ $backup_choice =~ ^[Yy]$ ]]; then
    backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo -e "${BLUE}正在备份数据到: ${backup_file}${NC}"
    mysqldump -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} \
        alert_rule alert_history alert_notify_template > $backup_file
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据备份成功${NC}"
    else
        echo -e "${RED}❌ 数据备份失败${NC}"
        exit 1
    fi
fi

# 确认重建
echo -e "\n${RED}警告: 即将删除并重建以下表:${NC}"
echo -e "  - alert_history"
echo -e "  - alert_rule"
echo -e "  - alert_notify_template"
echo -e "\n${YELLOW}确认执行？(y/N)${NC}"
read -n 1 -r confirm
echo

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}操作已取消${NC}"
    exit 0
fi

# 执行建表脚本
echo -e "\n${BLUE}执行建表脚本...${NC}"
if $MYSQL_CMD < docs/database_schema.sql; then
    echo -e "${GREEN}✅ 表结构创建成功${NC}"
else
    echo -e "${RED}❌ 表结构创建失败${NC}"
    exit 1
fi

# 验证表结构
echo -e "\n${BLUE}验证表结构...${NC}"
table_count=$($MYSQL_CMD -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '${DB_NAME}' AND table_name IN ('alert_rule', 'alert_history', 'alert_notify_template');" -s)

if [ "$table_count" -eq 3 ]; then
    echo -e "${GREEN}✅ 所有表创建成功${NC}"
    
    # 显示数据统计
    echo -e "\n${BLUE}数据统计:${NC}"
    $MYSQL_CMD -e "
    SELECT 
        'Templates' as item, COUNT(*) as count FROM alert_notify_template
    UNION ALL
    SELECT 
        'Rules' as item, COUNT(*) as count FROM alert_rule
    UNION ALL
    SELECT 
        'History' as item, COUNT(*) as count FROM alert_history;
    "
else
    echo -e "${RED}❌ 表创建不完整，请检查${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 数据库重建完成！${NC}"
echo -e "\n${BLUE}新功能说明:${NC}"
echo -e "  1. ✅ 持续时间控制 - 告警超过设定时间后自动停止"
echo -e "  2. ✅ 发送次数限制 - 可设置最大发送次数"
echo -e "  3. ✅ 手动确认功能 - 支持手动确认停止告警"
echo -e "  4. ✅ 乐聊通知支持 - 新增乐聊模板类型"
echo -e "  5. ✅ 每日重置机制 - 计数器每天自动重置"

echo -e "\n${YELLOW}下一步:${NC}"
echo -e "  1. 重启后端服务使数据模型生效"
echo -e "  2. 在前端界面中配置告警规则"
echo -e "  3. 测试新的抑制和确认功能"

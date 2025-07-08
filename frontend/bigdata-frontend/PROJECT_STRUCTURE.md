# LejoyCluster 前端项目结构

## 📁 企业级目录结构

```
src/
├── components/          # 可复用组件
│   ├── common/         # 通用组件 (按钮、表单、模态框等)
│   ├── charts/         # 图表组件
│   └── forms/          # 表单组件
├── layouts/            # 布局组件
│   └── MainLayout.vue  # 主布局 (侧边栏 + 顶部导航)
├── views/              # 页面组件
│   ├── Login.vue       # 登录页
│   ├── Dashboard.vue   # 首页仪表板
│   ├── AlertRules.vue  # 告警规则管理
│   ├── AlertTemplates.vue # 告警模板管理
│   ├── UserManagement.vue # 用户管理
│   └── Monitoring.vue  # 集群监控
├── services/           # API 服务层
│   ├── api.ts          # 基础 API 配置
│   ├── alertService.ts # 告警相关 API
│   ├── userService.ts  # 用户相关 API
│   └── index.ts        # 服务统一导出
├── types/              # TypeScript 类型定义
│   └── index.ts        # 全局类型定义
├── constants/          # 常量定义
│   └── index.ts        # 全局常量
├── utils/              # 工具函数
│   ├── helpers/        # 辅助函数
│   │   └── format.ts   # 格式化函数
│   └── api.ts          # API 工具 (向后兼容)
├── hooks/              # Vue 组合式函数 (未来扩展)
├── stores/             # Pinia 状态管理
│   └── counter.ts      # 示例 store
├── router/             # 路由配置
│   └── index.ts        # 路由定义
└── assets/             # 静态资源
    ├── images/         # 图片
    └── styles/         # 样式文件
```

## 🏗️ 架构设计原则

### 1. **分层架构**
- **视图层 (Views)**: 页面组件，负责展示和用户交互
- **组件层 (Components)**: 可复用的UI组件
- **服务层 (Services)**: API调用和数据处理
- **工具层 (Utils)**: 纯函数工具和辅助功能

### 2. **模块化设计**
- 按功能模块组织代码
- 每个模块职责单一、高内聚低耦合
- 统一的导入导出规范

### 3. **类型安全**
- 完整的 TypeScript 类型定义
- 接口统一管理
- 编译时错误检查

## 📋 编码规范

### API 服务使用
```typescript
// ✅ 推荐：使用新的服务层
import { AlertService } from '@/services'
const rules = await AlertService.getRules()

// ⚠️ 兼容：仍可使用旧接口
import { alertAPI } from '@/utils/api'
const rules = await alertAPI.getRules()
```

### 类型定义使用
```typescript
// ✅ 统一使用类型定义
import type { AlertRule, User } from '@/types'

// ✅ 使用常量
import { ROUTES, ALERT_SEVERITY } from '@/constants'
```

### 工具函数使用
```typescript
// ✅ 使用格式化函数
import { formatDateTime, formatSeverity } from '@/utils/helpers/format'
```

## 🔄 迁移指南

### 从旧结构迁移
1. **API 调用**: 逐步迁移到新的 service 层
2. **类型定义**: 使用统一的 types 文件
3. **常量**: 替换硬编码为常量引用
4. **布局**: 使用新的 MainLayout 组件

### 向后兼容性
- 保留旧的 `utils/api.ts` 接口
- 现有代码无需立即修改
- 新功能建议使用新架构

## 🚀 最佳实践

1. **组件设计**: 单一职责，可复用，易测试
2. **状态管理**: 合理使用 Pinia，避免过度使用全局状态
3. **错误处理**: 统一的错误处理机制
4. **性能优化**: 懒加载、代码分割、缓存策略
5. **可维护性**: 清晰的命名、完整的文档、统一的代码风格

## 📦 依赖管理

### 核心依赖
- Vue 3 + TypeScript
- Element Plus UI 框架
- Vue Router 路由管理
- Pinia 状态管理
- Axios HTTP 客户端
- ECharts 数据可视化

### 开发工具
- Vite 构建工具
- ESLint 代码检查
- TypeScript 类型检查 
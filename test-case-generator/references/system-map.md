# System Map

## 1. Domain overview

本项目按业务域组织模块，而不是按平台拆成两套重复知识：

- `account-access`：认证中心、后台账号管理、角色权限、组织架构
- `commerce-ops`：商品中心、banner 投放、订单管理、退款审批
- `platform-ops`：运营看板、操作日志、消息中心

平台区分通过 `平台` 字段和 `platform_scope` / `client_signals` / `server_signals` 实现。同一业务模块可以在 `客户端` 和 `账服` 产生不同测试用例，不要把同一业务能力拆成两份完全独立的索引，除非前后端行为已经长期分叉成两个真正不同的子系统。

## 2. Primary-module extension rules

### 2.1 权限与账号相关

- 需求涉及登录、会话、账号启停、重置密码、组织归属时：
  - 主模块通常落在 `auth-center`、`admin-user`、`organization`
  - 关联检查 `role-permission` 和 `operation-log`
- 需求涉及菜单、按钮、接口权限、数据范围时：
  - 主模块通常落在 `role-permission`
  - 关联检查被授权的业务模块、`admin-user`、`operation-log`

### 2.2 商品与运营相关

- 需求涉及商品上下架、价格、库存、导入导出时：
  - 主模块通常落在 `product-catalog`
  - 关联检查 `marketing-banner`、`order-management`、`dashboard`、`operation-log`
- 需求涉及 banner 上下线、跳转和排序时：
  - 主模块通常落在 `marketing-banner`
  - 关联检查 `product-catalog`、`dashboard`、`operation-log`

### 2.3 订单与退款相关

- 需求涉及订单详情、关闭订单、订单筛选、履约信息时：
  - 主模块通常落在 `order-management`
  - 关联检查 `refund-approval`、`notification-center`、`dashboard`、`operation-log`
- 需求涉及退款审批、重审、拒绝原因、状态回写时：
  - 主模块通常落在 `refund-approval`
  - 关联检查 `order-management`、`role-permission`、`notification-center`、`dashboard`、`operation-log`

### 2.4 平台能力相关

- 需求涉及统计口径、趋势图、榜单、筛选统计时：
  - 主模块通常落在 `dashboard`
  - 关联检查指标来源模块和 `role-permission`
- 需求涉及日志留痕、日志查询、审计轨迹时：
  - 主模块通常落在 `operation-log`
  - 关联检查触发日志的业务模块
- 需求涉及消息模板、发送、触达、失败重试时：
  - 主模块通常落在 `notification-center`
  - 关联检查触发消息的业务模块和 `operation-log`

## 3. Always-check heuristics

当需求中出现以下信号时，必须增加关联校验：

- `permission`：菜单可见性、按钮可用性、接口越权、数据范围过滤
- `session`：登录态、生效时机、会话续期、失效后表现
- `security`：错误次数限制、验证码、敏感字段脱敏、风控或限流
- `data-integrity`：写库、状态一致性、前后端回显一致、导入导出一致
- `state-transition`：合法状态迁移、非法状态下操作、回退和中断流程
- `notification`：触达条件、收件人、模板变量、失败重试、重复发送
- `reporting`：统计口径、刷新时机、筛选维度、时间边界、分组织口径
- `audit-log`：操作留痕、审批轨迹、日志查询、日志字段完整性

## 4. Platform split examples

### 示例 1：前后端混合需求

需求：点击“审批通过”按钮后，页面提示成功，退款状态更新为“已通过”，并给申请人发送通知。

拆分方式：

- `客户端`：按钮可点击性、确认弹窗、成功提示、页面状态刷新
- `账服`：审批接口校验、状态回写、通知触发、操作日志留痕

### 示例 2：统计联动需求

需求：商品下架后，看板中的“上架商品数”实时减少。

拆分方式：

- `账服`：商品下架状态写库、统计接口口径、缓存刷新或任务同步
- `客户端`：看板页面筛选后展示正确、图表数值刷新正确

## 5. When to split index entries further

只有在下面情况出现时，才考虑把同一业务模块拆成更细的索引项：

1. 前端和账服已经有明显不同的功能命名和职责边界。
2. 两侧的关联模块和风险点长期不重合。
3. 同一业务域下存在多个大型子系统，导致用一个模块词无法准确命中。

在大多数后台管理系统里，优先保持“业务模块一个索引 + 平台字段拆用例”的设计即可。这样比“客户端一套索引、账服一套索引”更容易维护。

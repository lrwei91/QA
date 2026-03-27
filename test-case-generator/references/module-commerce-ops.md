# Commerce Ops Domain

## 1. Covered modules

- `product-catalog`
- `marketing-banner`
- `order-management`
- `refund-approval`

## 2. Common business objects

- 商品、spu、sku、分类、价格、库存
- banner、投放位置、上线下线时间、跳转链接
- 订单、履约信息、关闭原因、备注、导出任务
- 退款申请、审批状态、拒绝原因、通知收件人

## 3. High-risk test concerns

### 3.1 客户端

- 列表、详情、弹窗、抽屉、筛选栏、导出入口、排序操作
- 状态标签、按钮启用/禁用、批量操作可见性
- 跳转、预览、成功/失败提示、数据刷新与回显一致性

### 3.2 账服

- 商品保存、库存校验、价格规则、发布状态、批量任务
- banner 时间窗和排序生效逻辑、跳转链接校验
- 订单状态流转、关闭规则、导出任务、查询性能与分页
- 退款审批权限、状态回写、通知触发、日志留痕、幂等性

## 4. Common regression expansion rules

- 商品变更 -> 补查 `marketing-banner`、`order-management`、`dashboard`
- banner 变更 -> 补查 `dashboard` 与 `operation-log`
- 订单状态变更 -> 补查 `refund-approval`、`notification-center`、`dashboard`
- 退款审批变更 -> 补查 `order-management`、`notification-center`、`dashboard`、`operation-log`

## 5. Typical case ideas

### 商品中心

- 新增商品、编辑商品、价格修改、库存边界、上下架、导入导出
- 客户端关注编辑页交互、筛选、批量选择、状态展示
- 账服关注字段校验、上下架写库、库存与价格规则、生效时机

### banner 投放

- 新增 banner、编辑 banner、排序、时间窗、跳转配置、上下线
- 客户端关注预览、排序展示、操作按钮可用性
- 账服关注时间重叠、状态切换、链接配置合法性

### 订单管理

- 订单查询、详情、关闭订单、备注、导出、筛选组合
- 客户端关注列表展示、详情回显、导出提示
- 账服关注查询条件处理、关闭限制、导出任务、状态一致性

### 退款审批

- 审批通过、审批驳回、拒绝原因、重审、撤销审批、权限差异
- 客户端关注按钮、弹窗、状态刷新、无权限表现
- 账服关注审批接口、状态写库、通知与日志、重复提交与幂等

# Pet_Shop_v2

宠物商城项目前后端分离版本。后端使用 FastAPI，前端使用 uni-app/H5 页面，当前主要面向浏览器 B/S 使用场景。

## 项目结构

```text
Pet_Shop_v2/
  backend/                 后端 FastAPI 服务
    app/
      routers/             接口路由
      services/            业务逻辑
      repositories/        数据访问
      models/              SQLAlchemy 模型
      schemas/             Pydantic 入参和出参
    database/              数据库初始化脚本

pet_shop_v2_vue/           前端 uni-app 项目
  pages/                   页面
  App.vue                  全局 B/S 样式
  pages.json               页面路由配置
```

## 当前已完成

- 短信验证码登录和账号中心。
- 用户、角色、权限基础能力。
- 管理员用户管理：分配角色、启用/禁用用户。
- 商品分类、商品列表、商品详情。
- 购物车：加入商品、修改数量、勾选、删除。
- 订单模块：创建订单、订单列表、模拟支付、取消订单、商家发货、确认收货。
- 商家商品管理：创建、编辑、提交审核、下架。
- 平台审核：审核商家提交的商品。
- 宠物档案：列表、详情、新增/编辑、设为当前宠物。
- 宠物成长记录和提醒。
- 活体宠物浏览、详情和模拟购买后生成宠物档案。
- 前端已调整为浏览器 B/S 风格，去掉小程序底部 tabBar。
- 多个表格页面已适配操作列宽度，避免按钮被挤压。
- 商家商品页已按 `product:manage` 权限控制表单显示。

## 待完善

- 支付目前是模拟支付，真实支付暂未接入。
- 还没有独立完整的后台管理系统，目前管理能力分散在账号中心、平台审核等页面。
- 文件上传暂未实现，图片仍以 URL 或静态占位图为主。
- 数据库初始化脚本需要继续核对新增订单表，保证新环境能一键建表。
- 前端项目当前没有 `package.json`，暂不能通过 npm 脚本构建验证。
- 列表分页、筛选、表单校验和错误提示还可以继续细化。

## 后端启动

```powershell
cd Pet_Shop_v2\backend
pip install -r requirements.txt
python run.py
```

默认接口地址：

```text
http://127.0.0.1:8000/api/v1
```

## 数据库

数据库初始化脚本位于：

```text
Pet_Shop_v2/backend/database/init_mysql.sql
```

数据库说明见：

```text
Pet_Shop_v2/backend/database/README.md
```

## 前端运行

使用 HBuilderX 或 uni-app H5 方式运行 `pet_shop_v2_vue` 目录。

当前前端默认接口地址：

```text
http://127.0.0.1:8000/api/v1
```

## 常用账号说明

项目启动时会初始化角色和权限。普通短信登录用户默认是普通用户；商家功能需要账号拥有 `product:manage` 权限，管理员功能需要 `user:manage` 或对应审核权限。

## Git 推送

```powershell
git status
git add .
git commit -m "更新说明文档和宠物商城功能"
git push origin main
```

# cc-web

局域网内的 Claude Code QA Web 封装服务。

## 开发

```bash
cd cc-web
npm install
npm run dev
```

后端默认监听 `http://0.0.0.0:3030`，前端默认监听 `http://localhost:5173`。

## 生产构建

```bash
cd cc-web
npm install
npm run build
npm run start --workspace @cc-web/server
```

## 初始化账号

先通过环境变量启动一次服务，自动写入管理员账号；后续可用：

```bash
npm run add-user --workspace @cc-web/server -- --username alice --password secret
```

# Creator Source Passport MVP

Creator Source Passport 是一个本地优先的 MVP。它把一条重要观点先沉淀成
canonical source page，再生成可被 AI 读取的内容包、平台分发文案、发布记录、
检索监控和修订建议。

项目方向以 [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) 为准。当前只做
Creator Source Passport MVP，不做通用 GEO SaaS、完整 CMS、社交排期工具，
也不做微信/Zhihu 自动发布机器人。

## 项目背景

平台帖适合传播，不适合作为长期源头。内容一旦被 X、LinkedIn、微信、知乎反复
转载，原作者、原始 URL、版本和引用关系就容易丢失。

这个项目的目标很直接，先把“源头”做稳，再分发到各个平台。平台内容是副本，
canonical source page 才是引用目标。

## 主要功能

- 生成 Source Passport 模型和 canonical source page。
- 生成 AI-readable markdown、`llms.txt`、`sitemap.xml`、`robots.txt` 和 schema。
- 生成 X、LinkedIn、WeChat、Zhihu 平台变体。
- 在每个变体里保留可见 source anchor。
- 保存人工发布后的平台 URL。
- 运行本地 AI retrieval monitor，检查是否引用 canonical URL、hash 和创作者。
- 输出 revision suggestions，帮助修订源页面和平台文案。

## 如何使用

### 1. 安装

```bash
python -m pip install -e .
```

### 2. 生成 demo

```bash
python -m creator_passport generate examples/source_passport.json --out generated/demo
```

### 3. 保存平台发布 URL

```bash
python -m creator_passport publish --out generated/demo --platform x --url https://x.com/example/status/123
```

### 4. 跑 retrieval monitor

```bash
python -m creator_passport monitor --out generated/demo --response-file examples/monitor_response_missing_citation.txt
```

### 5. 检查生成结果

```bash
python -m creator_passport check generated/demo
```

### 6. 启动本地站点

```bash
python -m creator_passport serve examples/source_passport.json --out generated/demo --host 127.0.0.1 --port 8765
```

打开：

```text
http://127.0.0.1:8765/
```

### 7. 一次性验证

```bash
bash scripts/verify.sh
```

Windows 上如果系统 `bash` 不可用，用 Git Bash：

```powershell
& 'C:\Program Files\Git\bin\bash.exe' scripts/verify.sh
```

## 核心模块

- `src/creator_passport/models.py`，定义 Source Passport 数据模型和校验逻辑。
- `src/creator_passport/render.py`，生成 canonical page、AI 文件、`llms.txt`、`robots.txt`、`sitemap.xml` 和 schema。
- `src/creator_passport/variants.py`，生成 X、LinkedIn、WeChat、Zhihu 变体。
- `src/creator_passport/monitor.py`，分析 AI 回复，计算归因分数并输出修订建议。
- `src/creator_passport/server.py`，提供本地静态站点服务。
- `src/creator_passport/__main__.py`，实现 CLI 命令入口。

## 目录说明

```text
docs/        项目上下文、规划和决策文档
src/         主应用代码
tests/       单元测试和 workflow 测试
scripts/     验证脚本
examples/    示例 Source Passport 和 monitor fixture
generated/   生成的 demo 输出
public/      静态原型和设计资产
```

## 输入与输出

输入示例见 [examples/source_passport.json](examples/source_passport.json)。

默认生成目录下会包含：

- `passport.json`
- `index.html`
- `s/<slug>-<hash>/index.html`
- `s/<slug>-<hash>.md`
- `llms.txt`
- `llms-full.txt`
- `ai/index.md`
- `ai/profile.md`
- `schema.json`
- `sitemap.xml`
- `robots.txt`
- `variants/x.md`
- `variants/linkedin.md`
- `variants/wechat.md`
- `variants/zhihu.md`
- `publications.json`
- `monitor/report.md`
- `revision_suggestions.md`

## 项目边界

当前只保留这个闭环：

1. 写入一个 Source Passport。
2. 生成 canonical source page 和 AI-readable assets。
3. 分发平台变体。
4. 记录发布 URL。
5. 检查 AI 是否正确引用源头。
6. 根据失败点修订。

不做：

- 通用 GEO SaaS
- 完整 CMS
- 完整社交媒体排期
- 微信/Zhihu 自动发布机器人
- 支付系统
- 团队权限系统


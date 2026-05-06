# Project Goal: SKU Source Passport Engine

Date: 2026-05-06
Status: Draft
Branch: codex-auto

## 1. Goal

把当前 `Creator Source Passport MVP` 升级成面向电商 SKU 的 `SKU Source Passport Engine`。

第一阶段不做 demo，不做大而全 SaaS，不做完整 CMS，不做社媒自动发布。目标是先把项目已有能力整理清楚，然后补上最少的自动化模块，让系统可以围绕 3-5 个主推 SKU 自动生成、检查、维护 AI 可引用的产品源。

一句话目标：

> 输入一组主推 SKU 的官网页、说明书、FAQ、竞品信息和人工补充资料，系统生成可被 AI 理解、引用、比较、更新的产品事实源和购买决策源，并持续监测 AI 回答是否正确引用它们。

这不是“帮客户写更多内容”。这是给客户的主推产品建立 AI 时代的产品事实基础设施。
 也就是：客户给你 3-5 个主推 SKU，你的系统自动抓官网、说明书、FAQ、竞品页、平台页，生成 AI 能读懂、能引用、能推荐的产品知识站，并定期检测 AI 有没有说对。
  1. 诊断
     客户给 3-5 个主推 SKU、官网链接、Amazon/独立站链接、产品说明书、FAQ、竞品名单。
  2. 提取事实
     整理每个 SKU 的功率、接口、协议、适配设备、尺寸、卖点、限制、适合人群、不适合人群。
  3. 重写购买决策资料
     不是写软文。是写 AI 和用户都能用的决策页面：
      - 怎么选
      - 产品对比
      - 场景推荐
      - FAQ
      - 竞品差异
      - 注意事项
  4. 生成 AI 可抓取资产
     输出：
      - canonical product source page
      - markdown 页面
      - llms.txt
      - sitemap.xml
      - robots.txt
      - schema JSON-LD
      - source hash
      - FAQ schema
      - 对比表结构化数据
  5. 上线独立站或子目录
     两种交付：
      - 客户已有官网：放在 brand.com/ai-source/charger-guide
      - 客户不想动官网：你托管一个独立站，比如 brand-ai-source.com
  6. AI 检索测试
     用 20-50 个真实购买问题测试：
      - AI 是否提到品牌
      - 是否说对型号
      - 是否引用页面
      - 是否理解适用场景
      - 是否把竞品推荐走了
  7. 修订报告
     如果 AI 没抓到，就改页面结构、标题、FAQ、对比表、schema、内部链接。
## 2. Scope Boundary

当前阶段必须保留的边界：

- 不加入演示公司或演示 SKU 数据。
- 不做通用 GEO SaaS。
- 不做完整 CMS。
- 不做 WeChat、Zhihu、Amazon、Shopify 自动发布机器人。
- 不承诺 AI 一定引用，只监测、诊断、修正。
- 不把 Postiz、Mixpost、GEOFlow 这种大系统直接并进来。

当前阶段要做的是产品和工程桥接设计：

1. 统计当前已有模块。
2. 明确哪些模块可直接保留。
3. 明确哪些模块需要改造成 SKU 场景。
4. 拆解外部项目里值得借鉴的模块。
5. 设计最小桥接路径。

## 3. Current Project Inventory

### 3.1 Current Core Modules

| File | Current Capability | Keep / Change |
|---|---|---|
| `src/creator_passport/models.py` | 定义 Creator、Claim、Reference、SourcePassport，生成 slug、canonical path、markdown path、content hash、source anchor，并做基础校验 | 保留结构，新增 SKU / Brand / ProductClaim / Competitor fields |
| `src/creator_passport/render.py` | 生成 `passport.json`、HTML source page、markdown source page、`llms.txt`、`llms-full.txt`、`ai/index.md`、`schema.json`、`sitemap.xml`、`robots.txt` | 保留生成器，改造 schema 和页面结构为产品事实源 |
| `src/creator_passport/variants.py` | 生成 X、LinkedIn、WeChat、Zhihu 四种平台内容，并强制加入 source anchor | 保留 anchor 策略，平台文案从观点传播改为购买决策 / FAQ / comparison |
| `src/creator_passport/monitor.py` | 分析 AI response 是否提到 creator、canonical URL、content hash、platform URL、claim coverage，并输出 revision suggestions | 保留 scoring 逻辑，改为检测品牌、SKU、产品事实、购买建议、竞品比较是否正确 |
| `src/creator_passport/__main__.py` | CLI：generate、publish、monitor、check、serve | 保留 CLI 骨架，后续新增 intake、extract、maintain 子命令 |
| `src/creator_passport/server.py` | 本地静态站点服务 | 保留，用于本地预览和人工检查 |

### 3.2 Current Output Artifacts

当前系统已经能生成：

- `passport.json`
- `index.html`
- `s/{slug}-{hash}/index.html`
- `s/{slug}-{hash}.md`
- `ai/index.md`
- `ai/profile.md`
- `ai/sources/{slug}.md`
- `ai/topics/{topic}.md`
- `llms.txt`
- `llms-full.txt`
- `schema.json`
- `sitemap.xml`
- `robots.txt`
- `variants/x.md`
- `variants/linkedin.md`
- `variants/wechat.md`
- `variants/zhihu.md`
- `publications.json`
- `monitor/latest-run.json`
- `monitor/report.md`
- `revision_suggestions.md`

结论：底层闭环已经成立。缺的不是“生成文件”，而是电商 SKU 语义层。

## 4. Product Reframe

当前模型叫 `SourcePassport`，适合创作者观点。

电商 SKU 场景需要把核心对象换成：

```text
Brand
  name
  domain
  market
  support_urls

SkuSourcePassport
  sku_id
  brand
  product_name
  model_number
  canonical_url
  source_hash
  updated_at
  category
  positioning
  specs
  claims
  evidence
  compatibility
  limitations
  use_cases
  competitor_context
  buying_questions
  revision_history
```

核心变化：

- Creator -> Brand
- Idea -> SKU
- Thesis -> Product positioning
- Claim -> Product claim
- Evidence -> Spec / manual / support page / certification / official FAQ
- Platform variant -> Buying-decision variant
- Retrieval monitor -> AI shopping-answer monitor

## 5. Repetitive Work AI Should Replace

这些工作应该由 AI 自动做，人只做确认：

| Repetitive Work | AI Automation |
|---|---|
| 从官网页、说明书、FAQ 里摘产品参数 | SKU fact extraction |
| 把散乱参数整理成统一字段 | Product fact normalization |
| 把卖点改写成购买问题答案 | Buying-question generation |
| 生成“适合谁 / 不适合谁” | Use-case and limitation generation |
| 生成 SKU 对比页 | Comparison page generation |
| 生成 FAQ | AI-search FAQ generation |
| 生成 `llms.txt`、schema、markdown mirrors | AI index compilation |
| 周期性跑 AI 搜索问题 | Retrieval monitor scheduling |
| 找出 AI 回答错误或没引用的地方 | Citation and fact-gap analysis |
| 给出页面修改建议 | Revision suggestion generation |

人工必须保留的地方：

- 最终产品事实确认。
- 竞品比较边界确认。
- 价格、促销、库存是否纳入。
- 法务 / 合规措辞确认。
- 发布前审批。

## 6. External Project Breakdown

### 6.1 MarkItDown

Local path: `external/markitdown`

可借鉴模块：

- PDF / DOCX / PPTX / HTML / CSV / JSON / XML 转 Markdown。
- 保留 headings、tables、links 等结构。
- 适合说明书、产品白皮书、销售资料、FAQ 文档导入。

桥接方式：

```text
manual / PDF / DOCX / HTML
  -> MarkItDown adapter
  -> raw markdown
  -> SKU fact extractor
```

建议：第一批引入。它和当前 Python 项目栈匹配，边界清楚。

### 6.2 Crawl4AI

Local path: `external/crawl4ai`

可借鉴模块：

- URL 抓取。
- HTML 转 LLM-ready Markdown。
- 链接引用保留。
- 深度抓取和页面过滤。

桥接方式：

```text
product URL / support URL / FAQ URL
  -> Crawl4AI adapter
  -> cleaned markdown
  -> source snapshot
  -> SKU fact extractor
```

建议：第二批引入。网页抓取会带来浏览器依赖，先做 optional adapter。

### 6.3 Firecrawl

Local path: `external/firecrawl`

可借鉴模块：

- Search / scrape / crawl / map。
- 对 JS-heavy 页面和批量 URL 更友好。
- 可作为外部服务兜底。

桥接方式：

```text
if Firecrawl API key exists:
  use Firecrawl for difficult pages
else:
  use MarkItDown / Crawl4AI / manual paste
```

建议：不要自托管进 MVP。只作为外部 API adapter。

### 6.4 GEOFlow

Local path: `external/GEOFlow`

可借鉴模块：

- 知识库、素材、任务、AI 生成、审核、发布流水线。
- OpenAI-style provider 适配。
- Markdown rendering、SEO metadata、structured data。
- “知识库质量优先，再自动化”的产品原则。

不应照搬：

- Laravel 后台。
- PostgreSQL + Redis + queue 全套内容工厂。
- 大规模内容任务系统。

桥接方式：

```text
borrow workflow ideas:
  materials -> knowledge base -> generation -> review -> publish

implement only:
  SKU source intake -> fact extraction -> human review -> source pack generation
```

建议：只借鉴工作流，不引入代码。

### 6.5 Prompt Clarity

Local path: `external/promptclarity`

可借鉴模块：

- 多平台 AI prompt tracking。
- brand mention、competitor visibility、share of voice。
- sources dashboard。
- content roadmap。
- 定时执行。

桥接方式：

```text
SKU buying prompts
  -> model responses
  -> detect brand / SKU / canonical URL / competitor mentions
  -> score answer quality
  -> produce source revision suggestions
```

建议：借鉴监测维度和 dashboard 思路。不要迁移 Next.js / SQLite 栈。

### 6.6 llms-txt

Local path: `external/llms-txt`

可借鉴模块：

- `llms.txt` 格式参考。
- parser / convention 参考。

桥接方式：

```text
Brand source home
  -> /llms.txt
  -> /llms-full.txt
  -> /ai/products/{sku}.md
  -> /ai/comparisons/{category}.md
```

建议：继续作为规范参考，避免发明私有格式。

### 6.7 Mixpost / Postiz

Local paths:

- `external/mixpost`
- `external/postiz-app`

可借鉴模块：

- 平台账号、post version、发布状态、发布 URL、analytics。
- Postiz 的平台覆盖强，但 AGPL 约束更重。
- Mixpost 是 MIT，但 Laravel 栈不匹配。

桥接方式：

```text
MVP:
  generated variant -> manual copy -> save publication URL

Later:
  publisher adapter -> Mixpost/Postiz external service
```

建议：只借鉴数据概念，不进入当前阶段。

### 6.8 Payload / TinaCMS

Local paths:

- `external/payload`
- `external/tinacms`

可借鉴模块：

- draft / version / publish。
- markdown editing。
- content ownership。

建议：当前阶段不引入。否则项目会变成 CMS。

## 7. Missing Modules To Add

### 7.1 Source Intake

职责：

- 接收 URL、PDF、DOCX、HTML、manual paste。
- 生成统一 `RawSourceDocument`。

输入：

```text
origin_type
origin_url
file_path
raw_markdown
captured_at
warnings
```

借鉴：

- MarkItDown
- Crawl4AI
- Firecrawl

### 7.2 SKU Fact Extractor

职责：

- 从 raw markdown 提取 SKU 事实。
- 输出结构化 `SkuFacts`。
- 标记 confidence 和 evidence source。

字段：

```text
brand
product_name
model_number
category
ports
power_output
protocols
compatibility
dimensions
certifications
included_items
limitations
official_urls
```

这是最关键的新模块。

### 7.3 Buying Question Generator

职责：

- 根据 SKU 事实生成真实购买问题。

例子：

```text
Which Anker charger should I buy for iPhone 16?
Is 45W enough for a MacBook Air and iPhone?
What is the difference between Anker Nano 45W and Anker Prime 100W?
```

输出：

- FAQ。
- comparison prompts。
- monitor prompts。
- source page sections。

### 7.4 SKU Source Page Generator

职责：

- 把当前 source page 改造成产品事实源。

页面结构：

```text
Product identity
Official facts
Best for
Not for
Compatibility
Claim-evidence map
Comparison context
FAQ
Limitations
Canonical citation block
Markdown mirror
```

### 7.5 AI Index Compiler For Products

职责：

- 当前 `render.py` 已经有基础。
- 需要把 creator/topic/source 改成 brand/category/SKU。

新增输出：

```text
/ai/products/{sku}.md
/ai/categories/{category}.md
/ai/comparisons/{category}.md
/ai/faq.md
/ai/buying-guide.md
```

### 7.6 Retrieval Maintenance Loop

职责：

- 周期性跑购买问题。
- 判断 AI 是否正确推荐、引用、比较、说明限制。
- 自动生成维护建议。

评分维度：

```text
brand_mentioned
sku_mentioned
canonical_url_cited
wrong_specs_present
competitor_context_present
claim_coverage
limitation_preserved
buying_intent_matched
```

## 8. Bridge Architecture

Recommended bridge:

```text
Current SourcePassport
  -> keep hash, canonical URL, source anchor, render outputs

New SKU layer
  -> Brand
  -> SKU facts
  -> Buying questions
  -> Product source page sections

External adapters
  -> MarkItDown for files
  -> Crawl4AI for URLs
  -> Firecrawl optional API fallback

Monitor upgrade
  -> existing attribution monitor
  -> SKU answer quality monitor
  -> revision suggestions
```

Do not rewrite the project.

The current code already has the right skeleton:

```text
model -> render -> variants -> publish record -> monitor -> revision suggestions
```

The bridge should preserve that skeleton and swap the domain object from creator idea to product SKU.

## 9. Recommended Build Phases

### Phase 1: Inventory And Domain Model

Goal:

- Keep existing workflow.
- Add SKU domain model design.
- No external dependency yet.

Acceptance:

- Existing Creator Source Passport still works.
- New SKU model can be represented as JSON.
- No demo SKU included.

### Phase 2: SKU Fact Extraction

Goal:

- Add `RawSourceDocument`.
- Add `SkuFacts`.
- Add extractor interface.
- First implementation can be rule-assisted plus AI-assisted later.

Acceptance:

- Given product source markdown, system outputs normalized SKU facts with evidence pointers.

### Phase 3: Product AI Pack Generation

Goal:

- Generate product source page.
- Generate product markdown mirrors.
- Generate product-specific `llms.txt` and schema.

Acceptance:

- One SKU produces complete AI-readable artifacts.
- Every artifact points to canonical product source URL.

### Phase 4: Buying Decision Variants

Goal:

- Generate FAQ, comparison, suitable / not suitable, platform variants.

Acceptance:

- Variants are grounded in extracted facts.
- No unsupported claim appears without evidence.

### Phase 5: Retrieval Maintenance

Goal:

- Upgrade monitor from creator attribution to SKU answer quality.

Acceptance:

- System can detect missing citation, wrong specs, weak comparison, missing limitations.
- System outputs actionable revision suggestions.

### Phase 6: External Adapters

Goal:

- Add MarkItDown first.
- Add Crawl4AI second.
- Add Firecrawl optional fallback.

Acceptance:

- Files and URLs can become `RawSourceDocument`.
- Failures are visible and do not block manual input.

## 10. Recommendation

Recommended approach:

> Build a SKU layer on top of the existing Source Passport engine, then introduce intake and monitoring adapters one by one.

Do not start with GEOFlow-style content factory. That path looks powerful but pulls the product into CMS, queue, task, role, publishing, and dashboard complexity.

The smallest valuable version is:

```text
3-5 main SKUs
  -> product facts
  -> canonical SKU source pages
  -> AI-readable product pack
  -> buying-question variants
  -> weekly AI retrieval report
  -> revision suggestions
```

That is the service customers can understand and pay for.

## 11. Success Criteria

This goal is met when:

- The project has a documented SKU Source Passport model.
- The existing Creator Source Passport workflow is not broken.
- The module inventory is clear.
- External projects are mapped to adapter roles.
- No heavy CMS or publisher is introduced prematurely.
- The next engineering plan can be written without re-deciding product direction.

## 12. Next Assignment

Before implementation, pick one exact target customer shape:

```text
Electronics ecommerce brand with 3-5 high-margin SKUs,
selling through its own website plus marketplace channels,
and needing AI answers to explain, compare, and cite products correctly.
```

Then write one sample input contract, not a demo:

```text
brand.json
sku_sources.json
competitors.json
buying_questions.json
```

This keeps the project grounded without hardcoding Anker or any demo company into the codebase.

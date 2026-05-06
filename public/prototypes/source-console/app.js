const SOURCE = {
  canonicalUrl: "https://demo.creator-source.local/s/durable-source-page-a2957905adc9",
  hash: "a2957905adc9",
  creator: "Lin Source Lab",
  claim: "A canonical source page is more durable than a platform post."
};

const copy = {
  zh: {
    navSource: "登记源头",
    navCanonical: "源头页",
    navPublish: "分发与回填",
    navMonitor: "引用检查",
    navRevise: "一键修订",
    railMode: "MVP mode",
    railStatus: "本地原型，不自动发布",
    eyebrow: "Canonical source infrastructure",
    title: "把一条重要观点变成 AI 可引用源头",
    reset: "重置演示",
    next: "下一步",
    statusCanonical: "Canonical URL",
    statusHash: "Source hash",
    statusAi: "AI-ready assets",
    assetPending: "待生成",
    assetReady: "已生成",
    sourceEyebrow: "Step 01",
    sourceTitle: "只问创作者一件事",
    generate: "生成源头页",
    fieldTitle: "标题",
    fieldThesis: "核心论点",
    fieldBody: "正文",
    outcomeEyebrow: "What the creator gets",
    outcomeTitle: "不是写作工具，是源头登记台。",
    outcomeOne: "稳定源头页，带版本和 source hash",
    outcomeTwo: "X、LinkedIn、微信、知乎分发文案",
    outcomeThree: "发布 URL 回填和 source anchor 检查",
    outcomeFour: "AI 引用失败后的具体修订任务",
    citationLabel: "Recommended citation",
    claimOneLabel: "Claim",
    evidenceLabel: "Evidence",
    variantEyebrow: "Anchor kit",
    variantTitle: "每个平台都是副本，源头只有一个",
    copy: "复制文案",
    publishApi: "一键发布接口位",
    trackerEyebrow: "Publication map",
    trackerTitle: "发布后回填 URL",
    monitorEyebrow: "Citation check",
    monitorTitle: "粘贴 AI 回答，检查它是否回到源头",
    runCheck: "运行检查",
    scoreLabel: "源头回溯分",
    revisionEyebrow: "Revision tasks",
    revisionTitle: "给创作者 3 条能直接执行的修改",
    liveDiff: "Live source draft",
    saved: "已保存",
    missing: "未回填",
    manualFallback: "接口预留，当前手动发布",
    toastGenerated: "源头页已生成，AI assets 已就绪",
    toastCopied: "文案已复制到剪贴板",
    toastApi: "这是发布接口位，当前原型只模拟状态",
    toastSaved: "发布 URL 已回填",
    toastApplied: "已应用到源头草稿",
    checkCanonical: "Canonical URL",
    checkHash: "Source hash",
    checkCreator: "Creator name",
    checkClaim: "Core claim",
    present: "存在",
    absent: "缺失"
  },
  en: {
    navSource: "Register",
    navCanonical: "Source page",
    navPublish: "Publish map",
    navMonitor: "Citation check",
    navRevise: "Apply fixes",
    railMode: "MVP mode",
    railStatus: "Local prototype, no auto-posting",
    eyebrow: "Canonical source infrastructure",
    title: "Turn one serious idea into an AI-citable source",
    reset: "Reset demo",
    next: "Next",
    statusCanonical: "Canonical URL",
    statusHash: "Source hash",
    statusAi: "AI-ready assets",
    assetPending: "Pending",
    assetReady: "Ready",
    sourceEyebrow: "Step 01",
    sourceTitle: "Ask the creator one thing",
    generate: "Generate source",
    fieldTitle: "Title",
    fieldThesis: "Thesis",
    fieldBody: "Body",
    outcomeEyebrow: "What the creator gets",
    outcomeTitle: "Not a writing tool. A source registry.",
    outcomeOne: "Stable source page with version and hash",
    outcomeTwo: "X, LinkedIn, WeChat, Zhihu anchored variants",
    outcomeThree: "Publication URL backfill and anchor checks",
    outcomeFour: "Specific revision tasks when AI citation fails",
    citationLabel: "Recommended citation",
    claimOneLabel: "Claim",
    evidenceLabel: "Evidence",
    variantEyebrow: "Anchor kit",
    variantTitle: "Every platform is a copy. The source is one.",
    copy: "Copy variant",
    publishApi: "Publish API slot",
    trackerEyebrow: "Publication map",
    trackerTitle: "Backfill platform URLs after publishing",
    monitorEyebrow: "Citation check",
    monitorTitle: "Paste an AI answer and check source recovery",
    runCheck: "Run check",
    scoreLabel: "Source recovery score",
    revisionEyebrow: "Revision tasks",
    revisionTitle: "Give creators 3 changes they can apply",
    liveDiff: "Live source draft",
    saved: "Saved",
    missing: "Missing",
    manualFallback: "API slot reserved, manual publishing now",
    toastGenerated: "Source page generated. AI assets are ready.",
    toastCopied: "Variant copied to clipboard",
    toastApi: "API slot only. This prototype simulates status.",
    toastSaved: "Publication URL saved",
    toastApplied: "Applied to source draft",
    checkCanonical: "Canonical URL",
    checkHash: "Source hash",
    checkCreator: "Creator name",
    checkClaim: "Core claim",
    present: "Present",
    absent: "Missing"
  }
};

const variants = {
  x: `A serious idea needs a source page before it needs more posts.

Feeds create reach. Sources create memory.

If your best idea only lives inside platform posts, AI can summarize it without citing you.

Source Passport: ${SOURCE.hash}
Source: ${SOURCE.canonicalUrl}`,
  linkedin: `Professional creators need source authority, not just more distribution.

The practical workflow:
1. Publish one canonical source page.
2. Generate platform variants from that source.
3. Keep the same source anchor across every copy.
4. Monitor whether AI cites the source, creator, hash, and claims.

Source Passport: ${SOURCE.hash}
Source: ${SOURCE.canonicalUrl}`,
  wechat: `严肃观点应该先拥有一个源头页，再进入微信、知乎、X、LinkedIn 等平台分发。

平台适合传播，但不适合长期归因。源头页保留作者、版本、hash、主张、证据和推荐引用方式。

Source Passport: ${SOURCE.hash}
Source: ${SOURCE.canonicalUrl}`,
  zhihu: `为什么严肃观点需要先有源头页？

因为平台内容适合分发，不适合作为长期出处。一个可被 AI 和人引用的观点，需要稳定 URL、作者、版本、source hash、claims、evidence 和 citation block。

Source Passport: ${SOURCE.hash}
Source: ${SOURCE.canonicalUrl}`
};

const platforms = ["x", "linkedin", "wechat", "zhihu"];
const platformLabels = {
  x: "X",
  linkedin: "LinkedIn",
  wechat: "WeChat",
  zhihu: "Zhihu"
};

const suggestions = [
  {
    titleZh: "把 citation block 前置到首屏",
    titleEn: "Move the citation block above the fold",
    textZh: "AI 回答没有引用 canonical URL。把推荐引用方式放在标题下方，降低 crawler 忽略概率。",
    textEn: "The AI answer missed the canonical URL. Put the recommended citation directly under the title.",
    patch: "\n\nRecommended citation: Lin Source Lab, Source Passport v1, canonical URL https://demo.creator-source.local/s/durable-source-page-a2957905adc9."
  },
  {
    titleZh: "在平台变体开头重复 source anchor",
    titleEn: "Repeat the source anchor at the top of variants",
    textZh: "当前 source anchor 在结尾。长文平台可能折叠尾部链接，建议开头和结尾都出现一次。",
    textEn: "The source anchor appears at the end. Long platforms may collapse it, so show it at top and bottom.",
    patch: "\n\nSource Passport: a2957905adc9\nCanonical source: https://demo.creator-source.local/s/durable-source-page-a2957905adc9."
  },
  {
    titleZh: "补一句更硬的核心定义",
    titleEn: "Add a sharper definition",
    textZh: "AI 覆盖了主题，但没有保留核心 claim。补一条定义句：平台帖子是分发副本，canonical source page 才是引用目标。",
    textEn: "The answer covered the topic but softened the claim. Add a definition sentence that names the source target.",
    patch: "\n\nDefinition: platform posts are distribution copies; the canonical source page is the citation target."
  }
];

let state = {
  lang: "zh",
  view: "source",
  platform: "x",
  generated: false,
  urls: {
    x: "",
    linkedin: "",
    wechat: "",
    zhihu: ""
  },
  applied: new Set()
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function t(key) {
  return copy[state.lang][key] || key;
}

function applyLanguage() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  $(".app-shell").dataset.lang = state.lang;
  $$("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  $$(".lang").forEach((btn) => btn.classList.toggle("active", btn.dataset.lang === state.lang));
  if (state.generated) $("#assetState").textContent = t("assetReady");
  renderTracker();
  renderChecks();
  renderSuggestions();
}

function setView(view) {
  state.view = view;
  $(".app-shell").dataset.view = view;
  $$(".panel").forEach((panel) => panel.classList.toggle("active", panel.id === view));
  $$(".step").forEach((step) => step.classList.toggle("active", step.dataset.target === view));
}

function nextView() {
  const order = ["source", "canonical", "publish", "monitor", "revise"];
  const index = order.indexOf(state.view);
  setView(order[Math.min(index + 1, order.length - 1)]);
}

function generateSource() {
  state.generated = true;
  $("#canonicalUrl").textContent = SOURCE.canonicalUrl;
  $("#sourceHash").textContent = SOURCE.hash;
  $("#assetState").textContent = t("assetReady");
  setView("canonical");
  toast(t("toastGenerated"));
}

function renderVariant() {
  $("#variantText").value = variants[state.platform];
  $$(".platform").forEach((button) => {
    button.classList.toggle("active", button.dataset.platform === state.platform);
  });
}

function renderTracker() {
  const list = $("#trackerList");
  list.innerHTML = "";
  platforms.forEach((key) => {
    const row = document.createElement("div");
    row.className = "track-row";
    row.innerHTML = `
      <strong>${platformLabels[key]}</strong>
      <input data-url="${key}" value="${state.urls[key]}" placeholder="https://">
      <div class="row-actions">
        <button class="ghost" data-save="${key}">${state.lang === "zh" ? "保存 URL" : "Save URL"}</button>
        <span class="state ${state.urls[key] ? "ok" : "warn"}">${state.urls[key] ? t("saved") : t("missing")} · ${t("manualFallback")}</span>
      </div>
    `;
    list.appendChild(row);
  });
}

function runCitationCheck() {
  const text = $("#aiResponse").value.toLowerCase();
  const checks = [
    ["checkCanonical", text.includes(SOURCE.canonicalUrl.toLowerCase())],
    ["checkHash", text.includes(SOURCE.hash.toLowerCase())],
    ["checkCreator", text.includes(SOURCE.creator.toLowerCase())],
    ["checkClaim", text.includes("canonical") && text.includes("platform")]
  ];
  const score = checks.reduce((sum, item) => sum + (item[1] ? 25 : 0), 0);
  $("#scoreRing").textContent = score;
  $("#scoreRing").style.background = `radial-gradient(circle at center, #fff 56%, transparent 57%), conic-gradient(${score > 74 ? "var(--good)" : score > 49 ? "var(--warn)" : "var(--bad)"} ${score}%, #e8ece8 0)`;
  renderChecks(checks);
  setView("revise");
}

function renderChecks(existing) {
  const text = $("#aiResponse") ? $("#aiResponse").value.toLowerCase() : "";
  const checks = existing || [
    ["checkCanonical", text.includes(SOURCE.canonicalUrl.toLowerCase())],
    ["checkHash", text.includes(SOURCE.hash.toLowerCase())],
    ["checkCreator", text.includes(SOURCE.creator.toLowerCase())],
    ["checkClaim", text.includes("canonical") && text.includes("platform")]
  ];
  const box = $("#checks");
  if (!box) return;
  box.innerHTML = "";
  checks.forEach(([label, ok]) => {
    const row = document.createElement("div");
    row.className = "check";
    row.innerHTML = `<span>${t(label)}</span><span class="badge ${ok ? "good" : "bad"}">${ok ? t("present") : t("absent")}</span>`;
    box.appendChild(row);
  });
}

function renderSuggestions() {
  const box = $("#suggestions");
  if (!box) return;
  box.innerHTML = "";
  suggestions.forEach((item, index) => {
    const applied = state.applied.has(index);
    const card = document.createElement("div");
    card.className = `suggestion${applied ? " applied" : ""}`;
    card.innerHTML = `
      <h3>${state.lang === "zh" ? item.titleZh : item.titleEn}</h3>
      <p>${state.lang === "zh" ? item.textZh : item.textEn}</p>
      <button class="${applied ? "ghost" : "primary"}" data-apply="${index}">${applied ? (state.lang === "zh" ? "已应用" : "Applied") : (state.lang === "zh" ? "一键应用" : "Apply")}</button>
    `;
    box.appendChild(card);
  });
}

function applySuggestion(index) {
  if (state.applied.has(index)) return;
  state.applied.add(index);
  $("#revisionDraft").value += suggestions[index].patch;
  renderSuggestions();
  toast(t("toastApplied"));
}

function toast(message) {
  const existing = $(".toast");
  if (existing) existing.remove();
  const node = document.createElement("div");
  node.className = "toast";
  node.textContent = message;
  document.body.appendChild(node);
  window.setTimeout(() => node.remove(), 2400);
}

function resetDemo() {
  state.generated = false;
  state.urls = { x: "", linkedin: "", wechat: "", zhihu: "" };
  state.applied = new Set();
  $("#canonicalUrl").textContent = "pending";
  $("#sourceHash").textContent = "pending";
  $("#assetState").textContent = t("assetPending");
  $("#revisionDraft").value = $("#inputBody").value;
  renderTracker();
  renderSuggestions();
  setView("source");
}

document.addEventListener("click", async (event) => {
  const step = event.target.closest(".step");
  if (step) setView(step.dataset.target);

  const lang = event.target.closest(".lang");
  if (lang) {
    state.lang = lang.dataset.lang;
    applyLanguage();
  }

  const platform = event.target.closest(".platform");
  if (platform) {
    state.platform = platform.dataset.platform;
    renderVariant();
  }

  const save = event.target.closest("[data-save]");
  if (save) {
    const key = save.dataset.save;
    state.urls[key] = document.querySelector(`[data-url="${key}"]`).value.trim();
    renderTracker();
    toast(t("toastSaved"));
  }

  const apply = event.target.closest("[data-apply]");
  if (apply) applySuggestion(Number(apply.dataset.apply));

  if (event.target.id === "generateBtn") generateSource();
  if (event.target.id === "nextBtn") nextView();
  if (event.target.id === "resetBtn") resetDemo();
  if (event.target.id === "runCheck") runCitationCheck();
  if (event.target.id === "apiPublish") toast(t("toastApi"));
  if (event.target.id === "copyVariant") {
    try {
      await navigator.clipboard.writeText($("#variantText").value);
      toast(t("toastCopied"));
    } catch {
      $("#variantText").select();
      toast(t("toastCopied"));
    }
  }
});

$("#revisionDraft").value = $("#inputBody").value;
renderVariant();
renderTracker();
renderChecks();
renderSuggestions();
applyLanguage();

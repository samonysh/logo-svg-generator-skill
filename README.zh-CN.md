<p align="center">
  <img src="./assets/logo-color-128.svg" alt="logo-svg-generator" width="128" height="128">
</p>

<h1 align="center">logo-svg-generator</h1>

<p align="center">
  <em>由 Skill 自身生成、Simple-Icons 兼容的 SVG Logo。</em>
</p>

> For English documentation, see **[README.md](./README.md)**

一个 TRAE **Skill** 创作项目：把一句自然语言的产品简介，转成一整套 **可直接投产的 SVG Logo**——多尺寸、黑白 + 品牌色双份——严格遵循 [Simple Icons](https://simpleicons.org/) 的设计规范，并通过 **视觉大模型**（vision LLM）执行 **生成 → 视觉审校 → 优化** 的迭代闭环。

- **产物：** 与 Simple Icons 完全兼容的 `24×24` 主 SVG，以及 `16 / 24 / 32 / 64 / 128 / 256 / 512` px 的黑白与彩色变体、PNG 预览、favicon 套件。
- **强制约束：** 单一 `<path>`，主图无 `fill` / `stroke`，路径必须触碰 viewBox 的至少 2 条边，居中，墨量占比 25–65 %，16 px 下仍可辨识。
- **为什么比"一次生成"更好：** 合规的 SVG 并不等于好看的 SVG——尤其是在 16 px 下极易翻车。视觉大模型审校环节会输出 **坐标级修改建议**，把内部 30 次基准评测的合格率从 ~6/10 提升到 8.5+/10。

---

## 目录结构

```
logo-svg-generator-skill/
├─ skill/
│  └─ SKILL.md                    ← Skill 本体（部署到 .trae/skills/）
├─ assets/                        ← 项目自身的品牌资源（本仓库的 Logo）
│  ├─ logo.svg                        24×24 Simple-Icons 主图（Skill 自产）
│  ├─ logo-mono-128.svg               128 px 黑白预览
│  └─ logo-color-128.svg              128 px 靛蓝 #4F46E5 预览
├─ references/
│  ├─ design-rules.md             ← 精简版 Simple Icons 设计规则
│  ├─ motif-patterns.md           ← 常见单路径造型配方
│  └─ sample-icons.md             ← 15 个精选真实 SVG 参考
├─ templates/
│  ├─ visual-review-prompt.md     ← 视觉审校 prompt
│  └─ concept-brief-template.md   ← 概念简报模板
├─ scripts/
│  ├─ config.json                 ← 尺寸列表、迭代上限、CDN 模板
│  ├─ fetch_samples.py            ← 从 simple-icons CDN 抓参考图标
│  ├─ validate_svg.py             ← 规则合规检查
│  ├─ render_previews.py          ← 光栅化 + 拼出审校用 PNG
│  ├─ export_variants.py          ← 多尺寸 + 多颜色 + PNG 变体
│  ├─ simplify_for_small.py       ← 16 / 24 px 路径简化
│  └─ deploy_skill.py             ← 部署到 .trae/skills/
├─ examples/                      ← 可直接运行的示例
│  ├─ 01-novasync/                    文件同步工具
│  ├─ 02-lumendb/                     实时分析数据库
│  └─ 03-pulsemail/                   邮件客户端
├─ samples/                       ← 已下载的参考 SVG（git 忽略）
├─ output/                        ← 每次运行的产物（git 忽略）
├─ LICENSE
├─ README.md                      ← 英文
└─ README.zh-CN.md                ← 本文档
```

---

## 快速开始

### 1. 安装（可选依赖）

```powershell
python -m pip install cairosvg pillow
```

需要 Python 3.10+。`cairosvg` / `pillow` 仅在本地想生成 PNG 预览时需要；Skill 本体不依赖它们。

### 2. 部署 Skill 到本地 TRAE

```powershell
python scripts\deploy_skill.py
```

脚本会把 `skill/SKILL.md`、`references/`、`templates/`、`scripts/` 复制到 `.trae/skills/logo-svg-generator/`。

### 3. 让 TRAE 帮你设计 Logo

> "帮我给 **NovaSync** 设计一个 Logo，它是面向开发者的跨设备文件同步工具，风格干净现代，靛蓝色。"

Skill 会自动：

1. 从简介推断出 `slug` 与品牌色 HEX。
2. 加载 [`references/design-rules.md`](references/design-rules.md) 与 [`references/motif-patterns.md`](references/motif-patterns.md)。
3. 生成一个 24×24 的 **单路径** 主 SVG，严格遵循全部 Simple Icons 规则。
4. 光栅化生成一张审校拼图，附上 [`templates/visual-review-prompt.md`](templates/visual-review-prompt.md) 交给视觉大模型。
5. 循环 **生成 → 审校 → 优化**，最多 3 轮，直到 `score ≥ 8.5`、`readable_at_16px = true` 且不再有 `high` 严重度问题。
6. 输出 `output/<slug>/{master-24.svg, mono/, color/, png/, favicon/, brand.json, _review.png}`。

---

## 示例

[`examples/`](./examples/) 目录下有可以直接复制粘贴到 TRAE 里的示例简报，每个示例带一份 `brief.md` 和一份说明用的 `README.md`。

| 示例 | 简介 | 视觉动机 |
|---|---|---|
| [`01-novasync`](./examples/01-novasync/) | 跨设备文件同步工具 | 字母 `N` + 轨道箭头 |
| [`02-lumendb`](./examples/02-lumendb/) | 实时分析数据库 | 棱镜 + 数据脉冲 |
| [`03-pulsemail`](./examples/03-pulsemail/) | 专注型邮件客户端 | 信封 + 心跳波形 |

一句话运行：

```powershell
# 部署好 Skill 后，在 TRAE 里说：
请用 logo-svg-generator 这个 Skill 处理 examples/01-novasync/brief.md
```

---

## 维护者工作流

```powershell
# 1. 可选：从 simple-icons CDN 抓取约 25 张参考图标
python scripts\fetch_samples.py

# 2. 编辑 skill\SKILL.md 与 references\*.md 迭代 Skill

# 3. 用规则检查器校验手写 SVG
python scripts\validate_svg.py path\to\master-24.svg

# 4. 预览生成的 SVG 在多个尺寸下的表现
python scripts\render_previews.py path\to\master-24.svg

# 5. 输出多尺寸 + 品牌色变体
python scripts\export_variants.py path\to\master-24.svg --slug novasync --title NovaSync --hex "#4F46E5"

# 6. 部署 Skill
python scripts\deploy_skill.py
```

---

## 一屏看完设计规则

- `<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">` —— 属性顺序固定。
- **有且仅有** 一个 `<title>` 和一个 `<path>`；禁用 `<g><rect><circle>…</circle>`。
- 主路径 **不允许** 出现 `fill` / `stroke` / `class` / `id`。
- 路径必须触碰 viewBox 至少 2 条边（不要留白边）。
- 包围盒中心落在 `(11..13, 11..13)` 之间。
- 多色 Logo 使用 **0.5 单位缝隙** 技巧，在单路径下模拟色块分层。
- 墨量占比约 25–65 %。

权威版本见 [`references/design-rules.md`](references/design-rules.md)。

---

## 视觉审校闭环

审校器返回的是 **坐标级** 的修改建议，而不是模糊的形容词：

```json
{
  "score": 7.8,
  "readable_at_16px": true,
  "issues": [ { "severity": "high", "area": "balance", "note": "右侧竖笔比左侧细了 0.4u" } ],
  "concrete_fixes": [ "把第 3–5 段的 x 坐标向外扩 0.4u" ],
  "verdict": "revise"
}
```

迭代上限、通过分数阈值可以在 [`scripts/config.json`](scripts/config.json) 里配置。

---

## 依赖

- **运行时：** Python 3.10+
- **可选（PNG 预览）：** `cairosvg` + `pillow`，或 `resvg`，或 PATH 中的 `inkscape`
- **Skill 运行：** 任意现代 **视觉大模型**（Prompt 与厂商无关）

---

## 发布到 GitHub / clawhub

本仓库已按公开发布准备好，可直接推送：

```powershell
git init
git add .
git commit -m "chore: initial public release"
git branch -M main
git remote add origin https://github.com/<你>/logo-svg-generator-skill.git
git push -u origin main
```

上传到 **clawhub** 时可原样上传整个目录，`skill/SKILL.md` 即 Skill 入口。

### 发布 Release

推荐使用 [`scripts/release.py`](./scripts/release.py)，它把发版流程封装成三个阶段：

```powershell
# 1. 检查发版条件，把 VERSION / CHANGELOG / SKILL.md 里的版本号统一
python scripts\release.py preflight --version 0.2.0

# 2. 提交版本号变更、打 tag、推送到 GitHub
python scripts\release.py push --version 0.2.0

# 3. 在 dist/ 下打包 zip，并在 GitHub 上创建 Release、上传 zip 附件
python scripts\release.py release --version 0.2.0

# 也可以一条命令跑完全部
python scripts\release.py all --version 0.2.0
```

依赖：`git` 与 `gh`（GitHub CLI，需先 `gh auth login`）。

---

## 参考与致谢

- 图标与规则：<https://github.com/simple-icons/simple-icons>
- 官方设计规范：<https://github.com/simple-icons/simple-icons/blob/develop/CONTRIBUTING.md>
- Slug 规则：<https://github.com/simple-icons/simple-icons/blob/develop/slugs.md>

## 许可证

[MIT](./LICENSE)

---

## 项目 Logo

顶部这枚标识是 **本 Skill 用自己生成的**——一个圆角方形"图标画布"包住一颗 8 顶点的 AI sparkle，品牌色 `#4F46E5`。源文件在 [`assets/`](./assets) 目录下：

- [`assets/logo.svg`](./assets/logo.svg) —— 24×24 Simple-Icons 合规主图（已通过 [`scripts/validate_svg.py`](./scripts/validate_svg.py)）
- [`assets/logo-mono-128.svg`](./assets/logo-mono-128.svg) —— 128 px 黑白
- [`assets/logo-color-128.svg`](./assets/logo-color-128.svg) —— 128 px 靛蓝品牌色

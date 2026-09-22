# IntelliJ IDEA 主题 — 设计规格（定稿）

状态：**已完成**（两个阶段都交付）。色值以 `PALETTE.md` 为准，本文件记录设计决策与理由。

阶段一：4 个 `.icls`（编辑器配色）。阶段二：`dist/AnimeIDEAThemes.jar` 插件，内含 4 套界面
主题（面板、工具窗、标签页、工具栏、状态栏、弹窗、滚动条）+ 4 套 `.icls`，通过 `editorScheme`
字段配对，选主题即整套生效。

## 1. 交付物

| 文件 | IDEA 显示名 | 基调 | parent_scheme | 编辑器背景 |
|---|---|---|---|---|
| `KurumiTokisaki_Light.icls` | Kurumi Tokisaki Light | 暖白 | `Default` | `#FBF9F7` |
| `KurumiTokisaki_Dark.icls` | Kurumi Tokisaki Dark | 炭黑带紫 | `Darcula` | `#1E1C22` |
| `HatsuneMiku_Light.icls` | Hatsune Miku Light | 暖粉白 | `Default` | `#FBF7FA` |
| `HatsuneMiku_Dark.icls` | Hatsune Miku Dark | 深海蓝 | `Darcula` | `#0B1A2A` |

每份 38 个颜色项 + 284 个文本属性，`version="142"`。安装见 `README.md`。

## 2. 决策树（逐条定案）

| # | 决策 | 结论 |
|---|---|---|
| Q1 | 交付形态 | 先 `.icls`，再 `.jar`——两阶段均已完成 |
| Q2 | 视觉概念 | 由用户提供两张图，各做一套 |
| Q3 | 明暗基调 | 每套出浅色 + 深色，共 4 份 |
| Q4 | 语言覆盖 | Java/Kotlin 深度调校，其余基础一致覆盖 |
| Q5 | 可读性取向 | 平衡档：四大类保证一眼可辨，装饰元素柔和 |
| Q6 | 语义映射 | 按提议执行，用户改关键字为金色 |
| Q7 | 主推版本 | 两个 Light 忠实原图；Kurumi Dark 因源图自带重暗调最出彩 |
| Q8 | 命名 | 显示名用角色名，落盘 `E:\AI\GML\idea_themes\` |
| Q9 | 字形样式 | 关键字加粗、注释斜体、注解正常体 |
| Q10 | 安装落点 | 用户自行安装 |

阶段二由用户反馈「只有两个地方被应用了」触发：`.icls` 只能改编辑器与控制台，IDE 框架必须由
界面主题提供，而界面主题只有插件能提供。

## 3. 源图提取调色板

### 时崎狂三（3000×1688）
| 语义来源 | 提取色 |
|---|---|
| 头饰朱红 | `#D83828` `#E8604F` `#F06058` |
| 裙装深酒红 | `#982850` `#7A1F2B` `#802020` |
| 金瞳 / 发饰 | `#E0A838` `#E8C870` `#F0D068` |
| 黑发 / 蕾丝 / 颈饰 | `#2B2933` `#35323C` `#484048` `#403840` |
| 发丝冷灰 | `#8E959E` `#8890A0` |
| 发梢浅蓝灰 | `#C2D8F2` `#C3CBD6` |
| 裙摆橘调高光 | `#F8A878` `#F8C090` |
| 背景蛋壳暖白 | `#F8F8F8` `#FAF7F5` |

### 初音未来（2848×1600）— 全图无暗部
| 语义来源 | 提取色 |
|---|---|
| 天空正蓝 | `#0890E8` `#0098F0` `#30AEF4` |
| 青绿发色 / 海面 | `#45C0FB` `#48C0F8` |
| 浅海 / 浪花 | `#98D0F0` `#C7E1F9` `#B8E0F8` |
| 沙滩光晕暖粉白 | `#F8E8F0` `#F0E4F1` |

## 4. 角色分配

### Kurumi Light
| 角色 | 色值 | 角色 | 色值 |
|---|---|---|---|
| 关键字（加粗） | `#8C6414` 金 | 字符串 | `#B03A22` 朱红 |
| 数字 / 常量 | `#982850` 树莓 | 函数 / 方法 | `#7A2E4A` 酒红 |
| 类 / 类型（加粗） | `#2B2933` 炭黑 | 注解 / 类型参数 | `#AC601C` 赭金 |
| 局部变量 | `#35323C` | 参数 / 字段 | `#4A4650` |
| 注释（斜体） | `#6E7580` | 错误（加粗+波浪） | `#E5112C` |
| 警告（波浪） | `#A96200` | 搜索命中底 | `#F0C86A` |

### Kurumi Dark
| 角色 | 色值 | 角色 | 色值 |
|---|---|---|---|
| 关键字（加粗） | `#E0A838` 金 | 字符串 | `#E8604F` 朱红 |
| 数字 / 常量 | `#E8C870` 浅金 | 函数 / 方法 | `#F0A878` 橘粉 |
| 类 / 类型（加粗） | `#C2D8F2` 冷蓝白 | 注解 | `#C76581` 玫瑰 |
| 局部变量 | `#C8C4CE` | 参数 | `#A8A4B2` |
| 注释（斜体） | `#8E959E` | 错误（加粗+波浪） | `#FF4D4D` |
| 警告（琥珀波浪，文字默认色） | `#D8A03C` 下划线 | 搜索命中底 | `#C9A227` |

### Miku Light
| 角色 | 色值 | 角色 | 色值 |
|---|---|---|---|
| 关键字（加粗） | `#0777BF` | 字符串 | `#1D8169` 深青 |
| 数字 / 常量 | `#B2593B` 暖橘 | 函数 / 方法 | `#005EA8` |
| 类 / 类型（加粗） | `#0B3F63` 深海 | 注解 | `#AD5776` 粉玫瑰 |
| 注释（斜体） | `#618099` | 错误 | `#D32F2F` |
| 搜索命中底 | `#F7D9E4` 粉 | 选中底 | `#D6EBFA` |

### Miku Dark
| 角色 | 色值 | 角色 | 色值 |
|---|---|---|---|
| 关键字（加粗） | `#48C0F8` 亮青 | 字符串 | `#F0B8CC` 玫瑰 |
| 数字 / 常量 | `#A8E8F0` 淡青 | 函数 / 方法 | `#5FD0C0` 薄荷 |
| 类 / 类型（加粗） | `#C7E1F9` | 注解 | `#C8B0E8` 淡紫 |
| 注释（斜体） | `#6386A1` | 错误 | `#FF5F56` |
| 搜索命中底 | `#3A9BD8` | 选中底 | `#1B4A6E` |

## 5. 已知取舍

**狂三暖色密集**：关键字金、注解与转义赭金、警告琥珀同属金色族。这是「金色关键字」的必然
代价——红色完全让给了错误提示。备选是把注解释到冷色（源图发梢冷蓝灰有依据）。

**初音浅色关键字压暗**：源图亮天蓝 `#0890E8` 在近白底上对比度 3.21 不达标，压到 `#0777BF`
（保持色相饱和度、只降明度）后为 4.50。损失了一点「天空感」换取可读性。

**初音深色背景与注解淡紫为衍生**：源图无暗部，`#0B1A2A` 与 `#C8B0E8` 非提取值。

**狂三深色警告文字用默认文本色**：关键字已占金色，警告只能靠琥珀波浪下划线标示。

## 6. 界面主题（阶段二）

`dist/AnimeIDEAThemes.jar` 是无代码插件，条目布局与已装成功的 `one-dark-theme` /
`GitHub Theme` 完全一致：

```
META-INF/MANIFEST.MF      必须存在，否则 IDEA 判定「不是有效插件」
META-INF/plugin.xml       4 个 themeProvider，指向根目录的 theme.json
META-INF/pluginIcon.svg
<名字>.theme.json          jar 根目录
<名字>.xml                 编辑器配色，editorScheme 写作 "/<名字>.xml"
```

三处踩过的坑（第一版全部踩中，导致「.jar 不是有效插件」）：

1. **缺 `META-INF/MANIFEST.MF`**——决定性原因。IDEA 对无清单的 jar 直接拒收。
   清单行需 CRLF 结尾、72 字节换行，生成器用 `chr(13)+chr(10)` 构造以免被转义层破坏。
2. theme.json 与配色文件放进了 `themes/`、`colors/` 子目录——能用的插件都放**根目录**，
   `path` 与 `editorScheme` 都写 `"/<文件名>"`。
3. `editorScheme` 最初写作 `"/colors/X.icls"`。改为根目录的 `.xml`。

**注意**：`.icls` 与 `.xml` 是同一种格式，改扩展名只是为了和可用范例保持一致。工作目录里
仍然保留 `.icls` 命名，供手动装到配置目录 `colors/` 的方案使用；jar 内是 `.xml` 副本。

| 主题 | parentTheme | `dark` | editorScheme |
|---|---|---|---|
| Kurumi Tokisaki Light | `IntelliJ` | false | `/colors/KurumiTokisaki_Light.icls` |
| Kurumi Tokisaki Dark | `Darcula` | true | `/colors/KurumiTokisaki_Dark.icls` |
| Hatsune Miku Light | `IntelliJ` | false | `/colors/HatsuneMiku_Light.icls` |
| Hatsune Miku Dark | `Darcula` | true | `/colors/HatsuneMiku_Dark.icls` |

界面调色板（每套 8 个表面层级 + 强调色）：窗口 / 面板 / 抬起面 / 悬停 / 边框 / 主文字 /
次级文字 / 弱化文字 / 选区 / 强调 / 副强调 / 信息 / 错误 / 警告 / 各类提示底色。

**只改颜色，不改 UI 类名与度量**（`Button.border`、`Component.arc` 这类交给 parentTheme 继承），
因为 UI 实现类名跨版本易变、写错会导致控件渲染异常，而颜色键名是稳定的。

## 7. 不包含

- 图标图形：主题只能改颜色，图标集来自 IDEA 内置（深色继承 Darcula、浅色继承 IntelliJ，
  因此 `dark` 标记必须与 `parentTheme` 一致，`themes.py` 会校验这一点）
- 编辑器背景图：`.icls` 与主题键都无法设置，需 IDEA 自带的
  `Settings → Appearance & Behavior → Appearance → Background Image`

## 8. 验证手段

| 脚本 | 作用 |
|---|---|
| `build_themes.py` | 生成 .icls + PALETTE.md；对每个前景强制 WCAG 下界（只调明度）并打印调整记录 |
| `verify.py` | 结构校验：颜色段/属性段严格分离、无重名、属性名集合与规格一致、TEXT 背景等于编辑器背景 |
| `verify_render.py` | 渲染校验：把每套方案画到画布上，逐词元回读像素，必须命中声明的颜色 |
| `themes.py` | 界面主题：生成 .theme.json + plugin.xml + jar；校验顶层键名、叶子属性名、颜色格式、`parentTheme` 合法性与 `dark` 一致性、11 组界面文字对比度；`verify_jar()` 另校验清单存在且以 `Manifest-Version: 1.0`+CRLF 开头、`plugin.xml` 是合法 XML、4 个 `themeProvider` 的 `path` 与 4 个 `editorScheme` 均能在 jar 内解析到 |
| `preview.py` | 编辑器配色预览：`preview.png` + 4 张 2× 单图 + `preview.html` |
| `ui_preview.py` | 完整界面模拟图：项目树、标签页、工具栏、状态栏、滚动条、弹窗 |

### 属性名/键名的核对来源（本机 IntelliJ IDEA 2025.2，IC-252.28539.97）

| 来源 | 用途 |
|---|---|
| `lib/app-client.jar` → `themes/Light.xml`、`themes/expUI/expUI_darkScheme.xml` | 编辑器属性名 |
| `lib/app.jar` → `colorSchemes/XmlDarcula.xml`；`plugins/*/lib/*.jar` → `colorSchemes/*.xml` | 语言插件属性名 |
| `lib/app-client.jar` → `themes/*.theme.json` | 界面键名；导出为 `_ref/ui_keys.json`（顶层 231 个 + 叶子属性 680 个） |

编辑器侧改正的错误：`MATCHED_BRACES`→`MATCHED_BRACE_ATTRIBUTES`、
`WHITE_SPACES`→`WHITESPACES`、`SEARCH_MATCH_ATTRIBUTES`→`SEARCH_RESULT_ATTRIBUTES`、
`MARKDOWN_HEADER_LEVEL_1..6`→`MARKDOWN_HEADER`、`XML_PROLOG`→`XML_PROLOGUE`、
`METHOD_SEPARATORS`→`METHOD_SEPARATORS_COLOR`、`BREADCRUMBS_INLAY`→`BREADCRUMBS_INACTIVE`；
所有 `*_ATTRIBUTES` 项从颜色段移到属性段；不存在的 `READ_IDENTIFIER_UNDER_CARET_ATTRIBUTES`
与 `INLAY_HINTS_*` 删除。
界面侧改正：`remoteIconColor`→`remoteBranchIconColor`。

### 界面键名校验的两次自纠

1. 最初只收集自带主题的**顶层**键，导致合法的嵌套子键（`foreground`、`ArrowButton`）被批量
   误报。改为两级校验：顶层键对顶层白名单，叶子属性名对全量叶子名集合。
2. `SearchEverywhere.List.settingsBackground` 这种**键名本身含点**的合法键被后缀切分误判。
   改为逐级尝试所有后缀。

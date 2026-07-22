# 皮肤运行机制

理解这些机制才能写出「不出错」的皮肤。生成皮肤前必读。

## 1. 文件与加载规则

```
<皮肤名>/
├── config.yaml          必需，声明每种键盘用哪个配置文件
├── demo.png             必需，应用内的预览图
├── README.md            建议提供，纯文字，用户可在应用内查看
├── fonts/               可选，config.yaml 的 fontFace 引用这里的字体文件
├── sound/               可选，config.yaml 的 keySound 引用这里的音频文件
├── light/               必需，浅色模式配置
│   ├── <名称>.yaml
│   └── resources/       可选，fileImage 用的拼合图片与图片描述文件
└── dark/                必需，深色模式配置（结构与 light 完全一致）
    ├── <名称>.yaml
    └── resources/
```

加载路径由三件事决定：**键盘类型 → 设备与方向 → 系统深浅色**。

例如 iPhone 竖屏、浅色、拼音键盘，会读 `config.yaml` 的 `pinyin.iPhone.portrait`
拿到文件名 `X`，最终加载 `light/X.yaml`。

关键规则：

- `light/` 与 `dark/` 必须**成对**提供同名文件，否则切换深浅色时键盘空白。
- 缺某个设备 / 方向的声明 → 该场景下键盘显示为**空白**，不会回退。
- 不声明 `numeric` → 使用内置数字键盘；不声明 `symbolic` → 使用内置符号键盘。
- `numberPad` 与 `numeric` 两种类型都读 `config.yaml` 里的 `numeric` 一项。
- `pinyin` 是必须提供的，其余可选。

## 2. 四个区域与它们的覆盖关系

键盘从上到下由三个区域纵向排列，高度分别由 `preeditHeight` / `toolbarHeight` /
`keyboardHeight` 决定：

```
┌─────────────────────────────┐
│ 预编辑区  preeditStyle       │  高度 preeditHeight
├─────────────────────────────┤
│ 工具栏区  toolbarStyle       │  高度 toolbarHeight
│           toolbarLayout      │
├─────────────────────────────┤
│                             │
│ 按键区    keyboardStyle      │  高度 keyboardHeight
│           keyboardLayout     │
│                             │
└─────────────────────────────┘
```

候选栏**不是**第四个区域，而是浮在上面的两层覆盖视图：

- **横向候选栏**（`horizontalCandidatesStyle` / `horizontalCandidatesLayout`）
  进入输入状态时创建，frame 与工具栏区**完全相同**，覆盖在工具栏之上。
  也就是说：工具栏区在非输入态显示 `toolbarLayout`，输入态显示横向候选栏。
- **纵向候选栏**（`verticalCandidatesStyle` / `verticalCandidatesLayout`）
  候选栏展开时创建，覆盖**预编辑区以下的全部区域**（工具栏区 + 按键区）。

由此得出两条实用结论：

- 大多数皮肤把 `toolbarLayout` 写成 `{}`（空），因为工具栏区的实际内容就是候选栏。
- 想在工具栏放常驻按钮（如设置、剪贴板），要写进 `toolbarLayout`，
  但要意识到输入时它会被候选栏盖住。

另外：

- 开启「内嵌输入」后预编辑区高度按 0 计算，`preeditStyle` 不渲染。
- 没有定义 `keyboardStyle` → 按键区**根本不会被创建**；`toolbarStyle` 同理。
  即使不需要背景，也要至少写 `keyboardStyle: {}` 之外的有效内容（通常给个背景样式）。

## 3. 布局：HStack 是「行」，VStack 是「列」

这里的命名与直觉相反，务必记牢：

| 节点 | 同级之间怎么排 | 分配什么 | 直观含义 |
| --- | --- | --- | --- |
| `HStack` | 自上而下堆叠 | 平分**高度**，每个占满宽度 | 一**行** |
| `VStack` | 自左向右堆叠 | 平分**宽度**，每个占满高度 | 一**列** |
| `Cell`（父为 `HStack`） | 自左向右 | 平分**宽度**，占满行高 | 行中的一个键 |
| `Cell`（父为 `VStack`） | 自上而下 | 平分**高度**，占满列宽 | 列中的一个键 |

标准 26 键键盘 = 根数组放 4 个 `HStack`（4 行），每行的 `subviews` 放若干 `Cell`：

```yaml
keyboardLayout:
  - HStack:                      # 第 1 行
      subviews:
        - Cell: qButton
        - Cell: wButton
  - HStack:                      # 第 2 行
      subviews:
        - Cell: aButton
```

九宫格数字键盘则常用根数组放多个 `VStack`（多列），每列 `subviews` 放 `Cell`。

**硬性约束**（违反会直接报错并终止该层渲染）：

- 同级数组中不能同时出现 `HStack` 与 `VStack`
- 同级数组中不能同时出现 `HStack` 与 `Cell`
- 同级数组中不能同时出现 `VStack` 与 `Cell`
- `Cell` 不能直接放在布局根数组，必须是 `HStack` 或 `VStack` 的子节点

## 4. 尺寸分配算法

每个 `Cell` / `HStack` / `VStack` 的尺寸来自它引用样式中的 `size`：

- `width: 100` → 固定 100 point
- `width: '1/2'` → 父容器宽度的 50%
- `width: { percentage: 0.5 }` → 同上
- **不写** → 「均分剩余空间」

分配顺序：先扣掉所有固定值与百分比，剩余空间在所有未声明尺寸的元素之间**等分**，
再把像素取整的余数补给前几个元素。

实践建议：用一个虚拟设计宽度让分数可读。官方皮肤用 `1125`：

```yaml
# 第 1 行 10 个键：10 × 112.5 = 1125
size: { width: 112.5/1125 }
# 第 3 行 shift 与退格更宽：168.75 × 2 + 112.5 × 7 = 1125
size: { width: 168.75/1125 }
```

一行内所有键的分子加起来等于分母，就正好铺满。空格键干脆不写 `size`，自动吃掉剩余宽度。

### bounds：把「触摸区」和「显示区」分开

`size` 决定按键的**触摸区域**，`bounds` 在其中划出更小的**可视区域**，
所有图层都在可视区域内布局。典型用途是让边缘键（`a` / `l` / shift / 退格）
的触摸区延伸到屏幕边缘，但视觉上仍与其他键对齐：

```yaml
aButton:
  size: { width: 168.75/1125 }                        # 触摸区更宽
  bounds: { alignment: right, width: 111/168.75 }     # 显示区靠右，只占其中一部分
```

## 5. 样式解析

一个键盘配置文件的根节点是**扁平**的大字典：少量结构性 Key + 任意多个「样式名 → 样式节点」。
所有引用都是**按名字符串**，例如 `backgroundStyle: myButtonBg` 会去根节点找 `myButtonBg`。

> **最常见的致命错误**：引用了一个不存在的样式名。
> 系统不会报错、不会回退，那个位置**直接渲染为空白**。
> 因此每次生成完必须跑校验脚本。

按键的最终外观 = 一个背景图层 + 若干前景图层叠加：

```
Cell: qButton
      └─ qButton（按键样式节点：尺寸、动作、引用哪些样式）
           ├─ backgroundStyle: → 一个样式节点（buttonStyleType 决定怎么画）
           └─ foregroundStyle: → 一个或多个样式节点（可叠加）
```

`buttonStyleType` 是样式节点的必填项，缺失该样式**不渲染**。五种取值分别需要不同的配套 Key，
见 `keys.md` 第 4.5 节。

### 状态优先级

前景样式按以下顺序选取，只有对应 Key 存在时才切换：

```
上/下划样式 → 大写锁定样式 → 大写样式 → foregroundStyle
```

按键动作按以下顺序选取：

```
preeditStateAction（有预编辑文本时） → uppercasedStateAction（大写时） → action
```

## 6. YAML 合并键 `<<`

支持，且是控制皮肤体积的主要手段。大多数 Key 的读取方式是「先查本层，查不到再查 `<<`」。

```yaml
_base:
  letterFg: &letterFg
    buttonStyleType: text
    fontSize: 22.5
    normalColor: "#000000"
    highlightColor: "#000000"

qFg: { <<: *letterFg, text: q }
wFg: { <<: *letterFg, text: w }
```

> **陷阱**
>
> 少数 Key 只查本层，**不会**穿透 `<<`，放进被合并的基底里就会失效：
> `maxColumns`、`maxRows`、`contentRightToLeft`、`colorLocation`、`colorStartPoint`、
> `colorEndPoint`、`colorGradientType`、`shadowOpacity`、`type`、
> `floatKeyboardAlpha`、`floatKeyboardLockedState`、`floatTargetScale`。
> 这些必须直接写在使用它的节点内。校验脚本会检查这一点。

另外：以 `_` 开头的根 Key（如 `_palette`、`_base`）只是锚点容器，
不会被任何东西引用，属于惰性内容，可放心使用。

## 7. 其他容易踩的点

- **颜色**只支持 `#RRGGBB` 与 `#RRGGBBAA`（`#` 可省略）。写成 `red`、`rgb(...)`、
  3 位缩写都会解析失败并**静默变透明**。
- `animation` 必须是**数组**，写成单个字符串不会生效。
- 预编辑区的前景样式节点比较特殊：它不渲染成图层，只从中读 `fontSize`、`fontWeight`
  和 `textColor`（注意是 `textColor`，不是 `normalColor`）。
- `text` 支持变量：`$rimePreedit`、`$rimeCandidate`、`$rimeCandidateComment`、
  `$rimeSchemaName`、`$returnKeyType`。
- 长按符号面板有新旧两套：`hintSymbolsGridStyle`（网格，推荐）优先于
  `hintSymbolsStyle`（单行）。
- `fileImage` 用的是**拼合图片**：一张 png 里放多个小图，配一个同名 yaml 描述每个小图的
  `rect` 与不可拉伸的 `insets`。
- 划动只识别**上下**方向，没有左右划。

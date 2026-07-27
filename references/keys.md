# 元书皮肤 YAML 配置项索引

本文件由键盘扩展源码反推整理，列出皮肤 YAML 中全部会被读取的 Key、类型、默认值与枚举取值。
生成皮肤时以本文件为准；本文件没有的 Key 一律不要写。


本页是一份**速查索引**，按“文件 → 节点 → Key”的层级，列出键盘扩展在解析皮肤 YAML 时实际读取的**全部 Key**、
它们的值类型、默认值以及枚举类型的全部取值。

> **如何阅读本页**
>
> - 「类型」列使用 TypeScript 风格描述：`Float`、`String`、`Bool`、`Int`、`[T]` 表示数组、`{ a: T }` 表示对象、`A | B` 表示多选其一。
> - 「默认值」列中的 `—` 表示该 Key 未设置时不产生任何效果。
> - 标注为 `未使用` 的 Key 在当前版本的键盘扩展中不会被读取，仅为历史兼容保留。
> - 需要完整的使用说明与示例，请参阅左侧「键盘皮肤」下的其他章节；本页只负责“查得到、查得全”。

## 一、通用值类型

皮肤中的许多 Key 共享同一套值类型约定，先在此统一说明，后文不再重复。

| 值类型 | 书写形式 | 说明 |
| --- | --- | --- |
| `Color` | `'#RRGGBB'` 或 `'#RRGGBBAA'` | 十六进制颜色，`#` 可省略；8 位形式的最后 2 位为透明度。长度不是 6 或 8 位时解析失败（该颜色不生效）。 |
| `Length` | `Float` 或 `'<数值>vh'` | 用于 `preeditHeight` / `toolbarHeight` / `keyboardHeight`。纯数值表示 point；`vh` 结尾表示屏幕物理高度的百分比，如 `'10vh'` 表示 10%。 |
| `Size` | `Float` \| `'分子/分母'` \| `{ percentage: Float \| String }` | 用于 `size.width` / `size.height`。`Float` 为 point；`'1/2'` 为父容器的 50%；不设置时为“均分剩余空间”。 |
| `FontSize` | `Float` \| `'<数值>em'` \| `'<数值>'` | `em` 结尾表示相对于系统默认字号的倍数，如 `'1.2em'`；其余按绝对字号处理。 |
| `Insets` | `{ top: Float, left: Float, bottom: Float, right: Float }` | 四个方向均可省略，省略时为 `0`。 |
| `Point` | `{ x: Float, y: Float }` | 坐标 / 偏移，两个分量可分别省略。 |
| `Rect` | `{ x: Float, y: Float, width: Float, height: Float }` | 矩形区域，省略的分量为 `0`。 |
| `GridCell` | `{ row: Int, col: Int }` | 网格坐标，`row` 与 `col` 均**从 0 开始**，两者缺一则整体无效。 |
| `KeyboardAction` | `String` \| `Object` | 按键动作，取值见 [六、按键动作](#六按键动作-keyboardaction)。 |

> **关于 YAML 合并键 `<<`**
>
> 绝大多数 Key 通过“先查本层、再查 `<<` 合并节点”的方式读取，因此可以放心使用 YAML 锚点与合并键复用样式。
> 
> 少数 Key 只在**本层**查找，不会回落到 `<<`：`maxColumns`、`maxRows`、`contentRightToLeft`、`colorLocation`、
> `colorStartPoint`、`colorEndPoint`、`colorGradientType`、`shadowOpacity`、`floatKeyboardAlpha`、`floatKeyboardLockedState`、
> `floatTargetScale`、`type`（Cell 类型）。这些 Key 请直接写在使用它的节点内。

## 二、`config.yaml`（皮肤描述文件）

位于皮肤根目录，描述皮肤包含哪些键盘、使用哪些字体与按键音。

### 2.1 键盘类型映射

根节点下，每一个**键盘类型名**对应一组键盘配置文件名。

| Key | 类型 | 说明 |
| --- | --- | --- |
| `<键盘类型>` | `{ iPhone: DeviceEntry, iPad: DeviceEntry }` | 键盘类型名见下表；也可使用自定义名称（供浮动键盘 / `floatKeyboardType` 引用）。 |
| `<键盘类型>.iPhone.portrait` | `String` | iPhone 竖屏使用的键盘文件名（不含 `.yaml` 后缀）。 |
| `<键盘类型>.iPhone.landscape` | `String` | iPhone 横屏使用的键盘文件名。 |
| `<键盘类型>.iPad.portrait` | `String` | iPad 竖屏使用的键盘文件名。 |
| `<键盘类型>.iPad.landscape` | `String` | iPad 横屏使用的键盘文件名。 |
| `<键盘类型>.iPad.floating` | `String` | iPad 浮动键盘形态使用的键盘文件名。 |

内置键盘类型名（枚举）：

`alphabetic`、`pinyin`、`emojis`、`images`、`numeric`、`numberPad`、`symbolic`，以及任意**自定义名称**。

> `numberPad` 与 `numeric` 两种键盘类型在查找配置文件时都会读取 `numeric` 这一项。
> 
> 最终加载的文件路径为 `<皮肤名>/<light|dark>/<文件名>.yaml`，深浅色由系统外观决定。

### 2.2 `fontFace`（皮肤字体）

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `fontFace` | `[FontFace]` | — | 数组顺序即字体优先级。 |
| `fontFace[].url` | `String` | `''` | 皮肤 `fonts/` 目录下的字体文件名（含后缀）。 |
| `fontFace[].name` | `String` | `''` | 系统字体名称。`name` 非空时优先于 `url`。 |
| `fontFace[].ranges` | `[UnicodeRange]` | `[]` | 该字体生效的 Unicode 区间。 |
| `fontFace[].ranges[].location` | `Int` | `0` | 区间起始 Unicode 码点。 |
| `fontFace[].ranges[].length` | `Int` | `0` | 区间长度。 |

### 2.3 `keySound`（按键音）

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `keySound.input` | `String` | 系统输入音 | 皮肤 `sound/` 目录下的音频文件名。 |
| `keySound.delete` | `String` | 系统删除音 | 同上。 |
| `keySound.system` | `String` | 系统功能键音 | 同上。 |
| `keySound.actions` | `[Object]` | `[]` | 为特定按键动作单独指定按键音。 |
| `keySound.actions[].action` | `KeyboardAction` | — | 必填，匹配的按键动作。 |
| `keySound.actions[].url` | `String` | — | 必填，`sound/` 目录下的音频文件名。 |

### 2.4 其他

| Key | 类型 | 说明 |
| --- | --- | --- |
| `name` | `String` | `未使用`。当前皮肤名称取自皮肤文件夹名。 |
| `author` | `String` | `未使用`。仅作皮肤自述信息。 |

## 三、图片描述文件（`resources/<图片名>.yaml`）

与拼合图片 `resources/<图片名>.png` 同名，用于描述大图中每个小图的位置与保护区域。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `<小图名>` | `Object` | — | 小图名即样式中 `normalImage.image` / `highlightImage.image` 引用的名称。 |
| `<小图名>.rect` | `Rect` | `0` | 小图在大图中的像素区域。`rect` 为空或面积为 0 时该图不显示。 |
| `<小图名>.rect.x` / `.y` | `Float` | `0` | 以大图左上角为原点。 |
| `<小图名>.rect.width` / `.height` | `Float` | `0` | 小图宽高（像素）。 |
| `<小图名>.insets` | `Insets` | `0` | 图片拉伸时的**保护区域**（不可拉伸边距）。 |

## 四、键盘配置文件（`light/<名称>.yaml`、`dark/<名称>.yaml`）

一个键盘配置文件的根节点是一个大字典：既包含少量“结构性 Key”，也包含**任意数量的自定义样式名**。
所有样式（背景、前景、气泡、动画、通知、集合视图等）都以“样式名 → 样式节点”的形式平铺在根节点下，
再由结构性 Key 通过名称引用。

### 4.1 根节点结构性 Key

| Key | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `preeditHeight` | `Length` | 是 | 预编辑区高度。开启内嵌模式时该区域高度按 0 计算。 |
| `toolbarHeight` | `Length` | 是 | 工具栏区高度。 |
| `keyboardHeight` | `Length` | 是 | 按键区高度。 |
| `preeditStyle` | `Object` | 否 | 预编辑区样式节点，见 [4.6](#46-区域样式节点)。 |
| `toolbarStyle` | `Object` | 否 | 工具栏区样式节点。 |
| `toolbarLayout` | `[LayoutNode]` | 否 | 工具栏区布局，见 [4.2](#42-布局节点hstack--vstack--cell)。 |
| `keyboardStyle` | `Object` | 否 | 按键区样式节点。 |
| `keyboardLayout` | `[LayoutNode]` | 否 | 按键区布局。 |
| `horizontalCandidatesStyle` | `Object` | 否 | 横向候选区容器样式节点。 |
| `horizontalCandidatesLayout` | `[LayoutNode]` | 否 | 横向候选区布局。 |
| `verticalCandidatesStyle` | `Object` | 否 | 纵向候选区容器样式节点。 |
| `verticalCandidatesLayout` | `[LayoutNode]` | 否 | 纵向候选区布局。 |
| `candidateContextMenu` | `[Object]` | 否 | 长按候选字弹出的菜单，见 [4.10](#410-候选字长按菜单-candidatecontextmenu)。 |
| `floatTargetScale` | `Float \| Point` | 否 | 默认 `{ x: 0.8, y: 0.8 }`。浮动键盘的缩放比例；写成单个 `Float` 时表示 x、y 相同。 |
| `floatKeyboardAlpha` | `Float` | 否 | 默认 `0.95`。浮动键盘背景不透明度，取值 `0.1`~`1.0`，请勿设为 `0`。 |
| `floatKeyboardLockedState` | `Bool` | 否 | 默认 `false`。为 `false` 时点击浮动键盘上的按键后自动隐藏浮动键盘；为 `true` 时保持显示。 |
| `<任意样式名>` | `Object` | — | 自定义样式节点，由上述 Key 或其他样式按名称引用。 |

> `floatTargetScale`、`floatKeyboardAlpha`、`floatKeyboardLockedState` 读取的是**当前生效的浮动键盘配置文件**的根节点。

### 4.2 布局节点（`HStack` / `VStack` / `Cell`）

`toolbarLayout`、`keyboardLayout`、`horizontalCandidatesLayout`、`verticalCandidatesLayout` 的值都是布局节点数组。

| Key | 类型 | 说明 |
| --- | --- | --- |
| `HStack` | `Object` | 水平容器（同级平分**高度**）。同级数组中不能与 `VStack`、`Cell` 混用。 |
| `VStack` | `Object` | 垂直容器（同级平分**宽度**）。同级数组中不能与 `HStack`、`Cell` 混用。 |
| `Cell` | `String` | 单元格，值为根节点下的样式名。`Cell` 必须是 `HStack` 或 `VStack` 的子节点，不能直接出现在布局根数组中。 |
| `HStack.style` / `VStack.style` | `String` | 容器所引用的样式名，用于从该样式的 `size` 中取出宽 / 高。 |
| `HStack.subviews` / `VStack.subviews` | `[LayoutNode]` | 子布局节点数组。 |

> **布局约束**
>
> 同级节点中同时出现 `HStack` 与 `VStack`、`HStack` 与 `Cell`、`VStack` 与 `Cell` 都会报错并终止该层的构建。

### 4.3 Cell 类型：`type`

样式节点中的 `type` 决定该 `Cell` 渲染成什么控件。

| 值 | 说明 |
| --- | --- |
| `button` | **默认值**。普通按键。 |
| `symbols` | 纵向符号列表。 |
| `classifiedSymbols` | 一级分类符号列表。 |
| `subClassifiedSymbols` | 二级分类符号列表（与一级联动）。 |
| `horizontalSymbols` | 横向滑动符号列表。 |
| `horizontalCandidates` | 横向候选字列表。 |
| `verticalCandidates` | 纵向候选字列表。 |
| `numericSymbols` | 内置数字键盘符号列表。 |
| `categorySymbols` | 分类符号列表。 |
| `t9Symbols` | 九键纵向符号列表。 |
| `t9HorizontalSymbols` | 九键横向符号列表。 |

### 4.4 按键样式节点（`type: button`）

被 `Cell` 直接引用的样式节点。

#### 尺寸与位置

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `size` | `{ width: Size, height: Size }` | 均分 | 按键尺寸。父容器为 `HStack` 时取 `width`，为 `VStack` 时取 `height`。 |
| `size.width` / `size.height` | `Size` | 均分 | 见 [通用值类型](#一通用值类型)。 |
| `bounds` | `Object` | 整个按键区域 | 按键的**可视区域**，所有子图层都在其中布局。 |
| `bounds.alignment` | 枚举 | `center` | 可视区域在按键内的对齐方式，取值见 [七、枚举速查](#七枚举速查)。 |
| `bounds.width` / `bounds.height` | `Size` | 按键宽 / 高 | 可视区域尺寸。 |

#### 样式引用

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `backgroundStyle` | `String \| [ConditionStyle]` | — | 背景样式名；数组形式为条件样式，取首个命中项的第一个样式名。 |
| `foregroundStyle` | `String \| [String] \| [ConditionStyle]` | — | 前景样式名，可叠加多个。 |
| `uppercasedStateForegroundStyle` | 同上 | — | 大写状态下替换 `foregroundStyle`。 |
| `capsLockedStateForegroundStyle` | 同上 | — | 大写锁定状态下替换 `foregroundStyle`（优先级高于大写状态）。 |
| `swipeUpForegroundStyle` | 同上 | — | 上划过程中替换 `foregroundStyle`。 |
| `swipeDownForegroundStyle` | 同上 | — | 下划过程中替换 `foregroundStyle`。 |
| `hintStyle` | `String` | — | 短按气泡样式名，见 [4.7](#47-气泡样式节点)。 |
| `hintSymbolsStyle` | `String` | — | 长按符号（单行）样式名。 |
| `hintSymbolsGridStyle` | `String` | — | 长按符号网格样式名。配置有效时优先于 `hintSymbolsStyle`。 |
| `animation` | `[String]` | `[]` | 动画样式名数组，见 [4.9](#49-动画样式节点)。**必须写成数组**。 |
| `notification` | `String \| [String]` | `[]` | 通知样式名，见 [4.8](#48-通知样式节点)。 |

前景样式的选取优先级为：**上 / 下划样式 → 大写锁定样式 → 大写样式 → `foregroundStyle`**，
且只有对应 Key 存在时才会切换。

> 键盘只识别**上下**两个划动方向：水平位移大于垂直位移时，该次划动会被判定为失败。
> 因此**不存在** `swipeLeftForegroundStyle` 与 `swipeRightForegroundStyle`。

#### 按键动作

| Key | 类型 | 说明 |
| --- | --- | --- |
| `action` | `KeyboardAction` | 点击动作。 |
| `uppercasedStateAction` | `KeyboardAction` | 大写 / 大写锁定状态下的点击动作。 |
| `preeditStateAction` | `KeyboardAction` | 存在预编辑文本时的点击动作（优先级最高）。 |
| `repeatAction` | `KeyboardAction` | 长按连续触发的动作。 |
| `swipeUpAction` | `KeyboardAction` | 上划动作。 |
| `swipeDownAction` | `KeyboardAction` | 下划动作。 |

动作选取优先级：`preeditStateAction`（存在预编辑时）→ `uppercasedStateAction`（大写 / 大写锁定时）→ `action`。

划动动作同样只支持上、下两个方向，**不存在** `swipeLeftAction` 与 `swipeRightAction`。

#### 条件样式 `ConditionStyle`

| Key | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `conditionKey` | `String` | 是 | 条件名，取值见 [七、枚举速查](#七枚举速查)。 |
| `conditionValue` | `Bool \| [Int]` | 是 | 期望值。`$returnKeyType` 时为 `[Int]`，其余为 `Bool`。 |
| `styleName` | `String \| [String]` | 是 | 命中后使用的样式名。`backgroundStyle` 只取数组的第一个。 |

### 4.5 样式节点（`buttonStyleType`）

被 `backgroundStyle` / `foregroundStyle` 引用的节点。`buttonStyleType` 为必填，它决定该节点还能读取哪些 Key。

#### 全部类型通用

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `buttonStyleType` | 枚举 | — | 必填。`geometry` / `systemImage` / `assetImage` / `fileImage` / `text`。缺失时该样式不渲染。 |
| `insets` | `Insets` | `0` | 在可视区域内进一步收缩的边距。 |
| `center` | `Point` | — | 调整图层中心点。中心点 x = 可视区域宽 × `x` + 可视区域 minX，y 同理。`x`、`y` 可分别省略。 |

#### `geometry`

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `normalColor` | `Color \| [Color]` | — | 常态颜色。数组表示渐变色。 |
| `highlightColor` | `Color \| [Color]` | — | 按下时颜色。数组表示渐变色。 |
| `colorLocation` | `[Float]` | — | 渐变色位置，取值 `0.0`~`1.0`。**数组长度必须与颜色数量一致**才会生效。 |
| `colorStartPoint` | `Point` | `{ x: 0.5, y: 0 }` | 渐变起点，`x`、`y` 必须同时提供。 |
| `colorEndPoint` | `Point` | `{ x: 0.5, y: 1 }` | 渐变终点，`x`、`y` 必须同时提供。 |
| `colorGradientType` | 枚举 | `axial` | `axial` / `conic` / `radial`。 |
| `cornerRadius` | `Float` | — | 圆角半径（使用 `continuous` 圆角曲线）。 |
| `borderSize` | `Float` | — | 边框宽度。**必须与边框颜色同时设置**。 |
| `normalBorderColor` | `Color` | — | 常态边框颜色。 |
| `highlightBorderColor` | `Color` | — | 按下时边框颜色。 |
| `normalLowerEdgeColor` | `Color` | — | 常态底部边缘颜色。 |
| `highlightLowerEdgeColor` | `Color` | — | 按下时底部边缘颜色。 |
| `normalShadowColor` | `Color` | — | 常态阴影颜色。**未设置颜色时下方所有阴影参数均不生效**。 |
| `highlightShadowColor` | `Color` | — | 按下时阴影颜色。 |
| `shadowOpacity` | `Float` | `1` | 阴影不透明度，`0` 表示不显示阴影。 |
| `shadowRadius` | `Float` | `3` | 阴影模糊半径。 |
| `shadowOffset` | `Point` | `{ x: 0, y: 3 }` | 阴影偏移，映射为 `CGSize(width: x, height: y)`。 |

#### `systemImage`

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `systemImageName` | `String` | — | 必填。SF Symbols 图标名。 |
| `highlightSystemImageName` | `String` | 回落到 `systemImageName` | 按下时的 SF Symbols 图标名。 |
| `contentMode` | 枚举 | `center` | `scaleToFill` / `scaleAspectFit` / `scaleAspectFill` / `center`。 |
| `fontSize` | `FontSize` | 系统默认 | 图标点尺寸。 |
| `fontWeight` | 枚举 | 系统默认 | 图标字重，取值见 [七、枚举速查](#七枚举速查)。 |
| `normalColor` | `Color` | — | 常态着色。 |
| `highlightColor` | `Color` | — | 按下时着色。 |

#### `assetImage`

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `assetImageName` | `String` | — | 必填。App 内置资源图片名。 |
| `contentMode` | 枚举 | `center` | 同上。 |
| `normalColor` | `Color` | — | 常态着色。 |
| `highlightColor` | `Color` | — | 按下时着色。 |

#### `fileImage`

图片从**当前键盘配置文件所在目录的 `resources/`** 子目录读取。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `normalImage` | `{ file: String, image: String }` | — | 常态图片。`file` 为图片文件名（不含 `.png`），`image` 为图片描述文件中的小图名。两者缺一不显示。 |
| `highlightImage` | `{ file: String, image: String }` | — | 按下时图片，结构同上。 |
| `contentMode` | 枚举 | `scaleToFill` | 注意此处默认值与 `systemImage` 不同。 |

#### `text`

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `text` | `String` | — | 文本内容。支持特殊变量，见 [七、枚举速查](#七枚举速查)。 |
| `fontSize` | `FontSize` | 系统默认 | 字号。 |
| `fontWeight` | 枚举 | 系统默认 | 字重。 |
| `normalColor` | `Color` | 系统标签色 | 常态文字颜色。 |
| `highlightColor` | `Color` | 系统标签色 | 按下时文字颜色。 |

### 4.6 区域样式节点

`preeditStyle`、`toolbarStyle`、`keyboardStyle`、`horizontalCandidatesStyle`、`verticalCandidatesStyle` 共用以下 Key。

| Key | 类型 | 默认值 | 适用区域 | 说明 |
| --- | --- | --- | --- | --- |
| `backgroundStyle` | `String` | — | 全部 | 区域背景样式名。 |
| `insets` | `Insets` | `0` | 全部 | 区域内容边距。 |
| `foregroundStyle` | `String \| [String]` | — | `preeditStyle` | 预编辑文本样式名，取**最后一个**。从中读取 `fontSize`、`fontWeight` 与 `textColor`。 |
| `textColor` | `Color` | 系统标签色 | 预编辑文本样式节点 | 预编辑文本颜色。 |

### 4.7 气泡样式节点

#### `hintStyle`（短按气泡）

气泡本身就是一个完整的按键样式节点，可使用 [4.4](#44-按键样式节点type-button) 中的全部 Key。此外：

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `size` | `{ width: Size, height: Size }` | 按键可视区域尺寸 | 自定义气泡尺寸；`width` 与 `height` 必须**同时**为 `Float` 或百分比才生效。 |
| `checkIfOverflowsParentHeight` | `Bool` | `true` | 是否检测气泡超出父视图顶部并自动下移。 |

#### `hintSymbolsStyle`（长按符号，单行）

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `symbolStyles` | `[String]` | — | 必填。每个元素是一个按键样式名，横向依次排列。为空则不显示。 |
| `size` | `{ width: Size, height: Size }` | 按键可视区域尺寸 | 单个符号的尺寸。 |
| `insets` | `Insets` | `0` | 面板内边距（以**外扩**方式作用于整体气泡）。 |
| `backgroundStyle` | `String` | — | 面板背景样式名。 |
| `selectedBackgroundStyle` | `String` | — | 选中符号的背景样式名。 |
| `selectedIndex` | `Int` | `0` | 初始选中的符号下标。 |
| `checkIfOverflowsParentHeight` | `Bool` | `true` | 同上。 |

#### `hintSymbolsGridStyle`（长按符号，网格）

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `symbolRows` | `[[String \| null]]` | `[]` | 必填。每一行是一组样式名，`~` 或空字符串表示空单元格。全为空则回落到 `hintSymbolsStyle`。 |
| `size` | `{ width: Size, height: Size }` | 按键可视区域尺寸 | 单元格尺寸。 |
| `spacing` | `{ horizontal: Float, vertical: Float }` | `{ 0, 0 }` | 单元格间距。 |
| `insets` | `Insets` | `0` | 面板内边距。 |
| `offset` | `Point` | `{ x: 0, y: 0 }` | 面板整体偏移。 |
| `anchor` | `GridCell` | — | 锚点单元格；设置后该单元格中心与按键中心对齐，否则面板显示在按键正上方并水平居中。越界时视为未设置。 |
| `selected` | `GridCell` | — | 初始高亮的单元格。 |
| `moveStep` | `{ horizontal: Float, vertical: Float }` | 单元格尺寸 + `spacing` | 相对位移选择的灵敏度：手指移动多少距离切换一个单元格，值越小越灵敏。 |
| `moveThreshold` | `Float` | `10` | 相对位移选择的最小移动距离；位移未超过时维持初始状态（`selected` 单元格或无高亮）。 |
| `backgroundStyle` | `String` | — | 面板背景样式名。 |
| `selectedBackgroundStyle` | `String` | — | 高亮单元格的背景样式名。 |
| `checkIfOverflowsParentHeight` | `Bool` | `true` | 同上。 |

### 4.8 通知样式节点

被按键的 `notification` 引用。通知命中时，按键会改用该节点上定义的样式与动作。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `notificationType` | 枚举 | — | 必填。`rime` / `keyboardAction` / `returnKeyType` / `preeditChanged`。 |
| `rimeNotificationType` | 枚举 | — | `notificationType: rime` 时必填。`optionChanged` / `schemaChanged`。 |
| `rimeOptionName` | `String` | — | `optionChanged` 时必填，RIME option 名称。 |
| `rimeOptionValue` | `Bool` | — | `optionChanged` 时必填，期望的 option 值。 |
| `rimeSchemaID` | `String` | — | `schemaChanged` 时使用，匹配方案 ID（**推荐**）。 |
| `rimeSchemaName` | `String` | — | `schemaChanged` 时使用，匹配方案名称。 |
| `notificationKeyboardAction` | `KeyboardAction` | — | `notificationType: keyboardAction` 时必填。 |
| `returnKeyType` | `[Int]` | `[]` | `notificationType: returnKeyType` 时必填，系统回车键类型的原始值数组。 |
| `lockedNotificationMatchState` | `Bool` | `false` | 为 `true` 时，一旦命中就锁定样式，后续不匹配也不恢复。 |
| `backgroundStyle` / `foregroundStyle` / `action` / `swipeUpAction` / … | — | — | 命中后使用的样式与动作，写法同按键样式节点。 |

> `notificationType: preeditChanged` 不需要额外参数：存在预编辑文本时命中，为空时恢复。
> 
> 命中后按键完全按该节点渲染，若未定义样式，按键将显示为空白。

### 4.9 动画样式节点

被按键的 `animation` 数组引用。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `animationType` | 枚举 | — | 必填。`scale` / `cartoon` / `physics` / `transform`。 |

#### `animationType: scale`

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `scale` | `Float` | `0.95` | 缩放比例。 |
| `pressDuration` | `Float` | 内置 | 按下动画时长，**单位为毫秒**。 |
| `releaseDuration` | `Float` | 内置 | 抬起动画时长，**单位为毫秒**。 |
| `isAutoReverse` | `Bool` | `false` | 是否自动反向播放（按下缩小、抬起复原）。 |

#### `animationType: cartoon`

仅在按下时触发。图片取自当前键盘配置文件目录的 `resources/`。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `images` | `[String]` | `[]` | 必填。逐帧图片文件名（含后缀）。为空则不播放。 |
| `fps` | `Int` | `30` | 帧率。 |
| `targetScale` | `Float` | — | 图片等比缩小比例。 |
| `center` | `Point` | — | 动画图层中心点，算法同样式节点的 `center`。 |
| `zPosition` | `String` | `above` | `above` 显示在按键之上；`below` 插入到按键区背景之上、按键之下。 |

#### `animationType: physics`

仅在按下时触发。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `images` | `[String]` | — | 必填。参与动画的图片文件名（**含后缀**），取自当前键盘配置文件目录的 `resources/`。 |
| `targetScale` | `Float` | — | 图片等比缩放比例（图片像素 → 点）。 |
| `duration` | `Float` | 内置 | 动画时长，**单位为毫秒**。 |
| `randomImage` | `Bool` | `false` | 是否随机挑选图片。 |
| `startPosition` | `Point` | `{0, 0}` | 起始位置，相对**按键横向中点、纵向最低点**（底边中点）的偏移，单位为**点**，y 负方向朝上。需同时提供 `x`、`y`。 |
| `endPosition` | `Point` | `{0, 0}` | 结束位置，相对**按键横向中点、纵向最高点**（顶边中点）的偏移，其余同上。 |
| `startRandomPosition` | `Point` | 内置 | 起始位置的随机浮动范围，为 `0` 时忽略。 |
| `endRandomPosition` | `Point` | 内置 | 结束位置的随机浮动范围，为 `0` 时忽略。 |
| `useOpacity` | `Bool` | `false` | 是否启用透明度动画。 |
| `startOpacity` | `Float` | `1.0` | 起始透明度。 |
| `endOpacity` | `Float` | `0.8` | 结束透明度。 |
| `useRotation` | `Bool` | `false` | 是否启用旋转动画。 |
| `startAngle` | `Float` | 内置 | 起始角度（度）。 |
| `endAngle` | `Float` | 内置 | 结束角度（度）。 |
| `randomAngle` | `Float` | 内置 | 角度随机浮动范围（度）。 |

#### `animationType: transform`

作用于按键**已有的图层**的通用变换：位移 / 缩放（可指定锚点）/ 旋转 / 透明度。

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `target` | `String` | 整个按键 | 要作用的图层，取值为该按键 `backgroundStyle` / `foregroundStyle` 用到的**样式名**。样式不在该按键中时本次动画跳过。 |
| `trigger` | 枚举 | `press` | `press` 按下 / `release` 抬起 / `both` 两者。开了 `holdUntilRelease` 时此项失效。 |
| `holdUntilRelease` | `Bool` | `false` | 按下播到终点**停住**，抬起再反向播回起点。按住期间维持终点状态。 |
| `duration` | `Float` | `200` | 时长，**毫秒**。 |
| `releaseDuration` | `Float` | 同 `duration` | `holdUntilRelease` 回程的时长，**毫秒**。 |
| `delay` | `Float` | `0` | 起播延迟，**毫秒**。 |
| `timing` | 枚举 \| `[Float]` | `easeInEaseOut` | 枚举：`linear` / `easeIn` / `easeOut` / `easeInEaseOut` / `default`；也可写**四个数**的三次贝塞尔控制点，如 `[0.34, 1.56, 0.64, 1]`（回弹）。 |
| `repeatCount` | `Int` | `1` | 播放次数，最少 1。 |
| `autoreverses` | `Bool` | `false` | 播完后反向播回起点。 |
| `restoreOnFinish` | `Bool` | `true` | 播完恢复原状；`false` 时停在终点。 |
| `anchorPoint` | `Point` | `{0.5, 0.5}` | 缩放 / 旋转的锚点，**单位坐标**。不改动图层自身的 anchorPoint，不影响布局。 |
| `positionUnit` | 枚举 | `point` | 位移的单位：`point` 为点；`layer` / `button` 表示按**目标图层** / **整个按键**的宽高取倍数。 |
| `startPosition` / `endPosition` | `Point` | `{0,0}` | 位移起止值，相对图层原位置，y 负方向朝上。单位由 `positionUnit` 决定。 |
| `startScale` / `endScale` | `Float` \| `Point` | `1` | 缩放起止倍率。写标量为等比；写 `{ x:, y: }` 可分轴缩放。 |
| `useRotation` | `Bool` | `false` | 是否启用旋转。 |
| `startAngle` / `endAngle` | `Float` | `0` | 旋转起止角度（度）。 |
| `useOpacity` | `Bool` | `false` | 是否启用透明度动画。 |
| `startOpacity` / `endOpacity` | `Float` | `1` | 透明度起止值。 |
| `detached` | `Bool` | `false` | 脱离按键播放：复制一份浮到键盘之上，播完删除，原图层期间隐藏。仅对有图片内容的图层有效；`holdUntilRelease` 下不生效。 |

> **`positionUnit` 优先用 `layer` / `button`**。写死点值的位移在改了 `keyboardHeight`
> 或换了目标机型后就偏了；按图层宽高取倍数则自动跟着缩放。
> 例：某元素要上浮「按键高度的 16%」，写 `positionUnit: layer` + `endPosition: { x: 0, y: -0.16 }`。

> **`holdUntilRelease` 与 `detached` 是互斥的两种诉求**：
>
> - 想让效果**跟着手指**（按住就保持，松手才复原）→ `holdUntilRelease: true`。
>   按下与抬起各播一程，两程共用一条动画，抬起那程播完会把常驻动画摘干净。
> - 想让效果**放完自己的一生**（松手也要播完）→ `detached: true`。
>
> 按键抬起时图层会按抬起状态重绘，只写了 `highlightImage` 的图层内容会被清空——
> 「按下弹出个小东西、飘一下再收回」这类动画不脱离就会断在半路。脱离后动画在副本上跑完，
> 既不受按下 / 抬起状态影响，也不会被按键自身的 `scale` 动画连带缩放。
>
> 不设 `target` 时写的是整个按键图层的 `transform`，与 `scale` 动画冲突，
> 两者别挂在同一个按键上。要「整键缩放 + 某层单独动」时，给 `transform` 加 `target`。
>
> **版本要求**：TF >= 442 / 商店 >= 1.6.28。
> 旧版本识别不了这个 `animationType`，会**整条动画静默不生效**（不报错）。

---

**三种能做「动」的动画怎么选**：

| 想要的效果 | 用哪个 |
| --- | --- |
| 整个按键按下时缩一下 | `scale`（最省事） |
| 按键里**某一层**位移 / 缩放 / 旋转，或需要指定缩放锚点 | `transform` |
| 冒出**新的图片**（粒子、飘出来的小动物），可随机位置 / 角度 | `physics` |
| 原地播放一段帧动画 | `cartoon` |

> `physics` 会新建临时图层来播放图片，`transform` 动的是已有图层、不新建图层。
> 想让一张**按键上本来就有的图**动起来，用 `transform`；想凭空冒出一张图，用 `physics`：
>
> ```yaml
> splash:
>   animationType: physics
>   duration: 200
>   images: ["cow.png"]
>   targetScale: 0.4
>   startPosition: { x: 0, y: -39 }   # 底边中点往上 39pt
>   endPosition:   { x: 0, y: 7 }     # 顶边中点往下 7pt
>   useOpacity: true
>   startOpacity: 1.0
>   endOpacity: 0.0
> ```
>
> 缺点是没有缩放曲线——只有一个固定的 `targetScale`，做不出「边飘边变大」。
> 要「边飘边变大」且那张图是按键上已有的图层，用 `transform`（同时给
> `endPosition` 和 `endScale`）；若是凭空冒出来的图，只能改用 `cartoon` 预先生成几帧。

### 4.10 候选字长按菜单 `candidateContextMenu`

根节点下的固定 Key，值为数组。

| Key | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `candidateContextMenu[].name` | `String` | 是 | 菜单项标题。也可使用 `text` 作为等价 Key。 |
| `candidateContextMenu[].text` | `String` | — | `name` 的别名，二者取其一。 |
| `candidateContextMenu[].action` | `KeyboardAction` | 是 | 菜单项动作。 |

## 五、集合视图样式节点

被 `type` 为集合类的 `Cell` 引用。不同集合类型支持的 Key 略有差异。

### 5.1 通用

| Key | 类型 | 默认值 | 适用类型 | 说明 |
| --- | --- | --- | --- | --- |
| `type` | 枚举 | `button` | 全部 | 集合视图类型，见 [4.3](#43-cell-类型type)。 |
| `backgroundStyle` | `String` | — | 全部 | 背景样式名。 |
| `insets` | `Insets` | `0` | 全部 | 内容边距。 |
| `cellStyle` | `String` | — | 符号 / 九键 / 数字类 | 单元格使用的按键样式名。 |
| `dataSource` | `String` | — | `symbols`、`classifiedSymbols`、`subClassifiedSymbols`、`horizontalSymbols` | 数据源名称，指向根节点下的一个数组，见 [5.4](#54-数据源节点)。 |
| `displaySeparatorLine` | `Bool` | 见说明 | 符号 / 九键 / 数字 / 分类类 | 是否显示分隔线。`symbols` 默认 `false`，`numericSymbols`、`subClassifiedSymbols`、`categorySymbols`、`t9Symbols` 默认 `true`。 |
| `separatorLineColor` | `Color` | 系统灰 | 同上 | 分隔线颜色。 |
| `maximumRow` | `Int` | 见说明 | `symbols`(4)、`classifiedSymbols`(5)、`subClassifiedSymbols`、`t9Symbols` | 可视最大行数。 |
| `maximumColumn` | `Int` | 内置 | `subClassifiedSymbols` | 可视最大列数。 |
| `maxColumns` | `Int` | 见说明 | `horizontalCandidates`(7)、`horizontalSymbols`(5)、`verticalCandidates`(5)、`t9HorizontalSymbols`(6) | 可视最大列数。 |
| `maxRows` | `Int` | `4` | `verticalCandidates` | 可视最大行数。 |
| `contentRightToLeft` | `Bool` | `false` | `horizontalSymbols` | 内容从右往左排列。 |
| `separatorColor` | `Color` | — | `verticalCandidates` | 纵向候选区分隔线颜色。 |
| `candidateStyle` | `String` | — | `horizontalCandidates`、`verticalCandidates` | 候选字单元格样式名，见 [5.2](#52-候选字单元格样式candidatestyle-指向的节点)。 |

### 5.2 候选字单元格样式（`candidateStyle` 指向的节点）

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `insets` | `Insets` | `0` | 单元格内边距。 |
| `backgroundCornerRadius` | `Float` | — | 单元格背景圆角。 |
| `highlightBackgroundColor` | `Color` | 透明 | 按下时的背景色。 |
| `preferredBackgroundColor` | `Color` | 透明 | 首选候选字的背景色。 |
| `preferredTextColor` | `Color` | 系统标签色 | 首选候选字的文字颜色。 |
| `preferredCommentColor` | `Color` | 系统标签色 | 首选候选字的注释颜色。 |
| `preferredIndexColor` | `Color` | 系统标签色 | 首选候选字的序号颜色。 |
| `textColor` | `Color` | 系统标签色 | 候选字文字颜色。 |
| `commentColor` | `Color` | 系统标签色 | 候选字注释颜色。 |
| `indexColor` | `Color` | 系统标签色 | 候选字序号颜色。 |
| `textFontSize` | `FontSize` | `14` | 候选字字号。 |
| `textFontWeight` | 枚举 | — | 候选字字重。 |
| `commentFontSize` | `FontSize` | `12` | 注释字号。 |
| `commentFontWeight` | 枚举 | — | 注释字重。 |
| `indexFontSize` | `FontSize` | `12` | 序号字号。 |
| `indexFontWeight` | 枚举 | — | 序号字重。 |

> 若用户在 App 设置中自定义了候选字 / 注释 / 序号字号，App 的设置优先于皮肤中的 `*FontSize`。

### 5.3 二级分类符号单元格附加 Key

`subClassifiedSymbols` 的 `cellStyle` 节点额外支持：

| Key | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `badgeFontSize` | `Int` | 内置 | 角标字号。 |
| `badgeNormalColor` | `Color` | — | 常态角标颜色。 |
| `badgeHighlightColor` | `Color` | — | 选中态角标颜色。 |

### 5.4 数据源节点

`dataSource` 指向根节点下的一个数组，数组元素支持三种写法：

| 写法 | 类型 | 说明 |
| --- | --- | --- |
| 纯字符串 | `String` | 标题与上屏内容相同。 |
| 值对象 | `{ label: String, value: String, styleName: String }` | `label` 为显示文本，`value` 为上屏内容，`styleName` 可选。 |
| 动作对象 | `{ label: String, action: KeyboardAction, styleName: String }` | `label` 为显示文本，点击触发 `action`，`styleName` 可选。 |

> 值对象与动作对象都必须提供 `label`；缺少 `label`，或既没有 `value` 也没有合法 `action` 的元素会被直接丢弃。

### 5.5 约定样式名

以下样式名由代码按固定名称查找，皮肤可选择性提供：

| 样式名 | 说明 |
| --- | --- |
| `predictCloseButton` | 联想候选栏右侧关闭按钮。未提供时使用内置图标。 |

## 六、按键动作（`KeyboardAction`）

所有 `action` 类 Key（`action`、`swipeUpAction`、`notificationKeyboardAction`、数据源的 `action`、
`candidateContextMenu[].action`、`keySound.actions[].action`）都使用同一套结构。

### 6.1 字符串形式

直接写成字符串，可用值：

`backspace`、`command`、`control`、`dictation`、`dismissKeyboard`、`escape`、`function`、
`moveCursorBackward`、`moveCursorForward`、`nextKeyboard`、`option`、`settings`、`space`、
`systemSettings`、`tab`、`shift`、`enter`、`returnPrimaryKeyboard`、`returnLastKeyboard`、
`symbolicKeyboardLockStateToggle`、`none`

### 6.2 对象形式

按下表**从上到下**的顺序匹配，命中即止。

| Key | 类型 | 说明 |
| --- | --- | --- |
| `combine` | `[KeyboardAction]` | 组合动作，依次执行。数组为空或元素全部非法时整体无效。 |
| `character` | `String` | 输入字符。 |
| `symbol` | `String` | 输入符号。 |
| `shortcutCommand` | `String` | 快捷指令，取值见 [6.3](#63-快捷指令取值)。 |
| `shortcut` | `String` | `shortcutCommand` 的别名，`shortcutCommand` 优先。 |
| `floatKeyboardType` | `String` | 显示指定名称的浮动键盘（名称需在 `config.yaml` 中定义）。 |
| `sendKeys` | `String` | 向 RIME 发送按键序列。 |
| `openURL` | `String` | 打开 URL。 |
| `runScript` | `String` | 运行指定脚本。 |
| `openScript` | `String` | 打开指定脚本页面。 |
| `keyboardType` | `String` | 切换键盘类型，值为键盘类型名（含自定义名称）。 |
| `switchRimeSchema` | `String` | 切换到指定 RIME 方案。 |

> 未匹配到任何形式时该动作为 `nil`（按键无动作）；`shortcutCommand` / `shortcut` 的值若不在下表中，则解析为“无动作”。

### 6.3 快捷指令取值

| 值 | 说明 |
| --- | --- |
| `#简繁切换` | 简繁切换 |
| `#中英切换` | 中英切换 |
| `#RimeSwitcher` | 呼出 RIME Switcher |
| `#次选上屏` | 次选上屏 |
| `#三选上屏` | 三选上屏 |
| `#方案切换` | 打开方案切换列表 |
| `#行首` | 光标移到行首 |
| `#行尾` | 光标移到行尾 |
| `#换行` | 换行 |
| `#Enter` | 回车 |
| `#重输` | 清空拼写区 |
| `#左手模式` | 左手单手模式 |
| `#右手模式` | 右手单手模式 |
| `#cut` | 剪切 |
| `#copy` | 复制 |
| `#paste` | 粘贴 |
| `#subCollectionPageUp` | 二级分类符号上一页 |
| `#subCollectionPageDown` | 二级分类符号下一页 |
| `#verticalCandidatesPageUp` | 纵向候选字上一页 |
| `#verticalCandidatesPageDown` | 纵向候选字下一页 |
| `#showPhraseView` | 显示短语视图 |
| `#showPasteboardView` | 显示剪贴板视图 |
| `#toggleScriptView` | 切换脚本视图 |
| `#candidatesBarStateToggle` | 候选栏展开 / 收起 |
| `#rimePreviousPage` | RIME 上一页 |
| `#rimeNextPage` | RIME 下一页 |
| `#toggleEmbeddedInputMode` | 切换内嵌输入模式 |
| `#keyboardPerformance` | 键盘性能面板 |
| `#keyboardMenu` | 切换键盘菜单 |
| `#clearSystemPasteboard` | 清空系统剪贴板 |

## 七、枚举速查

| 枚举 Key | 全部取值 | 默认值 |
| --- | --- | --- |
| `buttonStyleType` | `geometry`、`systemImage`、`assetImage`、`fileImage`、`text` | 无（必填） |
| `type`（Cell 类型） | `button`、`symbols`、`classifiedSymbols`、`subClassifiedSymbols`、`horizontalSymbols`、`horizontalCandidates`、`verticalCandidates`、`numericSymbols`、`categorySymbols`、`t9Symbols`、`t9HorizontalSymbols` | `button` |
| `bounds.alignment` | `leftTop`、`left`、`leftBottom`、`centerTop`、`center`、`centerBottom`、`rightTop`、`right`、`rightBottom` | `center` |
| `contentMode` | `scaleToFill`、`scaleAspectFit`、`scaleAspectFill`、`center` | `systemImage` / `assetImage` 为 `center`；`fileImage` 为 `scaleToFill` |
| `colorGradientType` | `axial`（线性）、`conic`（锥形）、`radial`（辐射） | `axial` |
| `fontWeight` | `ultraLight`、`thin`、`light`、`regular`、`medium`、`semibold`、`bold`、`heavy`、`black` | 系统默认 |
| `notificationType` | `rime`、`keyboardAction`、`returnKeyType`、`preeditChanged` | 无（必填） |
| `rimeNotificationType` | `optionChanged`、`schemaChanged` | 无 |
| `animationType` | `scale`、`cartoon`、`physics` | 无（必填） |
| `zPosition`（cartoon 动画） | `above`、`below` | `above` |
| `conditionKey` | `$symbolicKeyboardLockState`、`$returnKeyType`、`rime$<optionName>` | 无（必填） |
| `text` 特殊变量 | `$rimePreedit`、`$rimeCandidate`、`$rimeCandidateComment`、`$rimeSchemaName`、`$returnKeyType` | 无 |
| 键盘类型名 | `alphabetic`、`pinyin`、`emojis`、`images`、`numeric`、`numberPad`、`symbolic`、自定义名称 | 无 |

> **`text` 的两个换行写法**
>
> `text` 的值为 `"\n"` 时显示为 `\n`，为制表符时显示为 `\t`；其余文本会去除首尾空白字符。


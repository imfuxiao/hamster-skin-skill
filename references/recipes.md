# 常用配方

可直接复制修改的 YAML 片段。所有片段都遵循 `keys.md` 中的类型约定。

## 背景样式

### 纯色圆角键帽（最常用）

```yaml
letterButtonBackgroundStyle:
  buttonStyleType: geometry
  insets: { top: 4, left: 3, bottom: 4, right: 3 }
  cornerRadius: 8.5
  normalColor: "#FFFFFF"
  highlightColor: "#E6E6E6"
  normalLowerEdgeColor: "#898A8D"      # 键帽底部的立体边缘
  highlightLowerEdgeColor: "#898A8D"
```

### 渐变背景

`normalColor` 写成数组即为渐变；`colorLocation` 的元素个数必须与颜色数**完全一致**。

```yaml
gradientBackgroundStyle:
  buttonStyleType: geometry
  cornerRadius: 10
  normalColor: ["#9BAFD9", "#103783"]
  highlightColor: ["#432371", "#FAAE7B"]
  colorLocation: [0, 1]
  colorStartPoint: { x: 0.5, y: 0 }
  colorEndPoint: { x: 0.5, y: 1 }
  colorGradientType: axial            # axial 线性 / conic 锥形 / radial 辐射
```

### 带阴影

阴影只有在设置了 `normalShadowColor` / `highlightShadowColor` 后才生效。

```yaml
shadowBackgroundStyle:
  buttonStyleType: geometry
  cornerRadius: 8
  normalColor: "#FFFFFF"
  highlightColor: "#EEEEEE"
  normalShadowColor: "#00000040"
  shadowOpacity: 0.8
  shadowRadius: 3
  shadowOffset: { x: 0, y: 3 }
```

### 描边

`borderSize` 与边框颜色必须**同时**设置。

```yaml
borderBackgroundStyle:
  buttonStyleType: geometry
  cornerRadius: 8
  normalColor: "#00000000"            # 全透明填充
  borderSize: 2
  normalBorderColor: "#F5D7A1"
  highlightBorderColor: "#FFFFFF"
```

## 前景样式

### 文本

```yaml
letterForegroundStyle:
  buttonStyleType: text
  text: q
  fontSize: 22.5                      # 也可写 '1.2em'，相对系统默认字号
  fontWeight: regular
  normalColor: "#000000"
  highlightColor: "#000000"
```

### 图标（SF Symbols）

```yaml
backspaceForegroundStyle:
  buttonStyleType: systemImage
  systemImageName: delete.left
  highlightSystemImageName: delete.left.fill    # 可选，不写则沿用上面那个
  fontSize: 18
  fontWeight: regular
  normalColor: "#000000"
  highlightColor: "#000000"
```

### 皮肤图片

图片放在与键盘配置文件同级的 `resources/` 下，一张 png 可以切出多个小图。

```yaml
# resources/keys.yaml 中描述了名为 keyNormal / keyPressed 的两个小图
imageBackgroundStyle:
  buttonStyleType: fileImage
  contentMode: scaleToFill
  normalImage:    { file: keys, image: keyNormal }
  highlightImage: { file: keys, image: keyPressed }
```

对应的 `resources/keys.yaml`：

```yaml
keyNormal:
  rect:   { x: 0, y: 0, width: 110, height: 120 }
  insets: { top: 30, bottom: 30, left: 30, right: 30 }   # 拉伸时的保护区域
keyPressed:
  rect:   { x: 0, y: 150, width: 110, height: 120 }
  insets: { top: 30, bottom: 30, left: 30, right: 30 }
```

> **保护区不能比目标还大**：`insets` 是九宫格的四角，`left + right` 必须小于目标宽度、
> `top + bottom` 必须小于目标高度，否则四角互相重叠，真机上会糊成一坨。
>
> 圆角很大的小图（比如 130x130、保护区 64 的圆角块）几乎整张都是角，
> 拿去铺一条 320x66 的长按面板必然出问题。这种情况**改用 `geometry` 复刻**：
> 取那张图中心的实际像素颜色当 `normalColor`，配 `cornerRadius` 和阴影，
> 任何尺寸都不会变形。位图只留给「本来就是插画」的键帽。

> **`contentMode: scaleAspectFit` 的 `rect` 必须收紧到图形的实际包围盒。**
> `scaleAspectFit` 是拿**整片 `rect`** 去适配可视区的，`rect` 里的透明空白也算数。
> 源皮肤的图标切片常常四周留着大片空白（例：`130x130` 的片子里图形只有 `14x39`），
> 照抄这个 `rect`，图形就只剩 `1.7 x 4.8pt` 一条丝——真机上看着就是「图没画出来」。
>
> 做法：用 Pillow 的 `getbbox()` 量出实际包围盒，左右各留 1px 抗锯齿余量，写进 `rect`。
> 常态图与按下态图要**取两者的并集**，否则其中一张会被裁掉一像素。
>
> ```python
> bb = sheet.crop((x, y, x + w, y + h)).getbbox()      # 相对切片的包围盒
> rect = (x + bb[0] - 1, y + bb[1] - 1, bb[2] - bb[0] + 2, bb[3] - bb[1] + 2)
> ```
>
> 收紧后再定尺寸：给一个**方形目标框**，让 `insets` 把可视区收成这个框，
> `scaleAspectFit` 会按各图标自己的纵横比填进去——齿轮（1:1）铺满，
> 扁的 `⌄`（2.5:1）按宽度对齐，竖的 `)`（0.39:1）按高度对齐，一套 `insets` 通吃：
>
> ```python
> lr = (单元格宽 - 目标框) / 2
> tb = (区域高度 - 目标框) / 2      # 工具栏高度用点值，不是 vh 字符串
> ```
>
> `scaleToFill`（`fileImage` 的默认值）不受这条影响——它本来就把整片拉满，
> 键帽、区域背景那些铺满型的图层照旧抄 `SOURCE_RECT` 即可。

## 按键

### 字母键（含大小写与长按气泡）

```yaml
qButton:
  size: { width: 112.5/1125 }
  backgroundStyle: letterButtonBackgroundStyle
  foregroundStyle: qFg
  uppercasedStateForegroundStyle: qUpFg
  hintStyle: qHint
  action: { character: q }
  uppercasedStateAction: { character: Q }
```

### 上划输入第二个字符

```yaml
qButton:
  action: { character: q }
  swipeUpAction: { character: "1" }
  foregroundStyle: qFg
  swipeUpForegroundStyle: qSwipeUpFg     # 划动过程中临时替换前景
```

### 切换键盘类型

```yaml
numericButton:
  action: { keyboardType: numeric }      # alphabetic / pinyin / symbolic / numeric / 自定义名
  foregroundStyle: numericFg
```

### 组合动作

```yaml
comboButton:
  action:
    combine:
      - { character: "（" }
      - { character: "）" }
      - moveCursorBackward
```

### 长按连续触发

```yaml
backspaceButton:
  action: backspace
  repeatAction: backspace                # 不写则长按不会连续删除
```

## 长按符号面板

### 网格版（推荐）

```yaml
aButton:
  hintSymbolsGridStyle: aGridStyle

aGridStyle:
  size: { width: 42, height: 52 }        # 单个格子的尺寸
  spacing: { horizontal: 2, vertical: 2 }
  insets: { top: 7, left: 7, bottom: 7, right: 7 }
  anchor: { row: 0, col: 0 }             # 该格中心与按键中心对齐；行列从 0 开始
  selected: { row: 0, col: 0 }           # 初始高亮格
  offset: { x: 0, y: -60 }               # 整体上移，让面板落在按键正上方
  backgroundStyle: hintPanelBackgroundStyle
  selectedBackgroundStyle: hintSelectedBackgroundStyle
  symbolRows:                            # 二维数组，~ 表示空格子
    - [aGrave, aAcute, aCircumflex]
    - [aTilde, aDiaeresis, ~]

aGrave: { backgroundStyle: hintCellBg, foregroundStyle: aGraveFg, action: { character: à } }
aGraveFg: { buttonStyleType: text, text: à, fontSize: 20, normalColor: "#000000", highlightColor: "#FFFFFF" }

# 高亮块要比格子小一圈：靠 insets 往里收，顶满格子就看不出选中的是哪一个
hintSelectedBackgroundStyle:
  buttonStyleType: geometry
  insets: { top: 4, left: 4, bottom: 4, right: 4 }
  cornerRadius: 9
  normalColor: "#535353"
  highlightColor: "#535353"
```

两个容易翻车的地方：

- **面板会整片伸出屏幕**。不设 `anchor` 时面板在按键正上方水平居中，
  一行 7 个格子就有 300pt 多宽，靠边的键（`a` / `o` / `。`）左右都会溢出。
  按这颗键的中心横坐标 `cx` 算一个锚点列，让面板左边缘落在屏幕内：

  ```
  span    = 格宽 + 水平间距
  面板宽   = 列数 x 格宽 + (列数-1) x 间距 + 左右 insets
  锚点列 c = clamp(floor((cx - 边距 - 左inset - 格宽/2) / span), 0, 列数-1)
  左边缘   = cx - (左inset + c x span + 格宽/2)      # 需落在 [边距, 屏宽-面板宽-边距]
  ```

  每颗键各生成一份 grid 样式，`anchor` 取各自算出的 `c`。
- **面板背景别用保护区过大的九宫格图**，见下一节。

### 单行版

```yaml
aButton:
  hintSymbolsStyle: aSymbolsStyle

aSymbolsStyle:
  size: { width: 1/9, height: 1/5 }
  insets: { top: 6, left: 6, bottom: 6, right: 6 }
  selectedIndex: 0
  backgroundStyle: hintPanelBackgroundStyle
  selectedBackgroundStyle: hintSelectedBackgroundStyle
  symbolStyles: [aGrave, aAcute, aCircumflex]
```

## 条件样式

根据运行时状态切换外观。数组按顺序匹配，命中即止；`backgroundStyle` 只取命中项的第一个样式名。

```yaml
lockButton:
  backgroundStyle:
    - { conditionKey: "$symbolicKeyboardLockState", conditionValue: false, styleName: unlockedBg }
    - { conditionKey: "$symbolicKeyboardLockState", conditionValue: true,  styleName: lockedBg }
  foregroundStyle:
    - { conditionKey: "rime$ascii_mode", conditionValue: true,  styleName: [enFg, enBadgeFg] }
    - { conditionKey: "rime$ascii_mode", conditionValue: false, styleName: zhFg }
```

`conditionKey` 三种写法：`$symbolicKeyboardLockState`、`$returnKeyType`（`conditionValue` 为整数数组）、
`rime$<option 名>`。

## 事件通知

按键订阅通知，命中时整体换用通知节点上定义的样式与动作。

### 跟随回车键类型变色

```yaml
enterButton:
  action: enter
  backgroundStyle: systemBg
  foregroundStyle: enterFg
  notification: [enterKeyTypeNotification]

enterKeyTypeNotification:
  notificationType: returnKeyType
  returnKeyType: [1, 4, 7, 9, 10]        # 命中这些类型时变蓝
  backgroundStyle: accentBg
  foregroundStyle: enterAccentFg
```

### 跟随 RIME 中英状态

```yaml
langButton:
  notification: [asciiModeNotification]

asciiModeNotification:
  notificationType: rime
  rimeNotificationType: optionChanged
  rimeOptionName: ascii_mode
  rimeOptionValue: true
  foregroundStyle: enFg
  action: { shortcut: "#中英切换" }
```

### 跟随输入方案切换

```yaml
schemaNotification:
  notificationType: rime
  rimeNotificationType: schemaChanged
  rimeSchemaID: flypy                    # 推荐用 ID，中文名可能有编码问题
  lockedNotificationMatchState: true     # 命中后锁定，不再因不匹配而恢复
  foregroundStyle: flypyFg
```

### 有预编辑文本时变化

```yaml
spaceButton:
  notification: [preeditNotification]

preeditNotification:
  notificationType: preeditChanged
  foregroundStyle: commitFg
  action: enter
```

## 集合视图

### 横向候选栏 + 展开按钮

```yaml
horizontalCandidatesLayout:
  - HStack:
      subviews:
        - Cell: candidatesCell
        - Cell: expandButton

candidatesCell:
  type: horizontalCandidates
  candidateStyle: candidateCellStyle
  maxColumns: 7
```

### 纵向候选栏 + 底部功能行

展开态覆盖预编辑区以下的全部区域，**别只放一个候选列表**——用户翻页、收起、退格
都得靠这一行按钮。四个动作是约定俗成的：

```yaml
verticalCandidatesLayout:
  - HStack:                              # 不写 size，吃掉剩余高度
      subviews:
        - Cell: verticalCandidatesCell
  - HStack:
      style: verticalLastRowStyle        # 固定高度的功能行
      subviews:
        - Cell: verticalPageUpButton
        - Cell: verticalPageDownButton
        - Cell: verticalReturnButton
        - Cell: verticalBackspaceButton

verticalLastRowStyle: { size: { height: 45 } }

verticalCandidatesCell:
  type: verticalCandidates
  candidateStyle: candidateCellStyle
  maxRows: 5
  maxColumns: 6
  separatorColor: "#C8C9CC"
  insets: { top: 8, left: 8, bottom: 8, right: 8 }

verticalPageUpButton:
  action: { shortcut: "#verticalCandidatesPageUp" }
  backgroundStyle: systemButtonBackgroundStyle
  foregroundStyle: pageUpFg                 # SF Symbol chevron.up
verticalPageDownButton:
  action: { shortcut: "#verticalCandidatesPageDown" }
  backgroundStyle: systemButtonBackgroundStyle
  foregroundStyle: pageDownFg               # chevron.down
verticalReturnButton:
  action: { shortcut: "#candidatesBarStateToggle" }   # 收起候选栏
  backgroundStyle: systemButtonBackgroundStyle
  foregroundStyle: returnFg                 # return
verticalBackspaceButton:
  action: backspace
  repeatAction: backspace
  backgroundStyle: systemButtonBackgroundStyle
  foregroundStyle: backspaceFg              # delete.left
```

键帽与图标**全部从源皮肤里取**，别用 `geometry` 另画、也别用 SF Symbols 或自己打的文字顶替——
这一行的素材源皮肤基本都齐，找不到多半是没找对地方。

```yaml
verticalPageUpButton:
  action: { shortcut: "#verticalCandidatesPageUp" }
  backgroundStyle: verticalKeycapStyle          # 宽键帽，铺满格子
  foregroundStyle: verticalPageUpButtonIcon
verticalPageUpButtonIcon:
  buttonStyleType: fileImage
  contentMode: center                           # ← 关键：原始尺寸居中，不缩放
  normalImage:    { file: sym, image: k2 }
  highlightImage: { file: symax, image: k2 }
verticalKeycapStyle:
  buttonStyleType: fileImage
  normalImage:    { file: anjian123, image: k16 }
  highlightImage: { file: anjian123ax, image: k16 }
```

- **图标一律 `contentMode: center`。** 源皮肤的图标切片本来就是照着按键尺寸画的，
  原样居中画出来就是对的。这时 `rect` **直接用 `.til` 的 `SOURCE_RECT`，不要收紧**——
  切片四周的透明留白会被可视区裁掉，不参与缩放，收紧了反而要另外算 `insets`。
  （收紧 `rect` 那套只在 `scaleAspectFit` 下才需要，见上面的「皮肤图片」。）

  > `contentMode: center` 下 **1 图片像素约合 1/3 点**（3x 设备按图片自身 scale 折算），
  > 所以 110x80 的切片画出来约 37x27pt，正好是一颗键的大小——这也是为什么源切片能原样用。

- **一颗键上要摆多个图标时，用 `center: { x, y }`（可视区域的分数）定位，别用
  `insets` 或 `offset`。** `insets` 是「缩进 + 缩放」，会连尺寸一起改；`offset` 是点值，
  换机型就偏。`center` 是纯比例，天然跨设备：

  ```yaml
  # 退格键：「删除」角标 + 箭头两层，都取自 more.png
  verticalBackspaceButton:
    foregroundStyle: [verticalBackspaceDeleteLabel, verticalBackspaceArrow]
  verticalBackspaceDeleteLabel:
    buttonStyleType: fileImage
    contentMode: center
    center: { x: 0.293, y: 0.5 }      # 角标偏左
    normalImage: { file: more, image: k32 }
  verticalBackspaceArrow:
    buttonStyleType: fileImage
    contentMode: center               # 不写 center 即居中
    normalImage: { file: more, image: k2 }
  ```

  分数怎么算：源皮肤 `[KEY*]` 的 `POS_TYPE` 指向 `gen.ini` 的 `[OFFSET*]`，
  拿到 `POS=(dx,dy)`（**源像素**），换算成 `center.x = 0.5 + dx / 3 / 格子宽`。
  上例的角标 `POS=(-65,0)`，格子宽 104.5pt → `0.5 - 65/3/104.5 = 0.293`。
- **键帽挑源皮肤里的「宽功能键」片**，不要挑字母键。这一行的格子是扁的
  （约 105x48，纵横比 2.2），字母键帽是竖的（106x151，纵横比 0.70），铺进去圆角会被拉成椭圆；
  数字面板的拼合图（百度皮肤是 `anjian123.png`）里有 240x151 的宽键帽，铺进去就自然多了。
  九宫格保护区**救不了**这件事：键帽圆角半径 27~32px，要完整包住得 ~39px 保护区，
  上下加起来 78pt 已超过 48pt 的行高，圆弧下半截照样被压扁，还会挤出两片「翅膀」。
- **图标在哪找**（百度皮肤的常见排布）：

  | 图标 | 拼合图 | 片号 |
  | --- | --- | --- |
  | ∧ 上一页 | `sym.png` / `symax.png` | `IMG2` |
  | ∨ 下一页 | 同上 | `IMG3` |
  | 「返回」 | 同上 | `IMG1`（有的皮肤在 `letter*.png` 里） |
  | ← 删除箭头 | `more.png` / `moreax.png` | `IMG2` |

- **退格：与主键盘上那颗退格键用同一套样式**（键帽片 + 预合成的前景，含「删除」字样与箭头）。
  它比另外三个更方，用 `bounds` 把绘制区锁回原键的宽高比就不会变形：

  ```yaml
  verticalBackspaceButton:
    bounds: { width: 55 }        # 48pt 行高 x (165/143)，165x143 是原键的 viewRect
    backgroundStyle: verticalBackspaceKeycapStyle   # 与主键盘退格键同一片键帽
    foregroundStyle: verticalBackspaceLabel         # 同一片预合成前景
  ```

  这样退格会比另外三个窄一圈——原皮肤本来就是这个比例，看着是对的。

### 符号列表 + 自定义数据源

```yaml
symbolsCell:
  type: symbols
  dataSource: mySymbols                  # 指向根节点下的一个数组
  cellStyle: symbolCellStyle
  maximumRow: 4
  displaySeparatorLine: true
  separatorLineColor: "#C8C9CC"

mySymbols:
  - "，"                                  # 显示与上屏内容相同
  - { label: "…", value: "……" }          # 显示 … 上屏 ……
  - { label: "换行", action: { shortcut: "#换行" } }
```

## 按键动画

```yaml
qButton:
  animation: [pressScale]                # 必须是数组

pressScale:
  animationType: scale
  scale: 0.92
  pressDuration: 60                      # 毫秒
  releaseDuration: 120
  isAutoReverse: true
```

逐帧动画（图片放在 `resources/` 下）：

```yaml
sparkle:
  animationType: cartoon
  images: [s1.png, s2.png, s3.png, s4.png]
  fps: 24
  targetScale: 0.6
  zPosition: above                       # above 盖在按键上 / below 垫在按键下
```

### 只让按键里的某一层动（位移 / 绕锚点缩放 / 旋转）

`transform` 动的是按键**已有的图层**，靠 `target` 指定样式名。
不新建图层、不额外占内存，也是唯一能指定缩放锚点的类型。

```yaml
qButton:
  foregroundStyle: [qFg, qBadgeFg]
  animation: [pressDown, badgeFloat]

# 绕底边缩放，像被压下去
pressDown:
  animationType: transform
  duration: 80
  timing: easeInEaseOut
  anchorPoint: { x: 0.5, y: 1.0 }        # 单位坐标，(0.5,1) = 底边中点
  startScale: 1.0
  endScale: 0.9
  autoreverses: true                     # 缩回去

# 只让角标上浮 + 变大 + 淡出，键帽本身不动
badgeFloat:
  animationType: transform
  target: qBadgeFg                       # ← 指向前景样式名
  duration: 200
  timing: easeOut
  endPosition: { x: 0, y: -9 }
  endScale: 1.2
  useOpacity: true
  startOpacity: 1.0
  endOpacity: 0.0
```

`trigger` 可选 `press`（默认）/ `release` / `both`；
另有 `delay`、`repeatCount`、`restoreOnFinish`（`false` 时停在终点状态）。

> 不带 `target` 的 `transform` 与 `scale` 都会写整个按键的 transform，**不能同时用**。

### 只在按下时出现的图层

`fileImage` 的两个状态是**分别**取的：常态只读 `normalImage`，按下态只读 `highlightImage`，
**不会互相回退**。利用这一点，只写 `highlightImage` 就得到一个「常态不显示、按下才出现」的图层：

```yaml
qButton:
  foregroundStyle: [qFg, qSplashLayer]   # 放最后 = 盖在最上面
  animation: [pressScale, splashFloat]

qSplashLayer:
  buttonStyleType: fileImage
  contentMode: scaleToFill
  highlightImage: { file: splash, image: k1 }   # 没有 normalImage

splashFloat:
  animationType: transform
  target: qSplashLayer
  detached: true                         # 松手后要继续放完，必须脱离
  duration: 200
  timing: linear
  autoreverses: true                     # 升上去再落回来，共 400ms
  positionUnit: layer                    # 位移按图层高度取倍数，不写死点值
  endPosition: { x: 0, y: -0.16 }        # 上浮 16% 的按键高度
  endScale: 1.2
```

`detached` 是这类动画的关键：不脱离的话，手指一抬图层内容就被清空，动画断在半路；
而且按键自身的 `scale` 动画会把它一起缩小。

`positionUnit: layer` 让位移跟着按键尺寸缩放——写死 `-9`（点）在改了 `keyboardHeight`
或换目标机型后就偏了。

### 按住期间保持、松手才复原

想要「按下变形，手指按住就一直保持，松手再弹回」，用 `holdUntilRelease`——
按下与抬起各播一程，不用自己写两条动画：

```yaml
glyphSink:
  animationType: transform
  target: qFg
  holdUntilRelease: true
  duration: 80                           # 按下这一程
  releaseDuration: 120                   # 松手回程，可以更慢一点
  anchorPoint: { x: 0.5, y: 1.0 }
  endScale: 0.9
```

开了 `holdUntilRelease` 之后 `trigger` 与 `detached` 都不再生效（两个状态都要处理）。
整键缩放用内置的 `scale`（`isAutoReverse: false`）即可，行为一样且老版本也支持；
只有需要**指定锚点**或**只动某一层**时才用 `transform` + `holdUntilRelease`。

### 自定义缓动曲线

`timing` 除了五档预设，还能写四个数的三次贝塞尔控制点，做预设表达不了的曲线：

```yaml
bounceIn:
  animationType: transform
  target: qBadgeFg
  duration: 260
  timing: [0.34, 1.56, 0.64, 1]          # 冲过头再回落的回弹感
  endScale: 1.25
```

比 `physics` 好在能同时做位移和缩放；代价是那张图必须**与按键等大**
（`fileImage` 总是铺满可视区），元素要预先摆到画布里的正确位置。

> 反过来说：`fileImage` 只写 `normalImage` 时，**按下会整片变空白**。这是个常见事故。

### 按下时从键帽后面冒出一张图并上浮

`physics` 是三种动画里**唯一能做位移**的。
`startPosition` 以按键**底边中点**为基准，`endPosition` 以**顶边中点**为基准，
单位是点，y 负方向朝上。

```yaml
qButton:
  animation: [pressScale, splash]        # 可以和 scale 叠加

splash:
  animationType: physics
  duration: 200
  images: ["cow.png"]                    # resources/cow.png，注意带后缀
  targetScale: 0.4                       # 图片像素 -> 点 的比例
  startPosition: { x: 0, y: -39 }        # 从键帽偏上的位置开始
  endPosition:   { x: 0, y: 7 }          # 飘到键帽顶上方
  useOpacity: true
  startOpacity: 1.0
  endOpacity: 0.0                        # 边飘边淡出
```

想让它「边飘边变大」做不到——`physics` 只有一个固定的 `targetScale`，
真要变大就改用 `cartoon`，预先生成几帧不同大小的图。

## 按键音

写在 `config.yaml`，音频文件放皮肤根目录的 `sound/` 下。

```yaml
keySound:
  input: tap.wav
  delete: delete.wav
  system: system.wav
  actions:
    - { action: space, url: space.wav }
    - { action: enter, url: enter.wav }
```

## 皮肤字体

```yaml
fontFace:
  - url: MyFont-Regular.ttf              # 放在皮肤根目录的 fonts/ 下
    ranges:
      - { location: 65, length: 26 }     # 只对 A-Z 生效
  - name: PingFang SC                    # 系统字体，name 优先于 url
```

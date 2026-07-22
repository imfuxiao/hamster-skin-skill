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
  size: { width: 1/9, height: 1/5 }      # 单个格子的尺寸
  spacing: { horizontal: 4, vertical: 4 }
  insets: { top: 6, left: 6, bottom: 6, right: 6 }
  offset: { x: 0, y: -6 }
  anchor: { row: 1, col: 0 }             # 该格中心与按键中心对齐；行列从 0 开始
  selected: { row: 1, col: 0 }           # 初始高亮格
  backgroundStyle: hintPanelBackgroundStyle
  selectedBackgroundStyle: hintSelectedBackgroundStyle
  symbolRows:                            # 二维数组，~ 表示空格子
    - [aGrave, aAcute, aCircumflex]
    - [aTilde, aDiaeresis, ~]

aGrave: { backgroundStyle: hintCellBg, foregroundStyle: aGraveFg, action: { character: à } }
aGraveFg: { buttonStyleType: text, text: à, fontSize: 20, normalColor: "#000000", highlightColor: "#FFFFFF" }
```

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

### 纵向候选栏

```yaml
verticalCandidatesCell:
  type: verticalCandidates
  candidateStyle: candidateCellStyle
  maxRows: 4
  maxColumns: 5
  separatorColor: "#C8C9CC"
```

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

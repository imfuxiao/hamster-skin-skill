# 百度手机输入法皮肤格式（转换来源）

整理自《百度手机输入法皮肤文档 V2.11.21》，并补上文档里没有、但实际皮肤在用的部分
（`anim.ini` 按键动画、按键音、暗色模式等）。用于把 `.bdi` / `.bds` 图片皮肤转换成元书 `.cskin`。
**不需要再另外提供那份 PDF。**

百度皮肤是**纯图片皮肤**：所有外观都是「拼合图 + 切片矩形 + 相对偏移」，没有颜色/圆角描述。
转换的核心工作是把这套「小图 + 偏移」翻译成元书的「一个图层铺满一个可视区」。

> 标注 **`[实测]`** 的条目是官方文档没写、或写法与实际皮肤不符、由真实皮肤反推得出的。
> 遇到冲突时**以 `[实测]` 为准**——官方文档年代久远，iOS 端的实现已经偏离。

## 1. 皮肤包结构

后缀名：**`.bdi` = iPhone 版**，`.bds` = 其他触屏平台，`.bdskk` / `.bdsk` = 键盘（非触屏）版。
实际是 zip，解开后：

```
<皮肤>/
├── Info.txt              皮肤元信息
├── demo.png              预览图
├── light/skin/           浅色（SupportDarkMode=1 的皮肤才有 light + dark 两套）[实测]
│   ├── Info.txt
│   ├── port/             竖屏：全部布局 ini
│   ├── land/             横屏：全部布局 ini
│   └── res/              图片、.til 切片、default.css、anim.ini、字体、按键音
└── dark/skin/            深色，结构完全相同
```

老皮肤还可能有 `240/` `320/` `480/` 这类分辨率目录（并非精确像素，而是档位：横屏 400 走 240 档，
横屏 854 走 480 档）。优先级：`根目录 < 根目录 land|port < 分辨率目录 < 分辨率目录 land|port`。

`Info.txt` 字段：

| 字段 | 说明 |
| --- | --- |
| `Title` | 皮肤显示名（缺省用包名） |
| `Name` | 指定的皮肤文件名 |
| `Style` | 风格 |
| `Description` / `Author` | 描述 / 作者 |
| `SupportPlatform` | 适配平台，`S` `W` `I` `A` 四个平台字母的组合 |
| `MinImeCode` | 要求输入法的最低版本 |
| `SkinType` | **`[实测]`** 皮肤类型 |
| `SupportDarkMode` | **`[实测]`** `1` 表示带 `light/` + `dark/` 两套资源 |
| `Abilities` | **`[实测]`** 能力声明，`Animation` 表示带 `res/anim.ini` 按键动画 |
| `SkinFlags` / `VersionCode` | **`[实测]`** 标志位 / 版本号 |

> 文档第 II 部分「键盘皮肤」（`NEWTAB` / `NEWCAND` / `NEWIDCT` / `TEXT_*` / `ICONX` 等段）
> 是给**非触屏**的 `.bdskk` 用的，与 iPhone 皮肤无关，转换时可以整段忽略。

### 文件类型

| 后缀 | 作用 |
| --- | --- |
| `*.png` | 拼合图 |
| `*.til` | 切片定义（哪块矩形是第几张小图） |
| `*.css` | 样式表（样式号 → 颜色 / 字体 / 图片 / 动画 / 按键音） |
| `*.ini` | 键盘布局；`res/anim.ini` 是动画定义 **`[实测]`** |
| `*.cnd` | 候选条布局 |
| `*.pop` | 气泡布局 |
| `*.ttf` | 字体 |
| `*.aiff` / `*.ogg` | 按键音（`.aiff` 给 iOS，`.ogg` 给安卓）**`[实测]`** |

编码规范：文件名一律英文，图片一律 PNG，ini 一律 UTF-8（常带 BOM）。

### 布局 ini 一览

| 文件 | 面板 |
| --- | --- |
| `gen.ini` | **全局默认**：面板尺寸、候选条、偏移表 `[OFFSET*]`、公共段 |
| `py_26.ini` / `py_9.ini` | 拼音 26 键 / 九宫格（T9） |
| `en_26.ini` / `en_26s.ini` | 英文 26 键 小写 / 大写 |
| `en_9.ini` / `en_9s.ini` | 英文九宫格 小写 / 大写 |
| `num_26.ini` / `num_9.ini` | 数字面板 |
| `def_26.ini` / `def_9.ini` | 自定义输入面板 |
| `symbol.ini` / `sel_ch.ini` / `sel_en.ini` | 符号 / 更多候选（中 / 英） |
| `bh.ini` | 笔画 |
| `hw_grid.ini` / `hw_full.ini` | 手写 非全屏 / 全屏 |
| `net.ini` | 网址 / 密码 |
| `tool_*.ini` | 工具栏（26 键的是 `tool_26.ini`） |
| `logo.ini` / `help.ini` | logo 菜单 / 帮助 |

所有 ini / css / til / cnd / pop 都是同一种 `[SECTION]` + `key=value` 格式。

## 2. 布局 ini 的段

### `[PANEL]` 主面板

| 属性 | 说明 |
| --- | --- |
| `SIZE` | `宽,高`——**整套皮肤的设计稿坐标系**，如 `1125,595`。下面所有矩形都在这个坐标系里。**它不是宽高比**，见第 8 节 |
| `BACK_STYLE` | 面板背景样式号 |
| `FORE_STYLE` | 划线效果的颜色与大小 |
| `NO_BLUR` | `0` 模糊输入 / `1` 精确输入 |
| `KEY_NUM` / `TIP_NUM` | 按键数 / 补丁数 |
| `OFFSET_NUM` | 偏移类型个数 |
| `CUSTOM_RECT` | `1` 表示有自定义矩形 |
| `BAR_H` | 底部 bar 高度（wm / v5 平台特有，iPhone 用不到） |
| `SOUND_STYLE` | 面板默认按键音样式号 **`[实测]`** |

### `[KEY*]` 按键（核心）

| 属性 | 说明 |
| --- | --- |
| `VIEW_RECT` | `X,Y,宽,高`——**绘制**矩形 |
| `TOUCH_RECT` | `X,Y,宽,高`——**点击检测**矩形，缺省时同 `VIEW_RECT` |
| `BACK_STYLE` | 背景样式号（一个） |
| `FORE_STYLE` | 前景样式号，**逗号分隔可多个**，按顺序叠加 |
| `POS_TYPE` | 与 `FORE_STYLE` **一一对应**的偏移类型号，指向 `gen.ini` 的 `[OFFSET*]`；无对应值＝居中 |
| `CENTER` | 点击时的字符或功能键 |
| `UP` / `DOWN` / `LEFT` / `RIGHT` | 四个方向划动的字符或功能键 |
| `HOLD` | 长按的字符或功能键 |
| `HOLDSYM` | 长按弹出的字符集，**无分隔符**，如 `E3eēéěè` |
| `SHOW` | 点击时传给内核的键值（九宫格上是数字） |
| `STAT_STYLE` | 特殊状态下换用哪个 `[TIP*]`，写法 `S1_1\|S2_2`（状态_补丁号） |
| `BACK_ANIM_STYLE` | 背景层按下动画的样式号 **`[实测]`**，见第 6 节 |
| `FORE_ANIM_STYLE` | 前景层按下动画样式号，**逗号分隔、与 `FORE_STYLE` 一一对应** **`[实测]`** |
| `SOUND_STYLE` | 该键单独的按键音样式号 **`[实测]`** |

> 只有 `VIEW_RECT` 而没有 `FORE_STYLE` 的键，往往是**跨多键的背景板**
> （例如九宫格左侧符号栏的底板），转换时要按比例切开分给相邻的键，或让它独占一列。

### `[TIP*]` 补丁

被 `[KEY*]` 的 `STAT_STYLE` 引用，表示某个状态下这颗键换个样子/动作。
属性是 `[KEY*]` 的子集：`BACK_STYLE` / `FORE_STYLE` / `CENTER` / `HOLD` / `SHOW`，
外加 **`[实测]`** 的 `POS_TYPE` 与动画属性。`[TIP*]` 自己**没有 `VIEW_RECT`**，
画布尺寸取引用它的那颗键。

典型：shift 键 `STAT_STYLE=S14_1|S4_2|S1_3|S2_4` ——
有输入码（S4）时变成分词键，首字母大写（S1）、大写锁定（S2）各换一张图。

### `[OFFSET*]` 偏移表（**只在 `gen.ini` 里生效**）

```ini
[OFFSET41]
POS=8,15
```

`POS=dx,dy`：前景小图**按自身原始尺寸**摆放，再平移 `(dx, dy)`，y 正方向朝下。

> **`[实测]` 与文档不一致**：官方文档写的是「自身矩阵**左上角**相对目标矩阵**中心点**的偏移量」，
> 但真实皮肤里绝大多数 `POS=0,0`，若按左上角对齐会把图层甩到右下角。
> 实测行为是**小图中心对准按键中心，再平移 `(dx, dy)`**：
>
> ```python
> paste_x = (key_w - img_w) // 2 + dx
> paste_y = (key_h - img_h) // 2 + dy
> ```
>
> `scripts/baidu_extract.py` 按后者实现，产出的贴图与 `demo.png` 逐像素吻合。

### `[LIST]` 列表区（九宫格左侧的符号栏等）

| 属性 | 说明 |
| --- | --- |
| `BACK_STYLE` | 列表**外框**背景样式 |
| `CELL_STYLE` | 单元格样式 |
| `FORE_STYLE` | 列表内文字样式 |
| `CELL_SIZE` | `宽,高`；列表整体尺寸由它 × `LIST_NUM` 再加 `PADDING` 算出 |
| `POS` | 列表起始位置 `X,Y` |
| `LIST_NUM` | 显示几格 |
| `LIST_ORDER` | `0` 竖排 `1` 横排 |
| `PADDING` | `左,上,右,下` |
| `NAMES` / `VALUES` | 半角空格分隔的显示文本 / 对应的上屏内容或功能键 |
| `TYPE` | `0` 面板内常显 `1` 面板内有项才显 `2` 面板上方常显 `3` 面板上方有项才显 |
| `SCROLL_STYLE` | 滚动条混合色 |
| `SCROLL_SIDE` | 滚动条位置，`0` 向内（默认）`1` 向外 |

### 其余段

| 段 | 说明 |
| --- | --- |
| `[INPUT]` | 输入框：`BACK_STYLE` / `FORE_STYLE` |
| `[SCAND]` | 拼写码显示区：`BACK_STYLE` / `FORE_STYLE` / `INPUT_STYLE` / `SCAND_STYLE` / `PADDING` |
| `[CAND]` | 候选条：`VIEW_RECT` / `LAYOUT_NAME`（指向 `.cnd`）/ `TYPE` |
| `[HINT]` | 气泡：`LAYOUT_NAME`（指向 `.pop`）/ `TYPE`（`0` 跟随按键 `1` 置顶） |
| `[MORE]` | 更多候选：`GRID=行,列` / `LAYOUT_NAME` / `SYM_LAYOUT` / `CELL_STYLE` / `FORE_STYLE` / `HLINE_STYLE` / `VLINE_STYLE` / `LOCK_STYLE` |
| `[LOGO]` `[EMOJI]` | `LAYOUT_NAME` |

`[CAND] TYPE` 全部取值：

| 值 | 含义 |
| --- | --- |
| `0` | 处于面板内，靠划动选择候选字（划选皮肤） |
| `1` | 处于面板内 |
| `2` | 固定于面板上方 |
| `3` | 处于面板内，常驻显示 |
| `4` | 处于面板上方，常驻显示 |

## 3. `.til` 切片文件

```ini
[GLOBAL]
USE_ALPHA=1          ; 0 不透明 1 半透明 2 全透明
TILE_NUM=35

[IMG1]
SOURCE_RECT=0,0,106,151      ; 小图在大图中的 X,Y,W,H
INNER_RECT=0,0,106,151       ; 九宫格拉伸的内框（与 SOURCE_RECT 同一坐标系，绝对坐标）
SCALE=1,1,1,1,1              ; 中上,左中,中部,右中,中下  0 平铺 1 拉伸
TYPE=0                       ; 0 普通图片 1 父图片 2 子图片
COMPLEX=1,3,5,8              ; 复合图片时参与合成的切片序号
POS=0,0                      ; 子图片相对父图片的位置
```

- 没有 `INNER_RECT`，或它的 W/H 为 0 → **不拉伸，居中绘制**到目标矩形。
- `INNER_RECT` 与 `SOURCE_RECT` 完全一致 → **整张图直接拉伸**填满目标矩形（最常见）。
- 其余情况 → 九宫格拉伸，`INNER_RECT` 之外的边框不缩放。
- `TYPE` / `COMPLEX` / `POS` 用于复合图片，罕见。

> `.til` 与元书 `resources/<图片名>.yaml` 几乎一一对应：
> `SOURCE_RECT` → `rect`，`INNER_RECT` 换算成四边边距 → `insets`。
>
> **但图标类切片不能照抄 `SOURCE_RECT`**：它常常四周留着大片透明空白
> （`cand.png` 里 `130x130` 的片子，图形只占中间 `14x39`）。铺满型图层用
> `scaleToFill` 无所谓，可**工具栏 / 候选栏那几个 `scaleAspectFit` 的图标**会被整片空白
> 一起缩进去，真机上只剩一条一两个点宽的丝，看着就是「图没画出来」。
> 这类切片要按实际像素包围盒把 `rect` 收紧，做法见 `recipes.md` 的「皮肤图片」。

## 4. `.css` 样式表

```ini
[GLOBAL]
STYLE_NUM=2000
FOR=480                  ; 针对哪档分辨率

[STYLE1103]
NM_IMG=bj,3              ; 普通态：bj.png 的第 3 张切片
HL_IMG=bj,3              ; 高亮（按下）态
INFO=fhbj                ; 作者注释，无功能

[STYLE1]
FONT_SIZE=54             ; 字号也在设计稿坐标系里
FONT_WEIGHT=500
FONT_CLEARTYPE=1         ; 0 关闭 1 开启平滑字体
FONT_NAME=son.ttf        ; 优先搜索皮肤自带字体
NM_COLOR=D9DAFF          ; RRGGBB 或 AARRGGBB（注意 alpha 在前，与元书相反）
HL_COLOR=AAA6FF
BORDER_COLOR=000000
BORDER_SIZE=1
SHOW=，                   ; [实测] 该样式直接画一个固定字符

[STYLE800]
PRESS_ANIM=1                 ; [实测] 指向 res/anim.ini 的 [ANIM1]

[STYLE1000]
PRESS_SOUND_PATH=a_aj.aiff   ; [实测] 按键音文件
```

- 按下态的拼合图通常是同名加 `ax` 后缀：`anjian26` / `anjian26ax`、`letter1` / `letter1ax`。
- **只写 `HL_IMG`、不写 `NM_IMG` 的样式**是「按下才出现」的图层（水印、角标、
  从键帽后面冒出来的小动物）。普通态**不要**回退去画 `NM_IMG`，否则常态就多了一层。
  这类图层往往配着 `FORE_ANIM_STYLE`，应该做成元书的动画，见第 6 节。

## 5. `.cnd`（候选条）与 `.pop`（气泡）

`.cnd` 分四层绘制：背景层 → 图标层 → 单元格背景层 → 文本层（后两层有候选字时才出现）。
建议把 `PERSIST=3` 的图标和背景层一起预先合成到一张缓存图里。

| 段 | 属性 |
| --- | --- |
| `[TAB]` | `BACK_STYLE` / `FORE_STYLE` / `CELL_STYLE` / `PADDING=左,上,右,下` / `CELL_W` 字间隔 |
| `[CAND]` | 同 `[TAB]`，另加 `FIRST_GAP`（首选字额外间隔）/ `FIRST_FORE` / `FIRST_BACK`（首选字前景 / 背景样式，iPhone 专用）/ `ICON_NUM` / `MORE_W`（「更多」按钮宽，`0` 为不要） |
| `[SWITCH]` | 切换键盘的容器：`NML_BACK_STYLE` / `SEL_BACK_STYLE` / `NML_FONT_STYLE` / `SEL_FONT_STYLE` / `PADDING` |
| `[ICON*]` | `BACK_STYLE` / `FORE_STYLE` / `SIZE=宽,高` / `POS`（图标**左上点**相对锚点的偏移）/ `KEY`（按下执行的功能键）/ `ANCHOR_TYPE` / `PERSIST` |

`ANCHOR_TYPE` 取 1–9，对应矩形的九个点：`1` 左上 `2` 中上 `3` 右上 `4` 左中 `5` 中间
`6` 右中 `7` 左下 `8` 中下 `9` 右下。
`PERSIST`：`1` 无候选字时显示（推荐默认）`2` 有候选字时显示 `3` 都显示 `0` 都不显示。

### `.cnd` 的 `[ICON*]` 搬到元书的哪里

**按 `KEY=` 认图标，不要按图标画的是什么去猜。** 同一张 `.cnd` 里常有两三个长得几乎一样的
「⌄」，靠外观分不出谁是谁；`KEY=` 才是唯一可靠的判据。

| `[ICON*]` 的 `KEY` | 含义 | 元书放哪 | 动作 |
| --- | --- | --- | --- |
| `F31` | logo / 菜单 | `toolbarLayout` 最左 | `{ shortcut: "#keyboardMenu" }` |
| `F8` | 隐藏面板 | `toolbarLayout` 最右 | `dismissKeyboard` |
| **`F9`** | **查看更多候选字**（通常 `PERSIST=2`，有候选字才显示） | **`horizontalCandidatesLayout` 末尾的展开键** | `{ shortcut: "#candidatesBarStateToggle" }` |
| `F14` | 面板切换容器 | 多半没有 `FORE_STYLE`，是块透明热区 —— 丢弃 |  |

> **不要拿元书的语义习惯去替换源皮肤的图标。**
> 元书的展开键是「向下展开候选面板」，直觉上想配一个 `⌄`；但源皮肤给 `F9` 配的往往是
> 右向的 `)` / `›`（百度的「更多 →」是横向展开）。**照搬 `F9` 那一片**——
> 用户要的是原皮肤那个图标，换成自认为更贴切的另一片就是错的。
> 真觉得不合适，做完先问，别直接换。
>
> `[ICON*]` 带 `STAT_STYLE` 时会在某些状态下换片（例：`F9` 在联想态换成 `F8` 的 `⌄`），
> 元书没有对应机制，**只取常态那一片**。

`.pop` 的段：

| 段 | 属性 |
| --- | --- |
| `[GLOBAL]` | `ICON_NUM` |
| `[HINT]` | 普通气泡：`BACK_ICON` / `ARROW_ICON` |
| `[BAR]` | 长按后的条状气泡：`BACK_ICON` / `ARROW_ICON` / `CELL_STYLE`（选中格的样式） |
| `[CROSS]` | 十字长按：`UP_ICON` / `DOWN_ICON` / `LEFT_ICON` / `RIGHTT_ICON`（文档就是三个 T）/ `CENTER_ICON` |
| `[DRAW]` | 拖拉气泡（仅 iPhone）：文档写 `DRAW_UP_ICON` / `DRAW_DN_ICON` / `DRAW_LT_ICON` / `DRAW_RT_ICON`，**`[实测]` 实际皮肤里写的是 `ICON_UP` / `ICON_DN` / `ICON_LT` / `ICON_RT`**，两种都要认 |
| `[ICON*]` | `BACK_STYLE` / `FORE_STYLE` / `SIZE` / `POS` / `PADDING=左,上,右,下` |

## 6. `res/anim.ini` 按键动画 **`[实测]`**

官方文档没有这一节。`Info.txt` 里出现 `Abilities=Animation` 就说明有。
引用链：`[KEY*]` 的 `BACK_ANIM_STYLE` / `FORE_ANIM_STYLE` → `.css` 的
`[STYLE*] PRESS_ANIM=<n>` → `res/anim.ini` 的 `[ANIM<n>]`。

```ini
[GLOBAL]
ANIM_NUM=800

[ANIM1]
TYPE=4               ; 2=位移  4=缩放
REPEAT_CNT=1
REPEAT_MODE=1
DURATION=80          ; 毫秒
DELAY=0
REMOVE=1             ; 1=播完后移除，回到常态
INTPOL=2             ; 插值：0 线性 2 缓动
FROM=100,100         ; TYPE=4 时是百分比；TYPE=2 时是位移量（设计单位）
TO=85,85
PIVOT=50,40          ; 缩放锚点，百分比，50,50 为中心；缺省即中心

[ANIM31]             ; 组合动画：把 BUILD_LIST 里的几条一起播
BUILD_NUM=2
BUILD_LIST=32,33
BUILD_METHOD=0
[ANIM32]
TYPE=2
DURATION=200
FROM=0,0
TO=0,-23             ; 向上位移 23 设计单位
[ANIM33]
TYPE=4
DURATION=200
REMOVE=1
FROM=100,100
TO=120,120           ; 同时放大到 120%
```

### 映射到元书

| 百度 | 元书 |
| --- | --- |
| `BACK_ANIM_STYLE` → `TYPE=4`（键帽整体缩放，无 `PIVOT`） | `animationType: scale`，`scale = TO/100`，`pressDuration` / `releaseDuration` = `DURATION`，`REMOVE=1` → `isAutoReverse: true` |
| `FORE_ANIM_STYLE` 里的任意一层（**该层在元书里也是一个独立图层**） | `animationType: transform` + `target: <该层的样式名>`，`TYPE=2` 写进 `startPosition` / `endPosition`，`TYPE=4` 写进 `startScale` / `endScale` |
| `PIVOT=px,py`（缩放锚点，百分比） | `transform` 的 `anchorPoint: { x: px/100, y: py/100 }` |
| `DURATION` / `DELAY` / `INTPOL` / `REPEAT_CNT` / `REMOVE` | `transform` 的 `duration` / `delay` / `timing`（`0`→`linear`，`2`→`easeInEaseOut`）/ `repeatCount` / `restoreOnFinish` |
| `TYPE=2` + `TYPE=4` 的 `BUILD` 组合 | `transform` 一条就够：位移与缩放同时给起止值 |
| 那一层在元书里**不是独立图层**（被预合成进 `fg_*` 了） | 只能用 `physics` 另起一张贴图；它没有缩放曲线，`TYPE=4` 的放大取首尾中值固定进 `targetScale` |

> `transform` 需 **TF >= 442 / 商店 >= 1.6.28**；旧版本识别不了会**整条动画静默失效**
> （那一层会静止显示，不动也不消失）。要兼容旧版就退回 `physics`。
> 键帽整体缩放用 `scale` 即可，老版本也支持。

**怎么选**：能保住独立图层就用 `transform`（位移、缩放锚点、延迟、重复都能还原）；
只有当那一层被 `baidu_extract.py` 预合成掉、元书里已经没有对应图层时，才退回 `physics`。

**关键**：带位移动画的那一层（通常是只有 `HL_IMG` 的「按下才冒出来」的贴图）
**不能烘进 `fg_*ax` 的静态贴图**，否则会出现两份——一份不动的、一份在动的。
`baidu_extract.py` 会自动把这类图层从合成里剔除，并同时导出两种形态，
参数写进 `<布局>.json` 的 `splashAnimations`：

| 产物 | 给谁用 |
| --- | --- |
| `anim_<拼合图>_<序号>.png` 原始切片 | `physics` 的 `images` |
| `splash_<拼合图>_<序号>_<宽>x<高>.png` **与按键等大**的整层贴图（配同名 `.yaml`） | `transform` 的 `target` 图层 |

**优先用 `transform`**，它能同时做位移和缩放（`physics` 只有一个固定的 `targetScale`，
做不出「边飘边变大」）。写法：把整层贴图做成一个**只有 `highlightImage`** 的前景样式
（常态不显示、按下才出现，与原皮肤一致），放在 `foregroundStyle` 数组**最后**（盖在最上面），
再挂一条 `transform` 指向它：

```yaml
qButton:
  foregroundStyle: [qFg, splashLayer]
  animation: [pressScale, splashFloat]

splashLayer:
  buttonStyleType: fileImage
  contentMode: scaleToFill
  highlightImage: { file: splash_slj_2_110x143, image: k1 }   # 没有 normalImage

splashFloat:
  animationType: transform
  target: splashLayer
  duration: 200                       # ← DURATION
  anchorPoint: { x: 0.5, y: 0.2867 }  # ← json 的 anchorPoint，元素中心
  startPosition: { x: 0, y: 0.0 }     # ← -layerShift x unitY
  endPosition:   { x: 0, y: -8.7 }    # ← (-layerShift + translate.y) x unitY
  startScale: 1.0
  endScale: 1.2                       # ← scaleTo
  useOpacity: true
  endOpacity: 0.0
  restoreOnFinish: false              # 停在透明状态，别播完又闪回来
```

json 里的 `layerShift` 是「为了不裁掉元素（画布只有按键那么大）整层下移了多少设计单位」，
动画起点减掉它就回到原位。`anchorPoint` 已经是算好的单位坐标，直接抄。

`physics` 的坐标：`startPosition` 以**按键底边中点**为基准，`endPosition` 以**按键顶边中点**为基准，
单位是点，y 负方向朝上。把百度的「贴图中心距按键顶边 c 点、位移 d 点」换算过去：

```
startPosition.y = c - 按键高度
endPosition.y   = c + d          （d 为负数时向上）
```

`targetScale` 是「图片像素 → 点」的比例：切片边长（像素）与设计单位 1:1，
所以 `targetScale = 竖直方向每设计单位的点数`（组合里还有放大动画时再乘个中值系数）。

按键音同理：`[STYLE*] PRESS_SOUND_PATH=a_aj.aiff` → 元书 `config.yaml` 的 `keySound`，
`.aiff` 直接搬进皮肤的 `sound/`（`.ogg` 那份是给安卓的，不要）。

## 7. 功能键 `F*` 与状态 `S*`

| | | | |
| --- | --- | --- | --- |
| F1 切换到符号面板 | F3 切换拇指(九宫格)、26 键 | F4 返回 | F5 切换到软键盘 |
| F6 切换数字面板 | F7 启动表情面板 | F8 隐藏面板 | F9 查看更多候选字 |
| F10 切换小写／首字母大写 | F11 切换小写／大写锁定 | F12 网络面板 | F13 一键换皮肤 |
| F14 面板切换容器 | F15 切到中文 | F16 切到英文 | F21 菜单 |
| F22 候选字上翻 | F23 候选字下翻 | F24 中文输入方式菜单 | F25 切换字母／联想 |
| F26 候选字单字/全部 | F27 锁定符号面板 | F28 修改英文排序 | F29 候选条上翻页 |
| F30 候选条下翻页 | F31 logo 菜单 | **F36 退格** | F37 删除 |
| **F38 空格** | **F39 回车** | F40 清除输入码 | F41 Tab |
| F42 Home | F43 End | F44 剪切 | F45 复制 |
| F46 粘贴 | F47 全选 | F48 清空文本 | F49 上箭头 |
| F50 下箭头 | F51 左箭头 | F52 右箭头 | F53 手写区 |
| F54 结束联想 | F55 候选字区域 | F61 启动选字模式 | F62 切换其他输入法(地球) |
| F63 输入法选择菜单 | F64 右上角 x／ok | F65 Win | F66 恢复 |
| F67 撤销 | F68 应用1(搜索) | F69 应用2(短信) | F70 应用3(邮件) |

> F10 与 F11 的区别：F10 是「小写 ↔ 首字母大写」，F11 是「小写 ↔ 大写锁定」。
>
> **`[实测]`** 新皮肤里还会出现 `F72` `F75` `F76` `F77` `F84` 等文档里没有的码，
> 都是后来加的功能。查不到含义时**直接丢弃**，不要猜——猜错会让按键行为出乎意料。

状态：`S1` 英文首字母大写｜`S2` 英文锁定大写｜`S3` 英文联想｜`S4` **有输入码**｜
`S5` 更多候选单字态｜`S6` 符号面板锁定｜`S7` 翻页面板处于页顶｜`S8` 处于页底｜
`S9` 联想状态｜`S10` 搜索框｜`S11` 浏览地址｜`S12` 有下一个输入框｜`S13` 表单提交。
**`[实测]`** 同样存在 `S14` `S30` 这类文档外的状态，查不到就跳过那个 `[TIP*]`。

其他键值约定：

- **笔画**：横 `B1` 竖 `B2` 撇 `B3` 点 `B4` 折 `B5` 通配 `B6`。
- **`Z+<文件名>`**：切换到该名字的自定义面板（拼上 `.ini`），如 `Z+tool_26`。

## 8. 转换到元书的做法

### 整体思路

百度：**一个键 = 一张背景图 + N 张按偏移摆放的前景小图**。
元书：**一个键 = 一个背景图层 + N 个铺满可视区的前景图层**，没有「按原始尺寸 + 偏移」这种摆法。

所以：**背景图原样复用**（只把 `.til` 翻成 `resources/*.yaml`），
**前景按 `[OFFSET*]` 预合成**成与按键等大的贴图，再打包成新的拼合图。
`scripts/baidu_extract.py` 就是干这件事的，直接用它，不要手算偏移。

### 键盘高度

`[PANEL] SIZE=1125,595` **就是面板的宽高比**——拿真机录屏逐帧量过：
在 428pt 宽的设备上，百度把面板画成 428 x 226pt，`226/428 = 0.528 = 595/1125`，
水平与竖直每设计单位都是 1.139px，缩放是**等比**的。

```
面板高(点) = 屏幕宽(点) x SIZE.h / SIZE.w
每设计单位 = 屏幕宽 / SIZE.w        （水平竖直相同）
```

于是：390pt 宽 -> 206pt，428pt 宽 -> 226pt。

**但元书的 `keyboardHeight` 是固定点值**（官方皮肤 iPhone 竖屏写死 216，
与 iOS 系统键盘一致，不随屏宽变化），没有「按屏宽取比例」的写法。
所以只能挑一个目标机型把值写死：

| 目标屏宽 | 机型举例 | `keyboardHeight` |
| --- | --- | --- |
| 390pt | iPhone 13 / 14 / 15 | 206 |
| 393pt | iPhone 15 Pro / 16 | 208 |
| 428pt | iPhone 12–14 Plus / Pro Max | 226 |
| 430pt | iPhone 15 / 16 Pro Max | 227 |

**其余用点作单位的值（`insets`、字号、气泡尺寸、动画位移…）必须按同一个屏宽换算**，
否则会出现「高度按 428 算、内边距按 390 算」的错配。

> **别用「键帽位图不变形」反推行高**。键帽切片 106x151 被拉进 110x143 的
> `VIEW_RECT`，百度本来就把它压扁了；照「不变形」反推会得到偏高的面板。
> 这条弯路我走过——真机录屏一量就露馅。

### 区域与尺寸

| 百度 | 元书 |
| --- | --- |
| `[PANEL] SIZE=W,H` | 设计稿坐标系。把所有 `VIEW_RECT` 写成 `size: { width: <值>/W }` 的分数 |
| `[SCAND]` 背景 | `preeditStyle` |
| `[CAND]` / `tool_*.ini` 区域 | `toolbarStyle` + `horizontalCandidatesStyle`（两者 frame 相同） |
| `[PANEL]` 背景 | `keyboardStyle` |
| `TOUCH_RECT` 比 `VIEW_RECT` 大 | `size` 用 `TOUCH_RECT` 的宽，`bounds` 用 `VIEW_RECT` 的宽 + `alignment` |
| `KEY_NUM` 个 `[KEY*]` | 按 `VIEW_RECT` 的 y 分行 → 若干 `HStack`；跨行的键改用 `VStack` 列切分 |
| `[LIST]` | `type: symbols` + `dataSource`（照抄 `NAMES` / `VALUES`）+ `cellStyle` |

面板背景常被切成三条（预编辑 / 候选条 / 按键区），分别接
`preeditStyle` / `toolbarStyle` / `keyboardStyle` 的 `backgroundStyle`，
三者高度按切片高度的比例分配。

### 跨行 / 跨列的键

九宫格的回车常跨两行、左侧符号栏跨三行，一行一个 `HStack` 排不下。
改成**根数组放若干 `VStack`（列）**，列内再放 `Cell` 或 `HStack`：

```yaml
keyboardLayout:
  - VStack: { style: colLeft,  subviews: [ { Cell: symbolList }, { Cell: symbolicKey } ] }
  - VStack: { style: colMid,   subviews: [ { HStack: { subviews: [ ... ] } }, ... ] }
  - VStack: { style: colRight, subviews: [ { Cell: backspace }, { Cell: clear }, { Cell: enter } ] }

colLeft:  { size: { width: 174/1098 } }
colMid:   { size: { width: 750/1098 } }
colRight: { size: { width: 174/1098 } }
```

`VStack` 里的 `Cell` 分**高度**，`VStack` 里的 `HStack` 也自上而下分高度、各自占满列宽。
这时候左右留白改用 `keyboardStyle.insets`（分母也随之变成「去掉留白后的宽度」），
比给每一列写 `bounds` 省事。

### 动作映射

| 百度 | 元书 |
| --- | --- |
| `CENTER=<字母>` | `action: { character: x }` |
| `CENTER=<标点>` | `action: { symbol: "，" }`（`symbol` 直接上屏；`character` 会喂给 RIME） |
| `CENTER=F36` | `action: backspace`（另加 `repeatAction: backspace`） |
| `CENTER=F38` / `F39` | `action: space` / `enter` |
| `CENTER=F1` / `F6` / `F7` | `{ keyboardType: symbolic }` / `{ keyboardType: numeric }` / `{ keyboardType: emojis }` |
| `CENTER=F11` | `action: shift` |
| `CENTER=F15` / `F16` | `action: { shortcut: "#中英切换" }` |
| `CENTER=F40` | `action: { shortcut: "#重输" }` |
| `CENTER=F41` | `action: tab` |
| `CENTER=F42` / `F43` | `{ shortcut: "#行首" }` / `{ shortcut: "#行尾" }` |
| `CENTER=F44/45/46` | `#cut` / `#copy` / `#paste` |
| `CENTER=F51/F52` | `moveCursorBackward` / `moveCursorForward` |
| `CENTER=F9` | `{ shortcut: "#candidatesBarStateToggle" }`（多半出现在 `.cnd` 的 `[ICON*]` 里，见第 5 节） |
| `CENTER=F62` | `nextKeyboard` |
| `CENTER=F3` | 26 键 ↔ 九宫格：在 `config.yaml` 加自定义键盘类型，`action: { keyboardType: <名字> }` |
| `UP=<符号>` | `swipeUpAction: { symbol: "…" }`（**别用 `character`**，否则会喂给 RIME） |
| `DOWN=` | `swipeDownAction` |
| **`LEFT=` / `RIGHT=`** | **没有对应项**——元书只识别上下划动，左右划的内容只能丢弃或挪到长按面板 |
| **`HOLD=`** | **没有对应项**——元书的长按只有 `repeatAction`（连续触发）与长按符号面板。原皮肤长按呼出的表情 / 地球，通常挪到该键的上划 |
| `HOLDSYM=…` | `hintSymbolsGridStyle`，把字符串逐字拆成一行网格 |
| `[HINT]` 短按气泡 | `hintStyle`，背景用 `.pop` 里 `[HINT] BACK_ICON` 指向的那张图 |
| `[BAR]` 长按条 | `hintSymbolsGridStyle` 的 `backgroundStyle` + `selectedBackgroundStyle`（后者取 `CELL_STYLE`） |
| `STAT_STYLE` 里的 `S1` / `S2` | `uppercasedStateForegroundStyle` / `capsLockedStateForegroundStyle` |
| `STAT_STYLE` 里的 `S4`（有输入码） | `notification` + `notificationType: preeditChanged`（通知节点里**必须**同时写 `backgroundStyle`，否则命中后按键变空白） |
| `Z+<面板名>` | 自定义键盘类型 + `action: { keyboardType: <名字> }` |

九宫格 2–9 用 `action: { character: "2" }`（数字喂给 RIME 的九宫格方案），
左上角那颗 `CENTER='` 是分词键，用 `action: { character: "'" }`。

### 已知的坑

1. **`keyboardHeight` 是固定点值，得挑一个目标屏宽写死**，并且所有以点为单位的值
   都要按同一个屏宽换算。`[PANEL] SIZE` 就是宽高比，见上文。
2. **背景图底部常有淡出到全透明的渐变**（原本落在面板之外）。元书的按键区是实心区域，
   要把 alpha 不满的部分裁掉，否则深色皮肤会透出系统底色。`baidu_extract.py` 已处理。
3. **跨多键的长条背景**（空格＋中英、跨两行的回车）：按比例把切片切开分给各键，
   或改用 `VStack` 让那颗键独占一列。
4. **只有 `HL_IMG` 且带位移动画的前景层**别烘进静态贴图，见第 6 节。
   顺带记住：`fileImage` 的两个状态互不回退——只写 `normalImage` 的图层**按下会变空白**。
5. `NM_COLOR` 是 **AARRGGBB**（alpha 在前），元书是 **RRGGBBAA**，转换时要挪位。
6. 字号等数值都在设计稿坐标系里，换算成点要乘对应方向的每设计单位。
7. `light/` 与 `dark/` 的**布局 ini 通常完全相同**，只有 `res/` 不同——
   先 `diff -rq` 确认，相同的话两边共用一份 yaml 生成逻辑，能省一半工作。
8. **源皮肤本身可能就「缺东西」**：拼合图里某个字母是空的、某个字母是白色的……
   先对着 `demo.png` 看一眼再判断。上面那两种多半是设计使然
   （那颗键是深色键帽、或者整颗键就是一张插画），不是提取出错，**不要自作主张补画**。

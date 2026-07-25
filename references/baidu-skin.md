# 百度手机输入法皮肤格式（转换来源）

整理自《百度手机输入法皮肤文档 V2.11.21》，用于把 `.bdi` / `.bds` 图片皮肤转换成元书 `.cskin`。
**不需要再另外提供那份 PDF。**

百度皮肤是**纯图片皮肤**：所有外观都是「拼合图 + 切片矩形 + 相对偏移」，没有颜色/圆角描述。
转换的核心工作是把这套「小图 + 偏移」翻译成元书的「一个图层铺满一个可视区」。

## 1. 皮肤包结构

后缀名：**`.bdi` = iPhone 版**，`.bds` = 其他平台，`.bdskk` / `.bdsk` = 键盘（非触屏）版。
实际是 zip，解开后：

```
<皮肤>/
├── Info.txt              皮肤元信息
├── demo.png              预览图
├── light/skin/           浅色（SupportDarkMode=1 的皮肤才有 light + dark 两套）
│   ├── Info.txt
│   ├── port/             竖屏：全部布局 ini
│   ├── land/             横屏：全部布局 ini
│   └── res/              图片、.til 切片、default.css、字体、按键音
└── dark/skin/            深色，结构完全相同
```

老皮肤还可能有 `240/` `320/` `480/` 这类分辨率目录。
优先级：`根目录 < 根目录 land|port < 分辨率目录 < 分辨率目录 land|port`。

`Info.txt` 字段：`Name` / `Title` / `Description` / `Author` / `Style` /
`SupportPlatform`（`S W I A` 四个平台）/ `MinImeCode` / `SkinType` / `SupportDarkMode` / `VersionCode`。

### 文件类型

| 后缀 | 作用 |
| --- | --- |
| `*.png` | 拼合图 |
| `*.til` | 切片定义（哪块矩形是第几张小图） |
| `*.css` | 样式表（样式号 → 颜色 / 字体 / 图片引用） |
| `*.ini` | 键盘布局 |
| `*.cnd` | 候选条布局 |
| `*.pop` | 气泡布局 |
| `*.ttf` | 字体 |

### 布局 ini 一览

| 文件 | 面板 |
| --- | --- |
| `gen.ini` | **全局默认**：面板尺寸、候选条、偏移表 `[OFFSET*]`、公共段 |
| `py_26.ini` / `py_9.ini` | 拼音 26 键 / 九宫格 |
| `en_26.ini` / `en_26s.ini` | 英文 26 键 小写 / 大写 |
| `en_9.ini` / `en_9s.ini` | 英文九宫格 小写 / 大写 |
| `num_26.ini` / `num_9.ini` | 数字面板 |
| `def_26.ini` / `def_9.ini` | 自定义输入面板 |
| `symbol.ini` / `sel_ch.ini` / `sel_en.ini` | 符号 / 更多候选 |
| `bh.ini` | 笔画 |
| `hw_grid.ini` / `hw_full.ini` | 手写 |
| `net.ini` | 网址 / 密码 |
| `tool_*.ini` | 工具栏（26 键的是 `tool_26.ini`） |
| `logo.ini` / `help.ini` | logo 菜单 / 帮助 |

所有 ini / css / til 都是同一种 `[SECTION]` + `key=value` 格式，UTF-8（常带 BOM）。

## 2. 布局 ini 的段

### `[PANEL]` 主面板

| 属性 | 说明 |
| --- | --- |
| `SIZE` | `宽,高`——**整套皮肤的设计稿坐标系**，如 `1125,595`。下面所有矩形都在这个坐标系里 |
| `BACK_STYLE` | 面板背景样式号 |
| `FORE_STYLE` | 划线效果颜色 |
| `NO_BLUR` | `0` 模糊输入 / `1` 精确输入 |
| `KEY_NUM` / `TIP_NUM` | 按键数 / 补丁数 |
| `OFFSET_NUM` | 偏移类型个数 |
| `SOUND_STYLE` | 按键音样式号 |

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
| `BACK_ANIM_STYLE` / `FORE_ANIM_STYLE` | 按下动画样式号（对应 `res/anim.ini`） |
| `SOUND_STYLE` | 该键单独的按键音 |

> 只有 `VIEW_RECT` 而没有 `FORE_STYLE` 的键，往往是**跨多键的背景板**
> （例如空格与「中英」共用一条长键帽），转换时要按比例切开分给相邻的键。

### `[TIP*]` 补丁

被 `[KEY*]` 的 `STAT_STYLE` 引用，表示某个状态下这颗键换个样子/动作。
属性是 `[KEY*]` 的子集：`BACK_STYLE` / `FORE_STYLE` / `POS_TYPE` / `CENTER` / `HOLD` / `SHOW`。

典型：shift 键 `STAT_STYLE=S14_1|S4_2|S1_3|S2_4` ——
有输入码（S4）时变成分词键，首字母大写（S1）、大写锁定（S2）各换一张图。

### `[OFFSET*]` 偏移表（**只在 `gen.ini` 里生效**）

```ini
[OFFSET41]
POS=8,15
```

`POS=dx,dy`：前景小图**按自身原始尺寸、以按键中心为基准**再平移 `(dx, dy)`，y 正方向朝下。
这是把百度皮肤画对的关键——不看这张表，字母和角标的位置全会错。

### `[LIST]` 列表区（九宫格左侧的符号栏等）

`BACK_STYLE` / `CELL_STYLE` / `FORE_STYLE` / `CELL_SIZE=宽,高` / `POS=X,Y` /
`LIST_NUM`（显示几格）/ `LIST_ORDER`（`0` 竖排 `1` 横排）/ `PADDING=左,上,右,下` /
`NAMES`（半角空格分隔的显示文本）/ `VALUES`（对应的上屏内容或功能键）/
`TYPE`（`0` 面板内常显、`1` 有项才显、`2` 面板上方常显、`3` 面板上方有项才显）。

### 其余段

| 段 | 说明 |
| --- | --- |
| `[INPUT]` | 输入框：`BACK_STYLE` / `FORE_STYLE` |
| `[SCAND]` | 拼写码显示区：`BACK_STYLE` / `FORE_STYLE` / `INPUT_STYLE` / `PADDING` |
| `[CAND]` | 候选条：`VIEW_RECT` / `LAYOUT_NAME`（指向 `.cnd`）/ `TYPE`（`0` 划选、`2` 固定于面板上方、`4` 上方常驻…） |
| `[HINT]` | 气泡：`LAYOUT_NAME`（指向 `.pop`）/ `TYPE`（`0` 跟随按键 `1` 置顶） |
| `[MORE]` | 更多候选：`GRID=行,列` / `LAYOUT_NAME` / `SYM_LAYOUT` / `CELL_STYLE` / `FORE_STYLE` |
| `[LOGO]` `[EMOJI]` | `LAYOUT_NAME` |

## 3. `.til` 切片文件

```ini
[GLOBAL]
USE_ALPHA=1          ; 0 不透明 1 半透明 2 全透明
TILE_NUM=35

[IMG1]
SOURCE_RECT=0,0,106,151      ; 小图在大图中的 X,Y,W,H
INNER_RECT=0,0,106,151       ; 九宫格拉伸的内框
SCALE=1,1,1,1,1              ; 中上,左中,中部,右中,中下  0 平铺 1 拉伸
```

- 没有 `INNER_RECT`，或它的 W/H 为 0 → **不拉伸，居中绘制**。
- `INNER_RECT` 与 `SOURCE_RECT` 完全一致 → **整张图直接拉伸**填满目标矩形（最常见）。
- `TYPE` / `COMPLEX` / `POS`：复合图片，罕见。

> `.til` 与元书 `resources/<图片名>.yaml` 几乎一一对应：
> `SOURCE_RECT` → `rect`，九宫格保护区 → `insets`。

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
FONT_SIZE=54             ; 字号也在设计稿坐标系里（除以 SIZE 的宽再乘屏幕宽得 pt）
FONT_WEIGHT=500
FONT_CLEARTYPE=1
NM_COLOR=D9DAFF          ; RRGGBB 或 AARRGGBB（注意 alpha 在前，与元书相反）
HL_COLOR=AAA6FF
BORDER_COLOR=000000
BORDER_SIZE=1
FONT_NAME=son.ttf
SHOW=，                   ; 该样式直接画一个固定字符
```

按下态的拼合图通常是同名加 `ax` 后缀：`anjian26` / `anjian26ax`、`letter` / `letterax`。

## 5. `.cnd`（候选条）与 `.pop`（气泡）

`.cnd` 分四层绘制：背景层 → 图标层 → 单元格背景层 → 文本层（后两层有候选字时才出现）。

- `[TAB]` / `[CAND]`：`BACK_STYLE` / `FORE_STYLE` / `CELL_STYLE` / `PADDING=左,上,右,下` /
  `CELL_W` 字间距 / `FIRST_GAP` `FIRST_FORE` `FIRST_BACK`（首选字特殊样式）/ `MORE_W`（「更多」按钮宽，0 为不要）。
- `[ICON*]`：`SIZE` / `POS`（相对锚点偏移）/ `KEY`（按下执行的功能键）/
  `ANCHOR_TYPE`（1–9 对应矩形九个点：1 左上 2 中上 3 右上 4 左中 5 中间 6 右中 7 左下 8 中下 9 右下）/
  `PERSIST`（`1` 无候选字时显示 `2` 有候选字时显示 `3` 都显示 `0` 都不显示）。
- `[SWITCH]`：切换键盘容器，`NML_BACK_STYLE` / `SEL_BACK_STYLE` / `NML_FONT_STYLE` / `SEL_FONT_STYLE`。

`.pop` 段：`[HINT]` 普通气泡、`[BAR]` 长按条状气泡、`[CROSS]` 十字长按、
`[DRAW]` 拖拉气泡（仅 iPhone），各自用 `BACK_ICON` / `ARROW_ICON` / 方向 `*_ICON` 指向 `[ICON*]`；
`[ICON*]` 有 `BACK_STYLE` / `FORE_STYLE` / `SIZE` / `POS` / `PADDING`。

## 6. 功能键 `F*`

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

其他键值约定：

- **笔画**：横 `B1` 竖 `B2` 撇 `B3` 点 `B4` 折 `B5` 通配 `B6`。
- **`Z+<文件名>`**：切换到该名字的自定义面板（拼上 `.ini`），如 `Z+tool_26`。

## 7. 状态 `S*`

`S1` 英文首字母大写｜`S2` 英文锁定大写｜`S3` 英文联想｜`S4` **有输入码**｜
`S5` 更多候选单字态｜`S6` 符号面板锁定｜`S7` 翻页面板处于页顶｜`S8` 处于页底｜
`S9` 联想状态｜`S10` 搜索框｜`S11` 浏览地址｜`S12` 有下一个输入框｜`S13` 表单提交

## 8. 转换到元书的做法

### 整体思路

百度：**一个键 = 一张背景图 + N 张按偏移摆放的前景小图**。
元书：**一个键 = 一个背景图层 + N 个铺满可视区的前景图层**，没有「按原始尺寸 + 偏移」这种摆法。

所以：**背景图原样复用**（只把 `.til` 翻成 `resources/*.yaml`），
**前景按 `[OFFSET*]` 预合成**成与按键等大的贴图，再打包成新的拼合图。
`scripts/baidu_extract.py` 就是干这件事的，直接用它，不要手算偏移。

### 区域与尺寸

| 百度 | 元书 |
| --- | --- |
| `[PANEL] SIZE=W,H` | 设计稿坐标系。把所有 `VIEW_RECT` 写成 `size: { width: <值>/W }` 的分数 |
| `[SCAND]` 背景 | `preeditStyle` |
| `[CAND]` / `tool_*.ini` 区域 | `toolbarStyle` + `horizontalCandidatesStyle`（两者 frame 相同） |
| `[PANEL]` 背景 | `keyboardStyle` |
| `TOUCH_RECT` 比 `VIEW_RECT` 大 | `size` 用 `TOUCH_RECT` 的宽，`bounds` 用 `VIEW_RECT` 的宽 + `alignment` |
| `KEY_NUM` 个 `[KEY*]` | 按 `VIEW_RECT` 的 y 分行 → 若干 `HStack`；跨行的键改用 `VStack` 列切分 |

行高：`VIEW_RECT` 的 y 步长即行高，面板顶部/底部余量放进 `keyboardStyle.insets`（点值 ≈ 余量 ÷ `H` × `keyboardHeight`）。

### 动作映射

| 百度 | 元书 |
| --- | --- |
| `CENTER=<字母>` | `action: { character: x }` |
| `CENTER=F36` | `action: backspace`（另加 `repeatAction: backspace`） |
| `CENTER=F38` / `F39` | `action: space` / `enter` |
| `CENTER=F1` / `F6` | `action: { keyboardType: symbolic }` / `{ keyboardType: numeric }` |
| `CENTER=F11` | `action: shift` |
| `CENTER=F15` / `F16` | `action: { shortcut: "#中英切换" }` |
| `CENTER=F40` | `action: { shortcut: "#重输" }` |
| `CENTER=F44/45/46` | `#cut` / `#copy` / `#paste` |
| `CENTER=F51/F52` | `moveCursorBackward` / `moveCursorForward` |
| `CENTER=F62` | `nextKeyboard` |
| `UP=<符号>` | `swipeUpAction: { symbol: "…" }`（用 `symbol` 直接上屏，别用 `character`，否则会喂给 RIME） |
| `DOWN=` | `swipeDownAction` |
| **`LEFT=` / `RIGHT=`** | **没有对应项**——元书只识别上下划动，左右划的字符只能丢弃或挪到长按面板 |
| `HOLDSYM=…` | `hintSymbolsGridStyle`，把字符串逐字拆成一行网格 |
| `STAT_STYLE` 里的 `S1` / `S2` | `uppercasedStateForegroundStyle` / `capsLockedStateForegroundStyle` |
| `STAT_STYLE` 里的 `S4`（有输入码） | `notification` + `notificationType: preeditChanged` |
| `Z+<面板名>` | 在 `config.yaml` 里加一个**自定义键盘类型**，用 `action: { keyboardType: <名字> }` 切过去 |

九宫格 2–9 用 `action: { character: "2" }`（数字喂给 RIME 的九宫格方案），
`[LIST]` 的符号栏用 `type: symbols` + `dataSource`（照抄 `NAMES` / `VALUES`）。

### 已知的坑

1. **背景图底部常有淡出到全透明的渐变**（原本落在面板之外）。元书的按键区是实心区域，
   要把 alpha 不满的部分裁掉，否则深色皮肤会透出系统底色。
2. **跨多键的长条背景**（空格＋中英、跨两行的回车）：要么按宽/高比例把切片切开分给各键，
   要么改用 `VStack` 让那颗键独占一列。
3. `NM_COLOR` 是 **AARRGGBB**（alpha 在前），元书是 **RRGGBBAA**，转换时要挪位。
4. 字号 / 圆角这些数值都在设计稿坐标系里，换算成点要乘 `屏幕宽 ÷ PANEL 宽`（iPhone 竖屏约 `390/1125`）。
5. `light/` 与 `dark/` 的 ini 通常**完全相同**，只有 `res/` 不同——先 `diff` 确认，能省一半工作。
6. 按键音 `res/*.aiff` 可以直接搬进皮肤的 `sound/`（`.ogg` 那份是给安卓的，不要）。

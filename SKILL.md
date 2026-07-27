---
name: hamster-skin-skill
description: 根据用户的文字描述生成元书输入法（Hamster3）的键盘皮肤。当用户要求制作、生成、修改键盘皮肤，或提到皮肤配色、按键样式、键盘布局、cskin 文件时使用。产出可直接安装的 .cskin 皮肤包。
---

# 元书键盘皮肤生成

根据用户描述生成一套完整、可安装的元书输入法键盘皮肤。

皮肤是一组 YAML 文件打包成的 `.cskin`（zip）。**不要写 jsonnet**——仓库里的官方皮肤用
jsonnet 生成 YAML，但手写皮肤直接产出 YAML 更可靠，元书加载的也是 YAML。

## 工作流程

### 第 1 步：明确需求

从用户描述中提取以下信息。**没提到的一律采用默认值直接开做，不要逐条追问。**

| 项目 | 默认值 |
| --- | --- |
| 皮肤名 | 从描述里取一个合适的英文短名（小写、无空格） |
| 键盘类型 | 仅 `pinyin`（26 键）；用户明确要九宫格 / 数字 / 符号键盘时再加 |
| 设备 | iPhone 竖屏 + 横屏；用户提到 iPad 时再加 |
| 深浅色 | 两套都出（必需） |
| 配色 | 按描述推导；描述模糊时用 iOS 原生风格 |
| 圆角 / 阴影 | 圆角 8.5，带底部立体边缘 |

只有在描述**自相矛盾**或缺少无法推断的关键信息时才提问，其余情况先做出来再让用户调。

### 第 2 步：读参考资料

按需读取，不要凭记忆写 Key：

- `references/architecture.md` — **必读**。区域覆盖关系、`HStack` 是行 / `VStack` 是列、
  尺寸分配、样式解析、合并键陷阱。
- `references/keys.md` — 全部 Key、类型、默认值、枚举取值的权威索引。写任何 Key 前先查。
- `references/recipes.md` — 可直接复制的片段（渐变、阴影、条件样式、通知、长按面板、动画等）。
- `references/baidu-skin.md` — 只在**转换百度输入法皮肤**（`.bdi` / `.bds`）时读，见下方专章。

### 第 3 步：从模板起步

```bash
cp -r <skill目录>/assets/template <工作目录>/<皮肤名>
```

`assets/template` 是一套**已通过校验的**完整 iPhone 竖屏 26 键拼音键盘，包含
预编辑区、工具栏、横向 / 纵向候选栏、26 字母键、功能键、长按气泡、深浅两色。

在它基础上改，不要从空文件开始。

### 第 4 步：改造

**改配色**：模板顶部有 `_palette` 锚点块，集中定义了全部颜色。多数换肤需求只需改这十几个值，
`light/` 与 `dark/` 各改一次。

```yaml
_palette:
  keyboardBg:   &cKeyboardBg   "#D1D4DA"
  letterBg:     &cLetterBg     "#FFFFFF"
  ...
```

**改布局**：改 `keyboardLayout`。`HStack` = 一行，`Cell` = 一个键。
一行内所有键的 `size.width` 分子之和应等于分母（模板用 `/1125`），不写 `size` 的键均分剩余宽度。

**加功能键 / 换图标 / 加动画**：从 `references/recipes.md` 复制片段。

**新增键盘类型**（如九宫格、符号键盘）：在 `config.yaml` 增加对应类型，
并在 `light/` 与 `dark/` 各增加同名 yaml。

### 第 5 步：校验（不可跳过）

```bash
python3 <skill目录>/scripts/validate_skin.py <皮肤目录>
```

必须做到 **0 错误**才算完成。校验器会抓出：

- 引用了不存在的样式名 —— **最常见也最致命**，系统不报错，那个位置直接渲染成空白
- `config.yaml` 声明的键盘文件缺失、light/dark 不成对
- 枚举值拼错（`buttonStyleType`、`type`、`contentMode`、`fontWeight`、`alignment` 等）
- 颜色格式非法（只允许 `#RRGGBB` / `#RRGGBBAA`）
- 布局违规（同级混用 `HStack`/`VStack`/`Cell`、`Cell` 直接放在布局根）
- 动作名 / 快捷指令不存在
- `buttonStyleType` 缺少配套 Key（如 `systemImage` 没写 `systemImageName`）
- 通知节点缺少必填项
- 把不穿透合并键的 Key 放进了 `<<` 基底

警告可以酌情忽略，但「引用了不存在的样式」「颜色格式非法」这类**错误**必须清零。

### 第 6 步：出预览图看一眼（不可跳过）

```bash
python3 <skill目录>/scripts/preview_skin.py <皮肤目录> [输出目录]
```

按元书的布局算法给每个键盘的 light / dark 各渲**四张** png，**用 Read 工具打开看**：

| 文件 | 内容 |
| --- | --- |
| `preview_<side>_<名>.png` | 常态 |
| `..._pressed.png` | 全部按键的按下态（`highlightImage`、按下才出现的图层对不对） |
| `..._hint.png` | 长按符号面板（红框标出格子边界，高亮块应比红框小一圈） |
| `..._vertical.png` | 纵向候选栏展开态（底部功能行在不在、键帽有没有被压扁） |

校验器只能查结构，查不出几何问题；下面这些**只有看图才发现得了**：

- 键盘整体偏矮 / 偏高，键帽被压扁
- 某一行没铺满或溢出（`size` 分子之和 ≠ 分母）
- 跨行 / 跨列的键错位
- 长按面板整片伸出屏幕、高亮块顶满格子
- 按下态整片空白（`fileImage` 只写了 `normalImage`——按下态**不会**回退，直接画空）
- 九宫格保护区比目标还大，图糊成一坨
- 前景图层跑到键外、深色皮肤下透出底色

转换现成皮肤时，把预览图和原皮肤的 `demo.png` **并排比一眼**再交付。

需要 Pillow 与 PyYAML。系统 python 装不上时（PEP 668）建一个 venv：
`python3 -m venv venv && ./venv/bin/pip install Pillow pyyaml`。

### 第 7 步：打包

```bash
<skill目录>/scripts/package_skin.sh <皮肤目录> [输出目录]
```

脚本会先自动跑校验，通过后生成 `<皮肤名>.cskin`。

打包前记得放一张 `demo.png`（应用内的皮肤预览图）。没有时提醒用户补，
或直接拿第 6 步的预览图充数。

### 第 8 步：交付

告诉用户：

- 生成的 `.cskin` 路径
- 改了哪些配色 / 布局
- 安装方式：把文件传到 iOS 设备，用元书打开即可导入
- 后续想微调可以直接说（如「键帽再圆一点」「空格键换成显示方案名」）

## 转换百度输入法图片皮肤

用户给的是 `.bdi` / `.bds`（或已解包的目录）时走这条路，**不要**照着截图重新配色——
背景、键帽、字形、图标全都能原样复用，成品跟原皮肤几乎一模一样。

先读 `references/baidu-skin.md`（格式速查 + 功能键表 + 映射表 + 坑），然后：

```bash
# 0. .bdi 本质是 zip，先解包
unzip -q <皮肤>.bdi -d <工作目录>/src

# 1. 确认 light/dark 的布局 ini 是否相同（通常完全相同，能省一半工作）
diff <工作目录>/src/dark/skin/port/py_26.ini <工作目录>/src/light/skin/port/py_26.ini

# 2. 提取资源：背景图原样复制 + .til 翻成图片描述 yaml + 前景层按 [OFFSET*] 预合成
#    + 解析 anim.ini + 反推 keyboardHeight
python3 <skill目录>/scripts/baidu_extract.py \
    <工作目录>/src/dark/skin  <皮肤名>/dark  py_26 py_9
python3 <skill目录>/scripts/baidu_extract.py \
    <工作目录>/src/light/skin <皮肤名>/light py_26 py_9
```

脚本还会输出 `<皮肤名>/<light|dark>/baidu_layout.json`——每个键的
`viewRect` / `touchRect` / 背景图 / `center`、`up`、`holdSymbols`、动画、按键音，
以及换算好的 `metrics`。**照着它写键盘 yaml**，不要再回头去啃 ini。

要点：

- **`keyboardHeight` 用 `metrics.keyboardHeight`**，别拿 `[PANEL] SIZE` 的高宽比去算——
  那只是设计稿坐标系，照它折算键会明显偏矮，是这类转换的头号翻车点。
  `metrics` 里还有 `rowHeight` / `unitX` / `unitY` / `insetTop` / `insetBottom`。
- `viewRect` 直接写成 `size: { width: <值>/<设计稿宽> }`；竖直方向的数值换算用 `unitY`，
  水平方向用 `unitX`，**两个方向比例不同，别混用**。
- `touchRect` 比 `viewRect` 大的边缘键，用 `size` 取触摸宽 + `bounds` 取绘制宽。
- 跨多个键 / 跨行的长条（空格＋中英、跨两行的回车、九宫格左侧符号栏）：
  改用 `VStack` 分列，列里再套 `HStack` 排行。
- `pressAnimation` → `animationType: scale`；`splashAnimations` → `animationType: physics`
  （对应的贴图已经单独导成 `anim_*.png`，并且**已从 `fg_*ax` 里剔除**，直接引用即可）。
- 功能键 `F*` → 元书动作的对照表在 `references/baidu-skin.md`。
- 左右划动、长按动作元书都不支持，只能丢弃或挪到上下划 / 长按符号面板。
- 源皮肤本身可能就缺图（某个字母是空的、是白色的），**先对着 `demo.png` 确认**，
  多半是设计使然，不要自作主张补画。

做完后照常走第 5 步校验、**第 6 步出预览图和 `demo.png` 对比**、第 7 步打包。

## 硬性规则

1. **每个引用的样式名都必须在根节点存在**。这是第一大坑，且失败是静默的。
2. **`light/` 与 `dark/` 必须成对**，同名文件都要有，否则切换深浅色时键盘空白。
3. **必须定义 `keyboardStyle` 和 `toolbarStyle`**，否则对应区域根本不会被创建。
4. **颜色只能是 `#RRGGBB` 或 `#RRGGBBAA`**。`red`、`rgb()`、3 位缩写都会静默失效。
5. **`HStack` 是行，`VStack` 是列**，与直觉相反。
6. **`animation` 必须是数组**。
7. **划动只有上下**，没有 `swipeLeftAction` / `swipeRightAction`。
8. 不穿透合并键 `<<` 的 Key（`type`、`maxColumns`、`maxRows`、`colorLocation`、
   `shadowOpacity` 等）必须直接写在使用它的节点内。
9. 生成完**必须跑校验**，0 错误才算交付；**并且必须出预览图亲眼看过**。
10. 三种动画各管一件事：`scale` 只缩放、`cartoon` 只在原地逐帧播、
    **`physics` 是唯一能做位移的**。别说「元书做不了位移」。
11. **`verticalCandidatesLayout` 底部要放 上一页 / 下一页 / 返回 / 退格 四个键**，
    只给一个候选列表的话用户翻不了页也退不出来。片段见 `recipes.md`。
12. 长按面板：高亮块用 `insets` 收进格子里；面板按各键的横坐标算 `anchor`，
    否则靠边的键会把面板顶出屏幕；面板背景别用保护区大于目标尺寸的九宫格图。

## 目录

```
references/
  architecture.md   运行机制：区域、布局（含跨行跨列）、三个高度怎么定、样式解析、坑
  keys.md           全部 Key 索引（类型 / 默认值 / 枚举）
  recipes.md        可直接复制的配方片段
  baidu-skin.md     百度输入法皮肤格式 + 转换映射表（转 .bdi/.bds 时才读）
assets/template/    已通过校验的完整皮肤模板
scripts/
  validate_skin.py  校验器（优先用 PyYAML，缺失时自动回退到 macOS 自带 ruby 解析 YAML）
  preview_skin.py   按元书布局算法渲成 png，用来肉眼检查几何（需 Pillow + PyYAML）
  package_skin.sh   打包成 .cskin（内置校验）
  baidu_extract.py  从百度皮肤提取：背景图 + 预合成前景 + physics 用图 + 布局摘要 json
```

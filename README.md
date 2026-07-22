# hamster-skin-skill

用一句话描述，让 AI 帮你做一套[元书输入法](https://github.com/imfuxiao/Hamster3)的键盘皮肤。

这是一个 [Claude Code](https://claude.com/claude-code) Skill。装好之后，你只需要说
「帮我做一个莫兰迪色系的键盘皮肤」，它会产出一个可以直接装进 iPhone 的 `.cskin` 文件。

仓库里同时包含两个**可以脱离 AI 单独使用**的命令行工具：皮肤校验器和打包器。
即使你完全手写皮肤，也可以用它们检查错误、生成安装包。

---

## 目录

- [它能做什么](#它能做什么)
- [安装](#安装)
- [环境要求](#环境要求)
- [使用方法](#使用方法)
- [独立使用命令行工具](#独立使用命令行工具)
- [仓库结构](#仓库结构)
- [皮肤是怎么回事](#皮肤是怎么回事)
- [常见问题](#常见问题)
- [兼容性说明](#兼容性说明)
- [贡献](#贡献)
- [许可](#许可)

---

## 它能做什么

| 你说 | 它做 |
| --- | --- |
| 「做一个莫兰迪色系的皮肤」 | 生成深浅双色完整皮肤并打包 |
| 「键帽圆角再大一点，去掉阴影」 | 定位到对应样式改参数 |
| 「空格键改成显示当前输入方案名」 | 用 `$rimeSchemaName` 变量替换文本 |
| 「给字母键加个按下缩放动画」 | 加 `scale` 动画节点并挂到按键上 |
| 「a 键长按要能出 à á â ä」 | 配置长按符号网格面板 |
| 「我这皮肤装上去有几个键是空白的」 | 跑校验器定位到写错的样式引用 |

生成的皮肤包含：预编辑区、工具栏、横向 / 纵向候选栏、26 个字母键、
功能键（Shift / 退格 / 数字 / 空格 / 回车）、长按气泡，以及浅色和深色两套配置。

---

## 安装

Skill 就是一个包含 `SKILL.md` 的目录，放到 Claude Code 的 skills 目录下即可。

### 方式一：个人级（推荐，所有项目都能用）

```bash
git clone https://github.com/imfuxiao/hamster-skin-skill.git \
  ~/.claude/skills/hamster-skin-skill
```

### 方式二：项目级（只在某个项目里可用）

```bash
cd /path/to/your/project
git clone https://github.com/imfuxiao/hamster-skin-skill.git \
  .claude/skills/hamster-skin-skill
```

> 个人 / 项目 Skill 的斜杠命令由**目录名**决定，所以请保持目录名为 `hamster-skin-skill`。

### 验证安装

打开 Claude Code，输入 `/` 应该能在列表里看到 `hamster-skin-skill`。

两种触发方式：

- **手动**：输入 `/hamster-skin-skill`
- **自动**：直接说「帮我做个键盘皮肤」，Claude 会根据描述自动加载它

也可以先跑一下自带的模板，确认脚本环境正常：

```bash
python3 ~/.claude/skills/hamster-skin-skill/scripts/validate_skin.py \
        ~/.claude/skills/hamster-skin-skill/assets/template
```

看到 `合计：0 个错误，1 个警告`（唯一的警告是模板没有 `demo.png`）就说明一切正常。

### 更新

```bash
cd ~/.claude/skills/hamster-skin-skill && git pull
```

### 卸载

```bash
rm -rf ~/.claude/skills/hamster-skin-skill
```

---

## 环境要求

| 依赖 | 用途 | 说明 |
| --- | --- | --- |
| Claude Code | 运行 Skill | 只用命令行工具的话不需要 |
| Python 3.8+ | 校验器 | macOS / 大多数 Linux 自带 |
| PyYAML **或** Ruby | 解析 YAML | 见下方说明 |
| `zip`、`rsync` | 打包 `.cskin` | macOS / Linux 自带 |

关于 YAML 解析：校验器会**优先使用 PyYAML**；如果没装，会自动回退到调用系统 `ruby`
（macOS 自带 `/usr/bin/ruby`）来解析。也就是说在 macOS 上开箱即用，无需任何额外安装。

如果两者都没有，脚本会明确提示。想装 PyYAML：

```bash
pip install pyyaml
# 若遇到 externally-managed-environment 报错，用虚拟环境：
python3 -m venv ~/.venvs/hamster && ~/.venvs/hamster/bin/pip install pyyaml
```

---

## 使用方法

### 基本流程

在 Claude Code 里直接用自然语言描述你想要的皮肤即可。Skill 会自动走完这些步骤：

```
理解需求 → 读取参考资料 → 从模板起步 → 按需改造 → 校验（必须 0 错误）→ 打包 .cskin
```

### 从零做一套新皮肤

```
帮我做一个键盘皮肤，深蓝色底，键帽是半透明白色，
圆角大一点，回车键用橙色高亮。
```

描述里没提到的部分会用合理默认值补齐（iPhone 竖屏 + 横屏、26 键拼音、深浅双色），
不会反复追问你。做完之后再让它微调即可。

### 在已有皮肤上改

```
把 ~/Downloads/mytheme 这个皮肤的键帽改成毛玻璃效果，
另外空格键上显示当前输入方案名。
```

### 排查问题

```
我装了这个皮肤之后，第三排有两个键是空白的，帮我看看：
~/Downloads/mytheme
```

校验器会直接指出是哪个样式名引用错了——这是皮肤最常见的故障，
而且元书本身不会报错，只会静默地把那个位置渲染成空白。

### 好用的追加指令

上面任意一步做完后，可以继续说：

- 「键帽再圆一点」「按下的颜色对比再强一些」
- 「加一个九宫格数字键盘」
- 「给 a s d f 都配上长按变音符号」
- 「Shift 键在大写锁定时换个图标」
- 「按键音换成机械键盘的声音」（需要你自己提供音频文件）

### 拿到 `.cskin` 之后

1. 把文件传到 iPhone / iPad（AirDrop、微信、iCloud 云盘都行）
2. 在 iOS 上点开这个文件，选择用「元书」打开
3. 元书会自动导入，然后在 App 里切换到这套皮肤

---

## 独立使用命令行工具

两个脚本不依赖 Claude Code，可以直接当工具用。

### `scripts/validate_skin.py` — 皮肤校验器

```bash
python3 scripts/validate_skin.py <皮肤目录>
```

退出码：`0` = 无错误（可能有警告），`1` = 有错误，`2` = 用法或环境问题。

检查项：

| 类别 | 具体检查 |
| --- | --- |
| 引用完整性 | 所有 `backgroundStyle` / `foregroundStyle` / `Cell` / `hintStyle` 等引用的样式名是否真实存在 |
| 文件结构 | `config.yaml` 声明的键盘文件是否存在、`light/` 与 `dark/` 是否成对 |
| 必填项 | `preeditHeight` / `toolbarHeight` / `keyboardHeight`、各 `buttonStyleType` 的配套 Key |
| 枚举值 | `buttonStyleType`、`type`、`contentMode`、`fontWeight`、`alignment`、`animationType` 等 |
| 颜色格式 | 只允许 `#RRGGBB` 与 `#RRGGBBAA` |
| 布局合法性 | 同级不能混用 `HStack`/`VStack`/`Cell`，`Cell` 不能直接放在布局根 |
| 动作 | 按键动作名、快捷指令是否存在 |
| 通知 | 各 `notificationType` 所需的必填参数 |
| 资源 | 字体文件、音频文件是否存在 |
| 合并键陷阱 | 不穿透 `<<` 的 Key 被放进了锚点基底 |

示例输出：

```
校验皮肤: /Users/me/Downloads/mytheme

警告 (2)
  ! 皮肤目录: 缺少 demo.png（应用中的皮肤预览图）
  ! light/pinyinPortrait.yaml: 有 3 个样式从未被引用：oldButton, oldFg, tmpStyle

错误 (2)
  x light/pinyinPortrait.yaml: 引用了不存在的样式 `qButtonFg`（该处会渲染为空白）
  x light/pinyinPortrait.yaml/enterBg/normalColor: 颜色 `blue` 格式非法，应为 #RRGGBB 或 #RRGGBBAA

合计：2 个错误，2 个警告。
```

警告可以按需忽略，错误应当清零。

### `scripts/package_skin.sh` — 打包器

```bash
./scripts/package_skin.sh <皮肤目录> [输出目录]
```

会先自动跑一遍校验，**校验不通过就中止打包**，避免产出一个装上去是空白的皮肤。
通过后生成 `<皮肤名>.cskin`。

```bash
$ ./scripts/package_skin.sh ~/Downloads/mytheme ~/Desktop
==> 打包前校验
校验皮肤: /Users/me/Downloads/mytheme

通过：未发现问题。
==> 已生成: /Users/me/Desktop/mytheme.cskin
    大小: 124K
```

### 拿模板当脚手架

`assets/template/` 本身就是一套完整可用的皮肤，可以直接复制来改：

```bash
cp -r assets/template ~/Downloads/mytheme
# 改 light/pinyinPortrait.yaml 顶部的 _palette 调色板即可整体换色
python3 scripts/validate_skin.py ~/Downloads/mytheme
./scripts/package_skin.sh ~/Downloads/mytheme
```

---

## 仓库结构

```
hamster-skin-skill/
├── SKILL.md                      Skill 主文件：工作流程与硬性规则
├── references/
│   ├── architecture.md           皮肤运行机制：区域关系、布局语义、样式解析、坑
│   ├── keys.md                   全部配置项索引（类型 / 默认值 / 枚举取值）
│   └── recipes.md                可直接复制的配方片段
├── assets/template/              一套已通过校验的完整皮肤模板
│   ├── config.yaml
│   ├── light/pinyinPortrait.yaml
│   └── dark/pinyinPortrait.yaml
└── scripts/
    ├── validate_skin.py          皮肤校验器
    └── package_skin.sh           打包成 .cskin
```

`references/keys.md` 是从元书键盘扩展源码反推整理的配置项索引，
覆盖 `config.yaml`、图片描述文件、键盘配置文件的全部 Key，
以及 13 组枚举的完整取值。手写皮肤时也可以当字典查。

---

## 皮肤是怎么回事

不看也能用，但了解这几点能让你更清楚地描述需求。

### 文件结构

```
<皮肤名>/
├── config.yaml     声明每种键盘在不同设备 / 方向下用哪个配置文件
├── demo.png        应用内的预览图
├── light/          浅色模式的键盘配置
└── dark/           深色模式的键盘配置（必须与 light 同名成对）
```

打包成 zip 并改后缀为 `.cskin` 就是安装包。

### 三个区域 + 两层候选栏

```
┌─────────────────────┐
│ 预编辑区             │  preeditHeight
├─────────────────────┤
│ 工具栏区             │  toolbarHeight   ← 输入时被横向候选栏覆盖
├─────────────────────┤
│                     │
│ 按键区               │  keyboardHeight
│                     │
└─────────────────────┘
```

候选栏不是独立区域，而是浮在上面的覆盖层：横向候选栏盖住工具栏区，
纵向候选栏（展开态）盖住预编辑区以下的全部区域。

### 两个反直觉的点

1. **`HStack` 是「行」，`VStack` 是「列」**。同级的 `HStack` 自上而下堆叠、平分高度，
   所以一个 `HStack` 就是键盘的一行。
2. **样式引用错了不会报错，只会变成空白**。所有样式都平铺在配置文件根节点，
   靠名字字符串互相引用，拼错一个字母那个位置就消失了。这也是本仓库要带一个校验器的原因。

更多细节见 [`references/architecture.md`](references/architecture.md)。

---

## 常见问题

<details>
<summary><b>装上皮肤后键盘整个是空白的</b></summary>

大概率是 `config.yaml` 里声明的文件名与实际文件对不上，或者缺少当前设备 / 方向的声明。
元书在找不到配置时不会回退，直接显示空白。跑一次校验器就能定位：

```bash
python3 scripts/validate_skin.py <皮肤目录>
```
</details>

<details>
<summary><b>只有某几个键是空白的</b></summary>

这些键引用了不存在的样式名。校验器会报
`引用了不存在的样式 `xxx`（该处会渲染为空白）`。
</details>

<details>
<summary><b>切换到深色模式后键盘空白</b></summary>

`dark/` 目录里缺少与 `light/` 同名的文件。两个目录必须成对提供。
</details>

<details>
<summary><b>颜色设置了但没生效</b></summary>

颜色只支持 `#RRGGBB` 和 `#RRGGBBAA` 两种写法（`#` 可省略）。
写成 `red`、`rgb(255,0,0)`、`#f00` 都会解析失败并静默变透明。
</details>

<details>
<summary><b>长按按键没有弹出符号面板</b></summary>

检查按键样式里有没有配 `hintSymbolsGridStyle`（网格版）或 `hintSymbolsStyle`（单行版），
以及对应节点里的 `symbolRows` / `symbolStyles` 是否为空。
</details>

<details>
<summary><b>动画不生效</b></summary>

`animation` 必须写成**数组**：`animation: [myAnimation]`，写成字符串不会生效。
</details>

<details>
<summary><b>校验器报「需要一个 YAML 解析器」</b></summary>

当前环境既没有 PyYAML 也没有 Ruby。任选其一安装即可，见[环境要求](#环境要求)。
</details>

<details>
<summary><b>能生成九宫格 / 双拼 / 五笔布局吗</b></summary>

可以。直接描述你要的布局即可，例如「做一个九宫格拼音键盘」。
皮肤只管按键的外观与动作，输入方案（双拼、五笔等）是 RIME 那边的配置，两者独立。
</details>

---

## 兼容性说明

`references/keys.md` 中的配置项是从元书键盘扩展源码反推整理的，随版本可能变化。
如果你在使用中发现某个 Key 的行为与文档不符，欢迎提 issue。

已知的几点：

- 划动只识别**上下**方向，不存在 `swipeLeftAction` / `swipeRightAction`
- `preeditStateForegroundStyle` 的读取逻辑已停用，请改用 `notificationType: preeditChanged` 通知

---

## 贡献

欢迎提 issue 和 PR：

- 补充 `references/recipes.md` 里的配方
- 修正 `references/keys.md` 中与实际行为不符的地方
- 给校验器增加新的检查项
- 贡献新的皮肤模板

改动脚本后请至少验证这三项：

```bash
# 模板必须 0 错误
python3 scripts/validate_skin.py assets/template
# 打包链路正常
./scripts/package_skin.sh assets/template /tmp
# 对官方皮肤不产生误报（如果你手上有）
python3 scripts/validate_skin.py <某个已知正常的皮肤>
```

---

## 许可

[MIT](LICENSE)

## 相关链接

- [元书输入法](https://github.com/imfuxiao/Hamster3)
- [元书使用文档](https://ihsiao.com/apps/hamster/v3/docs/)
- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)

<div align="center">

<img src="assets/icon-drive-192.png" width="96" alt="GitHub Drive">

# github_drive_plugins

GitHub Drive 的官方扩展市场清单。开发者也可以提交自己的扩展。

</div>

## v2 扩展平台（API 2）

`v2` 指的是**扩展宿主 API 的世代**，不是界面形态。从 `0.10.0` 起，扩展不再只是「点开一个全屏网页」；从 `0.10.2` 起，**点扩展一律开独立浮窗**（沿用 v1 的交互），v2 只负责把能力补齐：

- **可选的侧栏视图**：`GD.sidebar.show()` 可把当前视图嵌进主侧边栏，切换导航不重载。默认不用，想用才调
- **多窗口 / 独立标签**：`GD.window.open()` / `GD.window.popout()`，窗口可拖动、缩放、全屏
- **完整网络请求**：`GD.net.fetch()`，首次访问新域名会弹授权框，可「仅本次 / 总是允许 / 拒绝」；`GD.net.github()` 由宿主代发，扩展拿不到 token
- **命令面板与右键菜单**：`contributes.commands` / `contributes.menus`，或运行时 `GD.commands.register()` / `GD.menus.contribute()`
- **状态栏、通知、进度、主题、国际化**
- **文件与命名空间存储**：`GD.files.*`、`GD.storage.*`，`sync()` 可写回 Drive 隐藏目录 `.gd/extensions/`

扩展跑在 **opaque sandbox iframe** 里：读不到宿主的 `localStorage`（那里有 token），只能经 SDK 按声明的能力通信。

## 清单里的扩展

| 扩展 | 说明 |
|---|---|
| 🧰 万能工作台 | 合并文本/代码编辑、Markdown、JSON 格式化；图片、音频、PDF 等交给宿主原生预览，不重复造轮子 |
| 🐙 GitHub 仪表盘 | 合并仓库 Hash 监控：账号、仓库、最新 commit、API 限流 |
| 🌐 HTTP 实验室 | 完整 HTTP 客户端：方法 / 头 / 请求体 / 域名授权 / 后端代理 / 响应查看 |
| 🗒 随手记 | 独立窗口里的记事本，跟随选中文件、自动保存、同步到 Drive |
| ⌘ 命令中心 | 演示命令注册、命令面板、菜单注入、多窗口与独立标签 |
| 🎮 游戏中心 | 合并贪吃蛇与修仙模拟器，在独立窗口里打开 |
| 📺 B站视频下载器 | 旧版插件，需配合本地后端 |
| 🧮 数学题库 | 旧版插件 |

## 开发一个扩展

1. 写一个自包含的 HTML（内联 CSS/JS，不依赖外部 CDN）
2. 等 `GD.ready` 之后再调用能力，例如：

   ```js
   GD.ready.then(() => {
     GD.window.setTitle('我的扩展');
     GD.status.set('就绪');
   });
   ```

3. 在 `plugins.json` 里登记，`api: 2`，并在 `permissions` 里**列出用到的每一项能力**
4. 跑 `python validate.py` 校验

`validate.py` 会从源码里抽出所有 `GD.*` 调用，反查所需权限，并检查文件存在、id 唯一、菜单引用的命令确实注册过。权限漏声明在运行时会抛「扩展未声明该能力」，而且发生在 sandbox iframe 里，很难查——所以推送前务必跑一次。

旧版插件（`api` 未声明）继续走原来的全屏运行路径，行为不变。

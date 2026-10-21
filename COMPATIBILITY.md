# 图表兼容性验证（2026-10-21）

## 远程同步

工作目录先对齐 `origin/main` 的 `9becfdc`。同步前的本地提交保存在 `codex/backup-before-remote-sync-20261021`；本次变更包含同步后完成的图表加载修复和诊断页面。

## 真机问题与修复

通过 USB 连接、已配对的 iPad Pro，在 iPadOS 27.0 Safari 中打开 Mac 的 8099 页面，并使用 Safari 远程网页检查器验证。

修复前：JSON 已加载、顶部卡片已有数值，但 `echarts` 未定义，图表实例为空、没有 Canvas。重新加载捕获到：

```text
https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js
Failed to load resource: TLS错误导致安全连接失败。
ReferenceError: Can't find variable: echarts
```

改为从 `vendor/echarts-5.4.3.min.js` 同源加载相同版本；许可证及来源保存在 `vendor/`。同时为初始化失败增加可见错误提示。默认继续使用 Canvas，`?renderer=svg` 可用于对照。

## 验证结果

| 环境 | 验证 | 结果 |
| --- | --- | --- |
| iPad Pro 真机 / Safari 27.0 / 当前横屏视口 1210×777 | 三个图表、实际 Canvas 曲线像素、1/3/5/10 年按钮 | 通过 |
| Mac / Chrome 与 WebKit 27.2 | 三个图表、Canvas/SVG、诊断页 | 通过 |
| iPad 横竖屏设备模拟 / WebKit 27.2 | 三个图表、Canvas/SVG、布局、诊断页 | 通过 |
| iPhone 横竖屏设备模拟 / WebKit 27.2 | 三个图表、Canvas/SVG、布局、诊断页 | 通过 |
| 阻断所有外部请求 | 本地依赖可正常初始化、无外部运行时请求 | 通过 |
| 阻断本地图表库文件 | 显示“图表加载失败，请刷新页面重试。” | 通过 |

iPad 真机红利低波、美债实际利率、沪深 300 分别读取 20/20、20、2428 个数据点；Canvas 中检测到相应彩色曲线像素。1/3/5/10 年数据点分别为 243/726/1212/2428。已在真机检查器的 Canvas 预览中目视确认沪深 300 曲线。

设备模拟不代表对应型号的真机结果。此次 iPhone 回归使用模拟环境；iPad 真机的纵向旋转未另行验证。

## 本地复查

运行 `python3 -m http.server 8099 --bind 0.0.0.0`，打开 `/test.html`。同一局域网的真机需使用 Mac 的局域网 IP，不能使用该设备自身的 `localhost`。诊断页支持 Canvas/SVG 对照、宽度切换以及加载状态查看；宽度切换本身不模拟操作系统。

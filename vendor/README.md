# ECharts 本地依赖

`echarts-5.4.3.min.js` 来自 npm 官方 `echarts@5.4.3` 发布包的 `dist/echarts.min.js`，未修改。

原页面依赖 jsDelivr。2026-10-21 在 iPadOS 27.0 Safari 真机上确认该 CDN 请求发生 TLS 错误，导致 `echarts` 未定义、数据卡片有值但图表空白。使用同源静态文件避免图表初始化依赖第三方 CDN。

- 来源：https://registry.npmjs.org/echarts/-/echarts-5.4.3.tgz
- SHA-256：`1156429a16a38cb8604dcc6518c19406d4226142d908f8edd2e3531443c54d19`
- 许可证：`echarts-LICENSE`
- 版权声明：`echarts-NOTICE`
- 子组件许可证：`licenses/LICENSE-d3`

升级时从对应版本的 npm 发布包更新脚本和许可证，修改 HTML 引用，并验证 Mac、iPad 和 iPhone 的三个图表及时间范围切换。

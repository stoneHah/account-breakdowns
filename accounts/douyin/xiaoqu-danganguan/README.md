# 小qu档案馆

抖音账号。本页是概况和导航。完整结论只写在[分析](analysis.md)，不在这里再写一遍。

- 主页：https://www.douyin.com/user/MS4wLjABAAAAnQsJMoVVk75MuBNyuvjcSN1vibGgLlxtRozln7PWSd6ruWbZxq5hg5ffX_qW3a88
- 公开抖音号：98631807259
- 采集快照：2026-11-15 08:37–08:38（北京时间）
- 日期快照：[snapshots/2026-11-15](snapshots/2026-11-15/README.md)

## 快照时的公开数字

这些数字是采集当时的事实，之后会变。播放量和收益没有采集。

| 项目 | 数值 |
|---|---|
| 粉丝 | 29,018 |
| 资料页作品数 | 27 |
| 本次列表样本 | 26 |
| 资料页获赞总数 | 702,516 |
| 样本时间跨度 | 2026-10-17 至 2026-11-12 |

【待核查】资料页 27 条，两页列表去重后 26 条，且当时接口没有下一页。少的 1 条原因还不知道。后面的统计只基于这 26 条。

26 条里，三条做了观看和静帧交叉核验，时长以 ffprobe 为准：入口条 46.833 秒、相对高互动条 15.033 秒、普通样本 96.767 秒。

## 三条样本

选择理由写在[调研过程](research-process.md#3-样本选择)。画面和证据等级写在[分析](analysis.md#3-三条已交叉核验样本)。

| 角色 | 作品 | ffprobe | 关键帧 |
|---|---|---|---|
| 入口样本 | [唐太宗·人物志](https://www.douyin.com/video/7705909563958749561) | 46.833 秒 | [联系表](snapshots/2026-11-15/keyframes/01-contact.jpg) |
| 相对高互动 | [关羽](https://www.douyin.com/video/7700491233940235685) | 15.033 秒 | [联系表](snapshots/2026-11-15/keyframes/02-contact.jpg) |
| 普通样本 | [官渡](https://www.douyin.com/video/7706308863466020571) | 96.767 秒 | [联系表](snapshots/2026-11-15/keyframes/03-contact.jpg) |

## 阅读顺序

1. [分析结论](analysis.md)
2. 核对数字时看[快照 JSON](snapshots/2026-11-15/snapshot.json) 和[作品表](snapshots/2026-11-15/works.csv)
3. [调研过程](research-process.md)，其中第 3 节是样本选择
4. [来源与归属](sources.md)
5. [关键帧说明](snapshots/2026-11-15/keyframes/README.md)
6. [修订记录](revision-log.md)

仓库的分级、抽样和时间口径见[工作规范](../../../docs/工作规范.md)。

## 这一页没有写完的事

用户在 2026-11-15 09:31（北京时间）判断这些作品是代码生成。这是用户确认/判断，作者工程源码还没有独立核实。详见分析里的「用户补充」。

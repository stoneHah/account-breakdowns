# 账号拆解资料库

这里存放短视频账号的拆解过程和结果：公开数据快照、抽样记录、分析结论和修订。正文以中文为主，文件是 Markdown、CSV 和 JSON。仓库不提供网站，也不带采集程序。

目前只收录一个账号。

## 从这里开始

- [工作规范](docs/工作规范.md)：事实、推断、用户补充、待核查怎么分级；抽样做到哪一步；时间统一用北京时间；赞和播放、收益怎么分开；公开仓库哪些内容不能进。
- [新账号模板](templates/account-breakdown.md)：下次收录账号时照这个目录写。
- [小qu档案馆（抖音）](accounts/douyin/xiaoqu-danganguan/README.md)：2026-11-15 的账号概况。完整分析在[分析结论](accounts/douyin/xiaoqu-danganguan/analysis.md)，当天的表和关键帧在[日期快照](accounts/douyin/xiaoqu-danganguan/snapshots/2026-11-15/README.md)。

## 已收录

| 平台 | 账号 | 快照日期（北京时间） | 入口 |
|---|---|---|---|
| 抖音 | [小qu档案馆](accounts/douyin/xiaoqu-danganguan/README.md) | 2026-11-15 | [26 条作品](accounts/douyin/xiaoqu-danganguan/snapshots/2026-11-15/works.csv) · [三条样本](accounts/douyin/xiaoqu-danganguan/research-process.md#3-样本选择) · [关键帧](accounts/douyin/xiaoqu-danganguan/snapshots/2026-11-15/keyframes/README.md) |

## 公开范围

可以留下公开作品链接、账号链接、昵称、账号 ID、发布时间和赞、评、藏、转。分析需要画面时，只留少量关键帧，并写上原作品链接；画面仍归原作者和平台。

密钥、会话凭据、请求头、响应头、带签名的播放地址、原始接口响应、原视频、商务联系方式和私人资料不进入本仓库。本仓库没有许可证文件，也不用 MIT 或其他许可证再授权这些关键帧。细则见[工作规范](docs/工作规范.md)。

入库前可以用本机 Python 3 做一次无依赖检查，脚本不访问网络：

```bash
python3 scripts/check_archive.py
```

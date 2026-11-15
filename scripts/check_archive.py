#!/usr/bin/env python3
"""检查账号拆解资料库的公开快照。只读本仓库，无第三方依赖，不访问网络。"""

from __future__ import annotations

import csv
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "accounts" / "douyin" / "xiaoqu-danganguan" / "snapshots" / "2026-11-15"
TEXT_SUFFIXES = {".md", ".json", ".csv", ".py", ".txt", ".gitignore"}

# 模式拆开存放，避免检查脚本扫描自身时命中说明文字。
PATH_MARKERS = (
    "/ho" + "me/",
    "/Us" + "ers/",
    "/tm" + "p/",
    "/work" + "space",
    "/opt/cur" + "sor",
)
SECRET_PATTERNS = (
    re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]{8,}"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(cookie|set-cookie)\s*:\s*\S+"),
    re.compile(
        r"(?i)(play_addr|playwm|x-expires|x-signature|"
        + "byte" + "cdn|aweme/v1/play)"
    ),
    re.compile(r"-----BEGIN |AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}"),
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile("|".join(re.escape(item) for item in PATH_MARKERS)),
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def check(self, ok: bool, message: str) -> None:
        if ok:
            self.notes.append(message)
        else:
            self.errors.append(message)


def median(values: list[float]) -> float:
    xs = sorted(values)
    n = len(xs)
    if n == 0:
        raise ValueError("empty")
    if n % 2:
        return float(xs[n // 2])
    return (float(xs[n // 2 - 1]) + float(xs[n // 2])) / 2


def close(a: float, b: float, tol: float = 1e-4) -> bool:
    return abs(a - b) <= tol


def load_csv() -> list[dict[str, str]]:
    with (SNAP / "works.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def jpeg_has_exif(path: Path) -> bool:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ValueError(f"{path.name} 不是 JPEG")
    index = 2
    while index < len(data) - 1:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in (0xD8, 0xD9) or marker == 0xDA or marker == 0x01 or 0xD0 <= marker <= 0xD7:
            if marker == 0xDA or marker == 0xD9:
                return False
            index += 2
            continue
        if index + 4 > len(data):
            break
        length = struct.unpack(">H", data[index + 2 : index + 4])[0]
        if marker == 0xE1:
            return True
        index += 2 + length
    return False


def scan_text(report: Report) -> None:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitignore":
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                hits.append(f"{rel}: {match.group(0)[:48]}")
    report.check(not hits, "文本未发现密钥、播放签名、联系方式或本机路径" if not hits else "敏感匹配: " + "; ".join(hits))


def check_gitignore(report: Report) -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    rules = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rules.append(stripped.split()[0])
    required = [".env", "raw/", "*.mp4", "*.zip"]
    missing = [item for item in required if item not in rules]
    report.check(
        not missing,
        "gitignore 排除 .env、raw/、原视频和临时压缩包"
        if not missing
        else "gitignore 缺少 " + ", ".join(missing),
    )
    report.check("*.json" not in rules and "*.csv" not in rules, "gitignore 保留快照 JSON 与 CSV")


def check_snapshot(report: Report) -> None:
    rows = load_csv()
    works = json.loads((SNAP / "works.json").read_text(encoding="utf-8"))
    snap = json.loads((SNAP / "snapshot.json").read_text(encoding="utf-8"))
    report.check(len(rows) == 26 and len(works) == 26, f"作品表 {len(rows)} 行 CSV、{len(works)} 条 JSON")
    report.check([r["aweme_id"] for r in rows] == [w["aweme_id"] for w in works], "CSV 与 JSON 的作品顺序一致")

    mismatches = []
    for row, item in zip(rows, works):
        for key in row:
            left = row[key]
            right = item[key]
            if key == "topic_tags":
                tags = [part for part in left.split("|") if part] if left else []
                if tags != right:
                    mismatches.append(row["aweme_id"] + ":" + key)
            elif key in {"duration_s", "width", "height", "digg_count", "comment_count", "collect_count", "share_count"}:
                if float(left) != float(right):
                    mismatches.append(row["aweme_id"] + ":" + key)
            elif left != right:
                mismatches.append(row["aweme_id"] + ":" + key)
    report.check(not mismatches, "CSV 与 JSON 字段一致" if not mismatches else "字段不一致 " + ",".join(mismatches[:8]))

    expected = {
        "7705909563958749561": 46.833,
        "7700491233940235685": 15.033,
        "7706308863466020571": 96.767,
    }
    for aweme_id, duration in expected.items():
        row = next(item for item in rows if item["aweme_id"] == aweme_id)
        report.check(
            row["duration_source"] == "ffprobe" and close(float(row["duration_s"]), duration),
            f"{aweme_id} 时长 {duration}（ffprobe）",
        )

    likes = [int(r["digg_count"]) for r in rows]
    comments = [int(r["comment_count"]) for r in rows]
    collects = [int(r["collect_count"]) for r in rows]
    shares = [int(r["share_count"]) for r in rows]
    durations = [float(r["duration_s"]) for r in rows]
    stats = snap["stats_in_sample"]
    report.check(close(stats["likes"]["median"], median(likes)), f"赞中位数 {stats['likes']['median']}")
    report.check(close(stats["comments"]["median"], median(comments)), f"评中位数 {stats['comments']['median']}")
    report.check(close(stats["collects"]["median"], median(collects)), f"藏中位数 {stats['collects']['median']}")
    report.check(close(stats["shares"]["median"], median(shares)), f"转中位数 {stats['shares']['median']}")
    report.check(close(stats["duration_s"]["median"], median(durations)), f"时长中位数 {stats['duration_s']['median']}")
    report.check(stats["likes"]["sum"] == sum(likes), f"样本赞数合计 {stats['likes']['sum']}")
    report.check(stats["likes"]["min"] == min(likes) and stats["likes"]["max"] == max(likes), "赞的最小最大与作品表一致")

    tags: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        for tag in [part for part in row["topic_tags"].split("|") if part]:
            tags.setdefault(tag, []).append(row)
    cats = snap["category_medians_descriptive_only"]
    report.check(cats["人物志"]["n"] == 12 and len(tags["人物志"]) == 12, "人物志按标签计 12 条")
    report.check(close(cats["人物志"]["like_median"], median([int(r["digg_count"]) for r in tags["人物志"]])), "人物志赞中位数与作品表一致")
    report.check(cats["七宗罪"]["n"] == 6 and cats["反事实"]["n"] == 4, "七宗罪 6 条、反事实 4 条")
    report.check(len(cats["untagged_aweme_ids"]) == 3, "未打标签 3 条")

    account = snap["account"]
    report.check(account["aweme_count_profile"] == 27 and account["posts_in_this_sample"] == 26, "资料页 27 条、样本 26 条")
    report.check("少 1 条" in snap["sample"]["count_discrepancy"] or "26" in snap["sample"]["count_discrepancy"], "快照写明 26 与 27 的差额")
    judgment = snap["user_judgment"]
    report.check(
        judgment["time_asia_shanghai"] == "2026-11-15 09:31"
        and "代码生成" in judgment["summary"]
        and "未取得作者工程源码独立核实" in judgment["evidence_level"],
        "代码生成记为 2026-11-15 09:31 的用户判断，且未把源码写成已核实",
    )
    report.check(snap["collection_method"]["requests"] == 4 and snap["collection_method"]["actual_fee_usd"] is None, "采集 4 次、实际费用为空（未核实）")

    analysis = (ROOT / "accounts" / "douyin" / "xiaoqu-danganguan" / "analysis.md").read_text(encoding="utf-8")
    for token in ("46.833", "15.033", "96.767", "洛水", "洺水", "项羽", "关羽", "待核查", "用户补充"):
        report.check(token in analysis, f"分析结论包含「{token}」")
    report.check("已证实" not in analysis and "已验证" not in analysis, "分析结论没有把制作手段写成已证实或已验证")

    frames = [
        SNAP / "keyframes" / "01-contact.jpg",
        SNAP / "keyframes" / "02-contact.jpg",
        SNAP / "keyframes" / "03-contact.jpg",
    ]
    for frame in frames:
        report.check(frame.is_file() and frame.stat().st_size > 0, f"关键帧存在 {frame.name}")
        try:
            has_exif = jpeg_has_exif(frame)
        except ValueError as exc:
            report.check(False, str(exc))
            continue
        report.check(not has_exif, f"{frame.name} 无 EXIF")
        sheet = (SNAP / "keyframes" / "README.md").read_text(encoding="utf-8")
        report.check(frame.name in sheet and "douyin.com/video/" in sheet, "关键帧说明含文件名和作品链接")


def main() -> int:
    report = Report()
    check_gitignore(report)
    check_snapshot(report)
    scan_text(report)
    for note in report.notes:
        print(f"通过  {note}")
    for error in report.errors:
        print(f"失败  {error}")
    print(f"合计  通过 {len(report.notes)}，失败 {len(report.errors)}")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())

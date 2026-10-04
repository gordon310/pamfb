#!/usr/bin/env python3
"""导出 GitHub 上餐饮需求答卷（Issues）为 CSV 与 Markdown 汇总。

用法：
    python3 scripts/export_issues.py --repo gordon310/pamfb \
        --label business-feedback --out ./exports

依赖：已安装并登录的 GitHub CLI (gh)。
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

# 题号 -> 简短列名（导出 CSV 用）
COLS = [
    ("submitter_name", "填写人"),
    ("hotel_name", "酒店"),
    ("dept", "部门"),
    ("fill_date", "填写日期"),
    ("q1", "1_数据换报告"),
    ("q2", "2_年费接受度"),
    ("q3", "3_报告类型"),
    ("q4", "4_城市区位"),
    ("q5", "5_酒店档次"),
    ("q6", "6_客房数"),
    ("q7", "7_餐饮单元"),
    ("q8", "8_近年份"),
    ("q9", "9_面积"),
    ("q10", "10_座位数"),
    ("q11", "11_业态归类"),
    ("q12", "12_收入颗粒度"),
    ("q13", "13_人数颗粒度"),
    ("q14", "14_宴会细分"),
    ("q15", "15_回溯区间"),
    ("q16", "16_更新频次"),
    ("q17", "17_投资额颗粒度"),
    ("q18", "18_投资构成"),
    ("q19", "19_开业改造年份"),
    ("q20", "20_投资录入方式"),
    ("q21", "21_投资口径"),
    ("q22", "22_回报指标"),
    ("q23", "23_是否扣成本"),
    ("q24", "24_回报对比维度"),
    ("q25", "25_基准周期"),
    ("q26", "26_敏感性分析"),
    ("q27", "27_回报呈现形式"),
    ("q28", "28_对标范围"),
    ("q29", "29_对比指标"),
    ("q30", "30_收入占比分析"),
    ("q31", "31_宴会独立分析"),
    ("q32", "32_平均消费维度"),
    ("q33", "33_竞对数据范围"),
    ("q34", "34_竞对营业额细分"),
    ("q35", "35_竞对指标"),
    ("q36", "36_竞对范围确定"),
    ("q37", "37_对标意愿"),
    ("q38", "38_社会餐饮类型"),
    ("q39", "39_社会餐饮指标"),
    ("q40", "40_社会餐饮获取"),
    ("q41", "41_社会餐饮付费"),
    ("q42", "42_上传方式"),
    ("q43", "43_是否脱敏"),
    ("q44", "44_数据权限"),
    ("q45", "45_保密协议"),
    ("q46", "46_报告形式"),
    ("q47", "47_报告频率"),
    ("q48", "48_付费方式"),
    ("q49", "49_回报顾问解读"),
    ("q50", "50_重点功能"),
    ("q51", "51_优先解决"),
    ("q52", "52_补充"),
]


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit("命令失败: " + " ".join(cmd))
    return result.stdout


def fetch_issues(repo, label):
    out = run([
        "gh", "issue", "list",
        "--repo", repo,
        "--label", label,
        "--state", "all",
        "--limit", "1000",
        "--json", "number,title,body,author,createdAt,url,state",
    ])
    return json.loads(out)


def parse_body(body):
    """把 Issue 正文解析为 {id: value}。兼容精简式、标题式与 HTML 表单生成的 Markdown。"""
    answers = {}
    current = None
    for raw in (body or "").splitlines():
        line = raw.rstrip()
        if not line:
            continue
        m4 = re.match(
            r"^[-*]\s*(填写人姓名|酒店名称|所属部门\s*/\s*岗位|填写日期)[：:]\s*(.+)$", line)
        if m4:
            key = {
                "填写人姓名": "submitter_name",
                "酒店名称": "hotel_name",
                "所属部门 / 岗位": "dept",
                "填写日期": "fill_date",
            }[m4.group(1)]
            answers[key] = m4.group(2).strip()
            continue
        mh = re.match(r"^(?:\*\*|#{2,3}\s*)(\d+)\.\s", line)
        if mh:
            current = "q" + mh.group(1)
            answers.setdefault(current, [])
            continue
        if not re.match(r"^[-*#>]", line):
            mq = re.match(r"^(\d+)\.\s+(.+)$", line)
            if mq:
                answers["q" + mq.group(1)] = mq.group(2).strip()
                continue
        if current:
            m2 = re.match(r"^\s*[-*]\s*\[(x| )\]\s*(.+)$", line)
            if m2:
                if m2.group(1).lower() == "x":
                    answers[current].append(m2.group(2).strip())
                continue
            m3 = re.match(r"^\s*[-*]\s*(.+)$", line)
            if m3:
                answers[current].append(m3.group(1).strip())
                continue
            if not re.match(r"^(#|>|---|\*\*)", line):
                answers[current].append(line.strip())
                continue
    for k, v in list(answers.items()):
        if isinstance(v, list):
            answers[k] = "；".join(v)
    return answers


def write_csv(issues, outdir):
    path = os.path.join(outdir, "business-feedback.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["issue", "url", "提交人", "创建时间", "状态"] + [c[1] for c in COLS])
        for it in issues:
            a = parse_body(it.get("body", ""))
            writer.writerow([
                it["number"], it["url"],
                (it.get("author") or {}).get("login", ""),
                it.get("createdAt", ""), it.get("state", ""),
            ] + [a.get(cid, "") for cid, _ in COLS])
    return path


def write_md(issues, outdir):
    path = os.path.join(outdir, "business-feedback.md")
    lines = ["# 餐饮需求答卷汇总", ""]
    for it in issues:
        a = parse_body(it.get("body", ""))
        lines.append("## #{n} {title}".format(n=it["number"], title=it.get("title", "").strip()))
        lines.append("")
        lines.append("- 提交人：{}".format((it.get("author") or {}).get("login", "")))
        lines.append("- 时间：{}".format(it.get("createdAt", "")))
        lines.append("- 链接：{}".format(it.get("url", "")))
        lines.append("")
        for cid, name in COLS:
            if a.get(cid):
                lines.append("- **{}**：{}".format(name, a[cid]))
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="OWNER/pamfb")
    ap.add_argument("--label", default="business-feedback")
    ap.add_argument("--out", default="./exports")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    issues = fetch_issues(args.repo, args.label)
    csv_path = write_csv(issues, args.out)
    md_path = write_md(issues, args.out)
    print("已导出 {} 份答卷：\n- {}\n- {}".format(len(issues), csv_path, md_path))


if __name__ == "__main__":
    main()

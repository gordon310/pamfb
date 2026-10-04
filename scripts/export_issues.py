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
    ("q1", "1_服务形态"),
    ("q2", "2_数据换报告"),
    ("q3", "3_年费接受度"),
    ("q4", "4_报告类型"),
    ("q5", "5_城市区位"),
    ("q6", "6_酒店档次"),
    ("q7", "7_客房数"),
    ("q8", "8_餐饮单元"),
    ("q9", "9_近年份"),
    ("q10", "10_面积"),
    ("q11", "11_座位数"),
    ("q12", "12_业态归类"),
    ("q13", "13_设施字段"),
    ("q14", "14_收入颗粒度"),
    ("q15", "15_人数颗粒度"),
    ("q16", "16_宴会细分"),
    ("q17", "17_回溯区间"),
    ("q18", "18_更新频次"),
    ("q19", "19_投资额颗粒度"),
    ("q20", "20_投资构成"),
    ("q21", "21_开业改造年份"),
    ("q22", "22_投资录入方式"),
    ("q23", "23_投资口径"),
    ("q24", "24_回报指标"),
    ("q25", "25_是否扣成本"),
    ("q26", "26_回报对比维度"),
    ("q27", "27_基准周期"),
    ("q28", "28_敏感性分析"),
    ("q29", "29_回报呈现形式"),
    ("q30", "30_对标范围"),
    ("q31", "31_对比指标"),
    ("q32", "32_收入占比分析"),
    ("q33", "33_宴会独立分析"),
    ("q34", "34_平均消费维度"),
    ("q35", "35_竞对数据范围"),
    ("q36", "36_竞对营业额细分"),
    ("q37", "37_竞对指标"),
    ("q38", "38_竞对范围确定"),
    ("q39", "39_对标意愿"),
    ("q40", "40_社会餐饮类型"),
    ("q41", "41_社会餐饮指标"),
    ("q42", "42_社会餐饮获取"),
    ("q43", "43_社会餐饮付费"),
    ("q44", "44_上传方式"),
    ("q45", "45_是否脱敏"),
    ("q46", "46_数据权限"),
    ("q47", "47_保密协议"),
    ("q48", "48_报告形式"),
    ("q49", "49_报告频率"),
    ("q50", "50_付费方式"),
    ("q51", "51_回报顾问解读"),
    ("q52", "52_重点功能"),
    ("q53", "53_优先解决"),
    ("q54", "54_补充"),
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

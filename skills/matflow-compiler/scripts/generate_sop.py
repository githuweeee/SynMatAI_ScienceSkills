#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MatFlow SOP 生成脚本

从 protocol.json 生成人类可读的标准操作程序（SOP）Markdown 文档。

SOP 包含以下部分：
1. 标题和协议信息
2. 配方表（材料、用量、单位）
3. 设备清单
4. 步骤列表（编号、操作、参数、证据引用）
5. 关键控制点（温度、时间、搅拌速度等）
6. 注意事项（安全警告、缺失参数）
7. 人工确认点

使用方式：
    python generate_sop.py protocol.json
    python generate_sop.py protocol.json --output SOP.md
"""

import json
import sys
import os
import argparse
from datetime import datetime


# ============================================================
# 常量定义
# ============================================================

# 原子操作中文名称映射
ACTION_NAMES = {
    "weigh":      "称量",
    "dissolve":   "溶解",
    "stir":       "搅拌",
    "heat":       "加热",
    "cool":       "冷却",
    "add":        "加入",
    "drop":       "滴加",
    "wash":       "洗涤",
    "filter":     "过滤",
    "centrifuge": "离心",
    "dry":        "干燥",
    "collect":    "收集",
    "transfer":   "转移",
    "purge":      "吹扫",
    "evacuate":   "抽空",
    "measure":    "测量",
    "wait":       "等待",
    "quench":     "淬灭",
}

# 步骤状态标记映射
STATUS_MARKS = {
    "ready":    "✅ ready",
    "warning":  "⚠️ warning",
    "blocked":  "🚫 blocked",
    "inferred": "🔒 inferred",
}

# 单位显示映射：将内部单位名转为人类可读符号
UNIT_DISPLAY = {
    # 温度
    "celsius":            "°C",
    "fahrenheit":         "°F",
    "kelvin":             "K",
    # 时间
    "second":             "s",
    "minute":             "min",
    "hour":               "h",
    "day":                "d",
    # 搅拌
    "rpm":                "rpm",
    # 质量
    "g":                  "g",
    "mg":                 "mg",
    "kg":                 "kg",
    # 体积
    "mL":                 "mL",
    "L":                  "L",
    # 物质的量
    "mol":                "mol",
    "mmol":               "mmol",
    # 百分比 / 当量
    "wt%":                "wt%",
    "vol%":               "vol%",
    "eq":                 "eq",
    # 压力
    "mbar":               "mbar",
    "bar":                "bar",
    "kPa":                "kPa",
    "MPa":                "MPa",
    "atm":                "atm",
    "torr":               "torr",
    # 升温速率
    "celsius_per_minute": "°C/min",
    "celsius_per_hour":   "°C/h",
}


# ============================================================
# 格式化辅助函数
# ============================================================

def format_unit(unit):
    """将内部单位名格式化为人类可读符号"""
    return UNIT_DISPLAY.get(unit, unit if unit else "")


def format_value(value, unit):
    """
    格式化数值与单位

    参数:
        value: 数值
        unit:  单位（内部名称）

    返回:
        格式化后的字符串，如 "80 °C"、"2 h"
    """
    if value is None:
        return "⚠️ 缺失参数"
    u = format_unit(unit)
    return f"{value} {u}".strip()


def format_evidence(ev):
    """
    格式化证据引用为可读字符串

    参数:
        ev: 证据字典

    返回:
        如 "DOC-001, p.5, 实施例1 (explicit, confidence: 0.98)"
    """
    doc = ev.get("document", "?")
    page = ev.get("page", "?")
    section = ev.get("section", "")
    etype = ev.get("evidence_type", "?")
    conf = ev.get("confidence", "?")

    parts = [str(doc), f"p.{page}"]
    if section:
        parts.append(str(section))
    ref = ", ".join(parts)

    return f"{ref} ({etype}, confidence: {conf})"


def get_step_evidence_ref(step):
    """
    从步骤中提取第一条证据的简短引用

    返回:
        如 "DOC-001 p.5"，无证据时返回 "—"
    """
    evidence_list = step.get("evidence", [])
    if evidence_list and isinstance(evidence_list, list):
        ev = evidence_list[0]
        doc = ev.get("document", "?")
        page = ev.get("page", "?")
        return f"{doc} p.{page}"
    return "—"


# ============================================================
# SOP 生成主函数
# ============================================================

def generate_sop(protocol):
    """
    从协议字典生成 Markdown 格式的 SOP

    参数:
        protocol: 解析后的协议字典

    返回:
        Markdown 格式的 SOP 字符串
    """
    lines = []

    # ============================================================
    # 第一部分：标题和协议信息
    # ============================================================
    lines.append("# 实验标准操作程序 (SOP)")
    lines.append("")

    protocol_id = protocol.get("protocol_id", "未知")
    material = protocol.get("material", "未知")

    # 生成时间：优先使用协议 metadata 中的时间，否则使用当前时间
    meta = protocol.get("metadata", {})
    if isinstance(meta, dict) and "generated_at" in meta:
        generated_at = meta["generated_at"]
    else:
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append(f"**协议ID**: {protocol_id}  ")
    lines.append(f"**目标材料**: {material}  ")
    lines.append(f"**生成时间**: {generated_at}")
    lines.append("")

    # 协议状态与综合置信度
    overall_status = protocol.get("overall_status", "")
    overall_conf = protocol.get("overall_confidence", "")
    if overall_status or overall_conf:
        if overall_status:
            status_mark = STATUS_MARKS.get(overall_status, overall_status)
            lines.append(f"**协议状态**: {status_mark}  ")
        if overall_conf:
            lines.append(f"**综合置信度**: {overall_conf}")
        lines.append("")

    # 源文档列表
    source_docs = protocol.get("source_documents", [])
    if source_docs:
        doc_names = [d.get("title", d.get("doc_id", "?")) for d in source_docs]
        lines.append(f"**源文档**: {', '.join(doc_names)}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # ============================================================
    # 第二部分：配方表
    # ============================================================
    lines.append("## 配方表")
    lines.append("")

    reagents = protocol.get("reagents", [])
    if reagents:
        # 从 reagents 列表生成配方表
        lines.append("| 序号 | 材料 | 用量 | 单位 | 证据 |")
        lines.append("|------|------|------|------|------|")
        for i, reg in enumerate(reagents, 1):
            name = reg.get("name", "未知")
            total = reg.get("total_amount", {})
            value = total.get("value", "—") if total else "—"
            unit = total.get("unit", "") if total else ""

            # 尝试从步骤中查找该材料的证据引用
            evidence_str = "—"
            for step in protocol.get("steps", []):
                if step.get("material") == name and step.get("evidence"):
                    evidence_str = get_step_evidence_ref(step)
                    break

            lines.append(
                f"| {i} | {name} | {value} | {format_unit(unit)} | {evidence_str} |"
            )
    else:
        # 无 reagents 时，从步骤中提取材料信息
        lines.append("| 序号 | 材料 | 用量 | 单位 | 证据 |")
        lines.append("|------|------|------|------|------|")
        idx = 1
        seen = set()
        for step in protocol.get("steps", []):
            mat_name = step.get("material", "")
            amount = step.get("amount")
            if mat_name and mat_name not in seen:
                seen.add(mat_name)
                value = "—"
                unit = ""
                if amount and isinstance(amount, dict):
                    value = amount.get("value", "—")
                    unit = amount.get("unit", "")
                evidence_str = get_step_evidence_ref(step)
                lines.append(
                    f"| {idx} | {mat_name} | {value} | {format_unit(unit)} | {evidence_str} |"
                )
                idx += 1

    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # 第三部分：设备清单
    # ============================================================
    lines.append("## 设备清单")
    lines.append("")

    equipment = protocol.get("equipment", [])
    if equipment:
        lines.append("| 设备 | 类型 | 状态 |")
        lines.append("|------|------|------|")
        for eq in equipment:
            dev_id = eq.get("device_id", "未知")
            dev_type = eq.get("device_type", "未知")
            dev_name = eq.get("device_name", dev_id)

            # 检查设备是否在步骤中被绑定
            bound = False
            for step in protocol.get("steps", []):
                binding = step.get("device_binding", {})
                if isinstance(binding, dict) and binding.get("device_id") == dev_id:
                    bound = True
                    break

            status = "✅ 已绑定" if bound else "⬜ 未绑定"
            lines.append(f"| {dev_name} | {dev_type} | {status} |")
    else:
        lines.append("无设备信息")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # 第四部分：实验步骤
    # ============================================================
    lines.append("## 实验步骤")
    lines.append("")

    steps = protocol.get("steps", [])
    for step in steps:
        sid = step.get("step_id", "?")
        action = step.get("action", "未知")
        action_name = ACTION_NAMES.get(action, action)
        material = step.get("material", "")
        status = step.get("status", "")

        lines.append(f"### 步骤 {sid}: {action_name}")
        lines.append("")

        # 操作描述
        if material:
            lines.append(f"- **操作**: {action_name} {material}")
        else:
            lines.append(f"- **操作**: {action_name}")

        # 用量
        amount = step.get("amount")
        if amount and isinstance(amount, dict):
            val = amount.get("value")
            unit = amount.get("unit", "")
            tol = amount.get("tolerance")
            amount_str = format_value(val, unit)
            if tol is not None:
                amount_str += f" (±{tol} {format_unit(unit)})".strip()
            lines.append(f"- **用量**: {amount_str}")

        # 温度
        temp = step.get("temperature")
        if temp and isinstance(temp, dict):
            val = temp.get("value")
            unit = temp.get("unit", "")
            temp_str = format_value(val, unit)
            # 升温速率
            ramp = temp.get("ramp_rate")
            if ramp and isinstance(ramp, dict):
                ramp_str = format_value(ramp.get("value"), ramp.get("unit"))
                temp_str += f" (升温速率: {ramp_str})"
            # 保温标记
            if temp.get("hold"):
                temp_str += " (保温)"
            lines.append(f"- **温度**: {temp_str}")

        # 持续时间
        duration = step.get("duration")
        if duration and isinstance(duration, dict):
            val = duration.get("value")
            unit = duration.get("unit", "")
            lines.append(f"- **持续时间**: {format_value(val, unit)}")
        else:
            # 检查是否有缺失的 duration 字段
            has_missing_duration = any(
                "duration" in mf.get("field_name", "")
                for mf in step.get("missing_fields", [])
            )
            if has_missing_duration:
                lines.append("- **持续时间**: ⚠️ 缺失参数 - 需要人工确认")

        # 搅拌速度
        stirring = step.get("stirring_speed")
        if stirring and isinstance(stirring, dict):
            val = stirring.get("value")
            unit = stirring.get("unit", "")
            lines.append(f"- **搅拌速度**: {format_value(val, unit)}")

        # 气氛
        atmosphere = step.get("atmosphere")
        if atmosphere:
            lines.append(f"- **气氛**: {atmosphere}")

        # 压力
        pressure = step.get("pressure")
        if pressure and isinstance(pressure, dict):
            val = pressure.get("value")
            unit = pressure.get("unit", "")
            lines.append(f"- **压力**: {format_value(val, unit)}")

        # 设备绑定
        binding = step.get("device_binding", {})
        if binding and isinstance(binding, dict) and binding.get("device_id"):
            dev_id = binding.get("device_id", "")
            cap_check = binding.get("capability_check", "")
            lines.append(f"- **设备**: {dev_id} (能力检查: {cap_check})")

        # 证据引用
        evidence_list = step.get("evidence", [])
        if evidence_list:
            for ev in evidence_list:
                lines.append(f"- **证据**: {format_evidence(ev)}")

        # 步骤状态
        if status:
            status_mark = STATUS_MARKS.get(status, status)
            lines.append(f"- **状态**: {status_mark}")

        # 缺失字段
        missing_fields = step.get("missing_fields", [])
        if missing_fields:
            lines.append("")
            lines.append("**缺失字段**:")
            for mf in missing_fields:
                field = mf.get("field_name", "?")
                risk = mf.get("risk_level", "?")
                blocks = mf.get("blocks_execution", False)
                suggestion = mf.get("suggestion", "")
                requires_conf = mf.get("requires_confirmation", False)

                # 阻塞执行用 🚫，否则用 ⚠️
                marker = "🚫" if blocks else "⚠️"
                conf_marker = " 🔒 需人工确认" if requires_conf else ""
                suggestion_str = f" (建议: {suggestion})" if suggestion else ""

                lines.append(
                    f"- {marker} {field} (风险: {risk}){suggestion_str}{conf_marker}"
                )

        # 人工备注
        notes = step.get("notes")
        if notes:
            lines.append(f"- **备注**: {notes}")

        lines.append("")

    lines.append("---")
    lines.append("")

    # ============================================================
    # 第五部分：关键控制点
    # ============================================================
    lines.append("## 关键控制点")
    lines.append("")

    control_points = []
    for step in steps:
        sid = step.get("step_id", "?")

        # 温度控制点
        temp = step.get("temperature")
        if temp and isinstance(temp, dict) and temp.get("value") is not None:
            val = temp.get("value")
            unit = format_unit(temp.get("unit", ""))
            control_points.append(f"- {sid}: 温度 {val}{unit}")

        # 搅拌速度控制点
        stirring = step.get("stirring_speed")
        if stirring and isinstance(stirring, dict) and stirring.get("value") is not None:
            val = stirring.get("value")
            unit = format_unit(stirring.get("unit", ""))
            control_points.append(f"- {sid}: 搅拌速度 {val} {unit}")

        # 持续时间控制点
        duration = step.get("duration")
        if duration and isinstance(duration, dict) and duration.get("value") is not None:
            val = duration.get("value")
            unit = format_unit(duration.get("unit", ""))
            control_points.append(f"- {sid}: 时间 {val} {unit}")

        # 压力控制点
        pressure = step.get("pressure")
        if pressure and isinstance(pressure, dict) and pressure.get("value") is not None:
            val = pressure.get("value")
            unit = format_unit(pressure.get("unit", ""))
            control_points.append(f"- {sid}: 压力 {val} {unit}")

    if control_points:
        lines.extend(control_points)
    else:
        lines.append("无关键控制点")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # 第六部分：注意事项
    # ============================================================
    lines.append("## 注意事项")
    lines.append("")

    notes_list = []

    # 从安全检查中提取注意事项
    safety_checks = protocol.get("safety_checks", [])
    for check in safety_checks:
        target = check.get("target_step", "?")
        status = check.get("status", "")
        message = check.get("message", "")

        if status == "blocked":
            notes_list.append(f"- 🚫 {target}: {message}")
        elif status == "warning":
            notes_list.append(f"- ⚠️ {target}: {message}")

    # 从步骤缺失字段中提取注意事项
    for step in steps:
        sid = step.get("step_id", "?")
        for mf in step.get("missing_fields", []):
            field = mf.get("field_name", "?")
            risk = mf.get("risk_level", "?")
            blocks = mf.get("blocks_execution", False)
            requires_conf = mf.get("requires_confirmation", False)

            if blocks:
                notes_list.append(
                    f"- 🚫 {sid}: {field} 缺失，阻塞执行 (风险: {risk})"
                )
            elif risk == "high":
                notes_list.append(
                    f"- ⚠️ {sid}: {field} 缺失，高风险 (风险: {risk})"
                )
            elif requires_conf:
                notes_list.append(f"- 🔒 {sid}: {field} 需要人工确认")

    # 从 inferred 状态步骤中提取注意事项
    for step in steps:
        sid = step.get("step_id", "?")
        if step.get("status") == "inferred":
            notes_list.append(f"- 🔒 {sid}: 含推断参数，需要人工确认后方可执行")

    if notes_list:
        # 去重并保持顺序
        seen = set()
        unique_notes = []
        for note in notes_list:
            if note not in seen:
                seen.add(note)
                unique_notes.append(note)
        lines.extend(unique_notes)
    else:
        lines.append("无特别注意事项")

    lines.append("")
    lines.append("---")
    lines.append("")

    # ============================================================
    # 第七部分：人工确认点
    # ============================================================
    lines.append("## 人工确认点")
    lines.append("")

    confirmation_points = []

    for step in steps:
        sid = step.get("step_id", "?")

        # inferred 状态步骤需要确认
        if step.get("status") == "inferred":
            confirmation_points.append(f"- {sid}: 步骤含推断参数，需人工确认")

        # missing_fields 中需要确认的
        for mf in step.get("missing_fields", []):
            if mf.get("requires_confirmation"):
                field = mf.get("field_name", "?")
                suggestion = mf.get("suggestion", "")
                suggestion_str = f" (建议值: {suggestion})" if suggestion else ""
                confirmation_points.append(
                    f"- {sid}: {field} 需人工确认{suggestion_str}"
                )

    # 安全检查中需要确认的
    for check in safety_checks:
        if check.get("status") == "warning":
            target = check.get("target_step", "?")
            message = check.get("message", "")
            confirmation_points.append(f"- {target}: {message}")

    if confirmation_points:
        # 去重并保持顺序
        seen = set()
        unique_points = []
        for point in confirmation_points:
            if point not in seen:
                seen.add(point)
                unique_points.append(point)
        lines.extend(unique_points)
    else:
        lines.append("无人工确认点")

    lines.append("")

    return "\n".join(lines)


# ============================================================
# 命令行入口
# ============================================================

def main():
    """命令行主入口函数"""
    parser = argparse.ArgumentParser(
        description="MatFlow SOP 生成脚本 - 从 protocol.json 生成人类可读 SOP"
    )
    parser.add_argument(
        "protocol_file",
        help="protocol.json 文件路径",
    )
    parser.add_argument(
        "--output", "-o",
        dest="output_file",
        default=None,
        help="输出 MD 文件路径（不指定则输出到 stdout）",
    )

    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.isfile(args.protocol_file):
        print(f"错误: 文件不存在: {args.protocol_file}")
        sys.exit(1)

    # 读取并解析 JSON 文件
    try:
        with open(args.protocol_file, "r", encoding="utf-8") as f:
            protocol = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 文件读取失败: {e}")
        sys.exit(1)

    # 生成 SOP
    sop_text = generate_sop(protocol)

    # 输出
    if args.output_file:
        try:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(sop_text)
            print(f"SOP 已生成至: {args.output_file}")
        except Exception as e:
            print(f"错误: 文件写入失败: {e}")
            sys.exit(1)
    else:
        print(sop_text)


if __name__ == "__main__":
    main()

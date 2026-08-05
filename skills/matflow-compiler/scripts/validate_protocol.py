#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MatFlow Protocol 验证脚本

验证生成的 protocol.json 是否符合 MatFlow Compiler 规范。

检查项包括：
1. 顶层必需字段（protocol_id, material, steps 等）
2. 步骤字段完整性（step_id, action）
3. 证据字段完整性（document, page, section, evidence_type）
4. 置信度范围（0.0-1.0）
5. 缺失字段 risk_level 合法性（high/medium/low）
6. 单位一致性（同一物质在不同步骤中的单位是否可转换）
7. 步骤依赖完整性（depends_on 引用的 step_id 是否存在）
8. 静默补全检测（inferred 类型字段是否标记了 require_confirmation）
9. 安全检查与检查点引用完整性

使用方式：
    python validate_protocol.py protocol.json
    python validate_protocol.py protocol.json --report report.json
"""

import json
import sys
import os
import argparse
import re


# ============================================================
# 常量定义
# ============================================================

# 协议顶层必需字段
REQUIRED_TOP_FIELDS = ["protocol_id", "material", "source_documents", "steps", "metadata"]

# 步骤必需字段
REQUIRED_STEP_FIELDS = ["step_id", "action", "evidence", "confidence", "status"]

# 证据必需字段（缺失则判定为失败）
REQUIRED_EVIDENCE_FIELDS = ["document", "page", "quote", "evidence_type", "confidence"]

# 证据推荐字段（缺失则产生警告）
RECOMMENDED_EVIDENCE_FIELDS = ["section"]

# 合法的 evidence_type 值
VALID_EVIDENCE_TYPES = {"explicit", "derived", "inferred"}

# 合法的 risk_level 值
VALID_RISK_LEVELS = {"high", "medium", "low"}

# 合法的步骤状态值
VALID_STEP_STATUSES = {"ready", "warning", "blocked", "inferred"}

# 合法的原子操作类型
VALID_ACTIONS = {
    "weigh", "dissolve", "stir", "heat", "cool", "add", "drop",
    "wash", "filter", "centrifuge", "dry", "collect", "transfer",
    "purge", "evacuate", "measure", "wait", "quench",
}

# 合法的安全检查状态值
VALID_SAFETY_STATUSES = {"pass", "warning", "blocked"}

# 单位类别映射：同一物理量类别内的单位可互相转换
UNIT_CATEGORIES = {
    # 质量
    "g": "mass", "mg": "mass", "kg": "mass",
    # 体积
    "mL": "volume", "L": "volume",
    # 物质的量
    "mol": "amount", "mmol": "amount",
    # 温度
    "celsius": "temperature", "fahrenheit": "temperature", "kelvin": "temperature",
    # 时间
    "second": "time", "minute": "time", "hour": "time", "day": "time",
    # 搅拌速度
    "rpm": "stirring_speed",
    # 压力
    "mbar": "pressure", "bar": "pressure", "kPa": "pressure",
    "MPa": "pressure", "atm": "pressure", "torr": "pressure",
    # 百分比 / 当量
    "wt%": "percentage", "vol%": "percentage", "eq": "equivalent",
}

# 协议 ID 正则：PROTO-<MATERIAL>-<8位十六进制>
PROTOCOL_ID_PATTERN = re.compile(r"^PROTO-[A-Z0-9]+-[a-f0-9]{8}$")

# 步骤 ID 正则：S<两位数字>
STEP_ID_PATTERN = re.compile(r"^S\d{2}$")


# ============================================================
# 验证结果与报告类
# ============================================================

class ValidationItem:
    """单条验证结果项"""

    def __init__(self, level, message):
        """
        初始化验证结果项

        参数:
            level:   结果级别，取值 "pass" / "warning" / "fail"
            message: 结果描述信息
        """
        self.level = level
        self.message = message

    def __str__(self):
        """格式化为带前缀的字符串"""
        prefix_map = {
            "pass":    "[通过]",
            "warning": "[警告]",
            "fail":    "[失败]",
        }
        prefix = prefix_map.get(self.level, "[未知]")
        return f"{prefix} {self.message}"


class ValidationReport:
    """验证报告，收集并汇总所有验证结果"""

    def __init__(self, file_path):
        """
        初始化验证报告

        参数:
            file_path: 被验证的 JSON 文件路径
        """
        self.file_path = file_path
        self.items = []

    # ---- 添加结果 ----

    def add(self, level, message):
        """添加一条验证结果"""
        self.items.append(ValidationItem(level, message))

    def add_pass(self, message):
        """添加通过项"""
        self.add("pass", message)

    def add_warning(self, message):
        """添加警告项"""
        self.add("warning", message)

    def add_fail(self, message):
        """添加失败项"""
        self.add("fail", message)

    # ---- 统计属性 ----

    @property
    def pass_count(self):
        """通过项数量"""
        return sum(1 for i in self.items if i.level == "pass")

    @property
    def warning_count(self):
        """警告项数量"""
        return sum(1 for i in self.items if i.level == "warning")

    @property
    def fail_count(self):
        """失败项数量"""
        return sum(1 for i in self.items if i.level == "fail")

    @property
    def result(self):
        """
        总体验证结果：
        - 有失败项 -> FAIL
        - 有警告项 -> WARN
        - 全部通过 -> PASS
        """
        if self.fail_count > 0:
            return "FAIL"
        if self.warning_count > 0:
            return "WARN"
        return "PASS"

    # ---- 输出格式 ----

    def to_text(self):
        """生成文本格式的验证报告（用于 stdout 输出）"""
        lines = []
        lines.append("=== MatFlow Protocol 验证报告 ===")
        lines.append(f"文件: {self.file_path}")
        lines.append("")
        for item in self.items:
            lines.append(str(item))
        lines.append("")
        lines.append(
            f"总计: {self.pass_count} 通过, "
            f"{self.warning_count} 警告, "
            f"{self.fail_count} 失败"
        )
        lines.append(f"验证结果: {self.result}")
        return "\n".join(lines)

    def to_dict(self):
        """生成字典格式的验证报告（用于 JSON 文件输出）"""
        return {
            "file": self.file_path,
            "summary": {
                "pass": self.pass_count,
                "warning": self.warning_count,
                "fail": self.fail_count,
            },
            "result": self.result,
            "items": [
                {"level": i.level, "message": i.message}
                for i in self.items
            ],
        }


# ============================================================
# 验证函数
# ============================================================

def validate_top_level(protocol, report):
    """
    检查协议顶层结构

    验证必需字段是否存在，protocol_id 格式是否合法，
    steps 和 source_documents 是否为非空数组。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    # 检查必需字段
    missing = [f for f in REQUIRED_TOP_FIELDS if f not in protocol]
    if missing:
        report.add_fail(f"协议顶层缺少必需字段: {', '.join(missing)}")
    else:
        report.add_pass("协议顶层结构检查")

    # 检查 protocol_id 格式
    pid = protocol.get("protocol_id", "")
    if pid and not PROTOCOL_ID_PATTERN.match(str(pid)):
        report.add_warning(
            f"protocol_id '{pid}' 不符合格式 PROTO-<MATERIAL>-<hash8>，"
            f"例如 PROTO-EPOXY-a1b2c3d4"
        )

    # 检查 steps 非空
    steps = protocol.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        report.add_fail("steps 字段必须为非空数组")

    # 检查 source_documents 非空
    docs = protocol.get("source_documents")
    if not isinstance(docs, list) or len(docs) == 0:
        report.add_fail("source_documents 字段必须为非空数组")


def validate_steps(protocol, report):
    """
    检查每个步骤的字段完整性

    验证 step_id 和 action 是否存在且合法，status 是否合法，
    step_id 是否重复。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])
    if not steps:
        return

    step_ids_seen = set()
    all_valid = True

    for step in steps:
        sid = step.get("step_id", "<未知>")

        # 检查必需字段
        missing = [f for f in REQUIRED_STEP_FIELDS if f not in step]
        if missing:
            report.add_fail(f"步骤 {sid}: 缺少必需字段: {', '.join(missing)}")
            all_valid = False

        # 检查 step_id 格式
        if "step_id" in step:
            if not STEP_ID_PATTERN.match(str(step["step_id"])):
                report.add_warning(
                    f"步骤 {sid}: step_id '{step['step_id']}' "
                    f"不符合 S<序号> 格式（如 S01）"
                )
            # 检查重复
            if step["step_id"] in step_ids_seen:
                report.add_fail(f"步骤 {sid}: step_id 重复")
                all_valid = False
            step_ids_seen.add(step["step_id"])

        # 检查 action 合法性
        action = step.get("action", "")
        if action and action not in VALID_ACTIONS:
            report.add_fail(
                f"步骤 {sid}: action '{action}' 不合法，"
                f"应为: {', '.join(sorted(VALID_ACTIONS))}"
            )

        # 检查 status 合法性
        status = step.get("status", "")
        if status and status not in VALID_STEP_STATUSES:
            report.add_fail(
                f"步骤 {sid}: status '{status}' 不合法，"
                f"应为: {', '.join(sorted(VALID_STEP_STATUSES))}"
            )

    # 全部步骤字段完整时统一报告通过
    if all_valid:
        report.add_pass(f"步骤字段检查 ({len(steps)} steps)")


def validate_evidence(protocol, report):
    """
    检查证据字段完整性

    验证每条证据是否包含必需字段（document, page, quote,
    evidence_type, confidence）以及推荐字段（section）。
    同时检查 evidence_type 合法性、document 引用是否存在、
    page 是否为正整数、inferred/derived 是否有 derivation。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])
    doc_ids = {
        d.get("doc_id") for d in protocol.get("source_documents", [])
        if isinstance(d, dict)
    }

    for step in steps:
        sid = step.get("step_id", "<未知>")
        evidence_list = step.get("evidence", [])

        if not isinstance(evidence_list, list) or len(evidence_list) == 0:
            report.add_fail(f"步骤 {sid}: evidence 为空或非数组，至少需要 1 条证据")
            continue

        for i, ev in enumerate(evidence_list):
            label = f"步骤 {sid} evidence[{i}]"

            # 检查必需字段
            missing = [f for f in REQUIRED_EVIDENCE_FIELDS if f not in ev]
            if missing:
                report.add_fail(f"{label}: 缺少必需字段: {', '.join(missing)}")

            # 检查推荐字段（section）
            for field in RECOMMENDED_EVIDENCE_FIELDS:
                if field not in ev:
                    report.add_warning(f"{label}: 缺少推荐字段 '{field}'")

            # 检查 evidence_type 合法性
            etype = ev.get("evidence_type", "")
            if etype and etype not in VALID_EVIDENCE_TYPES:
                report.add_fail(
                    f"{label}: evidence_type '{etype}' 不合法，"
                    f"应为: {', '.join(sorted(VALID_EVIDENCE_TYPES))}"
                )

            # 检查 document 引用是否存在
            doc_ref = ev.get("document", "")
            if doc_ref and doc_ids and doc_ref not in doc_ids:
                report.add_warning(
                    f"{label}: document '{doc_ref}' 未在 source_documents 中找到"
                )

            # 检查 page 是否为正整数
            page = ev.get("page")
            if page is not None:
                if not isinstance(page, int) or page < 1:
                    report.add_fail(
                        f"{label}: page 值 '{page}' 不合法，应为 >= 1 的整数"
                    )

            # 检查 inferred / derived 是否有 derivation
            if etype in ("inferred", "derived") and "derivation" not in ev:
                report.add_warning(
                    f"{label}: evidence_type 为 {etype} 但缺少 derivation 字段"
                )


def validate_confidence(protocol, report):
    """
    检查置信度值范围

    验证步骤置信度、证据置信度和全流程置信度是否在 [0.0, 1.0] 范围内。
    对低于 0.5 的置信度产生警告。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])

    for step in steps:
        sid = step.get("step_id", "<未知>")

        # 步骤置信度
        conf = step.get("confidence")
        if conf is not None:
            if not isinstance(conf, (int, float)):
                report.add_fail(f"步骤 {sid}: confidence 值类型不合法，应为数值")
            elif conf < 0.0 or conf > 1.0:
                report.add_fail(f"步骤 {sid}: confidence = {conf}，超出范围 [0.0, 1.0]")
            elif conf < 0.5:
                report.add_warning(
                    f"步骤 {sid}: evidence.confidence = {conf}，建议提高证据质量"
                )

        # 证据置信度
        for i, ev in enumerate(step.get("evidence", [])):
            ev_conf = ev.get("confidence")
            if ev_conf is not None:
                if not isinstance(ev_conf, (int, float)):
                    report.add_fail(
                        f"步骤 {sid} evidence[{i}]: confidence 值类型不合法，应为数值"
                    )
                elif ev_conf < 0.0 or ev_conf > 1.0:
                    report.add_fail(
                        f"步骤 {sid} evidence[{i}]: confidence = {ev_conf}，"
                        f"超出范围 [0.0, 1.0]"
                    )

    # 全流程置信度
    overall = protocol.get("overall_confidence")
    if overall is not None:
        if not isinstance(overall, (int, float)):
            report.add_fail("overall_confidence 值类型不合法，应为数值")
        elif overall < 0.0 or overall > 1.0:
            report.add_fail(f"overall_confidence = {overall}，超出范围 [0.0, 1.0]")


def validate_missing_fields(protocol, report):
    """
    检查缺失字段的 risk_level 是否合法

    验证 missing_fields 中 risk_level 值是否为 high/medium/low，
    blocks_execution 是否存在，high 风险是否标记为阻塞执行。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])

    for step in steps:
        sid = step.get("step_id", "<未知>")
        missing_fields = step.get("missing_fields", [])
        if not missing_fields:
            continue

        for mf in missing_fields:
            field_name = mf.get("field_name", "<未知>")

            # 检查 risk_level 合法性
            risk = mf.get("risk_level", "")
            if risk and risk not in VALID_RISK_LEVELS:
                report.add_fail(
                    f"步骤 {sid}: missing_fields 中 risk_level 值 '{risk}' 不合法, "
                    f"应为 high/medium/low"
                )

            # 检查 blocks_execution 是否存在
            if "blocks_execution" not in mf:
                report.add_warning(
                    f"步骤 {sid}: missing_fields '{field_name}' "
                    f"缺少 blocks_execution 字段"
                )

            # high 风险应阻塞执行
            if risk == "high" and mf.get("blocks_execution") is False:
                report.add_warning(
                    f"步骤 {sid}: missing_fields '{field_name}' risk_level 为 high "
                    f"但 blocks_execution 为 false"
                )


def validate_unit_consistency(protocol, report):
    """
    检查单位一致性

    验证同一物质在不同步骤中使用的单位是否属于同一物理量类别
    （即可互相转换）。覆盖 amount、temperature、duration 三类参数。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])

    # 收集每种物质在各步骤中使用的单位
    # 结构: { material: { param_name: [(step_id, unit), ...] } }
    material_units = {}

    for step in steps:
        sid = step.get("step_id", "<未知>")
        material = step.get("material", "")
        if not material:
            continue

        if material not in material_units:
            material_units[material] = {}

        # 检查 amount / temperature / duration 的单位
        for param_name, param_key in [
            ("amount", "amount"),
            ("temperature", "temperature"),
            ("duration", "duration"),
        ]:
            param = step.get(param_key)
            if param and isinstance(param, dict) and "unit" in param:
                material_units[material].setdefault(param_name, []).append(
                    (sid, param["unit"])
                )

    # 检查同一物质的同类参数单位是否可转换
    found_inconsistency = False
    for material, param_map in material_units.items():
        for param_name, unit_list in param_map.items():
            if len(unit_list) < 2:
                continue

            categories = set()
            for sid, unit in unit_list:
                cat = UNIT_CATEGORIES.get(unit)
                if cat:
                    categories.add(cat)
                else:
                    report.add_warning(
                        f"物质 '{material}' 步骤 {sid}: 未知单位 '{unit}'，"
                        f"无法验证一致性"
                    )

            if len(categories) > 1:
                found_inconsistency = True
                unit_strs = [f"{sid}:{u}" for sid, u in unit_list]
                report.add_fail(
                    f"物质 '{material}' 的 {param_name} 单位不一致: "
                    f"{', '.join(unit_strs)}，单位类别不可转换"
                )

    if not found_inconsistency:
        report.add_pass("单位一致性检查")


def validate_dependencies(protocol, report):
    """
    检查步骤依赖完整性

    验证 depends_on 引用的 step_id 是否存在。
    depends_on 为可选字段，仅当存在时才进行验证。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])
    step_ids = {s.get("step_id") for s in steps if "step_id" in s}

    has_deps = False
    for step in steps:
        sid = step.get("step_id", "<未知>")
        depends_on = step.get("depends_on", [])

        if depends_on:
            has_deps = True
            for dep_id in depends_on:
                if dep_id not in step_ids:
                    report.add_fail(
                        f"步骤 {sid}: depends_on 引用的 step_id '{dep_id}' 不存在"
                    )

    if has_deps:
        report.add_pass("步骤依赖完整性检查")


def validate_no_silent_inference(protocol, report):
    """
    检查是否有静默补全

    验证 inferred 类型的证据是否正确标记了 require_confirmation，
    以及步骤状态是否与证据类型一致。
    核心原则：绝不静默补全，推断参数必须暴露并要求人工确认。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])

    for step in steps:
        sid = step.get("step_id", "<未知>")

        # 检查 evidence 中是否有 inferred 类型
        has_inferred_evidence = False
        for ev in step.get("evidence", []):
            if ev.get("evidence_type") == "inferred":
                has_inferred_evidence = True
                if "derivation" not in ev:
                    report.add_warning(
                        f"步骤 {sid}: inferred 类型证据缺少 derivation 字段"
                    )

        # 有 inferred 证据时，步骤状态应为 inferred
        if has_inferred_evidence:
            status = step.get("status", "")
            if status != "inferred":
                report.add_warning(
                    f"步骤 {sid}: 含有 inferred 类型证据但状态为 '{status}'，"
                    f"建议设为 'inferred'"
                )

        # 检查 missing_fields 中有建议值但未标记需要确认的情况
        for mf in step.get("missing_fields", []):
            field_name = mf.get("field_name", "<未知>")
            suggestion = mf.get("suggestion")
            requires_conf = mf.get("requires_confirmation")

            # 有建议值但未标记需要确认 -> 可能是静默补全
            if suggestion and requires_conf is not True:
                report.add_fail(
                    f"步骤 {sid}: inferred 类型字段 '{field_name}' "
                    f"未标记 require_confirmation"
                )

        # 步骤状态为 inferred 时，所有 missing_fields 都应标记 requires_confirmation
        if step.get("status") == "inferred":
            for mf in step.get("missing_fields", []):
                field_name = mf.get("field_name", "<未知>")
                if mf.get("requires_confirmation") is not True:
                    report.add_fail(
                        f"步骤 {sid}: inferred 类型字段 '{field_name}' "
                        f"未标记 require_confirmation"
                    )


def validate_safety_checks(protocol, report):
    """
    检查安全检查的引用完整性

    验证 safety_checks 中 target_step 引用的步骤是否存在，
    status 值是否合法。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])
    step_ids = {s.get("step_id") for s in steps if "step_id" in s}

    safety_checks = protocol.get("safety_checks", [])
    if not safety_checks:
        return

    for check in safety_checks:
        check_id = check.get("check_id", "<未知>")
        target = check.get("target_step", "")

        # 检查 target_step 引用
        if target and target not in step_ids:
            report.add_fail(
                f"安全检查 {check_id}: target_step '{target}' 引用的步骤不存在"
            )

        # 检查 status 合法性
        status = check.get("status", "")
        if status and status not in VALID_SAFETY_STATUSES:
            report.add_fail(
                f"安全检查 {check_id}: status '{status}' 不合法，"
                f"应为: {', '.join(sorted(VALID_SAFETY_STATUSES))}"
            )

    report.add_pass(f"安全检查引用检查 ({len(safety_checks)} checks)")


def validate_checkpoints(protocol, report):
    """
    检查检查点引用完整性

    验证 checkpoints 中 after_step 引用的步骤是否存在。

    参数:
        protocol: 解析后的协议字典
        report:   验证报告对象
    """
    steps = protocol.get("steps", [])
    step_ids = {s.get("step_id") for s in steps if "step_id" in s}

    checkpoints = protocol.get("checkpoints", [])
    if not checkpoints:
        return

    for cp in checkpoints:
        cp_id = cp.get("checkpoint_id", "<未知>")
        after_step = cp.get("after_step", "")

        if after_step and after_step not in step_ids:
            report.add_fail(
                f"检查点 {cp_id}: after_step '{after_step}' 引用的步骤不存在"
            )

    report.add_pass(f"检查点引用检查 ({len(checkpoints)} checkpoints)")


# ============================================================
# 主验证流程
# ============================================================

def validate_protocol(protocol, file_path):
    """
    执行完整的协议验证

    按顺序调用各验证函数，收集所有验证结果。

    参数:
        protocol:  解析后的协议字典
        file_path: 被验证的 JSON 文件路径

    返回:
        ValidationReport 对象
    """
    report = ValidationReport(file_path)

    # 1. 顶层结构检查
    validate_top_level(protocol, report)

    # 2. 步骤字段检查
    validate_steps(protocol, report)

    # 3. 证据字段完整性检查
    validate_evidence(protocol, report)

    # 4. 置信度范围检查
    validate_confidence(protocol, report)

    # 5. 缺失字段 risk_level 检查
    validate_missing_fields(protocol, report)

    # 6. 单位一致性检查
    validate_unit_consistency(protocol, report)

    # 7. 步骤依赖完整性检查
    validate_dependencies(protocol, report)

    # 8. 静默补全检测
    validate_no_silent_inference(protocol, report)

    # 9. 安全检查引用检查
    validate_safety_checks(protocol, report)

    # 10. 检查点引用检查
    validate_checkpoints(protocol, report)

    return report


# ============================================================
# 命令行入口
# ============================================================

def main():
    """命令行主入口函数"""
    parser = argparse.ArgumentParser(
        description="MatFlow Protocol 验证脚本 - 验证 protocol.json 是否符合规范"
    )
    parser.add_argument(
        "protocol_file",
        help="待验证的 protocol.json 文件路径",
    )
    parser.add_argument(
        "--report",
        dest="report_file",
        default=None,
        help="验证报告输出文件路径（JSON 格式，可选）",
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

    # 执行验证
    report = validate_protocol(protocol, args.protocol_file)

    # 输出文本报告到 stdout
    print(report.to_text())

    # 如果指定了报告文件，输出 JSON 格式报告
    if args.report_file:
        try:
            with open(args.report_file, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"\n验证报告已保存至: {args.report_file}")
        except Exception as e:
            print(f"警告: 报告文件写入失败: {e}")

    # 根据验证结果设置退出码
    if report.result == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

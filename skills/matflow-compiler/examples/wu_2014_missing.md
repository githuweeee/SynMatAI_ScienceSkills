# 缺失条件报告
## NaBH4促进的芳基醚电化学还原裂解——二苯醚电还原

> **协议ID**: MF-REAL-004
> **来源文献**: Wu, W.-B.; Huang, J.-M. *J. Org. Chem.* 2014, 79, 10189-10195.
> **DOI**: 10.1021/jo5018537
>
> 本报告列出协议中所有未从源文档提取到的条件参数。
> 每个缺失项均标注风险等级、是否阻止执行及建议。
> **MatFlow Compiler 绝不静默补全任何以下缺失项。**
>
> **总览**: 本协议共识别 **19** 个缺失项。**0 个 High Risk（无阻塞）**、**10 个 Medium Risk**、**9 个 Low Risk**。协议状态 **needs_review**（可执行但需确认）。

---

## 1. 阻塞性缺失项 (High Risk - 阻止执行)

**无。** 本协议核心参数（配方、电流、时间、萃取剂量）均来自原文 General Procedure，为 explicit 高置信度。不存在 High Risk 阻塞性缺失项。

---

## 2. 中等风险缺失项 (Medium Risk - 不阻止执行但需确认)

| # | 缺失字段 | 所在步骤 | 缺失原因 | 建议 | 需确认 |
|---|---------|---------|---------|------|--------|
| 1 | stirring_speed | WB-02: 加入NaBH4 | 原文未给出搅拌速度 | 磁力搅拌 ~300-500 rpm 至溶解 | 是 |
| 2 | stirring_speed | WB-03: 溶解 | 原文未给出搅拌速度 | 磁力搅拌（NMP 中溶解性好） | 是 |
| 3 | electrode_spacing | WB-04: 组装电极 | 原文未给出阴阳极间距 | 确保不短路；间距数毫米 | 是 |
| 4 | duration.value (预混) | WB-05: 电解前混匀 | "were dissolved"隐含前置混匀但未给时间 | 5-15 min 溶解 | 是 |
| 5 | stirring_speed | WB-05: 电解前混匀 | 原文未给出 | 磁力搅拌 300-800 rpm | 是 |
| 6 | temperature.value (ambient) | WB-06: 恒流电解 | "ambient temperature"未量化 | 25 C（20-30 C 温带） | 是 |
| 7 | stirring_speed | WB-06: 恒流电解 | 原文未给出电解时是否搅拌 | 推荐电解时搅拌以改善传质 | 是 |
| 8 | amount.value (冰水量) | WB-08: 倒入冰水 | 原文仅写"ice water"，未给体积 | 50-100 mL | 是 |
| 9 | amount.value (HCl量) | WB-09: 淬灭 | 原文仅写"1 M HCl"，未给体积 | 加至酸性 | 是 |
| 10 | atmosphere | WB-10: 乙醚萃取 | 原文未给出萃取气氛（乙醚易燃） | 通风橱、无点火源 | 是 |

---

## 3. 低风险缺失项 (Low Risk)

| # | 缺失字段 | 所在步骤 | 缺失原因 | 建议 |
|---|---------|---------|---------|------|
| 11 | temperature.value | WB-01: 加二苯醚 | "室温"未量化，25 C 近似 | 环境温度即可 |
| 12 | duration.value (溶解) | WB-03: 溶解 | "were dissolved"未给时间 | 搅拌至完全溶解 |
| 13 | cathode_connection（并联） | WB-04: 组装电极 | 原文未给出4片电网电气连接方式 | 4片需并联同电位；单片降低收率 |
| 14 | stirring_speed | WB-07: 加内标 | 原文未给搅拌速度（仅"stirred 5 min"） | 约 300 rpm |
| 15 | stirring_speed | WB-09: 淬灭 | 原文未给搅拌速度 | 淬灭时搅拌控制起泡 |
| 16 | stirring_speed | WB-10: 乙醚萃取 | 原文未给搅拌/振摇方式 | 1-2 min/份，分液漏斗 |
| 17 | duration.value (干燥) | WB-11: Na2SO4干燥 | 原文未给干燥时间 | 15-30 min |
| 18 | amount.value (Na2SO4) | WB-11: Na2SO4干燥 | 原文未给干燥剂量 | 加至不再结块 |
| 19 | temperature.value (GC) | WB-12: GC/GC-MS | GC 进样器/柱温详细信息缺失 | 选程序A或B |

---

## 4. 统计汇总

| 类别 | 数量 | 是否阻止执行 |
|------|------|------------|
| High Risk (阻止执行) | 0 | 否 |
| Medium Risk (需确认) | 10 | 否 |
| Low Risk (影响较小) | 9 | 否 |
| **总计** | **19** | — |

### 按步骤分布

| 步骤 | High | Medium | Low | 总计 |
|------|------|--------|-----|------|
| WB-01: 加二苯醚 | 0 | 0 | 1 | 1 |
| WB-02: 加NaBH4 | 0 | 1 | 0 | 1 |
| WB-03: 溶解 | 0 | 1 | 1 | 2 |
| WB-04: 组装电极 | 0 | 1 | 1 | 2 |
| WB-05: 预混匀 | 0 | 2 | 0 | 2 |
| WB-06: 恒流电解 | 0 | 2 | 0 | 2 |
| WB-07: 加内标 | 0 | 0 | 1 | 1 |
| WB-08: 倒入冰水 | 0 | 1 | 0 | 1 |
| WB-09: HCl淬灭 | 0 | 1 | 1 | 2 |
| WB-10: 乙醚萃取 | 0 | 1 | 1 | 2 |
| WB-11: 干燥 | 0 | 0 | 2 | 2 |
| WB-12: GC/GC-MS | 0 | 0 | 1 | 1 |

### 按字段类型分布

| 字段类型 | 数量 | Medium Risk 数量 |
|---------|------|-----------------|
| stirring_speed（搅拌速度） | 6 | 3 |
| amount（用量/体积） | 5 | 2 |
| duration（时间） | 4 | 1 |
| temperature（温度） | 2 | 1 |
| electrode_spacing / connection | 2 | 1 |
| atmosphere（气氛） | 1 | 1 |

> **注意**: 以上 19 个缺失项均未被 MatFlow Compiler 静默补全。protocol.json 中对应字段标记为 `null` 或缺省值，并在各步骤的 `missing_fields` 数组中显式列出。0 个 High Risk 缺失项 → 协议状态 **needs_review**（非 blocked）。
# 缺失条件报告
## 恶唑烷酮环氧树脂/碳纤维复合材料制备

> **协议ID**: MF-REAL-003
> **来源文献**: Ye Yiwen, Liu Beijun, Peng Li. *Polymers and Polymer Composites* 2022, 30.
> **DOI**: 10.1177/09673911211065196
>
> 本报告列出协议中所有未从源文档提取到的条件参数。
> 每个缺失项均标注了风险等级、是否阻止执行及建议。
> **MatFlow Compiler 绝不静默补全任何以下缺失项。**

---

## 1. 阻塞性缺失项 (High Risk - 阻止执行)

### 1.1 MDI滴加速率 (S02)

| 字段 | 内容 |
|------|------|
| 缺失字段 | addition_rate |
| 所在步骤 | S02: MDI滴加 |
| 风险等级 | **High** |
| 是否阻止执行 | **是** |
| 缺失原因 | 原文写"MDI was added dropwise by the dropping apparatus"，提及滴加方式但未给出滴加速率 |
| 原文引用 | "MDI (the molar ratio of the epoxy-functional group and isocyanate was 3:1) was added dropwise by the dropping apparatus" (Section: Synthesis of the oxazolidinone epoxy resin) |
| 证据类型 | explicit（滴加方式明确）, null（速率缺失） |
| 影响 | 异氰酸酯与环氧基团反应为放热反应；滴加速率直接影响反应温度控制、产物分子量分布和恶唑烷酮环结构形成；滴加过快可能导致局部过热、副反应（如脲基甲酸酯生成）和凝胶化 |
| 建议 | 确认MDI滴加速率（如1-5 mL/min或0.5-2 g/min）。需人工确认后填入。 |
| 建议来源 | literature_default |
| 需人工确认 | 是 |

### 1.2 MDI继续滴加速率 (S03)

| 字段 | 内容 |
|------|------|
| 缺失字段 | addition_rate |
| 所在步骤 | S03: 升温至110C继续滴加MDI |
| 风险等级 | **High** |
| 是否阻止执行 | **是** |
| 缺失原因 | 原文写"MDI was continued to be added"，未给出此阶段的滴加速率 |
| 原文引用 | "After 1 h, the temperature was raised to 110C and MDI was continued to be added." (Section: Synthesis of the oxazolidinone epoxy resin) |
| 证据类型 | explicit（继续滴加明确）, null（速率缺失） |
| 影响 | 110C下MDI继续滴加，反应速率加快，滴加速率控制更为关键 |
| 建议 | 确认此阶段MDI滴加速率。需人工确认后填入。 |
| 建议来源 | literature_default |
| 需人工确认 | 是 |

### 1.3 双氰胺用量 (S09)

| 字段 | 内容 |
|------|------|
| 缺失字段 | amount.value |
| 所在步骤 | S09: 加入双氰胺 |
| 风险等级 | **High** |
| 是否阻止执行 | **是** |
| 缺失原因 | 原文写"a certain amount of dicyandiamide"，仅提及存在但未给出具体用量 |
| 原文引用 | "Then a certain amount of dicyandiamide was added into the flask and thoroughly mixed." (Section: Synthesis of the cured oxazolidinone epoxies) |
| 证据类型 | explicit（双氰胺存在明确）, null（用量缺失） |
| 影响 | 双氰胺作为环氧树脂固化剂，其用量直接决定固化度、交联密度、玻璃化转变温度和最终力学性能；用量不足导致固化不完全，过量导致性能下降；缺少此参数完全无法复现实验 |
| 建议 | 确认双氰胺的具体用量（g或phr，每百份树脂的份数）。需人工确认后填入。 |
| 建议来源 | literature_default |
| 需人工确认 | 是 |

---

## 2. 中等风险缺失项 (Medium Risk - 不阻止执行但需确认)

### 2.1 搅拌速度 (S01, S02, S03, S04, S05, S07, S09, S12)

| 缺失字段 | 所在步骤 | 风险等级 | 是否阻止执行 | 缺失原因 | 建议 |
|---------|---------|---------|------------|---------|------|
| stirring_speed | S01: DGEBA+2-MI混合 | medium | 否 | 原文未给出搅拌速度 | 200-400 rpm |
| stirring_speed | S02: MDI滴加 | medium | 否 | 原文未给出搅拌速度 | 300-500 rpm（滴加时需较快搅拌确保分散） |
| stirring_speed | S03: 110C继续滴加 | medium | 否 | 原文未给出搅拌速度 | 300-500 rpm |
| stirring_speed | S04: 120C继续滴加 | medium | 否 | 原文未给出搅拌速度 | 300-500 rpm |
| stirring_speed | S05: 保温反应 | medium | 否 | 原文未给出搅拌速度 | 200-400 rpm |
| stirring_speed | S07: OX+DGEBA混合 | medium | 否 | 原文未给出搅拌速度 | 200-400 rpm |
| stirring_speed | S09: 加双氰胺 | medium | 否 | "thoroughly mixed"为定性描述 | 300-500 rpm（确保粉末分散） |
| stirring_speed | S12: 溶液配制 | medium | 否 | 原文未给出搅拌速度 | 200-400 rpm |

### 2.2 升温/冷却速率 (S01, S03, S04, S07, S08, S11, S15)

| 缺失字段 | 所在步骤 | 风险等级 | 是否阻止执行 | 缺失原因 | 建议 |
|---------|---------|---------|------------|---------|------|
| temperature.ramp_rate | S01: 升至90C | medium | 否 | 原文未给出升温速率 | 2-5 C/min |
| temperature.ramp_rate | S03: 90->110C | medium | 否 | 原文未给出升温速率 | 2-5 C/min |
| temperature.ramp_rate | S04: 110->120C | medium | 否 | 原文未给出升温速率 | 2-5 C/min |
| temperature.ramp_rate | S07: 升至120C | medium | 否 | 原文未给出升温速率 | 2-5 C/min |
| temperature.ramp_rate | S08: 120->80C冷却 | medium | 否 | 原文未给出冷却速率 | 自然冷却或2-5 C/min |
| temperature.ramp_rate | S11: 80->130->190C | medium | 否 | 各阶段间升温速率未给出 | 2-5 C/min（总温升110C） |
| temperature.ramp_rate | S15: 升至150C | medium | 否 | 原文未给出升温速率 | 2-5 C/min |

### 2.3 压力单位不明确 (S15)

| 缺失字段 | 所在步骤 | 风险等级 | 是否阻止执行 | 缺失原因 | 建议 |
|---------|---------|---------|------------|---------|------|
| pressure.unit | S15: 热压 | medium | 否 | "45 Kg"单位不明确，可能为kgf/cm2(~4.4 MPa)、kgf(441 N)或其他 | 确认压力单位；若为kg/cm2则~4.4 MPa，为复合材料热压典型值 |

### 2.4 其他中等风险缺失项

| 缺失字段 | 所在步骤 | 风险等级 | 是否阻止执行 | 缺失原因 | 建议 |
|---------|---------|---------|------------|---------|------|
| amount.OX_resin | S07: OX+DGEBA混合 | medium | 否 | 仅给出15 wt%比例，未给绝对量 | 确认OX树脂和DGEBA的具体用量 |
| amount.DGEBA | S07: OX+DGEBA混合 | medium | 否 | 未明确给出DGEBA用量 | 同上 |
| duration.value | S04: 120C滴加MDI | medium | 否 | "until all MDI was added"但未给具体时间 | 取决于滴加速率（缺失） |
| duration.value | S09: 混合双氰胺 | medium | 否 | "thoroughly mixed"未给时间 | 5-15 min |
| pressure.value | S10: 真空脱泡 | medium | 否 | 真空度未给出 | 典型真空烘箱1-10 kPa |
| duration.value | S12: 溶液配制 | medium | 否 | 溶解时间未给出 | 10-30 min |
| amount.butanone | S12: 溶液配制 | medium | 否 | 丁酮用量仅以目标密度给出 | 按密度0.96 g/cm3反算 |
| temperature.value | S13: 预浸 | medium | 否 | 预浸温度未给出 | 室温~25C |
| duration.value | S13: 预浸 | medium | 否 | 预浸时间未给出 | 取决于溶剂法工艺 |
| temperature.value | S14: 铺层 | medium | 否 | 铺层温度未给出 | 室温~25C |
| duration.value | S14: 铺层 | medium | 否 | 铺层时间未给出 | 取决于操作者技能 |

---

## 3. 低风险缺失项 (Low Risk)

| 缺失字段 | 所在步骤 | 风险等级 | 是否阻止执行 | 缺失原因 | 建议 |
|---------|---------|---------|------------|---------|------|
| duration.value | S06: 冷却 | low | 否 | 冷却时间未给出 | 自然冷却至室温 |
| atmosphere | S07: OX+DGEBA混合 | low | 否 | 气氛未给出 | 可能空气 |
| atmosphere | S11: 固化 | low | 否 | 固化气氛未给出 | 可能空气（常规烘箱） |
| atmosphere | S15: 热压 | low | 否 | 热压气氛未给出 | 可能空气 |
| stirring_speed | S13: 预浸 | low | 否 | 溶剂法参数未给出 | 取决于工艺 |

---

## 4. 统计汇总

| 类别 | 数量 | 是否阻止执行 |
|------|------|------------|
| High Risk (阻止执行) | 3 | 是 |
| Medium Risk (需确认) | 25 | 否 |
| Low Risk (影响较小) | 5 | 否 |
| **总计** | **33** | — |

### 按步骤分布

| 步骤 | High | Medium | Low | 总计 |
|------|------|--------|-----|------|
| S01: DGEBA+2-MI混合 | 0 | 2 | 0 | 2 |
| S02: MDI滴加 | 1 | 1 | 0 | 2 |
| S03: 升温110C | 1 | 2 | 0 | 3 |
| S04: 升温120C | 0 | 3 | 0 | 3 |
| S05: 保温反应 | 0 | 1 | 0 | 1 |
| S06: 出料冷却 | 0 | 0 | 1 | 1 |
| S07: OX+DGEBA混合 | 0 | 4 | 1 | 5 |
| S08: 冷却至80C | 0 | 2 | 0 | 2 |
| S09: 加双氰胺 | 1 | 2 | 0 | 3 |
| S10: 真空脱泡 | 0 | 1 | 0 | 1 |
| S11: 固化 | 0 | 1 | 1 | 2 |
| S12: 溶液配制 | 0 | 3 | 0 | 3 |
| S13: 碳纤维预浸 | 0 | 2 | 1 | 3 |
| S14: 铺层 | 0 | 2 | 0 | 2 |
| S15: 热压 | 0 | 2 | 1 | 3 |

### 按字段类型分布

| 字段类型 | 数量 | High Risk 数量 |
|---------|------|---------------|
| stirring_speed (搅拌速度) | 9 | 0 |
| temperature.ramp_rate (升降温速率) | 7 | 0 |
| addition_rate (滴加速率) | 2 | 2 |
| duration (时间) | 6 | 0 |
| amount (用量) | 4 | 1 |
| temperature (温度) | 2 | 0 |
| pressure (压力/真空度) | 2 | 0 |
| atmosphere (气氛) | 3 | 0 |

---

## 5. 补充材料(SI)获取记录

| 项目 | 内容 |
|------|------|
| DOI | 10.1177/09673911211065196 |
| 出版商 | SAGE Journals |
| DOI前缀 | 10.1177 |
| SI获取状态 | 未尝试（原文实验方法部分信息相对完整，关键缺失为"a certain amount"和滴加速率，SI不太可能包含这些信息） |
| 建议 | 联系作者确认双氰胺用量和MDI滴加速率；查阅同类恶唑烷酮环氧树脂合成文献获取参考值 |

---

## 6. Derived 参数记录

以下参数由原文明确数据经计算推导得出，已确认并可进入协议：

| 参数 | 值 | 推导过程 | 确认来源 |
|------|-----|---------|---------|
| 2-MI用量 | 0.024 g | 240g (DGEBA) x 0.0001 (万分之一) = 0.024g | Table 1 确认 |
| 固化总时间 | 6 h | 1h + 3h + 2h = 6h | Table 2 各阶段相加 |

---

> **注意**: 以上33个缺失项均未被 MatFlow Compiler 静默补全。所有缺失字段在 protocol.json 中标记为 `null`，并在各步骤的 `missing_fields` 数组中显式列出。3个High Risk缺失项（MDI滴加速率x2、双氰胺用量x1）导致协议状态为 **blocked**。

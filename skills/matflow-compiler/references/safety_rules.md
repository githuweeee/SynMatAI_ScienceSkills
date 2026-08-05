# MatFlow Compiler 安全规则参考文档

> 本文档定义了 MatFlow Compiler Skill 在编译材料合成协议时执行的安全审计规则集。
> 所有规则按类别分组，每条规则包含唯一ID、触发条件、执行动作及消息模板。

---

## 目录

1. [温度安全规则](#1-温度安全规则)
2. [压力与密闭容器规则](#2-压力与密闭容器规则)
3. [化学品不相容性规则](#3-化学品不相容性规则)
4. [气氛安全规则](#4-气氛安全规则)
5. [加料顺序冲突规则](#5-加料顺序冲突规则)
6. [人工确认点规则](#6-人工确认点规则)
7. [设备能力边界规则](#7-设备能力边界规则)

---

## 动作类型说明

| 动作类型 | 含义 | 编译器行为 |
|----------|------|------------|
| `blocked` | 阻断编译 | 立即终止编译流程，输出错误报告，不生成协议文件 |
| `warning` | 警告 | 继续编译，在报告中标记警告，用户可选择忽略或修正 |
| `require_confirmation` | 要求人工确认 | 暂停编译，等待用户确认后方可继续 |
| `check_device_capability` | 检查设备能力 | 触发设备能力查询子流程，根据结果决定后续动作 |
| `info` | 信息提示 | 仅在报告中输出提示信息，不影响编译流程 |

---

## 1. 温度安全规则

温度是材料合成中最关键的安全参数之一。以下规则确保所有温度相关操作在安全范围内执行。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-T-001 | `step.temperature > device.max_temperature` | `blocked` | "步骤 {step_id} 设定温度 {temp}°C 超过设备 {device_name} 的温度上限 {max_temp}°C，存在设备损坏及安全事故风险" |
| SAFE-T-002 | `step.is_sealed == true AND step.temperature >= solvent.boiling_point` | `blocked` | "步骤 {step_id} 在密闭条件下加热至 {temp}°C，已达到或超过溶剂 {solvent_name} 的沸点 {bp}°C，存在容器超压破裂风险" |
| SAFE-T-003 | `step.temperature > room_temp AND step.ramp_rate == null` | `warning` + `require_confirmation` | "步骤 {step_id} 升温操作未指定升温速率，默认采用 {default_ramp}°C/min。如需自定义速率请补充 ramp_rate 参数" |
| SAFE-T-004 | `step.temperature_gradient == null AND step.target_temp_change > 100` | `warning` | "步骤 {step_id} 温度变化幅度达 {delta}°C，未指定温度梯度参数，可能导致局部过热或热应力不均" |
| SAFE-T-005 | `step.temperature < 0 AND device.supports_cryogenic == false` | `check_device_capability` | "步骤 {step_id} 要求低温操作（{temp}°C），当前设备 {device_name} 可能不支持低温控制，请确认设备制冷能力" |

### 规则详解

#### SAFE-T-001: 设备温度上限检查

- **触发条件**: 步骤设定温度超过绑定设备的最大允许温度
- **判断逻辑**:
  ```python
  if step.temperature is not None and device is not None:
      if step.temperature > device.capabilities.temperature.max:
          trigger("SAFE-T-001", action="blocked")
  ```
- **设计理由**: 超温操作可能导致加热元件损坏、传感器失效，严重时引发火灾
- **关联参数**: `step.temperature`, `device.capabilities.temperature.max`
- **豁免条件**: 无（安全阻断规则不可豁免）

#### SAFE-T-002: 密闭加热沸点检查

- **触发条件**: 步骤标记为密闭操作（`is_sealed: true`）且加热温度达到或超过所用溶剂的沸点
- **判断逻辑**:
  ```python
  if step.is_sealed and step.solvents:
      for solvent in step.solvents:
          if step.temperature >= solvent.boiling_point:
              trigger("SAFE-T-002", action="blocked")
  ```
- **设计理由**: 密闭容器中溶剂气化会产生巨大内压，可能导致容器爆炸
- **关联参数**: `step.is_sealed`, `step.temperature`, `solvent.boiling_point`
- **豁免条件**: 设备具备压力容器认证且 `device.max_pressure` 大于计算饱和蒸汽压时可降级为 `require_confirmation`

#### SAFE-T-003: 升温速率缺失

- **触发条件**: 步骤涉及升温操作但未指定升温速率（`ramp_rate`）
- **判断逻辑**:
  ```python
  if step.temperature > 25 and step.ramp_rate is None:
      trigger("SAFE-T-003", action="warning")
      trigger("SAFE-T-003", action="require_confirmation")
  ```
- **设计理由**: 缺失升温速率可能导致默认值过快，引发热失控或反应剧烈
- **默认值**: `5°C/min`（通用安全默认值）
- **关联参数**: `step.temperature`, `step.ramp_rate`

#### SAFE-T-004: 温度梯度未指定

- **触发条件**: 温度变化超过100°C但未指定温度梯度（`temperature_gradient`）
- **判断逻辑**:
  ```python
  delta = abs(step.temperature - step.previous_temperature)
  if delta > 100 and step.temperature_gradient is None:
      trigger("SAFE-T-004", action="warning")
  ```
- **设计理由**: 大幅温度变化无梯度控制可能导致样品热应力开裂或反应不均匀
- **关联参数**: `step.temperature`, `step.temperature_gradient`, `step.previous_temperature`

#### SAFE-T-005: 低温操作设备检查

- **触发条件**: 步骤要求温度低于0°C，需验证设备是否具备低温控制能力
- **判断逻辑**:
  ```python
  if step.temperature < 0:
      if device is None or not device.supports_cryogenic:
          trigger("SAFE-T-005", action="check_device_capability")
  ```
- **设计理由**: 低温操作需要制冷模块或液氮/干冰冷却系统，普通加热设备无法实现
- **关联参数**: `step.temperature`, `device.supports_cryogenic`
- **后续动作**: 若设备能力检查失败则升级为 `blocked`

---

## 2. 压力与密闭容器规则

压力相关操作是合成实验中的高风险环节，以下规则覆盖密闭加热、气体产生、压力容器及真空操作场景。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-P-001 | `step.is_sealed == true AND step.temperature > 80` | `warning` + `require_confirmation` | "步骤 {step_id} 在密闭容器中加热至 {temp}°C，密闭加热存在内压积聚风险，请确认容器耐压等级并安装泄压装置" |
| SAFE-P-002 | `step.reagents` 包含产气反应组合（如碳酸盐+酸、金属+酸） | `blocked` | "步骤 {step_id} 检测到产气反应组合：{reagent_a} + {reagent_b}，在{container_type}中可能产生大量气体，存在超压风险" |
| SAFE-P-003 | `step.pressure > device.max_pressure` | `blocked` | "步骤 {step_id} 要求压力 {pressure} MPa 超过设备 {device_name} 的耐压上限 {max_pressure} MPa" |
| SAFE-P-004 | `step.vacuum_level < device.min_vacuum` | `warning` | "步骤 {step_id} 要求真空度 {vacuum} Pa 低于设备 {device_name} 的极限真空度 {min_vacuum} Pa，可能无法达到目标真空度" |

### 规则详解

#### SAFE-P-001: 密闭容器加热风险

- **触发条件**: 步骤标记为密闭操作且加热温度超过80°C
- **判断逻辑**:
  ```python
  if step.is_sealed and step.temperature > 80:
      trigger("SAFE-P-001", action="warning")
      trigger("SAFE-P-001", action="require_confirmation")
  ```
- **设计理由**: 80°C以上密闭加热会使容器内气体膨胀产生显著内压，需确认容器耐压能力
- **关联参数**: `step.is_sealed`, `step.temperature`
- **检查项**: 容器耐压等级、泄压阀配置、温度监控措施

#### SAFE-P-002: 气体产生反应检测

- **触发条件**: 步骤中的试剂组合属于已知产气反应类型
- **判断逻辑**:
  ```python
  gas_producing_pairs = load_gas_reaction_database()
  for pair in gas_producing_pairs:
      if pair.reagent_a in step.reagents and pair.reagent_b in step.reagents:
          if step.is_sealed or step.container_type == "sealed_vial":
              trigger("SAFE-P-002", action="blocked")
  ```
- **已知产气反应组合**:
  - 碳酸盐/碳酸氢盐 + 酸 → CO₂
  - 活泼金属（Na/K/Ca） + 酸/水 → H₂
  - 过氧化物 + 有机物 → O₂
  - 叠氮化物 + 酸 → N₂/HN₃
  - 亚硫酸盐 + 酸 → SO₂
- **设计理由**: 密闭条件下的产气反应会迅速导致容器超压爆炸
- **关联参数**: `step.reagents`, `step.is_sealed`, `step.container_type`

#### SAFE-P-003: 压力容器要求

- **触发条件**: 步骤要求的工作压力超过设备的最大耐压能力
- **判断逻辑**:
  ```python
  if step.pressure is not None and device is not None:
      if step.pressure > device.capabilities.pressure.max:
          trigger("SAFE-P-003", action="blocked")
  ```
- **设计理由**: 超压操作可能导致容器破裂、碎片飞溅及化学品泄漏
- **关联参数**: `step.pressure`, `device.capabilities.pressure.max`
- **豁免条件**: 无

#### SAFE-P-004: 真空操作安全

- **触发条件**: 步骤要求的真空度（绝对压力值）低于设备能达到的极限真空度
- **判断逻辑**:
  ```python
  if step.vacuum_level is not None and device is not None:
      if step.vacuum_level < device.capabilities.vacuum.min:
          trigger("SAFE-P-004", action="warning")
  ```
- **设计理由**: 真空度不足可能导致溶剂无法有效脱除或反应无法在目标低压下进行
- **关联参数**: `step.vacuum_level`, `device.capabilities.vacuum.min`
- **注意**: 真空度数值越小表示真空程度越高，因此比较方向为 `step < device.min`

---

## 3. 化学品不相容性规则

化学品不相容性是实验室安全事故的主要来源之一。以下规则基于不相容性矩阵进行检测。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-C-001 | `step.reagents` 同时包含氧化剂与还原剂 | `blocked` | "步骤 {step_id} 同时使用氧化剂 {oxidizer} 与还原剂 {reducer}，可能发生剧烈氧化还原反应" |
| SAFE-C-002 | `step.reagents` 同时包含强酸与强碱 | `warning` + `require_confirmation` | "步骤 {step_id} 同时使用强酸 {acid} 与强碱 {base}，混合时将剧烈放热，请确认加料顺序与冷却措施" |
| SAFE-C-003 | `step.reagents` 包含水敏试剂且环境中存在水分来源 | `blocked` | "步骤 {step_id} 使用水敏试剂 {reagent}，但检测到水分来源（溶剂含水/未干燥容器/环境湿度），可能导致试剂失效或危险反应" |
| SAFE-C-004 | `step.reagents` 包含易燃溶剂且步骤温度超过闪点 | `blocked` | "步骤 {step_id} 使用易燃溶剂 {solvent}（闪点 {flash_point}°C），操作温度 {temp}°C 已超过闪点，存在引燃风险" |
| SAFE-C-005 | `step.reagents` 同时包含氰化物与酸 | `blocked` | "步骤 {step_id} 同时使用氰化物 {cyanide} 与酸 {acid}，将产生剧毒氰化氢气体（HCN），严禁混合" |
| SAFE-C-006 | `step.reagents` 匹配不相容性矩阵中的任意条目 | `blocked` | "步骤 {step_id} 检测到不相容化学品组合：{reagent_a} 与 {reagent_b}（不相容类型：{incompat_type}）" |

### 不相容性矩阵

以下矩阵定义了已知的不相容化学品组合及其风险类型：

| 试剂A | 试剂B | 不相容类型 | 风险描述 |
|-------|-------|------------|----------|
| 高锰酸钾 (KMnO₄) | 甘油/乙醇/有机物 | 氧化还原 | 剧烈放热，可能自燃 |
| 硝酸 (HNO₃) | 有机溶剂/还原剂 | 氧化还原 | 爆炸性反应 |
| 过氧化氢 (H₂O₂) | 有机物/金属盐 | 氧化还原 | 分解放热，可能爆炸 |
| 氯酸钾 (KClO₃) | 硫/磷/有机物 | 氧化还原 | 摩擦/撞击即爆炸 |
| 浓硫酸 (H₂SO₄) | 水/碱液 | 酸碱放热 | 剧烈放热，飞溅 |
| 浓盐酸 (HCl) | 浓氨水 (NH₃·H₂O) | 酸碱反应 | 产生大量氯化铵白烟 |
| 金属钠 (Na) | 水/醇 | 水敏反应 | 剧烈产氢放热，可能爆炸 |
| 氢化铝锂 (LiAlH₄) | 水/醇 | 水敏反应 | 剧烈产氢，火灾风险 |
| 格氏试剂 (RMgX) | 水/醇 | 水敏反应 | 试剂分解，产烷烃 |
| 正丁基锂 (n-BuLi) | 水/醇/CO₂ | 水敏反应 | 剧烈放热分解 |
| 氰化钠 (NaCN) | 酸（任何酸） | 毒气产生 | 产生剧毒HCN气体 |
| 氰化钾 (KCN) | 酸（任何酸） | 毒气产生 | 产生剧毒HCN气体 |
| 次氯酸钠 (NaClO) | 氨水/铵盐 | 毒气产生 | 产生爆炸性三氯化氮 |
| 硝酸银 (AgNO₃) | 乙醇/乙醛 | 氧化还原 | 生成易爆雷酸银 |
| 溴 (Br₂) | 氨/胺类 | 氧化还原 | 生成爆炸性氮溴化物 |

### 规则详解

#### SAFE-C-001: 氧化剂与还原剂

- **触发条件**: 同一步骤中同时出现氧化剂类和还原剂类试剂
- **氧化剂分类**: 高锰酸钾、硝酸、过氧化氢、氯酸钾、重铬酸钾、溴、碘
- **还原剂分类**: 金属粉末（Zn/Fe/Al）、亚硫酸盐、硫代硫酸盐、醇类、胺类
- **判断逻辑**:
  ```python
  oxidizers = classify_reagents(step.reagents, category="oxidizer")
  reducers = classify_reagents(step.reagents, category="reducer")
  if oxidizers and reducers:
      trigger("SAFE-C-001", action="blocked",
              oxidizer=oxidizers[0], reducer=reducers[0])
  ```
- **设计理由**: 氧化剂与还原剂直接混合可能引发不可控的剧烈放热反应

#### SAFE-C-002: 强酸与强碱

- **触发条件**: 同一步骤中同时出现强酸和强碱
- **强酸分类**: 硫酸、盐酸、硝酸、磷酸
- **强碱分类**: 氢氧化钠、氢氧化钾、氨水
- **设计理由**: 酸碱中和反应放热显著，直接混合可能导致沸腾飞溅
- **缓解措施**: 若加料顺序为先酸后碱（或先碱后酸）且配有冷却措施，可降级为 `warning`

#### SAFE-C-003: 水敏试剂与水

- **触发条件**: 步骤使用水敏试剂且检测到水分来源
- **水敏试剂**: 金属钠、氢化铝锂、格氏试剂、正丁基锂、二氯亚砜、三氯化铝
- **水分来源检测**:
  - 溶剂含水（如未标注无水的乙醇/甲醇）
  - 容器未标记为干燥状态
  - 步骤气氛为空气（非惰性气氛）
- **设计理由**: 水敏试剂遇水剧烈反应，产氢放热，可能引发火灾

#### SAFE-C-004: 易燃溶剂与高温

- **触发条件**: 步骤使用易燃溶剂且操作温度超过该溶剂闪点
- **常见易燃溶剂闪点**:
  | 溶剂 | 闪点 (°C) | 沸点 (°C) |
  |------|-----------|-----------|
  | 乙醚 | -45 | 34.6 |
  | 戊烷 | -49 | 36.1 |
  | 二硫化碳 | -30 | 46.2 |
  | 丙酮 | -20 | 56.0 |
  | 甲醇 | 11 | 64.7 |
  | 乙醇 | 13 | 78.4 |
  | 乙酸乙酯 | -4 | 77.1 |
  | 甲苯 | 4 | 110.6 |
  | 四氢呋喃 | -14 | 66.0 |
  | 二氯甲烷 | 无（不可燃） | 40.0 |
- **设计理由**: 超过闪点温度时溶剂蒸气可与空气形成爆炸性混合物

#### SAFE-C-005: 氰化物与酸

- **触发条件**: 同一步骤中同时出现氰化物和任何酸类试剂
- **氰化物分类**: 氰化钠、氰化钾、氰化铜、铁氰化物（低毒例外）
- **设计理由**: 氰化物与酸反应生成氰化氢（HCN）气体，致死浓度极低
- **豁免条件**: 铁氰化物（K₃[Fe(CN)₆]）和亚铁氰化物在常温下与稀酸不产生HCN，可豁免

#### SAFE-C-006: 不相容性矩阵匹配

- **触发条件**: 试剂组合命中不相容性矩阵中的任意条目
- **判断逻辑**:
  ```python
  matrix = load_incompatibility_matrix()
  for entry in matrix:
      if entry.reagent_a in step.reagents and entry.reagent_b in step.reagents:
          trigger("SAFE-C-006", action="blocked",
                  reagent_a=entry.reagent_a,
                  reagent_b=entry.reagent_b,
                  incompat_type=entry.type)
  ```
- **设计理由**: 作为兜底规则，确保所有已知不相容组合均被检测

---

## 4. 气氛安全规则

气氛控制对空气敏感材料的合成至关重要。以下规则确保气氛相关操作的正确性。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-A-001 | `step.reagents` 包含空气敏感试剂且 `step.atmosphere == "air"` | `blocked` | "步骤 {step_id} 使用空气敏感试剂 {reagent}，但气氛设置为空气，试剂将迅速氧化/水解失效" |
| SAFE-A-002 | `step.reagents` 包含氧气敏感试剂且 `step.atmosphere` 未设为惰性 | `warning` + `require_confirmation` | "步骤 {step_id} 使用氧气敏感试剂 {reagent}，建议使用惰性气氛（氮气或氩气）保护" |
| SAFE-A-003 | `step.atmosphere == "inert"` 且 `step.moisture_requirement` 或 `step.oxygen_requirement` 未指定 | `warning` | "步骤 {step_id} 使用惰性气氛但未指定水氧含量要求，建议明确 H₂O/O₂ 含量阈值（如 <1 ppm）" |
| SAFE-A-004 | `step.atmosphere == "inert"` 且 `step.purge_method == null` | `warning` | "步骤 {step_id} 要求惰性气氛但未指定气氛置换方式（如抽真空-充气循环、持续吹扫），默认采用3次抽真空-充气循环" |

### 规则详解

#### SAFE-A-001: 惰性气氛需求

- **触发条件**: 步骤使用空气敏感试剂但气氛设置为空气
- **空气敏感试剂**: 正丁基锂、格氏试剂、氢化铝锂、二乙基锌、三甲基铝、硼氢化钠（部分）、零价金属催化剂
- **判断逻辑**:
  ```python
  air_sensitive = classify_reagents(step.reagents, category="air_sensitive")
  if air_sensitive and step.atmosphere == "air":
      trigger("SAFE-A-001", action="blocked", reagent=air_sensitive[0])
  ```
- **设计理由**: 空气敏感试剂在空气中会迅速氧化或水解，不仅导致实验失败，部分试剂（如三甲基铝）遇空气自燃
- **推荐气氛**: 氮气（N₂）或氩气（Ar），氩气密度大于空气，保护效果更佳

#### SAFE-A-002: 氧气敏感反应检测

- **触发条件**: 步骤使用氧气敏感试剂或催化剂，气氛未明确设为惰性
- **氧气敏感试剂**: 钯催化剂（Pd/C）、铂催化剂、铑催化剂、零价镍配合物、铁配合物
- **判断逻辑**:
  ```python
  o2_sensitive = classify_reagents(step.reagents, category="oxygen_sensitive")
  if o2_sensitive and step.atmosphere not in ["nitrogen", "argon", "inert"]:
      trigger("SAFE-A-002", action="warning")
      trigger("SAFE-A-002", action="require_confirmation")
  ```
- **设计理由**: 氧气敏感催化剂在空气中可能失活或引发副反应
- **关联参数**: `step.reagents`, `step.atmosphere`

#### SAFE-A-003: 水氧含量要求

- **触发条件**: 步骤使用惰性气氛但未指定水氧含量阈值
- **常见水氧含量要求**:
  | 反应类型 | H₂O 要求 | O₂ 要求 |
  |----------|----------|---------|
  | 一般无水反应 | <100 ppm | <100 ppm |
  | 格氏反应 | <10 ppm | <10 ppm |
  | 有机金属催化 | <5 ppm | <5 ppm |
  | 超高纯反应 | <1 ppm | <1 ppm |
- **设计理由**: 仅声明惰性气氛而不指定水氧阈值，无法保证实验可重复性
- **关联参数**: `step.atmosphere`, `step.moisture_requirement`, `step.oxygen_requirement`

#### SAFE-A-004: 气氛置换方式缺失

- **触发条件**: 步骤要求惰性气氛但未指定置换方式
- **常见置换方式**:
  - `vacuum_cycles`: 抽真空-充气循环（推荐3次以上）
  - `continuous_purge`: 持续吹扫（需指定时长，建议≥15分钟）
  - `balloon`: 气球法（适用于简单操作，保护效果有限）
  - `glovebox`: 手套箱操作（最佳保护）
- **默认值**: 3次抽真空-充气循环
- **设计理由**: 置换方式影响气氛纯度，缺失时使用默认值可能导致保护不足

---

## 5. 加料顺序冲突规则

加料顺序直接影响反应安全性和产物选择性。以下规则检测加料顺序相关的冲突。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-M-001 | `step.addition_order` 违反已知顺序依赖规则 | `blocked` | "步骤 {step_id} 加料顺序违反依赖规则：{reagent_a} 必须在 {reagent_b} 之前加入（原因：{reason}）" |
| SAFE-M-002 | `step.addition_order` 匹配禁忌加料顺序 | `blocked` | "步骤 {step_id} 检测到禁忌加料顺序：{reagent_a} 不可先于 {reagent_b} 加入（原因：{reason}）" |
| SAFE-M-003 | `step.reagents` 中存在需分步加入但标记为同时添加的试剂 | `warning` + `require_confirmation` | "步骤 {step_id} 中 {reagent_a} 与 {reagent_b} 标记为同时添加，但该组合要求分步加入以控制反应速率" |

### 规则详解

#### SAFE-M-001: 顺序依赖检查

- **触发条件**: 加料顺序违反已知的顺序依赖规则
- **已知顺序依赖规则**:
  | 试剂A（先加） | 试剂B（后加） | 原因 |
  |---------------|---------------|------|
  | 溶剂 | 固体试剂 | 避免固体粘壁，确保溶解分散 |
  | 碱液 | 酸（中和反应） | 碱中加酸可控制放热，反向易飞溅 |
  | 还原剂 | 氧化剂 | 避免直接接触引发剧烈反应 |
  | 催化剂 | 反应物 | 确保催化剂均匀分散后再加入底物 |
  | 引发剂 | 单体 | 聚合反应中先加引发剂可控制聚合速率 |
- **判断逻辑**:
  ```python
  order_rules = load_addition_order_rules()
  for rule in order_rules:
      if rule.reagent_b_before_a_violation(step.addition_order):
          trigger("SAFE-M-001", action="blocked",
                  reagent_a=rule.required_first,
                  reagent_b=rule.required_second,
                  reason=rule.reason)
  ```

#### SAFE-M-002: 禁忌加料顺序

- **触发条件**: 加料顺序匹配禁忌组合
- **已知禁忌顺序**:
  | 禁忌顺序 | 原因 |
  |----------|------|
  | 水倒入浓硫酸 | 放热导致水沸腾飞溅，应将酸倒入水中 |
  | 浓碱倒入大量酸 | 局部过热飞溅 |
  | 活泼金属直接加入热水 | 剧烈反应可能爆炸 |
  | 过氧化氢加入有机溶剂 | 可能引发爆炸性氧化反应 |
- **设计理由**: 禁忌加料顺序是实验室事故的常见原因

#### SAFE-M-003: 同时添加冲突

- **触发条件**: 标记为同时添加（`simultaneous: true`）的试剂组合实际需要分步加入
- **判断逻辑**:
  ```python
  sequential_required = check_sequential_requirement(step.reagents)
  if sequential_required and step.simultaneous_addition:
      trigger("SAFE-M-003", action="warning")
      trigger("SAFE-M-003", action="require_confirmation")
  ```
- **设计理由**: 同时添加可能导致局部浓度过高，引发副反应或失控

---

## 6. 人工确认点规则

以下规则定义了需要人工确认的高风险操作场景。当触发这些规则时，编译器暂停并等待用户确认。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-H-001 | `step.temperature > 200` | `require_confirmation` | "步骤 {step_id} 操作温度 {temp}°C 超过200°C，属于高温操作，请确认设备耐温能力及安全防护措施" |
| SAFE-H-002 | `step.pressure > 0.5` (MPa) | `require_confirmation` | "步骤 {step_id} 操作压力 {pressure} MPa 超过0.5 MPa，属于高压操作，请确认压力容器认证及泄压装置" |
| SAFE-H-003 | `step.reagents` 包含高毒/剧毒试剂 | `require_confirmation` | "步骤 {step_id} 使用高毒试剂 {reagent}（毒性等级：{tox_class}），请确认通风橱操作、个人防护装备及应急处理方案" |
| SAFE-H-004 | `step.parameters` 中存在 `inferred` 类型参数 | `require_confirmation` | "步骤 {step_id} 参数 {param_name} 为推断值（{inferred_value}），非用户明确指定，请确认该值是否可接受" |
| SAFE-H-005 | `step.is_sealed == true AND step.temperature > 60` | `require_confirmation` | "步骤 {step_id} 在密闭条件下加热至 {temp}°C，请确认容器耐压等级、泄压措施及温度监控方案" |

### 规则详解

#### SAFE-H-001: 高温操作确认

- **触发条件**: 步骤温度超过200°C
- **确认要点**:
  - 设备最高耐温是否满足要求
  - 是否需要耐高温容器（石英/刚玉/不锈钢）
  - 周围是否有易燃物品
  - 温度监控及超温报警是否就位
- **设计理由**: 200°C以上操作涉及显著热辐射和材料降解风险

#### SAFE-H-002: 高压操作确认

- **触发条件**: 步骤压力超过0.5 MPa（约5个大气压）
- **确认要点**:
  - 压力容器是否通过认证（如ASME认证）
  - 泄压阀/安全阀是否安装且设定正确
  - 压力表量程是否匹配
  - 操作人员是否经过高压操作培训
- **设计理由**: 高压操作是实验室最危险的操作之一，容器失效可导致严重伤害

#### SAFE-H-003: 有毒试剂使用确认

- **触发条件**: 步骤使用高毒或剧毒试剂
- **毒性分级参考**:
  | 毒性等级 | LD₅₀ (mg/kg, 大鼠口服) | 示例试剂 |
  |----------|------------------------|----------|
  | 剧毒（Class I） | <5 | 氰化钠、砷化合物、汞化合物 |
  | 高毒（Class II） | 5-50 | 铍化合物、铅化合物、部分有机锡 |
  | 中等毒（Class III） | 50-500 | 苯胺、苯酚、甲醛 |
  | 低毒（Class IV） | 500-5000 | 乙醇、丙酮（常规溶剂） |
- **确认要点**:
  - 必须在通风橱内操作
  - 佩戴适当PPE（手套、护目镜、实验服）
  - 准备应急处理物资（如氰化物需备亚硝酸异戊酯）
  - 确认废弃物处理方案

#### SAFE-H-004: 不确定参数确认

- **触发条件**: 步骤参数来源标记为 `inferred`（由编译器推断而非用户指定）
- **推断场景**:
  - 用户未指定搅拌速度，编译器根据试剂粘度推断
  - 用户未指定反应时间，编译器根据文献数据推断
  - 用户未指定浓度，编译器根据摩尔比推断
- **设计理由**: 推断值可能不符合用户预期，需用户确认以避免实验失败
- **关联参数**: 所有 `source == "inferred"` 的参数

#### SAFE-H-005: 密闭加热确认

- **触发条件**: 步骤标记为密闭操作且加热温度超过60°C
- **确认要点**:
  - 容器耐压等级是否满足（参考饱和蒸汽压表）
  - 是否安装泄压装置
  - 温度监控及超温保护是否就位
  - 是否有远程操作/监控方案
- **设计理由**: 密闭加热是最常见的实验室事故场景之一
- **关联规则**: 与 SAFE-T-002 和 SAFE-P-001 联动

---

## 7. 设备能力边界规则

以下规则确保步骤参数在绑定设备的能力范围之内。

### 规则总览

| 规则ID | 条件 | 动作 | 消息模板 |
|--------|------|------|----------|
| SAFE-D-001 | `step.{param}` 超出 `device.capabilities.{param}` 范围 | `blocked` | "步骤 {step_id} 参数 {param} 值 {value} {unit} 超出设备 {device_name} 的能力范围（{min} ~ {max} {unit}）" |
| SAFE-D-002 | `step.operation_type` 不在 `device.supported_operations` 中 | `blocked` | "步骤 {step_id} 要求操作类型 {operation_type}，设备 {device_name} 不支持该操作（支持的操作：{supported_list}）" |
| SAFE-D-003 | `step.device_id` 与其他并行步骤的设备冲突 | `warning` | "步骤 {step_id} 绑定设备 {device_name}，但该设备在时间段 {time_range} 内已被步骤 {conflict_step_id} 占用" |

### 规则详解

#### SAFE-D-001: 参数超出设备范围

- **触发条件**: 步骤的任意参数超出绑定设备对应能力的范围
- **检查范围**:
  ```python
  param_capability_map = {
      "temperature": "temperature",
      "stirring_speed": "stirring_speed",
      "pressure": "pressure",
      "vacuum_level": "vacuum",
      "rotation_speed": "rotation_speed",
      "centrifuge_speed": "centrifuge_speed",
      "duration": "duration_limit",
      "batch_volume": "capacity"
  }
  for param, capability in param_capability_map.items():
      value = getattr(step, param)
      cap = device.capabilities.get(capability)
      if cap and (value < cap.min or value > cap.max):
          trigger("SAFE-D-001", action="blocked",
                  param=param, value=value,
                  min=cap.min, max=cap.max, unit=cap.unit)
  ```
- **设计理由**: 超出设备能力的操作无法执行，强行操作可能损坏设备
- **关联参数**: 所有设备能力对应的步骤参数

#### SAFE-D-002: 设备不支持该操作类型

- **触发条件**: 步骤要求的操作类型不在设备的支持操作列表中
- **操作类型与设备支持映射**:
  | 操作类型 | 支持的设备类型 |
  |----------|----------------|
  | heating | hotplate_stirrer, reactor, oven, tube_furnace, vacuum_oven |
  | stirring | hotplate_stirrer, reactor |
  | centrifugation | centrifuge |
  | vacuum_drying | vacuum_oven |
  | ball_milling | ball_mill |
  | dip_coating | dip_coater |
  | spin_coating | spin_coater |
  | weighing | balance |
  | spectroscopy | spectrometer |
  | inert_atmosphere | glovebox |
- **判断逻辑**:
  ```python
  if step.operation_type not in device.supported_operations:
      trigger("SAFE-D-002", action="blocked",
              operation_type=step.operation_type,
              supported_list=device.supported_operations)
  ```
- **设计理由**: 设备物理上无法执行不支持的操操作类型

#### SAFE-D-003: 设备占用冲突

- **触发条件**: 同一设备在同一时间段被多个步骤绑定
- **判断逻辑**:
  ```python
  schedule = build_device_schedule(all_steps)
  conflicts = detect_overlaps(schedule)
  for conflict in conflicts:
      trigger("SAFE-D-003", action="warning",
              device_name=conflict.device_name,
              time_range=conflict.time_range,
              conflict_step_id=conflict.conflict_step_id)
  ```
- **设计理由**: 物理设备在同一时间只能执行一个操作，需提示用户调整时间安排
- **缓解建议**: 建议用户调整步骤顺序或使用备用设备

---

## 附录: 规则优先级与执行顺序

### 规则执行优先级

编译器按以下优先级顺序执行安全规则检查：

| 优先级 | 规则类别 | 原因 |
|--------|----------|------|
| P0（最高） | SAFE-C-005（氰化物+酸） | 直接生命安全风险 |
| P1 | SAFE-C-001, SAFE-C-003, SAFE-C-004, SAFE-C-006 | 化学反应安全风险 |
| P2 | SAFE-T-001, SAFE-T-002, SAFE-P-001, SAFE-P-002, SAFE-P-003 | 物理/热力学安全风险 |
| P3 | SAFE-A-001, SAFE-M-001, SAFE-M-002, SAFE-D-001, SAFE-D-002 | 操作正确性风险 |
| P4 | SAFE-T-003, SAFE-T-004, SAFE-T-005, SAFE-P-004, SAFE-A-002, SAFE-A-003, SAFE-A-004, SAFE-M-003, SAFE-D-003 | 警告级风险 |
| P5 | SAFE-H-001 ~ SAFE-H-005 | 人工确认（不阻断，但需确认） |

### 执行流程

```
1. 解析协议步骤
2. 按优先级顺序执行规则检查
3. 遇到 blocked → 立即终止，输出错误报告
4. 遇到 require_confirmation → 暂停，等待用户确认
5. 遇到 warning → 记录，继续检查
6. 所有检查完成 → 输出安全审计报告
7. 无 blocked 且所有 require_confirmation 已确认 → 继续编译
```

### 规则版本

- **当前版本**: 1.0.0
- **最后更新**: 2026-08-06
- **维护者**: MatFlow Compiler Skill

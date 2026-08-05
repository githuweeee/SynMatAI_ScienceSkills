# MatFlow Compiler 设备描述 Schema 文档

> 本文档定义了 MatFlow Compiler Skill 中设备描述的 YAML 格式规范、设备类型、能力定义、参数边界、设备绑定逻辑及示例。
> 编译器使用此 Schema 对协议中的步骤进行设备能力校验和绑定。

---

## 目录

1. [设备描述 YAML 格式](#1-设备描述-yaml-格式)
2. [设备类型定义](#2-设备类型定义)
3. [能力 (Capability) 定义](#3-能力-capability-定义)
4. [参数边界定义](#4-参数边界定义)
5. [设备绑定逻辑](#5-设备绑定逻辑)
6. [示例设备描述](#6-示例设备描述)

---

## 1. 设备描述 YAML 格式

设备描述文件使用 YAML 格式，每个文件描述一台设备的完整能力与约束。

### 顶层结构

```yaml
device:
  name: string              # 设备名称（人类可读）
  type: string               # 设备类型（见第2节类型定义）
  id: string                # 设备唯一标识（如 "hotplate-001"）
  manufacturer: string       # 可选 - 制造商
  model: string              # 可选 - 型号
  location: string           # 可选 - 物理位置（如 "Lab-A-Bench-3"）
  capabilities:              # 能力列表（见第3节）
    temperature:
      min: number
      max: number
      unit: string
      precision: number      # 可选 - 控制精度
    stirring_speed:
      min: number
      max: number
      unit: string
      precision: number      # 可选
    # ... 更多能力
  constraints:               # 设备约束
    max_batch_volume: number  # 最大批次体积（mL）
    max_batch_mass: number    # 可选 - 最大批次质量（g）
    compatible_reagents:      # 可选 - 兼容试剂列表
      - string
    incompatible_reagents:    # 可选 - 不兼容试剂列表
      - string
    max_temperature_ramp: number  # 可选 - 最大升温速率（°C/min）
    max_pressure_ramp: number     # 可选 - 最大升压速率（MPa/min）
  supported_operations:       # 支持的操作类型列表
    - string
  metadata:                   # 可选 - 元数据
    calibration_date: string   # 校准日期
    next_calibration: string   # 下次校准日期
    notes: string              # 备注
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device.name` | string | 是 | 设备的人类可读名称 |
| `device.type` | string | 是 | 设备类型枚举值（见第2节） |
| `device.id` | string | 是 | 全局唯一标识符，用于步骤绑定 |
| `device.manufacturer` | string | 否 | 设备制造商 |
| `device.model` | string | 否 | 设备型号 |
| `device.location` | string | 否 | 设备物理位置 |
| `device.capabilities` | object | 是 | 设备能力定义（见第3节） |
| `device.constraints` | object | 否 | 设备使用约束 |
| `device.supported_operations` | list | 是 | 支持的操作类型列表 |
| `device.metadata` | object | 否 | 校准及维护元数据 |

---

## 2. 设备类型定义

MatFlow Compiler 支持以下13种设备类型，每种类型定义了其支持的能力集合。

### 设备类型总览

| 类型标识 | 中文名称 | 主要能力 | 典型应用场景 |
|----------|----------|----------|--------------|
| `hotplate_stirrer` | 加热搅拌器 | temperature, stirring_speed | 常规加热反应、溶解、混合 |
| `reactor` | 反应釜 | temperature, pressure, stirring_speed | 高压反应、水热合成、催化反应 |
| `oven` | 烘箱 | temperature | 干燥、退火、热处理 |
| `tube_furnace` | 管式炉 | temperature, atmosphere_control | 高温烧结、气氛退火、CVD前驱体 |
| `centrifuge` | 离心机 | centrifuge_speed | 固液分离、洗涤、粒径分级 |
| `vacuum_oven` | 真空烘箱 | temperature, vacuum | 低温干燥、溶剂脱除、真空热处理 |
| `glovebox` | 手套箱 | atmosphere_control, capacity | 空气敏感操作、称量、转移 |
| `fume_hood` | 通风橱 | capacity | 通用化学操作、通风保护 |
| `balance` | 天平 | capacity | 称量 |
| `spectrometer` | 光谱仪 | spectroscopy | 成分分析、表征 |
| `dip_coater` | 浸涂机 | dip_speed, withdrawal_speed | 薄膜制备、涂层 |
| `spin_coater` | 旋涂机 | rotation_speed | 薄膜制备、光刻胶涂布 |
| `ball_mill` | 球磨机 | rotation_speed, duration_limit | 粉碎、混合、机械合金化 |

### 各类型详细说明

#### hotplate_stirrer（加热搅拌器）

```yaml
type: hotplate_stirrer
supported_operations:
  - heating
  - stirring
  - mixing
  - dissolution
capabilities:
  - temperature
  - stirring_speed
```

- **说明**: 实验室最常用的基础设备，集成加热和磁力搅拌功能
- **典型参数**: 温度范围 RT~400°C，搅拌速度 0~1500 rpm
- **限制**: 无压力控制能力，不适合密闭反应

#### reactor（反应釜）

```yaml
type: reactor
supported_operations:
  - heating
  - stirring
  - pressurizing
  - sealed_reaction
  - hydrothermal_synthesis
capabilities:
  - temperature
  - pressure
  - stirring_speed
  - capacity
```

- **说明**: 可承受高压的高温反应容器，通常配有压力表和泄压阀
- **典型参数**: 温度范围 RT~300°C，压力范围 0~10 MPa
- **限制**: 需定期检查密封性和压力容器认证

#### oven（烘箱）

```yaml
type: oven
supported_operations:
  - heating
  - drying
  - annealing
capabilities:
  - temperature
  - capacity
```

- **说明**: 提供均匀加热环境的箱式设备，无搅拌和压力控制
- **典型参数**: 温度范围 RT~300°C
- **限制**: 无搅拌功能，加热速率较慢

#### tube_furnace（管式炉）

```yaml
type: tube_furnace
supported_operations:
  - heating
  - annealing
  - sintering
  - atmosphere_control
capabilities:
  - temperature
  - atmosphere_control
  - capacity
```

- **说明**: 管状高温炉，可通入气氛气体，适合高温处理
- **典型参数**: 温度范围 RT~1200°C（部分型号可达1700°C）
- **限制**: 无搅拌功能，样品量受管径限制

#### centrifuge（离心机）

```yaml
type: centrifuge
supported_operations:
  - centrifugation
  - separation
capabilities:
  - centrifuge_speed
  - capacity
  - temperature          # 部分型号支持温控
```

- **说明**: 利用离心力实现固液分离或密度分级
- **典型参数**: 转速范围 0~15000 rpm（部分超速离心机可达100000 rpm）
- **限制**: 需配平，样品体积有限

#### vacuum_oven（真空烘箱）

```yaml
type: vacuum_oven
supported_operations:
  - vacuum_drying
  - heating
  - degassing
capabilities:
  - temperature
  - vacuum
  - capacity
```

- **说明**: 可在真空条件下加热的烘箱，适合热敏性材料干燥
- **典型参数**: 温度范围 RT~250°C，真空度 1~101325 Pa
- **限制**: 无搅拌功能

#### glovebox（手套箱）

```yaml
type: glovebox
supported_operations:
  - inert_atmosphere
  - weighing
  - transfer
  - manual_operation
capabilities:
  - atmosphere_control
  - capacity
```

- **说明**: 提供惰性气氛环境的密封操作箱，用于空气敏感材料操作
- **典型参数**: 水氧含量 <1 ppm，气氛为氮气或氩气
- **限制**: 操作空间有限，需定期维护气氛纯度

#### fume_hood（通风橱）

```yaml
type: fume_hood
supported_operations:
  - ventilation
  - manual_operation
capabilities:
  - capacity
```

- **说明**: 提供通风保护的实验操作空间
- **限制**: 无主动控制能力，仅提供环境安全保护

#### balance（天平）

```yaml
type: balance
supported_operations:
  - weighing
capabilities:
  - capacity
  - precision
```

- **说明**: 精密称量设备
- **典型参数**: 量程 0~220 g，精度 0.0001 g（分析天平）
- **限制**: 需放置在防震台上，避免气流干扰

#### spectrometer（光谱仪）

```yaml
type: spectrometer
supported_operations:
  - spectroscopy
  - analysis
capabilities:
  - spectroscopy_range
  - resolution
```

- **说明**: 光谱分析设备（UV-Vis、FTIR、Raman等）
- **限制**: 分析设备，不参与合成操作

#### dip_coater（浸涂机）

```yaml
type: dip_coater
supported_operations:
  - dip_coating
capabilities:
  - dip_speed
  - withdrawal_speed
  - duration_limit
```

- **说明**: 通过浸入和提拉基材制备薄膜
- **典型参数**: 提拉速度 0.1~50 mm/min
- **限制**: 需要平整基材

#### spin_coater（旋涂机）

```yaml
type: spin_coater
supported_operations:
  - spin_coating
capabilities:
  - rotation_speed
  - duration_limit
```

- **说明**: 通过旋转载体制备均匀薄膜
- **典型参数**: 转速 500~8000 rpm
- **限制**: 基材尺寸有限，薄膜厚度受转速和溶液浓度影响

#### ball_mill（球磨机）

```yaml
type: ball_mill
supported_operations:
  - ball_milling
  - mixing
capabilities:
  - rotation_speed
  - duration_limit
  - capacity
```

- **说明**: 通过球磨介质实现粉碎和混合
- **典型参数**: 转速 100~1000 rpm
- **限制**: 可能引入杂质（磨球材质污染）

---

## 3. 能力 (Capability) 定义

能力是设备可控制的物理参数维度。每种能力定义了其数值范围和单位。

### 能力总览

| 能力标识 | 中文名称 | 数据类型 | 单位 | 说明 |
|----------|----------|----------|------|------|
| `temperature` | 温度控制 | float | °C | 设备可控制的温度范围 |
| `stirring_speed` | 搅拌速度 | float | rpm | 磁力/机械搅拌速度范围 |
| `pressure` | 压力控制 | float | MPa | 设备可承受/控制的压力范围 |
| `vacuum` | 真空度 | float | Pa | 设备可达到的真空度（绝对压力） |
| `rotation_speed` | 转速 | float | rpm | 旋转设备转速范围 |
| `centrifuge_speed` | 离心转速 | float | rpm | 离心机转速范围 |
| `capacity` | 容量 | float | mL | 设备可处理的体积/容量 |
| `duration_limit` | 最大持续时间 | float | min | 单次操作最大持续时间 |
| `atmosphere_control` | 气氛控制 | enum | - | 气氛控制能力（惰性/氧化/还原） |
| `dip_speed` | 浸涂速度 | float | mm/min | 浸涂机浸入/提拉速度 |
| `withdrawal_speed` | 提拉速度 | float | mm/min | 浸涂机提拉速度 |
| `spectroscopy_range` | 光谱范围 | object | nm | 光谱仪波长范围 |
| `resolution` | 分辨率 | float | - | 测量精度/分辨率 |
| `precision` | 精度 | float | - | 控制精度 |

### 各能力详细定义

#### temperature（温度控制）

```yaml
temperature:
  min: number        # 最低温度（°C），可为负值
  max: number        # 最高温度（°C）
  unit: "°C"        # 固定为摄氏度
  precision: number  # 可选 - 控制精度（°C），如 0.1
  ramp_rate_max: number  # 可选 - 最大升温速率（°C/min）
  cooling_rate_max: number  # 可选 - 最大降温速率（°C/min）
```

- **适用设备**: hotplate_stirrer, reactor, oven, tube_furnace, vacuum_oven, centrifuge（部分）
- **示例**: `min: 25, max: 400, precision: 1, ramp_rate_max: 10`

#### stirring_speed（搅拌速度）

```yaml
stirring_speed:
  min: number        # 最低转速（rpm）
  max: number        # 最高转速（rpm）
  unit: "rpm"
  precision: number  # 可选 - 转速控制精度（rpm）
```

- **适用设备**: hotplate_stirrer, reactor
- **示例**: `min: 0, max: 1500, precision: 10`

#### pressure（压力控制）

```yaml
pressure:
  min: number        # 最低工作压力（MPa），通常为 0（表压）
  max: number        # 最高工作压力（MPa）
  unit: "MPa"
  precision: number  # 可选 - 压力控制精度（MPa）
  rated_pressure: number  # 可选 - 设计压力（安全裕量参考）
```

- **适用设备**: reactor
- **示例**: `min: 0, max: 10, precision: 0.1, rated_pressure: 12`

#### vacuum（真空度）

```yaml
vacuum:
  min: number        # 极限真空度（Pa，绝对压力，数值越小真空度越高）
  max: number        # 最大工作压力（Pa，通常为 101325 即常压）
  unit: "Pa"
  precision: number  # 可选 - 真空度控制精度（Pa）
  pump_type: string  # 可选 - 泵类型（rotary_vane / diaphragm / turbomolecular）
```

- **适用设备**: vacuum_oven, reactor（部分）
- **示例**: `min: 1, max: 101325, precision: 10, pump_type: "rotary_vane"`
- **注意**: `min` 表示设备能达到的最低绝对压力（最佳真空度），数值越小越好

#### rotation_speed（转速）

```yaml
rotation_speed:
  min: number        # 最低转速（rpm）
  max: number        # 最高转速（rpm）
  unit: "rpm"
  precision: number  # 可选
```

- **适用设备**: spin_coater, ball_mill
- **示例**: `min: 100, max: 8000, precision: 50`

#### centrifuge_speed（离心转速）

```yaml
centrifuge_speed:
  min: number        # 最低转速（rpm）
  max: number        # 最高转速（rpm）
  unit: "rpm"
  precision: number  # 可选
  max_rcf: number    # 可选 - 最大相对离心力（g）
```

- **适用设备**: centrifuge
- **示例**: `min: 0, max: 15000, precision: 100, max_rcf: 25000`

#### capacity（容量）

```yaml
capacity:
  min: number        # 最小处理量（mL）
  max: number        # 最大处理量（mL）
  unit: "mL"
  precision: number  # 可选
```

- **适用设备**: reactor, oven, vacuum_oven, glovebox, fume_hood, balance, ball_mill
- **示例**: `min: 0, max: 500, precision: 1`

#### duration_limit（最大持续时间）

```yaml
duration_limit:
  min: number        # 最短持续时间（min）
  max: number        # 最长持续时间（min）
  unit: "min"
```

- **适用设备**: dip_coater, spin_coater, ball_mill
- **示例**: `min: 1, max: 720`（最长12小时）

#### atmosphere_control（气氛控制）

```yaml
atmosphere_control:
  supported_gases:     # 支持的气氛气体
    - "nitrogen"
    - "argon"
    - "oxygen"
    - "air"
    - "hydrogen"       # 可选
    - "forming_gas"    # 可选（成形气/还原气）
  max_flow_rate: number  # 最大气体流量（mL/min）
  min_flow_rate: number  # 最小气体流量（mL/min）
  unit: "mL/min"
  moisture_removal: boolean  # 是否具备除水能力
  oxygen_removal: boolean   # 是否具备除氧能力
  target_h2o_ppm: number    # 可选 - 可达水含量（ppm）
  target_o2_ppm: number     # 可选 - 可达氧含量（ppm）
```

- **适用设备**: glovebox, tube_furnace
- **示例**: `supported_gases: [nitrogen, argon], target_h2o_ppm: 0.1, target_o2_ppm: 0.1`

#### dip_speed / withdrawal_speed（浸涂/提拉速度）

```yaml
dip_speed:
  min: number
  max: number
  unit: "mm/min"
  precision: number

withdrawal_speed:
  min: number
  max: number
  unit: "mm/min"
  precision: number
```

- **适用设备**: dip_coater
- **示例**: `min: 0.1, max: 50, precision: 0.01`

---

## 4. 参数边界定义

以下表格汇总了各设备类型在各能力上的典型参数边界，供设备描述文件编写参考。

### 温度能力边界

| 设备类型 | min (°C) | max (°C) | 精度 (°C) | 最大升温速率 (°C/min) |
|----------|----------|----------|-----------|----------------------|
| hotplate_stirrer | 25 | 400 | 1 | 15 |
| reactor | 25 | 300 | 0.5 | 10 |
| oven | 25 | 300 | 1 | 5 |
| tube_furnace | 25 | 1200 | 1 | 20 |
| vacuum_oven | 25 | 250 | 1 | 5 |
| centrifuge（温控型） | -20 | 40 | 0.5 | - |

### 搅拌/转速能力边界

| 设备类型 | 能力 | min | max | 单位 | 精度 |
|----------|------|-----|-----|------|------|
| hotplate_stirrer | stirring_speed | 0 | 1500 | rpm | 10 |
| reactor | stirring_speed | 0 | 600 | rpm | 5 |
| spin_coater | rotation_speed | 100 | 8000 | rpm | 50 |
| ball_mill | rotation_speed | 100 | 1000 | rpm | 10 |
| centrifuge | centrifuge_speed | 0 | 15000 | rpm | 100 |

### 压力/真空能力边界

| 设备类型 | 能力 | min | max | 单位 | 精度 |
|----------|------|-----|-----|------|------|
| reactor | pressure | 0 | 10 | MPa | 0.1 |
| vacuum_oven | vacuum | 1 | 101325 | Pa | 10 |
| reactor（真空型） | vacuum | 100 | 101325 | Pa | 100 |

### 容量能力边界

| 设备类型 | min (mL) | max (mL) | 说明 |
|----------|----------|----------|------|
| hotplate_stirrer | 1 | 2000 | 受烧瓶尺寸限制 |
| reactor | 10 | 500 | 反应釜体积 |
| oven | 0 | 50000 | 受内腔尺寸限制 |
| tube_furnace | 0 | 100 | 受管径限制 |
| vacuum_oven | 0 | 10000 | 受内腔尺寸限制 |
| centrifuge | 0.5 | 500 | 受转子容量限制 |
| glovebox | 0 | 5000 | 受手套箱体积限制 |
| balance | 0 | 220 | 量程（g） |

### 持续时间能力边界

| 设备类型 | min (min) | max (min) | 说明 |
|----------|-----------|-----------|------|
| dip_coater | 1 | 600 | 单次浸涂循环 |
| spin_coater | 1 | 120 | 单次旋涂 |
| ball_mill | 5 | 720 | 单次球磨（最长12h） |

---

## 5. 设备绑定逻辑

设备绑定是编译器将协议步骤中的原子操作映射到具体物理设备的过程。

### 绑定流程

```
协议步骤 → 提取操作类型和参数 → 匹配设备类型 → 检查能力范围 → 确定绑定状态
```

### 绑定状态

| 状态 | 含义 | 编译器行为 |
|------|------|------------|
| `bound` | 完全绑定 | 步骤所有参数均在设备能力范围内，编译正常进行 |
| `partially_bound` | 部分绑定 | 设备支持操作类型，但部分参数超出范围或缺失，触发 SAFE-D-001 警告 |
| `unbound` | 未绑定 | 无设备信息或无匹配设备类型，输出设备无关协议 |
| `exceeded` | 超出能力 | 参数超出设备能力范围，触发 SAFE-D-001 阻断 |

### 绑定算法

```python
def bind_device(step, available_devices):
    """
    将步骤绑定到最合适的设备。
    
    参数:
        step: 协议步骤对象
        available_devices: 可用设备列表
    
    返回:
        binding_result: {
            "status": "bound" | "partially_bound" | "unbound" | "exceeded",
            "device": Device | None,
            "warnings": list,
            "errors": list
        }
    """
    
    # 1. 如果步骤已指定设备ID，直接使用
    if step.device_id:
        device = find_device_by_id(available_devices, step.device_id)
        if device is None:
            return {"status": "unbound", "errors": ["设备ID未找到"]}
        return check_capability(step, device)
    
    # 2. 根据操作类型筛选候选设备
    candidates = filter_by_operation_type(available_devices, step.operation_type)
    if not candidates:
        return {"status": "unbound", "warnings": ["无匹配设备类型，输出设备无关协议"]}
    
    # 3. 检查参数范围，选择最佳匹配
    best_match = None
    best_score = -1
    for device in candidates:
        result = check_capability(step, device)
        if result["status"] == "bound":
            score = calculate_match_score(step, device)
            if score > best_score:
                best_match = device
                best_score = score
    
    if best_match:
        return {"status": "bound", "device": best_match}
    
    # 4. 无完全匹配，检查是否有部分匹配
    for device in candidates:
        result = check_capability(step, device)
        if result["status"] == "partially_bound":
            return result
    
    # 5. 所有候选设备均超出能力
    return {"status": "exceeded", "errors": ["所有候选设备均无法满足参数要求"]}
```

### 能力检查逻辑

```python
def check_capability(step, device):
    """
    检查步骤参数是否在设备能力范围内。
    """
    warnings = []
    errors = []
    
    # 参数到能力的映射
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
    
    status = "bound"
    
    for param, capability_name in param_capability_map.items():
        value = getattr(step, param, None)
        if value is None:
            continue  # 步骤未使用此参数，跳过
        
        capability = device.capabilities.get(capability_name)
        if capability is None:
            warnings.append(f"设备 {device.name} 未声明 {capability_name} 能力")
            status = "partially_bound" if status == "bound" else status
            continue
        
        # 检查最小值
        if value < capability.min:
            errors.append(
                f"参数 {param} 值 {value} 低于设备 {device.name} "
                f"能力下限 {capability.min}"
            )
            status = "exceeded"
        
        # 检查最大值
        if value > capability.max:
            errors.append(
                f"参数 {param} 值 {value} 超过设备 {device.name} "
                f"能力上限 {capability.max}"
            )
            status = "exceeded"
    
    return {
        "status": status,
        "device": device,
        "warnings": warnings,
        "errors": errors
    }
```

### 设备无关协议

当步骤处于 `unbound` 状态时，编译器输出设备无关协议：

```yaml
# 设备无关协议示例
step:
  id: "step-001"
  operation_type: "heating"
  parameters:
    temperature: 80        # 目标温度，不绑定具体设备
    duration: 120           # 持续时间
    ramp_rate: 5            # 升温速率
  device_binding: "unbound" # 绑定状态
  device_requirements:     # 设备需求描述（供后续绑定参考）
    operation_type: "heating"
    required_capabilities:
      - capability: "temperature"
        min: 25
        max: 80
        unit: "°C"
    notes: "需要加热至80°C并保持2小时，升温速率5°C/min"
```

### 匹配评分算法

当多个设备均可满足步骤需求时，使用评分算法选择最佳匹配：

```python
def calculate_match_score(step, device):
    """
    计算设备与步骤的匹配评分。
    评分越高表示匹配度越好。
    """
    score = 0
    
    # 1. 能力覆盖度（覆盖的参数越多越好）
    covered_params = 0
    total_params = 0
    for param in step.get_all_parameters():
        total_params += 1
        if device.has_capability(param):
            covered_params += 1
    score += (covered_params / total_params) * 40
    
    # 2. 参数裕量（参数越接近能力中心越好，避免边界操作）
    for param, value in step.get_all_parameters():
        cap = device.get_capability(param)
        if cap and cap.min < value < cap.max:
            margin = min(value - cap.min, cap.max - value)
            range = cap.max - cap.min
            score += (margin / range) * 10  # 最多10分/参数
    
    # 3. 设备专用性（专用设备优先于通用设备）
    specificity_bonus = {
        "reactor": 5,      # 专用高压设备
        "tube_furnace": 5,  # 专用高温设备
        "glovebox": 5,      # 专用惰性气氛设备
        "hotplate_stirrer": 2,  # 通用设备
    }
    score += specificity_bonus.get(device.type, 0)
    
    # 4. 设备可用性（当前未被占用的设备优先）
    if not device.is_occupied:
        score += 10
    
    return score
```

---

## 6. 示例设备描述

以下提供4个完整的设备描述 YAML 示例。

### 示例1: 加热搅拌器（hotplate_stirrer）

```yaml
device:
  name: "IKA RCT basic 加热搅拌器"
  type: "hotplate_stirrer"
  id: "hotplate-001"
  manufacturer: "IKA"
  model: "RCT basic"
  location: "Lab-A-Bench-3"
  
  capabilities:
    temperature:
      min: 25
      max: 400
      unit: "°C"
      precision: 1
      ramp_rate_max: 15
      cooling_rate_max: 5
    stirring_speed:
      min: 0
      max: 1500
      unit: "rpm"
      precision: 10
  
  constraints:
    max_batch_volume: 2000
    max_batch_mass: 500
    max_temperature_ramp: 15
    incompatible_reagents:
      - "hydrofluoric_acid"  # HF会腐蚀加热板表面
  
  supported_operations:
    - heating
    - stirring
    - mixing
    - dissolution
  
  metadata:
    calibration_date: "2026-06-15"
    next_calibration: "2026-12-15"
    notes: "加热板表面有轻微划痕，建议使用铝箔保护"
```

### 示例2: 反应釜（reactor）

```yaml
device:
  name: "Parr 4560 高压反应釜"
  type: "reactor"
  id: "reactor-001"
  manufacturer: "Parr Instrument Company"
  model: "4560"
  location: "Lab-B-FumeHood-1"
  
  capabilities:
    temperature:
      min: 25
      max: 300
      unit: "°C"
      precision: 0.5
      ramp_rate_max: 10
      cooling_rate_max: 3
    pressure:
      min: 0
      max: 10
      unit: "MPa"
      precision: 0.1
      rated_pressure: 12  # 设计压力（含安全裕量）
    stirring_speed:
      min: 0
      max: 600
      unit: "rpm"
      precision: 5
    capacity:
      min: 50
      max: 300
      unit: "mL"
      precision: 1
  
  constraints:
    max_batch_volume: 300
    max_batch_mass: 400
    max_temperature_ramp: 10
    max_pressure_ramp: 0.5
    compatible_reagents:
      - "water"
      - "ethanol"
      - "DMF"
      - "toluene"
    incompatible_reagents:
      - "hydrofluoric_acid"
      - "fuming_nitric_acid"
  
  supported_operations:
    - heating
    - stirring
    - pressurizing
    - sealed_reaction
    - hydrothermal_synthesis
  
  metadata:
    calibration_date: "2026-07-01"
    next_calibration: "2026-10-01"
    notes: "配有机械搅拌和磁力搅拌双模式，压力表量程0-15 MPa，配有爆破片泄压装置"
```

### 示例3: 真空烘箱（vacuum_oven）

```yaml
device:
  name: "BINDER VD 23 真空烘箱"
  type: "vacuum_oven"
  id: "vacuum-oven-001"
  manufacturer: "BINDER"
  model: "VD 23"
  location: "Lab-C-Bench-2"
  
  capabilities:
    temperature:
      min: 25
      max: 250
      unit: "°C"
      precision: 1
      ramp_rate_max: 5
      cooling_rate_max: 2
    vacuum:
      min: 1
      max: 101325
      unit: "Pa"
      precision: 10
      pump_type: "rotary_vane"
    capacity:
      min: 0
      max: 8000
      unit: "mL"
      precision: 1
  
  constraints:
    max_batch_volume: 8000
    max_batch_mass: 2000
    max_temperature_ramp: 5
    incompatible_reagents:
      - "corrosive_gases"  # 腐蚀性气体会损坏内胆
      - "explosive_solvents"  # 爆炸性溶剂在真空下有风险
  
  supported_operations:
    - vacuum_drying
    - heating
    - degassing
    - thermal_treatment
  
  metadata:
    calibration_date: "2026-05-20"
    next_calibration: "2026-11-20"
    notes: "内腔尺寸300x300x300mm，配有数字真空计和油雾过滤器，真空泵需定期换油"
```

### 示例4: 手套箱（glovebox）

```yaml
device:
  name: "Vigor SG1200/750 惰性气氛手套箱"
  type: "glovebox"
  id: "glovebox-001"
  manufacturer: "Vigor"
  model: "SG1200/750"
  location: "Lab-D-Glovebox-Room"
  
  capabilities:
    atmosphere_control:
      supported_gases:
        - "nitrogen"
        - "argon"
      max_flow_rate: 500
      min_flow_rate: 10
      unit: "mL/min"
      moisture_removal: true
      oxygen_removal: true
      target_h2o_ppm: 0.1
      target_o2_ppm: 0.1
    capacity:
      min: 0
      max: 5000
      unit: "mL"
      precision: 1
  
  constraints:
    max_batch_volume: 5000
    max_batch_mass: 3000
    compatible_reagents:
      - "air_sensitive_reagents"
      - "moisture_sensitive_reagents"
    incompatible_reagents:
      - "corrosive_gases"  # 腐蚀性气体会损坏净化系统
      - "high_vapor_pressure_solvents"  # 高蒸汽压溶剂会污染净化柱
  
  supported_operations:
    - inert_atmosphere
    - weighing
    - transfer
    - manual_operation
    - sealed_reaction_setup
  
  metadata:
    calibration_date: "2026-07-10"
    next_calibration: "2026-08-10"
    notes: "双工位手套箱，配有过渡舱（大小过渡舱各一），净化柱需每3个月再生一次，当前水氧含量 <0.1 ppm"
```

---

## 附录: Schema 版本信息

- **Schema 版本**: 1.0.0
- **最后更新**: 2026-08-06
- **维护者**: MatFlow Compiler Skill
- **兼容性**: 与 safety_rules.md v1.0.0 配套使用

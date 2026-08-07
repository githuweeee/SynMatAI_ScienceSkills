# 评测案例说明

`examples/` 目录包含 9 组真实文献编译案例，每组包含 6 个输出文件（protocol.json/yaml、sop.md、missing.md、safety.md、recovery.yaml）。

## 案例列表

### 论文案例（4组）

| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `cui_kessler_2012_*` | Cui & Kessler (2012) | 聚脲/聚氨酯 | 多步聚合反应，分子量控制 |
| `zhou_2020_*` | Zhou et al. (2020) | TiO2-SiO2 Janus 材料 | 溶胶-凝胶法，Pickering 乳液 |
| `yiwen_2022_*` | Yiwen et al. (2022) | 环氧/CFRP 复合材料 | 机械性能优化，工业应用导向 |
| `alder_1938_*` | Alder & Rickert (1938) | Diels-Alder 加合物 | **德语 OCR 文档**，历史文献，高压反应风险 |

### 专利案例（2组）

| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `cn110577629b_*` | CN110577629B | 可降解环氧树脂 | 光固化，巯基-烯反应，DMDC 固化剂 |
| `cn113574101a_*` | CN113574101A | 卤化硼回收 CFRP | 复合材料回收，纤维再利用 |

### TDS 案例（2组）

| 案例 | 文献来源 | 材料类型 | 核心特点 |
|------|---------|---------|---------|
| `k80_tds_*` | Trigonox K-80 TDS | 过氧化氢异丙苯糊 | 自由基引发剂，SADT 75°C，安全储存 |
| `sivo560_tds_*` | Dynasylan SIVO 560 TDS | 硅烷偶联剂 | 水解活化，24小时使用窗口 |

## 案例统计

- **总计**: 9 组案例，54 个输出文件
- **验证状态**: 全部 9 组通过验证（WARN 状态，无 FAIL）
- **覆盖场景**: 论文/专利/TDS、中文/英文/德文、常温/高温/高压、合成/回收/应用

## 使用方式

这些案例可用于：
1. **测试 skill 功能**：验证 protocol.json 生成是否正确
2. **学习参考**：了解如何编写符合 schema 的协议文件
3. **调试问题**：对比正常案例找出问题所在

## 验证方法

使用 `scripts/validate_protocol.py` 验证案例：

```bash
python scripts/validate_protocol.py examples/cui_kessler_2012_protocol.json
```

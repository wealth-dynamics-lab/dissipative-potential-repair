
# dissipative-potential-repair

**过程-状态二元性语言与演化势函数的理论修复：财富热化相变的实证验证**

*Process-State Duality Language and the Theoretical Repair of Evolutionary Potential Function: An Empirical Validation of Wealth Thermalization Phase Transition*

---

## 论文信息

- 作者：Baowei Mi
- 联系方式：baowei.mi@ieee.org
- 论文状态：Working Paper, 2026

---

## 仓库简介

本仓库提供论文全部核心算法的 Python 实现，包括：

- 演化势函数 Psi 的数值求解
- 信息保留度 rho 的估计
- 恢复时间 tau 的滚动窗口 AR(1) 估计
- 五维预警矩阵 (NFWI) 的计算与预警等级划分
- CRJ 相变阈值的 Hansen 面板回归识别
- 四种政策干预场景的数学模拟
- 全文全部图表的重现脚本

所有代码采用 MIT 许可证，任何研究者可自由复现本文全部实证结果。

---

## 目录结构

- `dissipative-potential-repair/`
  - `README.md` — 本文件
  - `LICENSE` — MIT 开源许可证
  - `requirements.txt` — Python 依赖包列表
  - `code/` — 核心算法模块
    - `01_data_cleaning.py` — 数据清洗与面板构建
    - `02_parameter_estimation.py` — 参数估计：tau, rho, k, Hansen 阈值
    - `03_nfwi_computation.py` — 五维预警矩阵 (NFWI) 计算
    - `04_policy_simulation.py` — 政策干预场景模拟
    - `05_reproduce_figures.py` — 全文图表重现
    - `06_appendix_proofs.py` — 附录A：关键定理的数值验证
  - `data/` — 数据目录
    - `README.md` — 数据来源与使用说明
    - `panel_40countries.csv` — 40国面板数据（清洗后）
  - `output/` — 输出目录
    - `tables/` — 正文表格
      - `Table_7_3_parameters.csv`
      - `Table_7_4_scenarios.csv`
    - `figures/` — 正文图表
      - `Figure_6_1_commutative.pdf`
      - `Figure_6_2_rho_curve.pdf`
      - `Figure_7_1_tau_trend.pdf`
      - `Figure_8_1_scenarios.pdf`

---

## 快速开始

**1. 克隆仓库：**

```bash
git clone https://github.com/wealth-dynamics-lab/dissipative-potential-repair.git
cd dissipative-potential-repair
```

**2. 安装依赖：**

```bash
pip install -r requirements.txt
```

**3. 运行核心计算：**

```bash
python code/03_nfwi_computation.py
```

---

## 各模块说明

### 01_data_cleaning.py

**数据来源：**

- WID 2026 (World Inequality Database) — 财富份额数据
- WGI (Worldwide Governance Indicators) — 制度质量指数
- Edelman Trust Barometer 2025 — 社会信任指数
- Penn World Table 10.0 — 宏观变量
- Chetty et al. (2014) — 代际流动性

**功能：**

- 加载并合并多源原始数据
- 缺失值插值与异常值检测
- 构造衍生变量 (M, C, R, Phi)

### 02_parameter_estimation.py

- 信息保留度 rho 的估计 (公式 7.6)
- 恢复时间 tau 的滚动窗口 AR(1) 估计 (公式 7.8-7.9)
- 压缩常数 k 的面板回归估计 (公式 7.7)
- CRJ 相变阈值的 Hansen 面板回归识别
- GARCH 波动率修正

### 03_nfwi_computation.py

- 归一化五维预警指数 NFWI 的计算 (公式 7.16)
- 预警等级划分 (绿色、黄色、橙色、红色)
- 批量处理 40 个国家数据

### 04_policy_simulation.py

- 过程干预与状态干预的数学建模
- 四种政策干预场景的模拟：无干预、一级预防、二级校正、三级紧急
- 相变概率与累计社会成本估计
- 生成表 7-4 的全部对比数据

### 05_reproduce_figures.py

- 重现正文全部图表 (Figure 6.1, 6.2, 7.1 至 7.4, 8.1 等)

### 06_appendix_proofs.py

- 附录 A：忠实嵌入定理 (定理 6.6) 的数值验证
- 附录 A：过程-状态伴随关系 (定理 6.4) 的数值验证
- 附录 A：临界慢化-信息损失对偶原理 (引理 A.2) 的数值验证

---

## 数据说明

清洗后的面板数据文件 (`panel_40countries.csv`) 约 50MB，包含 40 个国家 1990 至 2024 年的年度观测值。

数据使用需遵守原始数据源的引用规范：

- WID 数据：须符合 https://wid.world 的开放获取条款
- WGI 数据：须引用 Kaufmann et al. (2010)
- Edelman 数据：须引用 Edelman Trust Barometer 2025

---

## 运行环境

- Python：3.10 或更高版本
- 主要依赖：
  - numpy >= 1.21
  - scipy >= 1.8
  - pandas >= 1.5
  - statsmodels >= 0.14
  - arch >= 5.3
  - matplotlib >= 3.6
  - scikit-learn >= 1.2

完整依赖列表见 `requirements.txt`。

---

## 开源许可证

MIT License. 详见 `LICENSE` 文件。
```

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Classificaiton config
ClsDataPath = '../data/processed_data.xlsx'  # Replace with your file path
SFTDataPath = '../data/SFTData/generated_compositions.jsonl'
ClsResultpath = '../results/'
ProcessColumns = ["是否电弧熔炼", "是否退火", "退火时间(h)", "退火温度(℃)", "是否放电等离子烧结", "是否激光熔覆", "是否电火花沉积", "是否定向能量沉积"]
ProcessColumnsEn = \
{
    "是否电弧熔炼": "Arc Melting",
    "是否退火": "Annealing",
    "退火时间(h)": "Annealing Time (h)",
    "退火温度(℃)": "Annealing Temperature (C)",
    "是否放电等离子烧结": "Spark Plasma Sintering",
    "是否激光熔覆": "Laser Cladding",
    "是否电火花沉积": "EDS",
    "是否定向能量沉积": "DED"
}
MaterialColumns = ['Co', 'Cr', 'Fe', 'Ni', 'Mo', 'Al', 'Ti', 'W', 'Nb', 'V', 'Ta', 'Zr', 'Hf', 'Mn', 'Cu']
CalculateColumns = ['ΔHmix (kJ/mol)', 'ΔSmix (J/(K×mol)', 'δ (%)', 'VEC', 'PSFE (%)', 'Na', "Δχ (%)", "Ω", 'avg_χ', 'PREN', 'ΔG (%)', 'P (at.%)']

CalculateColumnsDesc = {
    'ΔHmix (kJ/mol)': '混合焓 ΔHmix (kJ/mol) {value}',
    'ΔSmix (J/(K×mol)': '混合熵 ΔSmix (J/(K×mol)) {value}',
    'δ (%)': '原子尺寸差 δ (%) {value}',
    'VEC': '价电子浓度 VEC {value}',
    'PSFE (%)': '相分离驱动力 PSFE (%) {value}',
    'Na': '电子空穴数 Na {value}',
    'Δχ (%)': '电负性差 Δχ (%) {value}',
    'Ω': '热力学参数 Ω {value}',
    'avg_χ': '平均电负性 χ_avg {value}',
    'PREN': '耐点蚀当量 PREN {value}',
    'ΔG (%)': '弹性模量差 ΔG (%) {value}',
    'P (at.%)': '钝化元素含量 P (at.%) {value}'
}

EvalCalculateColumns = {
    'Phase': ['ΔHmix (kJ/mol)', 'ΔSmix (J/(K×mol)', 'δ (%)', 'VEC', 'PSFE (%)', 'Na', "Δχ (%)"],
    'Elongation': ['VEC', 'ΔSmix (J/(K×mol)', 'ΔHmix (kJ/mol)', 'δ (%)', "Δχ (%)", 'PSFE (%)', 'Na'],
    'UTS': ['ΔHmix (kJ/mol)', 'δ (%)', 'VEC', "Δχ (%)", "Ω",  'ΔG (%)'],
    'HV': ['ΔHmix (kJ/mol)', 'δ (%)', 'VEC', "Δχ (%)", "Na"],
    'Corrosion': ['P (at.%)', 'PREN', 'ΔSmix (J/(K×mol)', 'ΔHmix (kJ/mol)', 'δ (%)', "Δχ (%)", 'avg_χ'],
    'Oxidation': ['ΔSmix (J/(K×mol)', 'ΔHmix (kJ/mol)', 'δ (%)', "VEC"]
}


# FCC	BCC IM	label
LabelsColumns = ['FCC', 'BCC', 'IM', 'label']
TargetProps = ['Phase', 'Elongation', 'UTS', 'HV', 'Corrosion', 'Oxidation']
ClsModelDir = '../results/phase_cls_models/'



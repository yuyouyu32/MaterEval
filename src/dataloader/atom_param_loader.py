import pandas as pd
from config import *
import numpy as np
import math


class AtomParam:
    def __init__(self, data_path):
        self.R = 8.314 # J/(mol*K)
        self.atom_radius, self.valence_electron, self.electron_hole, self.electronegativity, self.atom_family, self.hmix_map , self.atom_Tm, self.shear_modulus= self._load_param(data_path)

    def _load_param(self, data_path):
        data_1 = pd.read_excel(data_path, sheet_name='param_1')
        # 设置索引
        data_1.set_index("Unnamed: 0", inplace=True)

        # 转换为字典
        atom_radius = data_1.loc["原子半径（ri）"].to_dict()
        valence_electron = data_1.loc["价电子数（VECi）"].to_dict()
        electron_hole = data_1.loc["电子空穴数（Na)"].to_dict()
        electronegativity = data_1.loc["电负性"].to_dict()
        atom_family = data_1.loc["A/B"].to_dict()
        atom_Tm = data_1.loc["熔点"].to_dict()
        shear_modulus = data_1.loc["Shear modulus G (GPa)"].to_dict()

        data_2 = pd.read_excel(data_path, sheet_name='param_2')
        hmix_map = {}
        for index, row in data_2.iterrows():
            original_maps = row["原子对混合焓"].split(" ")
            # 删除maps中空的字符串
            maps = []
            for map_str in original_maps:
                if map_str != "":
                    maps.append(map_str)
            elements, value = maps
            element_1, element_2 = elements.split("-")
            if element_1 not in hmix_map:
                hmix_map[element_1] = {}
            hmix_map[element_1][element_2] = float(value)
            if element_2 not in hmix_map:
                hmix_map[element_2] = {}
            hmix_map[element_2][element_1] = float(value)
        return atom_radius, valence_electron, electron_hole, electronegativity, atom_family, hmix_map, atom_Tm, shear_modulus

    def _process_element_values(self, element_values: np.ndarray):
         # 根据MaterialColumns的顺序, 生成element_values的字典
        element_dict = dict(zip(MaterialColumns, element_values))
        # 删除element_dict中值为0的元素
        element_dict = {key: value for key, value in element_dict.items() if value != 0}
        return element_dict

    def H_mix(self, element_values: np.ndarray):
        element_dict = self._process_element_values(element_values)
        # 计算混合焓
        h_mix = 0
        elements = list(element_dict.keys())
        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                h_mix += element_dict[elements[i]] * element_dict[elements[j]] * self.hmix_map[elements[i]][elements[j]] * 4
        return h_mix

    def S_mix(self, element_values: np.ndarray):
        s_mix = 0
        for i in range(len(element_values)):
            if element_values[i] != 0:
                s_mix += element_values[i] * np.log(element_values[i])
        return -self.R * s_mix
    
    def delta_x(self, element_values: np.ndarray):
        "计算电负性差"
        x = 0
        element_dict = self._process_element_values(element_values)
        avg_electronegativity = 0
        for element in element_dict:
            avg_electronegativity += self.electronegativity[element] * element_dict[element]

        for element in element_dict:
            x += element_dict[element] * ((self.electronegativity[element] - avg_electronegativity) ** 2)
        return np.sqrt(x) * 100
    
    def avg_x(self, element_values: np.ndarray):
        "计算平均电负性 χ_avg（Pauli 标度）"
        element_dict = self._process_element_values(element_values)
        avg_electronegativity = 0
        for element in element_dict:
            avg_electronegativity += self.electronegativity[element] * element_dict[element]
        return avg_electronegativity

    def atom_radius_diff(self, element_values: np.ndarray):
        "计算原子半径差δ (%)"
        element_dict = self._process_element_values(element_values)
        avg_atom_radius = 0
        for element in element_dict:
            avg_atom_radius += self.atom_radius[element] * element_dict[element]
        atom_radius_diff = 0
        for element in element_dict:
            atom_radius_diff += element_dict[element] * (((self.atom_radius[element] - avg_atom_radius)/ avg_atom_radius) ** 2)
        return np.sqrt(atom_radius_diff) * 100

    def PSFE(self, element_values: np.ndarray):
        "计算PSFE"
        psfe = 0
        element_dict = self._process_element_values(element_values)
        family_A = 0
        family_B = 0
        for element in element_dict:
            if self.atom_family[element] == "A":
                family_A += element_dict[element]
            elif self.atom_family[element] == "B":
                family_B += element_dict[element]
        if family_A <= family_B:
            psfe = 2 * family_A
        else:
            psfe = 2 * family_B
        return psfe * 100
        
    
    def VEC(self, element_values: np.ndarray):
        "计算VEC"
        element_dict = self._process_element_values(element_values)
        vec = 0
        for element in element_dict:
            vec += element_dict[element] * self.valence_electron[element]
        return vec
    
    def Na(self, element_values: np.ndarray):
        "计算Na"
        element_dict = self._process_element_values(element_values)
        na = 0
        for element in element_dict:
            na += element_dict[element] * self.electron_hole[element]
        return na
    
    def Omega(self, element_values: np.ndarray, s_mix=None, h_mix=None):
        "Ω (= T_m·ΔS_mix / |ΔH_mix|) T_m 为各组元熔点的加权平均值"
        element_dict = self._process_element_values(element_values)
        avg_Tm = 0
        for element in element_dict:
            avg_Tm += element_dict[element] * self.atom_Tm[element]
        if s_mix is None:
            s_mix = self.S_mix(element_values)
        if h_mix is None:
            h_mix = self.H_mix(element_values)
        return (avg_Tm * s_mix) / abs(h_mix * 1000)

    def PREN(self, element_values: np.ndarray):
        "计算耐点蚀当量 PREN（如 PREN = %Cr + 3.3×%Mo + 16×%N）"
        element_dict = self._process_element_values(element_values)
        pren = 0
        for element in element_dict:
            if element == "Cr":
                pren += element_dict[element] * 100
            elif element == "Mo":
                pren += 3.3 * element_dict[element] * 100
            elif element == "N":
                pren += 16 * element_dict[element] * 100
        return pren
    
    def delta_G(self, element_values: np.ndarray):
        """ΔG（弹性模量差，组元剪切模量不均匀性）
        加权平均剪切模量为：

        \[
        \bar{G} = \sum_{i=1}^n c_i G_i
        \]

        \[
        \Delta G = \sqrt{\sum_{i=1}^n c_i \left(1 - \frac{G_i}{\bar{G}}\right)^2}
        \]
        """
        element_dict = self._process_element_values(element_values)
        avg_G = 0
        for element in element_dict:
            avg_G += element_dict[element] * self.shear_modulus[element]
        delta_G = 0
        for element in element_dict:
            delta_G += element_dict[element] * ((1 - self.shear_modulus[element] / avg_G) ** 2)
        return np.sqrt(delta_G) * 100
    
    def P(self, element_values: np.ndarray):
        "计算钝化元素含量 P (at.%)"
        element_dict = self._process_element_values(element_values)
        P = 0
        for element in element_dict:
            if element in ["Cr", "Al", "Ti", "Mo"]:
                P += element_dict[element] * 100
        return P
    
    def cal_atom_param(self, element_values: np.ndarray):
        h_mix = self.H_mix(element_values)
        s_mix = self.S_mix(element_values)
        delta_x = self.delta_x(element_values)
        atom_radius_diff = self.atom_radius_diff(element_values)
        vec = self.VEC(element_values)
        psfe = self.PSFE(element_values)
        na = self.Na(element_values)
        omega = self.Omega(element_values, s_mix, h_mix)
        avg_x = self.avg_x(element_values)
        pren = self.PREN(element_values)
        delta_G = self.delta_G(element_values)
        P = self.P(element_values)
        return {
            'ΔHmix (kJ/mol)': round(h_mix,2),
            'ΔSmix (J/(K×mol)': round(s_mix,2),
            'Δχ (%)': round(delta_x,2),
            'δ (%)': round(atom_radius_diff,3),
            'VEC': round(vec,2),
            'PSFE (%)': round(psfe,2),
            'Na': round(na,2),
            'Ω': round(omega,2),
            'Avg_χ': round(avg_x,2),
            'PREN': round(pren,2),
            'ΔG (%)': round(delta_G,2),
            'P (at.%)': round(P,2)
        }



# python -m dataloader.atom_param_loader
if __name__ == "__main__":
    data_path = "../data/AtomParam.xlsx"
    atom_param = AtomParam(data_path)
    # 0.29	0.37	0.30	0.40	0.13	0	0	0	0	0	0	0	0	0	
    element_values = [0.29, 0.37, 0.30, 0.40, 0.13, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    all_atom_param = atom_param.cal_atom_param(element_values)
    print(all_atom_param)

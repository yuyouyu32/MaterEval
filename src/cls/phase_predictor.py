import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, Optional
from cls.phase_cls import PhaseClsModels
from dataloader.atom_param_loader import AtomParam
from config import *


import pandas as pd
from typing import Dict, Any, List, Union

class HEAPhasePredictor:
    """
    4 models:
      - fcc_model: binary -> FCC existence prob (can co-exist)
      - bcc_model: binary -> BCC existence prob
      - im_model : binary -> IM existence prob
      - label_model: multi-output -> [FCC, BCC, IM] probs together

    Output aligns with your pred_df style:
      FCC, FCC_prob, BCC, BCC_prob, IM, IM_prob, label, label_prob
    """

    def __init__(
        self,
        cls_models,                 # PhaseClsModels instance (with load/save already handled)
        atom_param_loader,          # AtomParam instance
        process_columns,
        material_columns,
        calculate_columns,
        fillna_value: float = 0.0,
    ):
        self.cls_models = cls_models
        self.atom_param_loader = atom_param_loader

        self.process_columns = process_columns
        self.material_columns = material_columns
        self.calculate_columns = calculate_columns
        self.fillna_value = fillna_value

        # IMPORTANT: use training feature order
        self.feature_columns = cls_models.feature_columns

    # =========================
    # Public APIs
    # =========================
    def predict_one(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Predict one sample, return dict (pred_df single-row)."""
        X, calc_dicts = self._featurize_one(sample)
        return self._predict_from_features(X), calc_dicts[0]

    def predict_batch(self, samples: List[Dict[str, Any]]) -> pd.DataFrame:
        """Predict a list of samples, return pred_df."""
        X, calc_dicts = self._featurize_batch(samples)
        pred_dict = self._predict_from_features(X)
        # _predict_from_features returns dict of columns -> list/values
        return pd.DataFrame(pred_dict), calc_dicts

    # =========================
    # Core prediction (features -> outputs)
    # =========================
    def _predict_from_features(self, features: pd.DataFrame) -> Dict[str, Any]:
        """
        features can be 1-row or N-row DataFrame.
        Returns dict like pred_df columns.
        """
        fcc_pred = self.cls_models.fcc_model.predict(features)
        fcc_prob = self.cls_models.fcc_model.predict_proba(features)[:, 1]
        fcc_prob = [round(float(p), 4) for p in fcc_prob]

        bcc_pred = self.cls_models.bcc_model.predict(features)
        bcc_prob = self.cls_models.bcc_model.predict_proba(features)[:, 1]
        bcc_prob = [round(float(p), 4) for p in bcc_prob]

        im_pred = self.cls_models.im_model.predict(features)
        im_prob = self.cls_models.im_model.predict_proba(features)[:, 1]
        im_prob = [round(float(p), 4) for p in im_prob]

        # label (multi-output)
        label_pred = self.cls_models.label_model.predict(features)
        label_pred_list = [[int(i) for i in label] for label in label_pred]

        # label prob (multi-output predict_proba returns list)
        # each item: (n_samples, 2) -> take [:, 1]
        phase_true_prob = []
        for phase_prob in self.cls_models.label_model.predict_proba(features):
            phase_true_prob.append(phase_prob[:, 1])

        label_prob_list = [
            [round(float(fcc), 4), round(float(bcc), 4), round(float(im), 4)]
            for fcc, bcc, im in zip(
                phase_true_prob[0],
                phase_true_prob[1],
                phase_true_prob[2],
            )
        ]

        # If single row, also provide scalar convenience (optional)
        single = (len(features) == 1)

        out = {
            "FCC": fcc_pred.tolist(),
            "FCC_prob": fcc_prob,
            "BCC": bcc_pred.tolist(),
            "BCC_prob": bcc_prob,
            "IM": im_pred.tolist(),
            "IM_prob": im_prob,
            "label": label_pred_list,
            "label_prob": label_prob_list,
        }

        if len(features) == 1:
            out = {k: v[0] if isinstance(v, list) else v for k, v in out.items()}

        return out

    # =========================
    # Feature engineering
    # =========================
    def _featurize_one(self, sample: Dict[str, Any]) -> pd.DataFrame:
        return self._featurize_batch([sample])

    def _featurize_batch(self, samples: List[Dict[str, Any]]) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        calc_dicts = []
        for sample in samples:
            comp: Dict[str, float] = sample.get("composition", {}) or {}
            proc: Dict[str, Any] = sample.get("process", {}) or {}

            row: Dict[str, Any] = {}

            # --- composition -> MaterialColumns ---
            for elem_col in self.material_columns:
                v = comp.get(elem_col, 0.0)
                row[elem_col] = float(v) if v is not None else 0.0

            # normalize if not sum to 1
            total = sum(row[c] for c in self.material_columns)
            if total > 0 and abs(total - 1.0) > 1e-6:
                for c in self.material_columns:
                    row[c] /= total

            # --- process -> ProcessColumns ---
            for pcol in self.process_columns:
                val = proc.get(pcol, None)
                if isinstance(val, bool):
                    row[pcol] = 1.0 if val else 0.0
                elif val is None:
                    row[pcol] = None
                else:
                    row[pcol] = float(val)

            # --- calculate descriptors via AtomParam ---
            # (you confirmed AtomParam uses MaterialColumns order -> safe)
            element_values = [row[e] for e in self.material_columns]
            calc_dict = self.atom_param_loader.cal_atom_param(element_values)
            calc_dicts.append(calc_dict)

            for ccol in self.calculate_columns:
                row[ccol] = calc_dict.get(ccol, None)

            rows.append(row)

        # Align to training feature order
        X = pd.DataFrame([{c: r.get(c, None) for c in self.feature_columns} for r in rows])

        # Fill NaN (SVC can't handle NaN)
        X = X.fillna(self.fillna_value)

        return X, calc_dicts


def unit_test():

    # Load models
    cls_models = PhaseClsModels(
        cls_data_path=ClsDataPath,
        model_dir=ClsModelDir,
        process_columns=ProcessColumns,
        material_columns=MaterialColumns,
        calculate_columns=CalculateColumns,
        labels_columns=LabelsColumns,
        force_retrain=False,
    )

    # Load atom param
    atom_param_loader = AtomParam("../data/AtomParam.xlsx")

    # Create predictor
    predictor = HEAPhasePredictor(
        cls_models=cls_models,
        atom_param_loader=atom_param_loader,
        process_columns=ProcessColumns,
        material_columns=MaterialColumns,
        calculate_columns=CalculateColumns,
        fillna_value=0.0,
    )

    # Test sample
    sample = {
        "composition": {
            "Co": 0.1566265060240964,
            "Ti": 0.14457831325301204,
            "W": 0.37349397590361444,
            "Nb": 0.25301204819277107,
            "Mn": 0.07228915662650602
        },
        "process": {
            "是否电弧熔炼": True,
            "是否放电等离子烧结": None,
            "是否激光熔覆": None,
            "是否电火花沉积": None,
            "是否定向能量沉积": None,
            "是否退火": True,
            "退火时间(h)": 1.5,
            "退火温度(℃)": 1200.0
        },
        "target_property": "Phase"
    }

    pred = predictor.predict_one(sample)
    print("Prediction for one sample:")
    print(pred)

    # Test batch
    samples = [sample, sample]
    pred_df = predictor.predict_batch(samples)
    print("Prediction for batch samples:")
    print(pred_df)

# python -m cls.phase_predictor
if __name__ == "__main__":
    unit_test()
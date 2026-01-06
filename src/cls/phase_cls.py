import itertools
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.svm import SVC
from tqdm import tqdm

from config import *
from dataloader.my_dataloader import CustomDataLoader

logger = logging.getLogger(__name__)

class PhaseClsModels:
    """
    Build / Load 4 classification models:
      - FCC: RF
      - BCC: SVC
      - IM : RF
      - label: RF

    Behavior:
      - If all model files exist under model_dir -> load them (no retrain)
      - Else -> train missing ones and save
    """

    def __init__(
        self,
        cls_data_path: str,
        model_dir: str,
        process_columns,
        material_columns,
        calculate_columns,
        labels_columns,
        force_retrain: bool = False,
    ):
        self.cls_data_path = cls_data_path
        self.model_dir = model_dir
        self.process_columns = process_columns
        self.material_columns = material_columns
        self.calculate_columns = calculate_columns
        self.labels_columns = labels_columns
        self.force_retrain = force_retrain

        os.makedirs(self.model_dir, exist_ok=True)

        # file paths
        self.paths = {
            "fcc": os.path.join(self.model_dir, "fcc_model.joblib"),
            "bcc": os.path.join(self.model_dir, "bcc_model.joblib"),
            "im": os.path.join(self.model_dir, "im_model.joblib"),
            "label": os.path.join(self.model_dir, "label_model.joblib"),
            "meta": os.path.join(self.model_dir, "meta.json"),
        }

        # Load columns (needed for meta)
        self.all_columns = pd.read_excel(cls_data_path).columns.tolist()
        self.drop_columns = [
            c for c in self.all_columns
            if c not in (process_columns + material_columns + calculate_columns + labels_columns)
        ]
        self.feature_columns = [
            c for c in self.all_columns
            if c in (process_columns + material_columns + calculate_columns)
        ]

        # Init dataloader (only needed if we train)
        self.dataloader = None

        # Decide load or train
        if (not force_retrain) and self._all_models_exist():
            self._load_all()
        else:
            self._train_and_save_all()

    # =========================
    # Existence / load / save
    # =========================
    def _all_models_exist(self) -> bool:
        needed = [self.paths["fcc"], self.paths["bcc"], self.paths["im"], self.paths["label"], self.paths["meta"]]
        return all(os.path.exists(p) for p in needed)

    def _load_all(self):
        self.fcc_model = joblib.load(self.paths["fcc"])
        self.bcc_model = joblib.load(self.paths["bcc"])
        self.im_model = joblib.load(self.paths["im"])
        self.label_model = joblib.load(self.paths["label"])

        # meta is optional for runtime, but good to keep consistent
        try:
            with open(self.paths["meta"], "r", encoding="utf-8") as f:
                meta = json.load(f)
            # If you want to strictly enforce same features:
            # self.feature_columns = meta.get("feature_columns", self.feature_columns)
        except Exception as e:
            logger.warning(f"Meta load failed (ignored): {e}")

        logger.info(f"Loaded 4 models from: {self.model_dir}")

    def _save_all(self):
        joblib.dump(self.fcc_model, self.paths["fcc"])
        joblib.dump(self.bcc_model, self.paths["bcc"])
        joblib.dump(self.im_model, self.paths["im"])
        joblib.dump(self.label_model, self.paths["label"])

        meta = {
            "cls_data_path": self.cls_data_path,
            "feature_columns": self.feature_columns,
            "drop_columns": self.drop_columns,
            "process_columns": self.process_columns,
            "material_columns": self.material_columns,
            "calculate_columns": self.calculate_columns,
            "labels_columns": self.labels_columns,
        }
        with open(self.paths["meta"], "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved 4 models to: {self.model_dir}")

    # =========================
    # Train
    # =========================
    def _train_and_save_all(self):
        self.dataloader = CustomDataLoader(self.cls_data_path, self.drop_columns, self.labels_columns)

        self.fcc_model = self._train_fcc_model()
        self.bcc_model = self._train_bcc_model()
        self.im_model = self._train_im_model()
        self.label_model = self._train_label_model()

        self._save_all()

    def _train_fcc_model(self):
        features, target = self.dataloader.get_features_for_target("FCC")
        params = {"class_weight": "balanced", "max_depth": 3, "max_features": 0.25, "n_estimators": 50}
        model = RF(**params)
        model.fit(features, target)
        logger.info("FCC Model Finished.")
        return model

    def _train_bcc_model(self):
        features, target = self.dataloader.get_features_for_target("BCC")
        params = {
            "C": 50,
            "class_weight": "balanced",
            "degree": 2,
            "gamma": "scale",
            "kernel": "linear",
            "probability": True,
        }
        model = SVC(**params)
        model.fit(features, target)
        logger.info("BCC Model Finished.")
        return model

    def _train_im_model(self):
        features, target = self.dataloader.get_features_for_target("IM")
        params = {"class_weight": "balanced", "max_depth": 5, "max_features": 0.25, "n_estimators": 100}
        model = RF(**params)
        model.fit(features, target)
        logger.info("IM Model Finished.")
        return model

    def _train_label_model(self):
        features, target = self.dataloader.get_features_for_target("label")
        model = RF()
        model.fit(features, target)
        logger.info("Label Model Finished.")
        return model


def unit_test():
    phase_cls_models = PhaseClsModels(
        cls_data_path=ClsDataPath,
        model_dir=ClsModelDir,
        process_columns=ProcessColumns,
        material_columns=MaterialColumns,
        calculate_columns=CalculateColumns,
        labels_columns=LabelsColumns,
        force_retrain=False,
    )

if __name__ == "__main__":
    unit_test()
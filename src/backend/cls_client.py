from config import *
from cls.phase_cls import PhaseClsModels
from dataloader.atom_param_loader import AtomParam
from cls.phase_predictor import HEAPhasePredictor

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

phase_predictor = HEAPhasePredictor(
        cls_models=cls_models,
        atom_param_loader=atom_param_loader,
        process_columns=ProcessColumns,
        material_columns=MaterialColumns,
        calculate_columns=CalculateColumns,
        fillna_value=0.0,
    )


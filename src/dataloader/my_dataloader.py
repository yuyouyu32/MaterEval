import pandas as pd
import ast
import numpy as np

class CustomDataLoader:
    def __init__(self, file_path, drop_columns, target_columns):

        if file_path.endswith('.csv'):
            self.data = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            self.data = pd.read_excel(file_path)
        elif file_path.endswith('.jsonl'):
            self.data = pd.read_json(file_path, lines=True)
        else:
            raise ValueError("Unsupported file format. Please provide a .csv, .xlsx, or .jsonl file.")
        self.drop_columns = drop_columns
        self.target_columns = target_columns
        
        self._prepare_data()
    
    def _prepare_data(self):
        # Drop specified columns
        self.data.drop(columns=self.drop_columns, inplace=True)
    
    def get_target_data(self, target_column):
        return self.data[target_column]
    
    def get_features_for_target(self, target):
        if target not in self.target_columns:
            raise ValueError(f"Target {target} is not in target columns {self.target_columns}.")
        if target is None:
            raise ValueError("Target column is not set. Use set_target_column method.")
        
        target_data = self.get_target_data(target)
        non_null_indices = target_data.notnull()
        
        features = self.data.loc[non_null_indices, :].drop(columns=self.target_columns)
        features.fillna(0, inplace=True)
        target = target_data[non_null_indices]
        if target.dtype == 'object':
            target = target.apply(lambda x: ast.literal_eval(x))
            target = np.array(target.tolist())
            return features, target
        
        return features, target

def unit_test():
    # Example usage
    file_path = '/Users/yuyouyu/WorkSpace/Lab106/MinePaper/RL-for-Inverse-Design/Dmax_data/New Data/data_processed.xlsx'  # Replace with your file path
    drop_columns = ['Chemical compostion（at.%）', "Chemical compostion"]  # Columns to drop
    target_columns = ['Critical Diameter/thickness(mm)', 'Tg(K)', 'Tx(K)' , 'Tl(K)', 'σy(MPa)', 'Modulus (GPa)', 'Ε(%)']

    dataloader = CustomDataLoader(file_path, drop_columns, target_columns)

    # Get features and target for a specific target column
    for target in target_columns:
        features, target = dataloader.get_features_for_target(target)
        print(features.shape, target.shape)

if __name__ == '__main__':
    unit_test()
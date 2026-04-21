import pandas as pd
from Desc.BsaeDesc import BaseDescription 

class EyeQDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_label_csv=None):
        # Initialize base class (loads fractal and quality CSVs)
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load DR Labels efficiently
        self.dr_df = None
        if dr_label_csv:
            try:
                # Use the first column (Image name) as index for O(1) lookup
                self.dr_df = pd.read_csv(dr_label_csv, index_col=0)
            except Exception as e:
                print(f"Error loading DR CSV: {e}")

        # 2. DR Level Mapping
        self.dr_map = {
            0: "No Diabetic Retinopathy",
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Proliferative"
        }

    def get_dr_label(self, name):
        if self.dr_df is None:
            return ""

        try:
            # Direct index lookup (fast)
            if name in self.dr_df.index:
                row = self.dr_df.loc[name]
                
                # Logic: In your original code, you took the value at index 2 (row.values[2])
                # Since index is moved out, we need to check the column structure.
                # Assuming the label is now in the 2nd column (index 1) of the remaining dataframe
                # Adjust 'iloc[1]' if the label column position is different.
                val = row.iloc[1] if isinstance(row, pd.Series) else row.iloc[0, 1]
                
                label_int = int(val)
                label_desc = self.dr_map.get(label_int, str(label_int))
                
                return f"the Diabetic Retinopathy Severity Level is:{label_int}({label_desc})"
                
        except Exception as e:
            # print(f"Error lookup DR label for {name}: {e}")
            pass
            
        return ""

    def get_description(self, file_name=""):
        # 1. Call Base method (Handles self.name update, fractal desc, quality desc)
        base_desc = super().get_description(name=file_name)
        
        parts = []
        if base_desc:
            parts.append(base_desc)
            
        # 2. Get DR Label
        dr_desc = self.get_dr_label(file_name)
        if dr_desc:
            parts.append(dr_desc)
            
        return ",".join(parts)

# Usage Example
if __name__ == "__main__":
    # Init once
    desc = EyeQDesc(
        fractal_analysis_csv='EyePACS/good/M4/macula_features.csv', 
        dr_label_csv='/path/to/EyePACS/Label_EyeQ_good.csv'
    )
    
    # Run multiple times fast
    info = desc.get_description(file_name='28413_left.png')
    
    # Specific requirement from your example (high quality check is usually handled by Base, 
    # but here you manually added it in your example, keeping it flexible)
    # info += ", this image is of high quality" 
    
    print(info)

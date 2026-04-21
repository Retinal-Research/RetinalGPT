import pandas as pd
try:
    from Desc.base_description import BaseDescription
except ImportError:
    try:
        from .base_description import BaseDescription
    except ImportError:
        from base_description import BaseDescription

class MessidorDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_label_csv=None):
        # Init base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load DR Labels efficiently
        self.dr_df = None
        if dr_label_csv:
            try:
                # Use first column (filename) as index for O(1) lookup
                self.dr_df = pd.read_csv(dr_label_csv, index_col=0)
            except Exception as e:
                print(f"Error loading DR CSV: {e}")

        # 2. Define Label Map
        # Maps integer label to specific clinical description
        self.dr_map = {
            0: "DR level is 0:Normal, no microaneurysms or hemorrhages",
            1: "DR level is 1:Mild lesion, microaneurysms between 1 and 5, with no hemorrhages",
            2: "DR level is 2:Moderate lesion, 5 to 15 microaneurysms or less than 5 hemorrhages, with no neovascularization (NV=0)",
            3: "DR level is 3:Severe lesion, microaneurysms ≥ 15 or hemorrhages ≥ 5, or presence of neovascularization"
        }

    def get_dr_label(self, name):
        if self.dr_df is None:
            return ""

        try:
            if name in self.dr_df.index:
                # Retrieve the row.
                # Original code used values[1] (2nd column). 
                # Since index is moved out (1st column), we now take the NEW 1st column (iloc[0]).
                val = self.dr_df.loc[name]
                
                # Handle Series (if duplicates exist) or Scalar
                label_val = int(val.iloc[0]) if isinstance(val, pd.Series) else int(val.iloc[0])
                
                return self.dr_map.get(label_val, "")
        except Exception:
            pass
            
        return ""

    def get_description(self, file_name=""):
        # 1. Base Description (Fractal + Quality)
        # Pass file_name so base class updates its state
        base_desc = super().get_description(name=file_name)
        
        parts = []
        if base_desc: 
            parts.append(base_desc)
            
        # 2. DR Label
        dr_desc = self.get_dr_label(file_name)
        if dr_desc: 
            parts.append(dr_desc)
            
        return ",".join(parts)

# Usage Example
if __name__ == "__main__":
    # Init once
    desc_gen = MessidorDesc(
        fractal_analysis_csv='frac_analysis/csv_sig/Messidor.csv', # Example path
        dr_label_csv='/path/to/Messidor/train.csv'
    )
    
    # Run
    # info = desc_gen.get_description(file_name='20051020_43906_0100_PP.png')
    # print(info)

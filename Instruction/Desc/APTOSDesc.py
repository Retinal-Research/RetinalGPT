import pandas as pd
try:
    from Desc.BsaeDesc import BaseDescription
except ImportError:
    try:
        from .BsaeDesc import BaseDescription
    except ImportError:
        from BsaeDesc import BaseDescription

class APTOSDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_label_csv=None):
        # Pass common args to Base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load Subclass-specific data (DR Labels)
        self.dr_df = None
        if dr_label_csv:
            try:
                # Use first column (id_code) as index for speed
                self.dr_df = pd.read_csv(dr_label_csv, index_col=0)
            except Exception as e:
                print(f"Error loading DR CSV: {e}")

        # 2. Map for DR levels
        self.dr_map = {
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Proliferative"
        }

    def get_dr_label(self, name):
        if self.dr_df is None:
            return ""
        
        # Strip extension to match CSV ID format (e.g. '123.png' -> '123')
        img_id = name.split('.')[0]
        
        try:
            if img_id in self.dr_df.index:
                # Get diagnosis value
                val = self.dr_df.loc[img_id]
                # Handle if result is a Series (duplicate IDs) or scalar
                label = int(val.iloc[0]) if isinstance(val, pd.Series) else int(val)
                
                # Format output string
                if label == 0:
                    return "No Diabetic Retinopathy"
                else:
                    level_str = self.dr_map.get(label, str(label))
                    return f"the Diabetic Retinopathy Severity Level is:{label}({level_str})"
        except Exception as e:
            print(f"Error lookup DR label for {img_id}: {e}")
            
        return ""

    def get_description(self, file_name=""):
        # 1. Call Base class method
        # This handles self.name update, fractal desc, and quality desc
        base_desc = super().get_description(name=file_name)
        
        parts = []
        if base_desc:
            parts.append(base_desc)

        # 2. Append Subclass specific logic (DR Label)
        dr_desc = self.get_dr_label(file_name)
        if dr_desc:
            parts.append(dr_desc)

        return ",".join(parts)

# Example Usage
if __name__ == "__main__":
    # Init once
    aptos = APTOSDesc(
        fractal_analysis_csv='frac_analysis/csv_sig/APTOS.csv', 
        dr_label_csv='/media/xinli38/T7 Touch/V&T/APTOS/train.csv', 
        quality_csv='Results_APTOS/M1/results_ensemble.csv'
    )
    
    # Run
    print(aptos.get_description(file_name='6d9effbcde78.png'))

import pandas as pd
from Desc.BsaeDesc import BaseDescription 

class ODIRDDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, disease_csv=None):
        # Init base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load Disease Excel efficiently
        self.disease_df = None
        if disease_csv:
            try:
                # Use ID (First column) as index. 
                # Assuming 'ID' is the first column. If not, adjust index_col.
                self.disease_df = pd.read_excel(disease_csv, index_col=0) 
            except Exception as e:
                print(f"Error loading Disease Excel: {e}")

    def get_disease(self, name):
        if self.disease_df is None:
            return ""

        try:
            # Parse ID and Side from filename (e.g., "1008_right.png")
            parts = name.split('_')
            if len(parts) < 2: return ""
            
            # Convert ID to int because Excel IDs are usually numbers
            patient_id = int(parts[0]) 
            side = parts[1].split('.')[0] # 'left' or 'right'

            if patient_id in self.disease_df.index:
                row = self.disease_df.loc[patient_id]
                
                # Determine column based on side
                if side == 'left':
                    # Check if column exists, handle potential whitespace
                    col_name = 'Left-Diagnostic Keywords'
                else:
                    col_name = 'Right-Diagnostic Keywords'
                
                # Retrieve value if column exists
                if col_name in row:
                    val = row[col_name]
                    return f"disease is {val}"
                else:
                    # Fallback if column names slightly differ
                    print(f"Column {col_name} not found in Excel.")
                    
        except Exception as e:
            # print(f"Error parsing disease for {name}: {e}")
            pass
            
        return ""

    def get_description(self, file_name=""):
        # 1. Base Description
        base_desc = super().get_description(name=file_name)
        
        parts = []
        if base_desc: 
            parts.append(base_desc)
            
        # 2. Disease Description
        dis_desc = self.get_disease(file_name)
        if dis_desc: 
            parts.append(dis_desc)
            
        return ",".join(parts)

# Usage Example
if __name__ == "__main__":
    # Init once (Reading Excel takes time, so do it only here)
    desc_gen = ODIRDDesc(
        fractal_analysis_csv='OIA-ODIR/Results/M4/macula_features.csv', 
        quality_csv='OIA-ODIR/Results/M1/results_ensemble.csv',
        disease_csv='OIA-ODIR/Training Set/Annotation/training annotation (English).xlsx'
    )
    
    # Run
    # info = desc_gen.get_description(file_name='1008_right.png')
    # print(info)
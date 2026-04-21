import json
import pandas as pd
try:
    from Desc.base_description import BaseDescription
except ImportError:
    try:
        from .base_description import BaseDescription
    except ImportError:
        from base_description import BaseDescription

class IDRIDDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_dme_label_csv=None, bd_path=None):
        # Init base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load DR/DME CSV efficiently
        self.labels_df = None
        if dr_dme_label_csv:
            try:
                # Use ID column as index for fast lookup
                self.labels_df = pd.read_csv(dr_dme_label_csv, index_col=0)
            except Exception as e:
                print(f"Error loading Label CSV: {e}")
        
        # 2. Load Bounding Box JSON efficiently (Load once, query many times)
        self.bd_data = None
        if bd_path:
            try:
                with open(bd_path, "r") as f:
                    self.bd_data = json.load(f)
            except Exception as e:
                print(f"Error loading JSON: {e}")

        # 3. Define Mappings (Cleaner than if-else chains)
        self.dr_map = {
            0: "No Diabetic Retinopathy)", # Kept your original closing parenthesis typo if intended? adjusted below
            1: "Mild",
            2: "Moderate",
            3: "Severe",
            4: "Proliferative"
        }
        
        self.dme_map = {
            0: "No fluid accumulation or thickening in the macular region",
            1: "DME is present but does not affect the central macula (fovea)",
            2: "DME involves the central macular area, posing a significant risk to vision due to its impact on the fovea"
        }

    def get_labels_row(self, img_id):
        """Helper to get the row from dataframe"""
        if self.labels_df is not None and img_id in self.labels_df.index:
            return self.labels_df.loc[img_id]
        return None

    def get_dr_label(self, img_id):
        row = self.get_labels_row(img_id)
        if row is not None:
            try:
                # Assuming DR label is in the 1st column (index 0 after setting ID as index) 
                # Originally values[1], now iloc[0] because index is moved out
                val = int(row.iloc[0]) if isinstance(row, pd.Series) else int(row.iloc[0, 0])
                
                desc = self.dr_map.get(val, "No Diabetic Retinopathy")
                if val == 0:
                    return f"the Diabetic Retinopathy Severity Level is: {desc}"
                return f"the Diabetic Retinopathy Severity Level is: {desc}"
            except:
                pass
        return ""

    def get_dme_label(self, img_id):
        row = self.get_labels_row(img_id)
        if row is not None:
            try:
                # Assuming DME label is in the 2nd column (index 1 after setting ID as index)
                # Originally values[2], now iloc[1]
                val = int(row.iloc[1]) if isinstance(row, pd.Series) else int(row.iloc[0, 1])
                return self.dme_map.get(val, "")
            except:
                pass
        return ""

    def get_bounding_box(self, img_id):
        if not self.bd_data or img_id not in self.bd_data:
            # print(f"No bbox data found for {img_id}")
            return ""

        parts = ["Here some bounding boxes for anomalies and lesions."]
        lesions = self.bd_data[img_id]
        
        for lesion_type, boxes in lesions.items():
            # Convert lists to string representation
            box_str = ", ".join([str(b) for b in boxes])
            parts.append(f"{lesion_type}: {box_str}.")
            
        return " ".join(parts)

    def get_description(self, file_name=""):
        # Update Base logic
        base_desc = super().get_description(name=file_name)
        img_id = file_name.split('.')[0]
        
        desc_list = []
        
        # 1. Base Description
        if base_desc: desc_list.append(base_desc)
        
        # 2. DR Label
        dr = self.get_dr_label(img_id)
        if dr: desc_list.append(dr)
        
        # 3. DME Label
        dme = self.get_dme_label(img_id)
        if dme: desc_list.append(dme)
        
        # 4. Bounding Boxes
        bbox = self.get_bounding_box(img_id)
        if bbox: desc_list.append(bbox)
        
        return ", ".join(desc_list)

# Usage
if __name__ == "__main__":
    # Load once
    desc_gen = IDRIDDesc(
        fractal_analysis_csv='frac_analysis/csv_sig/IDRID_seg.csv', 
        quality_csv='Results_IDRID_seg/M1/results_ensemble.csv', 
        bd_path='IDRID/bounding_boxes.json',
        dr_dme_label_csv='IDRID/labels.csv' # Added for completeness
    )
    
    # Run
    info = desc_gen.get_description(file_name='IDRiD_03.png')
    print(info)

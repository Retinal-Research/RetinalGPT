import json
import pandas as pd
from Desc.BsaeDesc import BaseDescription 

class MICCAIDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, MG_label_csv=None, bd_path=None):
        # Init base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load MG Labels efficiently
        self.mg_df = None
        if MG_label_csv:
            try:
                # Use first column (image name) as index for O(1) lookup
                self.mg_df = pd.read_csv(MG_label_csv, index_col=0)
            except Exception as e:
                print(f"Error loading MG CSV: {e}")

        # 2. Load Bounding Box JSON efficiently
        self.bd_data = None
        if bd_path:
            try:
                with open(bd_path, "r") as f:
                    self.bd_data = json.load(f)
            except Exception as e:
                print(f"Error loading JSON: {e}")

        # 3. Define Mappings
        self.mm_map = {
            0: "No macular lesions",
            1: "Tessellated fundus",
            2: "Diffuse chorioretinal atrophy",
            3: "Patchy chorioretinal atrophy",
            4: "Macular atrophy"
        }
        
        self.lesion_map = {
            'LC': "lacquer cracks",
            'CNV': "choroidal neovascularization",
            'FS': "fuchs spot"
        }

    def get_mm_label(self, name):
        """Get Myopic Maculopathy severity"""
        if self.mg_df is None:
            return ""

        try:
            if name in self.mg_df.index:
                # Get the label from the first column (iloc[0]) after index
                val = self.mg_df.loc[name]
                # Handle Series (duplicate IDs) or Scalar
                label_val = int(val.iloc[0]) if isinstance(val, pd.Series) else int(val.iloc[0])
                
                desc = self.mm_map.get(label_val, str(label_val))
                return f"severity of myopic maculopathy:{desc}"
        except Exception:
            pass
            
        return ""

    def get_disease(self, name):
        """Extract lesion type from filename structure (e.g., ..._LC_...)"""
        # Logic: Split by '_' and check 2nd to last element as per original code
        parts = name.split('_')
        if len(parts) >= 2:
            key = parts[-2]
            if key in self.lesion_map:
                return f"Lesion Types:{self.lesion_map[key]}"
        return ""

    def get_bounding_box(self, name):
        if not self.bd_data or name not in self.bd_data:
            # print(f"No bbox data found for {name}")
            return ""

        # Format: "Here are bounding boxes... [x,y,w,h], [x,y,w,h]"
        boxes = self.bd_data[name]
        # Ensure boxes are converted to string format
        box_strs = [str(box) for box in boxes]
        joined_boxes = ", ".join(box_strs)
        
        return f"Here are bounding boxes for anomalies and lesions. {joined_boxes}"

    def get_description(self, file_name=""):
        # 1. Base Description
        base_desc = super().get_description(name=file_name)
        
        parts = []
        if base_desc: parts.append(base_desc)
        
        # 2. Myopic Maculopathy Label
        mm_desc = self.get_mm_label(file_name)
        if mm_desc: parts.append(mm_desc)
        
        # 3. Disease Type (from filename)
        dis_desc = self.get_disease(file_name)
        if dis_desc: parts.append(dis_desc)
        
        # 4. Bounding Boxes
        bbox_desc = self.get_bounding_box(file_name)
        if bbox_desc: parts.append(bbox_desc)
        
        return ", ".join(parts)

# Usage Example
if __name__ == "__main__":
    # Init once
    desc_gen = MICCAIDesc(
        fractal_analysis_csv='Results_MCCAI/M4/macula_features.csv', 
        quality_csv='Results_MCCAI/M1/results_ensemble.csv', 
        MG_label_csv='MICCAI/2. Groundtruths/labels.csv'
        # bd_path='path/to/json' # Add if needed
    )
    
    # Run
    # info = desc_gen.get_description(file_name='mmac_task_1_train_0006.png')
    # print(info)
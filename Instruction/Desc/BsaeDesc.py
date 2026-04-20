import pandas as pd
try:
    from Desc.frac_dic import frac_dic
except ImportError:
    try:
        from .frac_dic import frac_dic
    except ImportError:
        from frac_dic import frac_dic

class BaseDescription:
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None):
        self.name = file_name
        
        # 1. Load DataFrames
        # Using 'index_col=0' allows O(1) lookup by filename instead of scanning the whole table.
        self.fractal_df = None
        if fractal_analysis_csv:
            try:
                self.fractal_df = pd.read_csv(fractal_analysis_csv, index_col=0)
            except Exception as e:
                print(f"Error loading fractal CSV: {e}")

        self.quality_df = None
        if quality_csv:
            try:
                self.quality_df = pd.read_csv(quality_csv, index_col=0)
            except Exception as e:
                print(f"Error loading quality CSV: {e}")

        # 2. Quality Status Map
        # Pre-define mapping for cleaner logic
        self.quality_map = {
            0: "this image is of high quality",
            1: "the image is of acceptable with noise"
        }
        self.poor_quality_desc = "the image is of poor quality, a replacement or retake is needed"

    def generate_fractal_desc(self, name=None):
        # Allow passing name dynamically to support reusing the instance
        target_name = name if name else self.name
        
        if self.fractal_df is None or target_name not in self.fractal_df.index:
            return ""

        desc_list = []
        try:
            # Get the row as a Series
            row = self.fractal_df.loc[target_name]
            
            # Iterate through column names and values directly
            for col_name, value in row.items():
                # Skip invalid values
                if pd.isna(value) or value in [-1, 0, 1] or value < 0.001:
                    continue
                
                # Use frac_dic to translate column name
                readable_name = frac_dic.get(col_name, col_name)
                desc_list.append(f"{readable_name} is {value:.3f}")

        except Exception as e:
            print(f"Error parsing fractal data for {target_name}: {e}")

        if len(desc_list) < 2:
            return ""
            
        return ",".join(desc_list)

    def get_quality_labels(self, name=None):
        target_name = name if name else self.name
        
        if self.quality_df is None or target_name not in self.quality_df.index:
            return ""

        try:
            # Direct lookup
            row = self.quality_df.loc[target_name]
            # Assuming 'Prediction' is the column name for quality label
            if 'Prediction' in row:
                label = int(row['Prediction'])
                return self.quality_map.get(label, self.poor_quality_desc)
                
        except Exception as e:
            print(f"Error parsing quality data for {target_name}: {e}")
            
        return ""

    def get_description(self, name=""): 
        # Update internal name if provided, otherwise use init name
        if name:
            self.name = name
            
        parts = []
        
        # 1. Fractal Description
        frac_desc = self.generate_fractal_desc(self.name)
        if frac_desc:
            parts.append(frac_desc)
            
        # 2. Quality Description
        qual_desc = self.get_quality_labels(self.name)
        if qual_desc:
            parts.append(qual_desc)
            
        return ",".join(parts)

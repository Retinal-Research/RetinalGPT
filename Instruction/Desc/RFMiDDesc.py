import pandas as pd
try:
    from Desc.base_description import BaseDescription
except ImportError:
    try:
        from .base_description import BaseDescription
    except ImportError:
        from base_description import BaseDescription

class RFMiDDesc(BaseDescription):
    # Mapping defined as a class attribute for cleaner organization
    DISEASE_MAP = {
        "DR": "Diabetic Retinopathy",
        "ARMD": "Age-related macular degeneration",
        "MH": "Media Haze",
        "DN": "Drusens",
        "MYA": "Myopia",
        "BRVO": "Branch retinal vein occlusio",
        "TSLN": "Tessellation",
        "ERM": "Epiretinal Membrane",
        "LS": "Laser scars",
        "MS": "Macular Scar",
        "CSR": "Central Serous Retinopathy",
        "ODC": "Optic disc cupping",
        "CRVO": "Central Retinal Vein Occlusion",
        "TV": "Tortuous vessels",
        "AH": "Asteroid hyalosis",
        "ODP": "Optic disc pallor",
        "ODE": "Optic disc edema",
        "ST": "shunt",
        "AION": "Anterior Ischemic Optic Neuropathy",
        "PT": "Parafoveal telangiectasia",
        "RT": "Retinal traction",
        "RS": "Retinitis",
        "CRS": "Chorioretinitis",
        "EDN": "Exudation",
        "RPEC": "Retinal pigment epithelium changes",
        "MHL": "Macular hole",
        "RP": "Retinitis Pigmentosa",
        "CWS": "Cotton-wool spots",
        "CB": "Coloboma",
        "ODPM": "Optic disc pit maculopathy",
        "PRH": "Preretinal hemorrhage",
        "MNF": "Myelinated nerve fibers",
        "HR": "Hemorrhagic retinopathy",
        "CRAO": "Central Retinal Artery Occlusion",
        "TD": "Tilted disc",
        "CME": "Cystoid Macular Edema",
        "PTCR": "Post-traumatic choroidal rupture",
        "CF": "Choroidal Folds",
        "VH": "Vitreous Hemorrhage",
        "MCA": "Macroaneurysm",
        "VS": "Vasculitis",
        "BRAO": "Branch Retinal Artery Occlusion",
        "PLQ": "Plaque",
        "HPED": "hemorrhagic pigment epithelial detachment",
        "CL": "Collateral"
    }

    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, disease_csv=None):
        # Init base class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)
        
        # 1. Load Disease Labels efficiently
        self.disease_df = None
        if disease_csv:
            try:
                # Use ID column (column 0) as index
                self.disease_df = pd.read_csv(disease_csv, index_col=0)
            except Exception as e:
                print(f"Error loading Disease CSV: {e}")

    def get_disease(self, name):
        if self.disease_df is None:
            return ""

        try:
            # Parse ID from filename (e.g. "1148.png" -> 1148)
            # Ensure int conversion matches CSV index type
            img_id = int(name.split('.')[0])
            
            if img_id in self.disease_df.index:
                row = self.disease_df.loc[img_id]
                
                # RFMiD Structure:
                # Col 0 (Index): ID
                # Col 1 (iloc[0]): Disease_Risk (0 or 1)
                # Col 2+ (iloc[1:]): Specific Diseases
                
                # Check "Disease_Risk" column (assuming it's the first column after index)
                disease_risk = row.iloc[0]
                
                if disease_risk == 1:
                    # Get all columns (diseases) where value is 1, skipping the Risk column itself
                    # row.iloc[1:] selects all specific disease columns
                    active_diseases = row.iloc[1:][row.iloc[1:] == 1].index.tolist()
                    
                    # Map codes to full names
                    desc_list = []
                    for code in active_diseases:
                        # Strip whitespace just in case keys have spaces
                        full_name = self.DISEASE_MAP.get(code.strip(), code)
                        desc_list.append(f"disease is {full_name}")
                    
                    return ",".join(desc_list)
                else:
                    return "No disease risk"
                    
        except ValueError:
            pass # Handle case where filename isn't an integer
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
            
        return ", ".join(parts)

# Usage Example
if __name__ == "__main__":
    # Init once
    desc_gen = RFMiDDesc(
        fractal_analysis_csv='/path/to/RFMiD/Results_train/M4/macula_features.csv',
        disease_csv='/path/to/RFMiD/Groundtruths/RFMiD_Training_Labels.csv',
        quality_csv='/path/to/RFMiD/Results_train/M1/results_ensemble.csv'
    )
    
    # Run
    # info = desc_gen.get_description(file_name='1148.png')
    # print(info)

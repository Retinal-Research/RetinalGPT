from Desc.BsaeDesc import BaseDescription 

class UKDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_label_csv=None):
        # Initialize base class
        # Note: dr_label_csv is accepted for interface consistency but currently unused in this class
        super().__init__(file_name=file_name, fractal_analysis_csv=fractal_analysis_csv, quality_csv=quality_csv)

    def get_description(self, file_name=""):
        # Since this class adds no extra logic, simply return the base description.
        # Passing name=file_name ensures the base class updates the current image ID.
        return super().get_description(name=file_name)

# Usage Example
if __name__ == "__main__":
    # Init once
    desc_gen = UKDesc(
        fractal_analysis_csv='Results_AD/M4/macula_features.csv', 
        quality_csv='Results_AD/M1/results_ensemble.csv'
    )
    
    # Run
    # info = desc_gen.get_description(file_name='1035375_21016_0_0.png')
    # print(info)
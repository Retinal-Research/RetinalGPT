from Desc.BsaeDesc import BaseDescription 
import pandas as pd

class AlignDesc(BaseDescription):
    def __init__(self, file_name="", fractal_analysis_csv=None, quality_csv=None, dr_label_csv=None, disease_csv=None):
        super().__init__(file_name = file_name, fractal_analysis_csv = fractal_analysis_csv, quality_csv=quality_csv)  # 调用基类的构造函数
        self.dr_label_csv = dr_label_csv  # 子类特有属性
        self.disease_csv = disease_csv  # 子类特有属性


    def get_dr_label(self):
        if not self.dr_label_csv:
            return ""
        des = []
        dr_label_csv = pd.read_csv(self.dr_label_csv)
        dr_label = dr_label_csv[dr_label_csv.iloc[:,0] == self.name.split('.')[0]]
        label = dr_label.iloc[0].values[1]
        if label == 1:
            des.append(f"the Diabetic Retinopathy Severity Level is:{label}(Mild)")
        elif label == 2:
            des.append(f"the Diabetic Retinopathy Severity Level is:{label}(Moderate)")
        elif label == 3:
            des.append(f"the Diabetic Retinopathy Severity Level is:{label}(Severe)")
        elif label == 4:
            des.append(f"the Diabetic Retinopathy Severity Level is:{label}(Proliferative)")
        else:
            des.append(f"the Diabetic Retinopathy Severity Level is:{label}(No Diabetic Retinopathy)")

        return ",".join(des)
    def get_disease(self):
        if not self.disease_csv:
            return ""
        des = []
        disease_labels = pd.read_excel(self.disease_csv)
        disease_content = disease_labels[disease_labels.iloc[:,0] == int(self.name.split('_')[0])]
        disease_content.iloc[0]

        # Age = disease_content['Patient Age'].values[0]
        # des.append(f"age is {Age}")
        # PatientSex = disease_content['Patient Sex'].values[0]
        # des.append(f"sex is {PatientSex}")
        position = self.name.split('_')[1].split('.')[0]
        # des.append(f"position is {position}")

        if position == 'left':
            disease_label = disease_content['Left-Diagnostic Keywords'].values[0]
        else:
            disease_label = disease_content['Right-Diagnostic Keywords'].values[0]

        des.append(f'disease is {disease_label}')

        return ",".join(des)        
    
    def get_description(self, file_name=""):
        self.name = file_name
        desc = ""
        # desc += super().get_qualuty_labels()
        # desc += ','
        desc += self.get_disease()
        desc += ','
        desc += self.get_dr_label()
        return desc


# print(AlignDesc(file_name='1008_right.png', fractal_analysis_csv='OIA-ODIR/Results/M4/macula_features.csv', disease_csv='OIA-ODIR/Training Set/Annotation/training annotation (English).xlsx', quality_csv='OIA-ODIR/Results/M1/results_ensemble.csv').get_description())
import pandas as pd
from sklearn.model_selection import train_test_split


# csv_file = "IDRID/B. Disease Grading/2. Groundtruths/b. IDRiD_Disease Grading_Testing Labels.csv"  
# output_train_file = "batch_new/csv/tmp_train.csv"
# output_test_file = "batch_new/csv/tmp_test.csv"

# # 读取 CSV 数据
# df = pd.read_csv(csv_file)

# # 假设标签列为 'label'，请根据实际情况替换
# label_column = 'Retinopathy grade'
# label_column2 = 'Risk of macular edema'

# df['combine'] = list(zip(df[label_column], df[label_column2]))

# # 按标签分布拆分数据集
# train_df, test_df = train_test_split(
#     df, 
#     test_size=0.1,  # 测试集占比
#     stratify=df['combine'],  # 根据标签分布划分
#     random_state=42  # 固定随机种子，保证结果可复现
# )

# # 只保留第一列
# train_df = train_df.iloc[:, [0]]  # 获取第一列
# test_df = test_df.iloc[:, [0]]    # 获取第一列


# # 持续写入（追加模式）
# train_df.to_csv(output_train_file, index=False, header=False, mode='a')  # 追加写入训练集
# test_df.to_csv(output_test_file, index=False, header=False, mode='a')   # 追加写入测试集

# print(f"训练集追加保存到 {output_train_file}，测试集追加保存到 {output_test_file}")

# csv_file = "OIA-ODIR/Training Set/Annotation/training annotation (English).xlsx"  
# data = pd.read_excel(csv_file)
# left = data.iloc[:, [3,5]]
# right = data.iloc[:, [4,6]]

# left.columns = ['image', 'diease']
# right.columns = ['image', 'diease']

# merg = pd.concat([left, right], ignore_index=True)
# merg['diease'] = merg['diease'].apply(lambda x: 0 if str(x).lower() == 'normal fundus' else 1)

# merg.to_csv('OIA-ODIR/Training Set/Annotation/label.csv', index=False)



# import pandas as pd

# # 输入 CSV 文件路径
# csv_file = "Results_VD/M4/macula_features.csv"  # 替换为你的 CSV 文件路径
# output_file = "batch_new/csv/VD.csv"  # 输出文件路径

# # 读取 CSV 文件
# df = pd.read_csv(csv_file)

# # 随机抽取 10% 的数据
# sampled_df = df.sample(frac=0.1, random_state=42)  # 设置 `frac=0.1` 表示抽取 10%，`random_state` 保证结果可复现
# sampled_df = sampled_df.iloc [:,[0]]
# # 保存抽取的数据
# sampled_df.to_csv(output_file, index=False)

# print(f"随机抽取的 10% 数据已保存到: {output_file}")
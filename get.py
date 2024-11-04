import pandas as pd
import os

directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop'
result_dir = os.path.join(directory_path, '地毯')
file_name = '12.xlsx'  # 动态设置文件名
file_path = os.path.join(directory_path, file_name)
result_path = os.path.join(result_dir, file_name)


# 读取没有标题的 Excel 文件
df = pd.read_excel(file_path, header=None)

# 提取第一列每行中的第一个数据
# extracted_data = df.iloc[:, 0].apply(lambda x: str(x).split()[0])
extracted_data = df.iloc[:, 0].apply(lambda x: pd.to_numeric(str(x).split()[0], errors='coerce'))

# 创建新的 DataFrame，仅包含提取的数据
new_df = pd.DataFrame(extracted_data)

# 将结果保存为新的 Excel 文件
new_df.to_excel(result_path, header=False, index=False)

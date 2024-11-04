import os
import pandas as pd


def batch_txt_to_excel(input_folder, output_folder):
    """
    将指定文件夹中的所有空格分隔的.txt文件批量转换为Excel文件。

    参数：
    - input_folder: str，输入.txt文件所在的文件夹路径
    - output_folder: str，保存输出.xlsx文件的文件夹路径
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有.txt文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            txt_file_path = os.path.join(input_folder, file_name)
            excel_file_name = file_name.replace('.txt', '.xlsx')
            excel_file_path = os.path.join(output_folder, excel_file_name)

            try:
                # 读取txt文件，假设数据由空格分隔
                data = pd.read_csv(txt_file_path, sep=r'\s+', header=None)

                # 转换为Excel文件
                data.to_excel(excel_file_path, index=False, header=False)
                print(f"转换成功：{file_name} -> {excel_file_name}")
            except Exception as e:
                print(f"转换失败：{file_name}，错误信息: {e}")


# 示例用法
input_folder = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\工作\\超声波材质数据'  # 替换为你的输入文件夹路径
output_folder = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\工作\\超声波材质数据\\xlsx'  # 替换为你想要的输出文件夹路径

batch_txt_to_excel(input_folder, output_folder)

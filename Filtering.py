import os
import pandas as pd
from collections import deque
from glob import glob
import statistics
import numpy as np

window_size: int = 15
threshold: int = 1200

# 地板：1 地毯：2
previous_status: int = 1
# 缓冲器
carpet_buffer: int = 0


def average_of_deque(dq):
    if len(dq) == 0:
        return 0

    return sum(dq) / len(dq)


def count_in_ranges(dq):
    less_than_1200 = 0
    between_1200_and_2000 = 0
    greater_than_2000 = 0

    # 遍历 deque 中的元素
    for num in dq:
        if num < threshold:
            less_than_1200 += 1
        elif threshold <= num < 2000:
            between_1200_and_2000 += 1
        else:
            greater_than_2000 += 1

    return less_than_1200, between_1200_and_2000, greater_than_2000


def calculate_std_dev(data_deque):
    """
    标准地毯中，标准差为312
    复杂地板中，标准差都在700以上
    机器不动时，标准差只有13左右
    500，50
    """
    data_list = [float(x) for x in data_deque]

    # 计算总体标准差
    std_dev = statistics.pstdev(data_list)

    return std_dev


def split_into_segments(data):
    data_array = np.array(data)
    # 计算段的数量
    num_segments = (len(data_array) + window_size - 1) // window_size

    # 初始化一个 NumPy 数组，用于存储所有段
    segments = np.empty(num_segments, dtype=object)

    for i in range(num_segments):
        # 提取每个段
        start_index = i * window_size
        end_index = min(start_index + window_size, len(data))
        segment = data_array[start_index:end_index]

        # 将段添加到结果中
        segments[i] = segment

    return segments


def filter_paragraph_main(data):
    global previous_status
    global carpet_buffer
    previous_status = 1
    carpet_buffer = 0
    data_paragraph = split_into_segments(data)
    result = pd.Series([1] * len(data), index=data.index)

    for i in range(len(data_paragraph)):
        sliding_window = data_paragraph[i]
        if len(sliding_window) != window_size:
            result.iloc[i * window_size:len(data)] = previous_status
            continue

        classification = count_in_ranges(sliding_window)
        average = average_of_deque(sliding_window)
        std_dev = calculate_std_dev(sliding_window)

        if average > threshold and classification[2] >= 2:
            result.iloc[i * window_size:(i + 1) * window_size] = 1
            previous_status = 1
            carpet_buffer = 0

        elif average < (threshold - 400) and classification[1] == 0 and classification[2] == 0 and std_dev <= 500:
            if carpet_buffer == 1:
                result.iloc[i * window_size:(i + 1) * window_size] = 2
                previous_status = 2
            else:
                result.iloc[i * window_size:(i + 1) * window_size] = previous_status
                carpet_buffer = 1

        else:
            result.iloc[i * window_size:(i + 1) * window_size] = previous_status
            carpet_buffer = 0

    return result


def filter_main(data):
    global previous_status
    previous_status = 1
    sliding_window = deque(maxlen=window_size)
    result = pd.Series([1] * len(data), index=data.index)

    for i in range(len(data)):
        sliding_window.append(data[i])
        if len(sliding_window) != window_size:
            result[i] = previous_status
            continue

        classification = count_in_ranges(sliding_window)
        average = average_of_deque(sliding_window)
        std_dev = calculate_std_dev(sliding_window)

        if average > threshold and classification[2] >= 2:
            result[i] = 1
            previous_status = 1
        elif average < (threshold - 400) and classification[1] == 0 and classification[2] == 0 and 100 < std_dev <= 500:
            result[i] = 2
            previous_status = 2
        else:
            result[i] = previous_status

    return result


def single_main():
    directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop'
    file_name = '标准地毯.xlsx'  # 动态设置文件名
    file_path = os.path.join(directory_path, file_name)

    # 读取 Excel 文件
    df = pd.read_excel(file_path, header=None)
    base_name = os.path.splitext(file_name)[0]
    result_file_name = base_name + ' 结果.xlsx'
    result_file_path = os.path.join(directory_path, result_file_name)

    # 提取第一列的数据
    data = df.iloc[:, 0]

    while len(df.columns) < 7:
        df[len(df.columns)] = None

    df.iloc[:, 6] = filter_paragraph_main(data)
    df.to_excel(result_file_path, index=False, header=False)


def process_file(file_path):
    df = pd.read_excel(file_path, header=None)

    # 提取文件名（不带路径和扩展名）
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    print(base_name)
    # directory_path = os.path.dirname(file_path)
    # directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\工作\\超声波材质数据\\result'
    directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\地毯\\result'

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # 生成结果文件的路径
    result_file_name = base_name + ' 结果.xlsx'
    result_file_path = os.path.join(directory_path, result_file_name)

    # 提取第一列的数据
    data = df.iloc[:, 0]

    # 确保列数至少为 7
    while len(df.columns) < 7:
        df[len(df.columns)] = None

    df.iloc[:, 6] = filter_paragraph_main(data)

    df.to_excel(result_file_path, index=False, header=False)


def main():
    # 定义目标文件夹
    # directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\工作\\超声波材质数据\\xlsx'
    directory_path = 'C:\\Users\\Belfast\\OneDrive\\Desktop\\地毯'

    # 获取该目录下的所有 .xlsx 文件
    file_paths = glob(os.path.join(directory_path, '*.xlsx'))

    # 遍历所有文件并处理
    for file_path in file_paths:
        process_file(file_path)


if __name__ == "__main__":
    main()
    # single_main()

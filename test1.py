import serial
import time
# import pandas as pd
from typing import Optional
import threading
import csv

# 初始化串口对象，使用类型注解
ser: Optional[serial.Serial] = None
# 标志位，用于停止数据接收
stop_receiving = True


def open_serial_port():
    """
    打开串口
    """
    global ser
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        if ser.is_open:
            print(f"串口 {ser.name} 已打开，波特率设为 {ser.baudrate}")
    except Exception as e:
        print(f"无法打开串口: {e}")


def close_serial_port():
    """
    关闭串口
    """
    global ser
    if ser is not None and ser.is_open:  # 使用类型检查
        ser.close()
        print("串口已关闭")
    else:
        print("串口已经是关闭状态或未初始化")


def stop_sending():
    global ser
    if ser is not None and ser.is_open:
        try:
            hex_data = bytes.fromhex('55 AA 0B 0A')
            ser.write(hex_data)
            print("数据已发送: 55 AA 0B 0A")
            print("停止信号已发送")
            time.sleep(0.05)
        except Exception as e:
            print(f"发送停止数据时出错: {e}")


def receive_data():
    """
    持续接收串口数据，直到接收到停止信号。
    """
    global ser, stop_receiving
    while not stop_receiving:
        if ser.in_waiting > 0:
            print(f"串口缓冲区大小: {ser.in_waiting}")
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"收到的数据: {response}")
        time.sleep(0.01)  # 短暂的睡眠以避免占用过多 CPU


def receive_data_with_csv():
    """
    持续接收串口数据，直到接收到停止信号。
    接收的数据由空格分隔，并将结果写入 CSV 文件。
    """
    global ser, stop_receiving

    # 打开一个 CSV 文件，用于写入数据
    with open('C:\\Users\\13012\\Desktop\\ultrasound_result\\A30_echo_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["一次回波", "二次回波", "三次回波", "处理结果"])  # 写入标题行（可选）
        index = 0

        while not stop_receiving:
            if ser.in_waiting > 0:
                index = index + 1
                print(f"串口缓冲区大小: {ser.in_waiting} index: {index}")
                if index > 10000:
                    stop_receiving = True
                    break
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"收到的数据: {response}")

                # 假设数据由空格分隔，拆分成多个字段
                data_fields = response.split(' ')

                # 写入到 CSV 文件
                csv_writer.writerow(data_fields)

            time.sleep(0.01)  # 短暂的睡眠以避免占用过多 CPU


def echo_data_mode():
    global ser, stop_receiving
    if ser is not None and ser.is_open:  # 使用类型检查
        try:
            # 定义要发送的十六进制数据
            hex_data = bytes.fromhex('55 AA 06 05')

            # 发送数据到串口
            ser.write(hex_data)
            print("数据已发送: 55 AA 06 05")

            time.sleep(0.05)

            # 启动接收数据的线程
            stop_receiving = False
            receiving_thread = threading.Thread(target=receive_data_with_csv)
            receiving_thread.start()

            # 监听用户输入以停止接收数据
            input("按下回车键以停止接收数据...\n")
            stop_receiving = True
            receiving_thread.join()
            print("停止接收数据")

            stop_sending()

        except Exception as e:
            print(f"发送或接收数据时出错: {e}")
    else:
        print("串口未打开，请先打开串口")


def parse_received_data(data: bytes):
    """
    解析接收到的数据，数据格式为:
    - 帧头 (1 字节): 值为 0x35 (53)
    - 2 字节的 Uint 数据，高字节在前
    - 4 字节的 Uint 数据，高字节在前
    - 1 字节的和校验
    """
    if len(data) != 8:
        print("接收到的数据长度不正确，无法解析")
        return

    frame_header = data[0]
    if frame_header != 0x35:
        print(f"帧头不匹配，收到的帧头: {frame_header}")
        return

    uint16_data = int.from_bytes(data[1:3], byteorder='big')  # 高字节在前
    uint32_data = int.from_bytes(data[3:7], byteorder='big')  # 高字节在前
    checksum = data[7]

    # print(f"帧头: {frame_header}")
    # print(f"2 字节 Uint 数据: {uint16_data}")
    # print(f"4 字节 Uint 数据: {uint32_data}")
    # print(f"校验和: {checksum}")
    print(f"一次回波: {frame_header} {uint16_data} {uint32_data} {checksum}")


def receive_and_parse_data():
    """
    持续接收串口数据，并按指定格式解析。
    """
    global ser, stop_receiving
    buffer = bytearray()
    while not stop_receiving:
        if ser.in_waiting > 0:
            buffer += ser.read(ser.in_waiting)  # 读取串口中所有可用数据

            # 检查缓冲区中是否有完整的数据包
            while len(buffer) >= 8:
                if buffer[0] == 0x35:  # 检查帧头
                    data_packet = buffer[:8]  # 提取一个完整的数据包
                    parse_received_data(data_packet)  # 解析数据包
                    buffer = buffer[8:]  # 移除已处理的数据
                else:
                    buffer.pop(0)  # 丢弃不符合的数据

        time.sleep(0.02)  # 短暂的睡眠以避免占用过多 CPU


def one_echo_mode():
    """
    向打开的串口发送指定的十六进制数据 '55 AA 0A 09'。
    并持续接收并解析数据。
    """
    global ser, stop_receiving
    if ser is not None and ser.is_open:  # 使用类型检查
        try:
            # 定义要发送的十六进制数据
            hex_data = bytes.fromhex('55 AA 0A 09')

            # 发送数据到串口
            ser.write(hex_data)
            print("数据已发送: 55 AA 0A 09")

            time.sleep(0.05)

            # 启动接收和解析数据的线程
            stop_receiving = False
            receiving_thread = threading.Thread(target=receive_and_parse_data)
            receiving_thread.start()

            # 监听用户输入以停止接收数据
            input("按下回车键以停止接收数据...\n")
            stop_receiving = True
            receiving_thread.join()
            print("停止接收数据")

            stop_sending()

        except Exception as e:
            print(f"发送或接收数据时出错: {e}")
    else:
        print("串口未打开，请先打开串口")


def main():
    while True:
        print("\n请选择操作:")
        print("0: 打开串口")
        print("1: 回波数据")
        print("2: 一次回波")
        print("3: 关闭串口")
        print("4: 退出程序")

        command = input("请输入 0, 1, 2, 3, 或 4: ").strip()

        if command == '0':
            open_serial_port()

        elif command == '1':
            echo_data_mode()

        elif command == '2':
            one_echo_mode()

        elif command == '3':
            close_serial_port()

        elif command == '4':
            close_serial_port()
            print("程序退出")
            break

        else:
            print("无效输入，请输入 0, 1, 2, 3, 或 4")


if __name__ == '__main__':
    main()

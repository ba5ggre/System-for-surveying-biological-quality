import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_sample_loss(file_path):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file tại {file_path}")
        return

    # 1. Đọc dữ liệu, bỏ qua các dòng rác (như log khởi động)
    # Cột 0: Sequence Number (Số thứ tự), Cột 1: Audio Value (Giá trị âm thanh)
    data = pd.read_csv(file_path, header=None, dtype=str)
    
    # Chuyển đổi sang số, dòng rác sẽ thành NaN và bị loại bỏ
    df = data.apply(pd.to_numeric, errors='coerce').dropna()
    df.columns = ['seq', 'val']
    
    # 2. Tính toán số mẫu mất
    total_received = len(df)
    first_seq = df['seq'].iloc[0]
    last_seq = df['seq'].iloc[-1]
    
    # Số mẫu đáng lẽ phải nhận được theo lý thuyết
    expected_samples = int(last_seq - first_seq + 1)
    lost_samples = int(expected_samples - total_received)
    loss_rate = (lost_samples / expected_samples) * 100 if expected_samples > 0 else 0

    print("-" * 40)
    print(f"BÁO CÁO PHÂN TÍCH: {os.path.basename(file_path)}")
    print(f"Số mẫu thực tế nhận được: {total_received:,}")
    print(f"Số mẫu bị mất (Lost):     {lost_samples:,}")
    print(f"Tỉ lệ mất mẫu:            {loss_rate:.4f} %")
    print("-" * 40)

    # 3. Vẽ biểu đồ để kiểm tra trực quan
    plt.figure(figsize=(12, 5))
    plt.plot(df['val'].values[:5000], color='teal', linewidth=0.8)
    plt.title(f"Sóng âm thanh (Mất mẫu: {loss_rate:.2f}%)")
    plt.xlabel("Chỉ số mẫu")
    plt.ylabel("Biên độ")
    plt.grid(True, alpha=0.3)
    plt.show()

# Thay đường dẫn file .csv bạn vừa capture từ CoolTerm vào đây
# Sử dụng 'r' trước đường dẫn để tránh lỗi gạch chéo ngược
path = r"D:\Code_ESP-IDF\PPG1\data\4002.csv"

analyze_sample_loss(path)
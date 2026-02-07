import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_sampling_points(file_path, fs=1600, zoom_range=(0, 200)):
    if not os.path.exists(file_path):
        print("Lỗi: Không tìm thấy file!")
        return

    # 1. Đọc dữ liệu (Giả sử Cột 0 là Seq, Cột 1 là Val)
    raw_data = pd.read_csv(file_path, header=None, dtype=str)
    
    # Chuyển đổi và làm sạch rác
    df = raw_data.apply(pd.to_numeric, errors='coerce').dropna()
    df.columns = ['seq', 'val']
    
    # Tính thời gian (giây) dựa trên số thứ tự mẫu
    # t = seq / fs
    time_sec = df['seq'].values / fs
    values = df['val'].values

    # 2. Vẽ đồ thị
    plt.figure(figsize=(15, 7))
    
    # Vẽ đường nối giữa các điểm (alpha thấp để làm nền)
    plt.plot(time_sec, values, color='steelblue', linewidth=1, alpha=0.5, label='Dạng sóng')
    
    # Đánh dấu từng điểm lấy mẫu thực tế bằng dấu chấm (marker)
    # Chúng ta chỉ đánh dấu một đoạn để tránh làm rối đồ thị nếu file quá dài
    start, end = zoom_range
    plt.scatter(time_sec[start:end], values[start:end], 
                color='red', s=20, label='Điểm lấy mẫu (Actual Samples)', zorder=3)

    plt.title(f"Chi tiết điểm lấy mẫu tại {fs}Hz", fontsize=14)
    plt.xlabel("Thời gian (Giây)")
    plt.ylabel("Biên độ")
    
    # Thêm lưới để nhìn rõ khoảng cách thời gian giữa các mẫu
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    
    # Phóng to đoạn cần quan sát
    plt.xlim(time_sec[start], time_sec[end])
    
    plt.tight_layout()
    plt.show()

# --- CHẠY CODE ---
path = r"D:\Code_ESP-IDF\PPG1\data\4002.csv"
# zoom_range=(0, 100) nghĩa là chỉ xem 100 điểm đầu tiên để thấy rõ từng điểm mẫu
plot_sampling_points(path, fs=16000, zoom_range=(0, 10000))
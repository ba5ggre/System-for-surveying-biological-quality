import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import os

def analyze_breathing_final(file_path, fs=16000):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file tại {file_path}")
        return

    # 1. ĐỌC VÀ LÀM SẠCH DỮ LIỆU
    # Đọc cột cuối cùng, loại bỏ dòng chữ (log hệ thống)
    raw_data = pd.read_csv(file_path, header=None, dtype=str)
    signal = pd.to_numeric(raw_data.iloc[:, 0], errors='coerce').dropna().values
    
    if len(signal) < 100:
        print("Dữ liệu quá ngắn để phân tích!")
        return

    # 2. TẠO ĐƯỜNG BAO (ENVELOPE DETECTION)
    rectified_signal = np.abs(signal)
    
    # Tần số cắt (lowcut) để đường bao nhấp nhô theo từng nhịp
    # Nếu nhịp thở của bạn nhanh, hãy tăng con số này lên (5.0 - 10.0)
    lowcut = 5.0  
    nyq = 0.5 * fs
    b, a = butter(4, lowcut / nyq, btype='low')
    soft_envelope = filtfilt(b, a, rectified_signal)

    # 3. THIẾT LẬP NGƯỠNG NHẬN DIỆN (DYNAMIC THRESHOLD)
    # Ngưỡng dựa trên trung vị (median) cộng với 20% biên độ cực đại
    threshold = np.median(soft_envelope) + (np.max(soft_envelope) - np.median(soft_envelope)) * 0.2
    square_envelope = np.where(soft_envelope > threshold, 1, 0)

    # 4. TÍNH TOÁN BPM (NHỊP THỞ/PHÚT)
    # Tìm điểm bắt đầu (0 lên 1)
    diff = np.diff(square_envelope)
    breath_starts = np.where(diff == 1)[0]
    
    avg_bpm = 0
    total_breaths = len(breath_starts)
    
    if total_breaths > 1:
        # Khoảng cách giữa các nhịp tính bằng giây
        intervals_sec = np.diff(breath_starts) / fs
        # Nhịp thở mỗi phút (BPM)
        bpm_values = 60 / intervals_sec
        
        # Lọc bỏ nhiễu: chỉ lấy nhịp từ 3 đến 100 BPM
        valid_bpm = bpm_values[(bpm_values >= 3) & (bpm_values <= 100)]
        if len(valid_bpm) > 0:
            avg_bpm = np.mean(valid_bpm)

    # 5. HIỂN THỊ KẾT QUẢ
    print("-" * 45)
    print(f"FILE: {os.path.basename(file_path)}")
    print(f"Tổng số nhịp đếm được: {total_breaths}")
    print(f"Nhịp thở trung bình:   {avg_bpm:.2f} BPM")
    print("-" * 45)

    # 6. VẼ ĐỒ THỊ
    plt.figure(figsize=(15, 10))
    
    # Đồ thị đường bao
    plt.subplot(2, 1, 1)
    plt.plot(signal, color='steelblue', alpha=0.3, label='Âm thanh thô')
    plt.plot(soft_envelope, color='red', linewidth=2, label='Đường bao (Envelope)')
    plt.axhline(y=threshold, color='black', linestyle='--', label='Ngưỡng (Threshold)')
    plt.title(f"Phân tích Nhịp thở - 15.78 BPM", fontsize=14)
    plt.ylabel("Biên độ")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.2)

    # Đồ thị xung vuông
    plt.subplot(2, 1, 2)
    plt.fill_between(range(len(square_envelope)), 0, square_envelope, color='green', alpha=0.2)
    plt.plot(square_envelope, color='darkgreen', label='Xung vuông trạng thái')
    plt.scatter(breath_starts, [1]*len(breath_starts), color='red', marker='x', label='Bắt đầu nhịp')
    plt.title("Trạng thái nhận diện nhịp thở", fontsize=12)
    plt.xlabel(f"Mẫu (Tổng thời gian: {len(signal)/fs:.2f} giây)")
    plt.ylabel("0: Nghỉ | 1: Thở")
    plt.ylim(-0.1, 1.1)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.show()

# --- THIẾT LẬP ĐƯỜNG DẪN VÀ CHẠY ---
path = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 05-11-32-644.csv"
analyze_breathing_final(path, fs=16000)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
import os

# =================================================================
# PHẦN 1: THUẬT TOÁN (ALGORITHMS)
# =================================================================

class PPGFilterToolkit:
    def __init__(self, fs=100):
        self.fs = fs

    def remove_dc_highpass(self, data, cutoff=0.5, order=2):
        """
        Thuật toán: Butterworth High-pass Filter
        Ý nghĩa: Loại bỏ thành phần DC Offset, đưa tín hiệu về trục 0.
        """
        nyq = 0.5 * self.fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return filtfilt(b, a, data)

class KalmanFilter:
    def __init__(self, Q=1e-4, R=1e-1):
        """
        Q: Process Noise (Nhiễu hệ thống)
        R: Measurement Noise (Nhiễu đo đạc)
        """
        self.Q = Q 
        self.R = R
        self.P = 1.0
        self.X = None # Sẽ khởi tạo bằng mẫu đầu tiên
        self.K = 0.0

    def update(self, measurement):
        if self.X is None:
            self.X = measurement
            return self.X

        # Dự đoán & Cập nhật
        self.K = (self.P + self.Q) / (self.P + self.Q + self.R)
        self.X = self.X + self.K * (measurement - self.X)
        self.P = (1 - self.K) * (self.P + self.Q)
        return self.X

# =================================================================
# PHẦN 2: XỬ LÝ VÀ VẼ BIỂU ĐỒ (VISUALIZATION)
# =================================================================

FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    if not os.path.exists(FILE_INPUT):
        print("Không tìm thấy file!")
        return

    # 1. Đọc dữ liệu
    df = pd.read_csv(FILE_INPUT)
    raw_ir = df.iloc[:, 1].values 
    x = np.arange(len(raw_ir))

    # 2. Thực thi thuật toán
    toolkit = PPGFilterToolkit(fs=100)
    
    # Bước 1: Removing DC
    dc_removed_signal = toolkit.remove_dc_highpass(raw_ir, cutoff=0.5)
    
    # Bước 2: Kalman Smoothing (Chạy trên tín hiệu đã khử DC)
    kf = KalmanFilter(Q=0.0001, R=0.5) # R càng lớn tín hiệu càng mượt
    kalman_smoothed = [kf.update(val) for val in dc_removed_signal]

    # 3. Vẽ biểu đồ theo form yêu cầu
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Biểu đồ 1: Raw IR
    axes[0].plot(x, raw_ir, color='gray', alpha=0.6)
    axes[0].set_title("1. Raw IR Signal (High DC Baseline)")
    axes[0].set_ylabel("Raw Counts")
    axes[0].grid(True, alpha=0.3)

    # Biểu đồ 2: Removing DC
    axes[1].plot(x, dc_removed_signal, color='orange', label='High-pass Filtered')
    axes[1].set_title("2. After Removing DC (Centered at 0)")
    axes[1].set_ylabel("AC Amplitude")
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)

    # Biểu đồ 3: Kalman Smoothing
    axes[2].plot(x, kalman_smoothed, color='purple', linewidth=1.5, label='Kalman Smoothed')
    axes[2].set_title("3. Kalman Filter Applied (Smoothed AC Signal)")
    axes[2].set_xlabel("Sample Index")
    axes[2].set_ylabel("Clean Amplitude")
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
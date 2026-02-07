import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter
import os

# =================================================================
# PHẦN 1: THUẬT TOÁN (ALGORITHMS)
# =================================================================
class PPGProcessor:
    def __init__(self, fs=100):
        self.fs = fs

    def remove_dc_and_filter(self, data, lowcut=0.5, highcut=4.0):
        """
        Bản chất: Kết hợp khử DC và lọc nhiễu cơ bản bằng Bandpass.
        - 0.5Hz: Chặn đứng thành phần DC (0Hz).
        - 4.0Hz: Chặn nhiễu tần số cao.
        """
        nyq = 0.5 * self.fs
        b, a = butter(2, [lowcut/nyq, highcut/nyq], btype='band')
        return filtfilt(b, a, data)

    def smooth_signal(self, data, window_size=11, polyorder=2):
        """
        Thuật toán: Savitzky-Golay Filter (hoặc Moving Average).
        - Bản chất: Khớp một đa thức vào cửa sổ dữ liệu để làm mịn mà không làm mất đỉnh.
        - Ý nghĩa: Làm mượt các gai nhiễu còn sót lại sau khi lọc Bandpass.
        """
        # Đảm bảo window_size là số lẻ
        if window_size % 2 == 0: window_size += 1
        return savgol_filter(data, window_size, polyorder)

# =================================================================
# PHẦN 2: XỬ LÝ VÀ VẼ BIỂU ĐỒ (VISUALIZATION)
# =================================================================

FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    if not os.path.exists(FILE_INPUT): return

    # 1. Đọc dữ liệu thô
    df = pd.read_csv(FILE_INPUT)
    raw_ir = df.iloc[:, 1].values # Lấy cột IR để xử lý chính
    x = np.arange(len(raw_ir))

    # 2. Thực thi thuật toán
    proc = PPGProcessor(fs=100)
    
    # Bước A: Khử DC & Lọc thông dải
    ac_signal = proc.remove_dc_and_filter(raw_ir)
    
    # Bước B: Làm mịn tín hiệu (Smoothing)
    smooth_signal = proc.smooth_signal(ac_signal, window_size=15)

    # 3. Vẽ biểu đồ
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Đồ thị 1: Tín hiệu gốc (DC lớn)
    axes[0].plot(x, raw_ir, color='gray', alpha=0.5)
    axes[0].set_title("1. Raw IR Signal (High DC offset)")
    axes[0].grid(True)

    # Đồ thị 2: Sau khi Remove DC (Về quanh mức 0)
    axes[1].plot(x, ac_signal, color='orange', label='AC Signal')
    axes[1].set_title("2. After DC Removal & Bandpass (AC Component)")
    axes[1].legend()
    axes[1].grid(True)

    # Đồ thị 3: Sau khi làm mịn (Smoothing)
    axes[2].plot(x, smooth_signal, color='green', linewidth=2, label='Smoothed Signal')
    axes[2].set_title("3. Final Smoothed Signal")
    axes[2].set_xlabel("Sample Index")
    axes[2].legend()
    axes[2].grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
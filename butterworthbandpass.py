import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
import os

# =================================================================
# PHẦN 1: THUẬT TOÁN XỬ LÝ TÍN HIỆU (SIGNAL PROCESSING)
# =================================================================
class SignalProcessor:
    def __init__(self, sampling_rate=100):
        self.fs = sampling_rate

    def _butter_bandpass_coeffs(self, lowcut, highcut, order=2):
        """
        Tính toán các hệ số bộ lọc Butterworth.
        - lowcut: Tần số cắt dưới (loại bỏ nhiễu DC/Hô hấp)
        - highcut: Tần số cắt trên (loại bỏ nhiễu tần số cao)
        """
        nyq = 0.5 * self.fs # Tần số Nyquist
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_filter(self, data, lowcut=0.5, highcut=3.5, order=4):
        """
        Áp dụng bộ lọc thông dải lên mảng dữ liệu.
        - Ý nghĩa: Giữ lại tần số từ 0.5Hz (30 BPM) đến 3.5Hz (210 BPM).
        """
        b, a = self._butter_bandpass_coeffs(lowcut, highcut, order=order)
        # Sử dụng filtfilt để không làm lệch pha (Zero-phase filtering)
        y = filtfilt(b, a, data)
        return y

# =================================================================
# PHẦN 2: CẤU HÌNH VÀ VẼ BIỂU ĐỒ (VISUALIZATION)
# =================================================================

# Đường dẫn file của bạn
FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    # 1. Đọc dữ liệu
    if not os.path.exists(FILE_INPUT):
        print("Lỗi: Không tìm thấy file dữ liệu!")
        return
        
    data = pd.read_csv(FILE_INPUT, header=0)
    raw_red = data.iloc[:, 0].values
    raw_ir = data.iloc[:, 1].values
    x = range(len(raw_red))

    # 2. Xử lý thuật toán
    processor = SignalProcessor(sampling_rate=100)
    # Lọc tín hiệu Red và IR
    filtered_red = processor.apply_filter(raw_red)
    filtered_ir = processor.apply_filter(raw_ir)

    # 3. Vẽ biểu đồ theo Form yêu cầu
    # Tạo 3 biểu đồ con: Raw Red, Filtered Red, Filtered IR
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Biểu đồ 1: Raw Red (Tín hiệu thô để kiểm tra biên độ)
    axes[0].plot(x, raw_red, color='gray', linewidth=0.8, label='Raw Red')
    axes[0].set_title("1. Raw Red Signal (Original)", fontsize=12, fontweight='bold')
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend(loc='upper right')

    # Biểu đồ 2: Filtered Red (Tín hiệu Red sau khi lọc - AC Component)
    axes[1].plot(x, filtered_red, color='red', linewidth=1.2, label='Filtered Red (AC)')
    axes[1].set_title("2. Filtered Red Signal (0.5Hz - 3.5Hz)", fontsize=12, fontweight='bold')
    axes[1].set_ylabel("Relative Amplitude")
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend(loc='upper right')

    # Biểu đồ 3: Filtered IR (Tín hiệu IR sau khi lọc - Thường dùng tính BPM/SpO2)
    axes[2].plot(x, filtered_ir, color='blue', linewidth=1.2, label='Filtered IR (AC)')
    axes[2].set_title("3. Filtered IR Signal (0.5Hz - 3.5Hz)", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Sample Index")
    axes[2].set_ylabel("Relative Amplitude")
    axes[2].grid(True, linestyle='--', alpha=0.6)
    axes[2].legend(loc='upper right')

    # Tên chung của biểu đồ
    fig.suptitle(f"Butterworth Bandpass Filter order=4", fontsize=14)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()
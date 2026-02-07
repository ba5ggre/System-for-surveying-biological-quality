import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import os

# =================================================================
# PHẦN 1: THUẬT TOÁN TRÍCH XUẤT cD (ALGORITHM)
# =================================================================
class WaveletDetailComparison:
    def __init__(self, wavelet='db4'):
        self.wavelet = wavelet

    def get_cd_at_levels(self, data, levels=[2, 4, 6, 8]):
        """
        Trích xuất hệ số chi tiết cD tại các Level cụ thể.
        """
        results = {}
        for lv in levels:
            # Phân tách đến level tương ứng
            coeffs = pywt.wavedec(data, self.wavelet, level=lv)
            # coeffs[1] luôn là cD của Level cao nhất trong lần phân tách đó (cD_lv)
            results[lv] = coeffs[1]
        return results

# =================================================================
# PHẦN 2: HIỂN THỊ (VISUALIZATION)
# =================================================================

FILE_PATH = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    if not os.path.exists(FILE_PATH):
        print("Lỗi: Không tìm thấy file!")
        return

    # 1. Đọc dữ liệu (Lấy cột 0)
    df = pd.read_csv(FILE_PATH, header=None)
    raw_signal = df.iloc[:, 0].values
    
    # 2. Thực thi trích xuất cD
    tester = WaveletDetailComparison(wavelet='db4')
    levels_to_plot = [2, 4, 6, 8]
    cd_data = tester.get_cd_at_levels(raw_signal, levels_to_plot)

    # 3. Vẽ biểu đồ
    fig, axes = plt.subplots(len(levels_to_plot), 1, figsize=(12, 12), sharex=False)
    colors = ['purple', 'crimson', 'darkgreen', 'navy']

    for i, lv in enumerate(levels_to_plot):
        axes[i].plot(cd_data[lv], color=colors[i], linewidth=0.8)
        axes[i].set_title(f"Hệ số Chi tiết cD Level {lv} (Samples: {len(cd_data[lv])})", fontweight='bold')
        axes[i].grid(True, alpha=0.3)
        
    plt.suptitle(f"Phân tích hệ số Chi tiết (cD) qua các mức - Wavelet: {tester.wavelet}", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.show()

if __name__ == "__main__":
    main()
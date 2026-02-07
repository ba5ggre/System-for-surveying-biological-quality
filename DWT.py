import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import os

# =================================================================
# PHẦN 1: THUẬT TOÁN PHÂN TÍCH (ALGORITHM)
# =================================================================
class WaveletComparison:
    def __init__(self, wavelet='sym4'):
        self.wavelet = wavelet

    def get_ca_at_level(self, data, level):
        """
        Trích xuất hệ số xấp xỉ cA tại một Level cụ thể.
        """
        coeffs = pywt.wavedec(data, self.wavelet, level=level)
        return coeffs[0] # coeffs[0] luôn là cA của Level cao nhất

# =================================================================
# PHẦN 2: HIỂN THỊ (VISUALIZATION)
# =================================================================

FILE_PATH = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    if not os.path.exists(FILE_PATH):
        print("Không tìm thấy file!")
        return

    # 1. Đọc dữ liệu
    df = pd.read_csv(FILE_PATH, header=None)
    raw_signal = df.iloc[:, 0].values
    
    # 2. Thực thi phân tách tại các mức 2, 4, 6, 8
    tester = WaveletComparison(wavelet='sym4')
    levels = [2, 4, 6, 8]
    ca_results = []
    
    for lv in levels:
        ca_results.append(tester.get_ca_at_level(raw_signal, lv))

    # 3. Vẽ biểu đồ so sánh
    fig, axes = plt.subplots(5, 1, figsize=(12, 12), sharex=False)
    
    # Vẽ tín hiệu gốc để đối chứng
    axes[0].plot(raw_signal, color='gray', alpha=0.6)
    axes[0].set_title("0. Tín hiệu Gốc (Raw IR)", fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    colors = ['blue', 'green', 'orange', 'red']
    for i, lv in enumerate(levels):
        axes[i+1].plot(ca_results[i], color=colors[i])
        axes[i+1].set_title(f"Hệ số Xấp xỉ cA ở Level {lv} (Samples: {len(ca_results[i])})", fontweight='bold')
        axes[i+1].grid(True, alpha=0.3)
        
    plt.suptitle(f"So sánh sự suy giảm nhịp tim trong cA qua các Level (Wavelet: {tester.wavelet})", fontsize=15)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()

if __name__ == "__main__":
    main()
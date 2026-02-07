import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import os

# =================================================================
# THUẬT TOÁN TÁI THIẾT MỨC 6 (RECONSTRUCTION LEVEL 6)
# =================================================================
class WaveletLevel6Cleaner:
    def __init__(self, wavelet='db4'):
        self.wavelet = wavelet
        self.level = 6

    def reconstruct(self, data):
        # 1. Phân tách Wavelet đến Level 6
        coeffs = pywt.wavedec(data, self.wavelet, level=self.level)
        # Cấu trúc coeffs: [cA6, cD6, cD5, cD4, cD3, cD2, cD1]

        # 2. Khởi tạo danh sách hệ số mới (toàn số 0)
        clean_coeffs = [np.zeros_like(c) for c in coeffs]
        
        # 3. CHỌN LỌC HỆ SỐ:
        # Giữ lại cD6 và cD5 (Dải tần nhịp tim ở Level 6)
        clean_coeffs[1] = coeffs[1] # cD6
        clean_coeffs[2] = coeffs[2] # cD5
        
        # cA6 (coeffs[0]) mặc định là 0 để khử Drift

        # 4. Tái thiết tín hiệu
        reconstructed_signal = pywt.waverec(clean_coeffs, self.wavelet)
        return reconstructed_signal

# =================================================================
# HIỂN THỊ KẾT QUẢ
# =================================================================

FILE_PATH = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"

def main():
    if not os.path.exists(FILE_PATH): return

    # Đọc dữ liệu (Cột 0)
    df = pd.read_csv(FILE_PATH, header=None)
    raw_signal = df.iloc[:, 0].values

    # Thực thi tái thiết
    cleaner = WaveletLevel6Cleaner(wavelet='db4')
    final_sig = cleaner.reconstruct(raw_signal)
    
    # Khớp độ dài và cắt bỏ đoạn lỗi biên
    final_sig = final_sig[:len(raw_signal)]
    offset = 300 # Level 6 cần offset lớn hơn để ổn định

    # Vẽ biểu đồ
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(raw_signal[offset:], color='gray', alpha=0.5)
    plt.title("1. Tín hiệu Gốc (Raw - Có Drift & Nhiễu)")
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(final_sig[offset:], color='darkcyan', linewidth=1.5)
    plt.title("2. Tái thiết từ Mức 6 (Chỉ giữ cD6 & cD5 - Khử Drift hoàn toàn)")
    plt.xlabel("Sample Index")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
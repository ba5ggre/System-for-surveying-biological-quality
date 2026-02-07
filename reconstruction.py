import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pywt
import os

def remove_drift_wavelet(signal, wavelet='db4', level=4):
    # 1. Phân tách lấy hệ số
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    
    # 2. Tạo bản sao chỉ giữ lại cA4, các cD khác bằng 0
    drift_coeffs = [np.zeros_like(c) for c in coeffs]
    drift_coeffs[0] = coeffs[0] # Giữ lại mỗi cA4 (thành phần drift)
    
    # 3. Tái thiết đường Drift về độ phân giải gốc
    drift_line = pywt.waverec(drift_coeffs, wavelet)
    drift_line = drift_line[:len(signal)]
    
    # 4. Tín hiệu sạch = Raw - Drift
    clean_signal = signal - drift_line
    return clean_signal, drift_line

# Chạy thử nghiệm
FILE_PATH = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"
df = pd.read_csv(FILE_PATH, header=None)
raw = df.iloc[:, 0].values

clean_sig, drift_curve = remove_drift_wavelet(raw)

# Vẽ biểu đồ
plt.figure(figsize=(12, 6))
plt.plot(raw, color='gray', alpha=0.5, label='Raw (Có Drift)')
plt.plot(drift_curve, color='red', label='Đường Drift (cA4)')
plt.plot(clean_sig, color='teal', label='Sau khi loại bỏ Drift')
plt.title("Khử Drift bằng cách trừ thành phần cA4")
plt.legend()
plt.show()
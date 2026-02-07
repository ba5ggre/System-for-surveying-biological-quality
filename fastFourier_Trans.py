import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import os

def check_loss_by_fft_cleaned(file_path, fs=16000):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file tại {file_path}")
        return

    # 1. Đọc dữ liệu thô (coi tất cả là chuỗi để không bị lỗi nửa chừng)
    data = pd.read_csv(file_path, header=None, dtype=str)
    
    # 2. Ép kiểu sang số, các dòng log 'ESP-ROM...' sẽ trở thành NaN (Not a Number)
    signal_series = pd.to_numeric(data.iloc[:, 0], errors='coerce')
    
    # 3. Xóa các dòng rác (NaN) và chuyển thành mảng số nguyên
    signal = signal_series.dropna().values.astype(np.int32)
    
    n = len(signal)
    if n < 2:
        print("Dữ liệu không đủ để thực hiện FFT!")
        return

    # 4. Thực hiện FFT
    yf = fft(signal)
    xf = fftfreq(n, 1 / fs)[:n//2]
    psd = 2.0/n * np.abs(yf[0:n//2])

    # 5. Vẽ đồ thị
    plt.figure(figsize=(12, 6))
    plt.semilogy(xf, psd, color='red', linewidth=0.8) 
    plt.title(f"Phổ FFT - File: {os.path.basename(file_path)}")
    plt.xlabel("Tần số (Hz)")
    plt.ylabel("Biên độ (Năng lượng)")
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.show()

# =================================================================
# QUAN TRỌNG: Thêm chữ 'r' trước dấu ngoặc kép để Python hiểu đúng đường dẫn
# =================================================================
path = r"D:\Code_ESP-IDF\PPG1\data\400.csv"

check_loss_by_fft_cleaned(path)

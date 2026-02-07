# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt

# # Đọc tín hiệu đã lọc từ file CSV
# file_path = "D:/Esp-idf/Mysource/inmp441_test/data_text/Filter_test/filter_white_noise_test_2nd.csv"
# data = pd.read_csv(file_path, header=None)

# # Lấy tín hiệu từ cột đầu tiên (giả sử dữ liệu là một cột)
# signal = data[0].values

# # Tính toán FFT của tín hiệu
# fft_signal = np.fft.fft(signal)
# frequencies = np.fft.fftfreq(len(signal), d=1/4000)  # Giả sử sample rate là 4000Hz

# # Lọc phần thực và phần ảo của FFT
# fft_magnitude = np.abs(fft_signal)

# # Vẽ đồ thị FFT
# plt.plot(frequencies[:len(frequencies)//2], fft_magnitude[:len(frequencies)//2])  # Lấy nửa đầu của tần số
# plt.title("FFT of Filtered Signal")
# plt.xlabel("Frequency (Hz)")
# plt.ylabel("Bien do")
# plt.grid(True)
# plt.show()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =======================
# 1. Đọc dữ liệu từ file CSV
# =======================
file_path = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-03 10-54-44-779.csv"

data = pd.read_csv(file_path, header=None)

# Lấy CỘT 1 (index = 0)
signal = data.iloc[:, 0].to_numpy()

# =======================
# 2. Tham số tín hiệu
# =======================
fs = 4000  # Sample rate (Hz) – chỉnh đúng theo thực tế
N = len(signal)

# (Khuyên dùng) Loại bỏ DC
signal = signal - np.mean(signal)

# =======================
# 3. FFT
# =======================
fft_signal = np.fft.fft(signal)
frequencies = np.fft.fftfreq(N, d=1/fs)
fft_magnitude = np.abs(fft_signal)

# =======================
# 4. Vẽ phổ tần số (1 phía)
# =======================
half = N // 2

plt.figure(figsize=(10, 5))
plt.plot(frequencies[:half], fft_magnitude[:half])
plt.title("FFT of Signal (Column 1)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Biên độ")
plt.grid(True)
plt.tight_layout()
plt.show()

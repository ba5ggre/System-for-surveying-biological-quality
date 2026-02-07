# import pandas as pd
# import matplotlib.pyplot as plt

# # ================== CẤU HÌNH ==================
# CSV_FILE = r"D:\Code_ESP-IDF\PPG1\data\1.csv"    # tên file csv
# DELIMITER = ","           # dấu phân cách (, ; \t ...)

# HAS_HEADER = True         # True nếu file có header, False nếu không

# # ----- TÊN TRỤC & ĐƠN VỊ -----
# x_label = "Thời gian (s)"

# y1_label = "Tín hiệu 1 (V)"
# y2_label = "Tín hiệu 2 (mV)"
# y3_label = "Tín hiệu 3 (a.u)"

# title1 = "Biểu đồ tín hiệu 1"
# title2 = "Biểu đồ tín hiệu 2"
# title3 = "Biểu đồ tín hiệu 3"
# # ==============================================

# # Đọc file CSV
# if HAS_HEADER:
#     df = pd.read_csv(CSV_FILE, delimiter=DELIMITER)
# else:
#     df = pd.read_csv(CSV_FILE, delimiter=DELIMITER, header=None)

# # Lấy 3 cột đầu
# y1 = df.iloc[:, 0]
# y2 = df.iloc[:, 1]
# y3 = df.iloc[:, 2]

# x = range(len(y1))

# # ================== VẼ BIỂU ĐỒ ==================

# plt.figure()
# plt.plot(x, y1)
# plt.xlabel(x_label)
# plt.ylabel(y1_label)
# plt.title(title1)
# plt.grid(True)

# plt.figure()
# plt.plot(x, y2)
# plt.xlabel(x_label)
# plt.ylabel(y2_label)
# plt.title(title2)
# plt.grid(True)

# plt.figure()
# plt.plot(x, y3)
# plt.xlabel(x_label)
# plt.ylabel(y3_label)
# plt.title(title3)
# plt.grid(True)

# plt.show()
# import pandas as pd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import os

def create_square_envelope(file_path, fs=16000):
    if not os.path.exists(file_path):
        print(f"Lỗi: Không tìm thấy file tại {file_path}")
        return

    # 1. Đọc dữ liệu và loại bỏ các dòng rác (nếu có)
    raw_data = pd.read_csv(file_path, header=None, dtype=str)
    signal = pd.to_numeric(raw_data.iloc[:, 0], errors='coerce').dropna().values

    # 2. Chỉnh lưu (Rectification)
    rectified_signal = np.abs(signal)

    # 3. Tăng tần số cắt (lowcut) lên 5.0Hz để đường bao không bị quá phẳng
    # Điều này giúp đường màu đỏ đi xuống sâu hơn khi bạn ngừng thở/nghỉ giữa nhịp
    lowcut = 5.0  
    nyq = 0.5 * fs
    b, a = butter(4, lowcut / nyq, btype='low')
    soft_envelope = filtfilt(b, a, rectified_signal)

    # 4. Tính toán ngưỡng tự động dựa trên Median và Max
    # Ngưỡng này sẽ nằm cao hơn mức nhiễu nền một chút
    threshold = np.median(soft_envelope) + (np.max(soft_envelope) * 0.15)
    square_envelope = np.where(soft_envelope > threshold, 1, 0)

    # 5. Vẽ đồ thị
    plt.figure(figsize=(15, 10))

    # Đồ thị đường bao: Xem đường màu đỏ có tách biệt các "ngọn núi" không
    plt.subplot(2, 1, 1)
    plt.plot(signal, label='Tín hiệu Raw', color='steelblue', alpha=0.3)
    plt.plot(soft_envelope, label='Đường bao (Đã sửa 5Hz)', color='red', linewidth=2)
    plt.axhline(y=threshold, color='black', linestyle='--', label='Đường ngưỡng (Threshold)')
    plt.title('Phân tích đường bao (Envelope Detection)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Đồ thị xung vuông: Kiểm tra xem các khối xanh đã tách rời chưa
    plt.subplot(2, 1, 2)
    plt.fill_between(range(len(square_envelope)), 0, square_envelope, color='green', alpha=0.3)
    plt.plot(square_envelope, color='darkgreen', label='Xung vuông nhịp thở')
    plt.title('Trạng thái nhịp thở (Square Pulse Status)')
    plt.ylim(-0.1, 1.1)
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# --- GỌI HÀM (ĐÃ SỬA LỖI TYPEERROR) ---
path = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 05-11-32-644.csv"
# Xóa bỏ tham số threshold_factor ở đây để khớp với định nghĩa hàm
create_square_envelope(path, fs=16000)

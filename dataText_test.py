import matplotlib.pyplot as plt
import os

# --- CẤU HÌNH ĐƯỜNG DẪN FILE ---
# Sử dụng r"..." để tránh lỗi ký tự đặc biệt trong đường dẫn Windows
file_path = r"D:\Code_ESP-IDF\PPG1\data\1khz.csv"

# Danh sách chứa dữ liệu sạch
y_values = []

# BƯỚC 1: ĐỌC DỮ LIỆU TỪ FILE
if os.path.exists(file_path):
    print(f"Đang đọc file: {file_path} ...")
    
    # errors='ignore': Bỏ qua các ký tự lạ nếu file bị lỗi encoding
    with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
        for line in file:
            line = line.strip() # Xóa khoảng trắng đầu cuối
            
            # Bỏ qua dòng trống
            if not line:
                continue

            # Tách các cột bằng dấu phẩy
            parts = line.split(',') 
            
            if len(parts) > 0:
                try:
                    # --- TRỌNG TÂM: LẤY CỘT 1 ---
                    # Cố gắng chuyển đổi phần tử đầu tiên sang số thực (float)
                    val = float(parts[0]) 
                    y_values.append(val)
                except ValueError:
                    # Nếu gặp dòng chữ (ví dụ: Log lỗi ESP32, Watchdog...) -> Bỏ qua
                    # print(f"Bỏ qua dòng rác: {line}") # Bỏ comment nếu muốn xem dòng rác
                    continue
else:
    print("LỖI: Không tìm thấy file! Hãy kiểm tra lại đường dẫn.")
    exit()

# BƯỚC 2: VẼ TÍN HIỆU
if len(y_values) > 0:
    print(f"Đã đọc thành công {len(y_values)} mẫu dữ liệu.")
    
    plt.figure(figsize=(12, 6))
    
    # Vẽ dữ liệu từ list y_values
    plt.plot(y_values, label="Raw Audio Signal", color='green', linewidth=0.8)
    
    plt.title(f"Biểu đồ tín hiệu thô từ file CSV\n({len(y_values)} mẫu)")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Tự động zoom vào phần dữ liệu có dao động (nếu cần)
    plt.tight_layout()
    plt.show()
else:
    print("Cảnh báo: File không chứa dữ liệu số hợp lệ nào!")

# import numpy as np
# import matplotlib.pyplot as plt

# # Đường dẫn đến file txt chứa dữ liệu thô
# file_path = "D:\Esp-idf\Mysource\inmp441_test\data_text\Filter_test\data_test400Hz_mclk1152_32bw_raw.csv"  # Đổi tên file thành tên file thực tế của bạn

# # Bước 1: Đọc dữ liệu từ file
# with open(file_path, "r") as file:
#     raw_data = file.read()

# # Bước 2: Xử lý dữ liệu thô thành danh sách số nguyên
# # Loại bỏ ký tự xuống dòng và khoảng trắng, sau đó chuyển thành số nguyên
# data = [int(value) for value in raw_data.strip().split()]

# # Bước 3: Vẽ tín hiệu âm thanh
# plt.figure(figsize=(12, 6))
# plt.plot(data, label="Audio Signal")
# plt.title("Raw Audio Signal from INMP441")
# plt.xlabel("Sample Index")
# plt.ylabel("Amplitude")
# plt.legend()
# plt.grid(True)
# plt.show()  
# import matplotlib.pyplot as plt

# # Đường dẫn đến file chứa dữ liệu bạn vừa copy (lưu thành .txt hoặc .csv)
# file_path = "D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-01 19-00-50-676.csv"

# y_values = []

# # Bước 1: Đọc và xử lý dữ liệu
# try:
#     with open(file_path, "r") as file:
#         for line in file:
#             # Bỏ qua dòng trống
#             if not line.strip():
#                 continue
            
#             # Tách dòng thành các cột (dựa vào khoảng trắng hoặc Tab)
#             # Dữ liệu của bạn: "193.76 1000 0" -> parts[0] = "193.76"
#             parts = line.strip().split()
            
#             if len(parts) > 0:
#                 try:
#                     # Lấy cột đầu tiên (index 0) và chuyển sang số thực (float)
#                     val = float(parts[0])
#                     y_values.append(val)
#                 except ValueError:
#                     continue # Bỏ qua nếu dòng đó không phải số
# except FileNotFoundError:
#     print(f"Lỗi: Không tìm thấy file '{file_path}'. Hãy tạo file này trước!")
#     exit()

# # Bước 2: Vẽ đồ thị
# if len(y_values) > 0:
#     plt.figure(figsize=(12, 6))
#     plt.plot(y_values, label="Breath Signal (RMS)", color='blue', linewidth=1.5)
    
#     # Vẽ thêm đường ngưỡng (tùy chọn, để dễ nhìn giống Serial Plotter)
#     plt.axhline(y=1000, color='r', linestyle='--', label='Threshold (1000)')
    
#     plt.title("Biểu đồ tín hiệu nhịp thở từ dữ liệu Log")
#     plt.xlabel("Sample Index")
#     plt.ylabel("Amplitude")
#     plt.legend()
#     plt.grid(True, which='both', linestyle='--', linewidth=0.5)
#     plt.show()
# else:
#     print("Không đọc được dữ liệu nào hợp lệ!")

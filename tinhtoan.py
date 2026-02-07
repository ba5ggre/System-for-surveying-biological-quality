# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.signal import find_peaks
# import os

# # --- CẤU HÌNH ---
# file_path = r"D:\Code_ESP-IDF\PPG1\data\removingDC_mean.csv"
# fs = 100  # Tần số lấy mẫu (Hz) - Rất quan trọng để tính thời gian chính xác

# def calculate_bio_metrics(path):
#     if not os.path.exists(path):
#         print("Không tìm thấy file!")
#         return

#     # 1. Đọc dữ liệu (Giả định Cột 2: Red_Filtered, Cột 3: IR_Filtered)
#     df = pd.read_csv(path, header=None)
#     red_f = df.iloc[:, 1].values
#     ir_f = df.iloc[:, 2].values

#     # 2. Tìm đỉnh sóng (Peak Detection) trên kênh IR để tính nhịp tim
#     # Tín hiệu đã lọc Bandpass nên đỉnh sẽ rất rõ
#     peaks, _ = find_peaks(ir_f, distance=fs*0.6, prominence=np.std(ir_f)*0.5)
    
#     # 3. Tính toán HRV (SDNN, RMSSD) và Heart Rate
#     # RR intervals (khoảng cách giữa các nhịp) tính bằng miligiây (ms)
#     rr_intervals = np.diff(peaks) * (1000 / fs)
    
#     if len(rr_intervals) > 0:
#         hr = 60 / (np.mean(rr_intervals) / 1000)
#         sdnn = np.std(rr_intervals)
#         rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
#     else:
#         hr, sdnn, rmssd = 0, 0, 0

#     # 4. Tính SpO2 (Phương pháp xấp xỉ Peak-to-Peak cho tín hiệu đã lọc)
#     # Vì đã lọc Bandpass, tín hiệu dao động quanh 0, AC có thể lấy bằng Peak-to-Peak
#     # Lưu ý: DC phải lấy từ tín hiệu thô (trước lọc), nếu file chỉ có tín hiệu lọc, 
#     # ta giả định DC là hằng số hoặc trung bình tín hiệu (nhưng kết quả sẽ kém chính xác hơn)
    
#     ac_red = np.max(red_f) - np.min(red_f)
#     ac_ir = np.max(ir_f) - np.min(ir_f)
    
#     # Giả định DC (Nếu bạn có dữ liệu thô nên dùng dc = np.mean(raw_signal))
#     # Trong trường hợp chỉ có dữ liệu lọc, ta dùng giá trị đại diện hoặc trung bình (nếu chưa khử DC)
#     dc_red = 1.0 # Giá trị giả định nếu không có dữ liệu thô
#     dc_ir = 1.0
    
#     R = (ac_red / dc_red) / (ac_ir / dc_ir)
#     spo2 = 110 - 25 * R # Công thức thực nghiệm cơ bản

#     # 5. In kết quả
#     print("="*40)
#     print(f"{'THÔNG SỐ SỨC KHỎE':^40}")
#     print("="*40)
#     print(f"Heart Rate (BPM) : {hr:.2f}")
#     print(f"SpO2 (%)         : {spo2:.2f}")
#     print(f"SDNN (ms)        : {sdnn:.2f}")
#     print(f"RMSSD (ms)       : {rmssd:.2f}")
#     print("="*40)

#     # 6. Vẽ biểu đồ quan sát
#     plt.figure(figsize=(12, 6))
#     plt.plot(ir_f, color='blue', label='IR (Filtered)')
#     plt.plot(peaks, ir_f[peaks], "ro", label='Detected Peaks')
#     plt.title('Phát hiện đỉnh sóng mạch (Peak Detection)')
#     plt.xlabel('Samples')
#     plt.ylabel('Amplitude')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.show()

# if __name__ == "__main__":
#     calculate_bio_metrics(file_path)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import os

# --- CẤU HÌNH ---
file_path = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-01 14-57-58-942.csv"
fs = 80 # Hãy kiểm tra kỹ xem có đúng 100Hz không

def calculate_full_metrics(path):
    if not os.path.exists(path):
        print("Không tìm thấy file!")
        return

    # 1. Đọc dữ liệu
    # Cột 2: Red Filtered, Cột 3: IR Filtered
    df = pd.read_csv(path, header=None)
    red_f = df.iloc[:, 1].values
    ir_f = df.iloc[:, 2].values

    # 2. Tìm đỉnh trên kênh IR (nhạy hơn với mạch máu)
    peaks, _ = find_peaks(ir_f, distance=fs*0.4, prominence=np.std(ir_f)*0.2)
    
    # 3. Tính Heart Rate và HRV
    rr_raw = np.diff(peaks) * (1000 / fs)
    rr_clean = rr_raw[(rr_raw > 300) & (rr_raw < 1300)] # Lọc nhiễu kỹ thuật
    
    if len(rr_clean) > 0:
        hr = 60000 / np.mean(rr_clean)
        sdnn = np.std(rr_clean)
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr_clean))))
    else:
        hr, sdnn, rmssd = 0, 0, 0

    # 4. Tính SpO2 (Công thức AC/DC)
    # AC tính bằng giá trị RMS hoặc độ lệch chuẩn của tín hiệu đã lọc
    ac_red = np.std(red_f)
    ac_ir = np.std(ir_f)
    
    # LƯU Ý QUAN TRỌNG: 
    # Vì tín hiệu đã lọc Bandpass, DC đã bị triệt tiêu về ~0.
    # Trong thực tế, DC của MAX30102 thường nằm khoảng 100,000 - 200,000.
    # Nếu không có cột dữ liệu thô, ta giả định tỉ lệ DC_red/DC_ir ≈ 1 
    # hoặc bạn hãy thay giá trị DC thực tế vào đây nếu có.
    dc_red = 1.0 
    dc_ir = 1.0
    
    R = (ac_red / dc_red) / (ac_ir / dc_ir)
    
    # Công thức hiệu chuẩn phổ biến cho MAX30102
    spo2 = 110 - 45 * R 
    
    # Giới hạn SpO2 trong khoảng sinh lý (0-100%)
    spo2 = max(0, min(100, spo2))

    # 5. In kết quả
    print("-" * 40)
    print(f"{'CHỈ SỐ SỨC KHỎE':^40}")
    print("-" * 40)
    print(f"Nhịp tim (HR)   : {hr:.2f} BPM")
    print(f"Nồng độ Oxy     : {spo2:.2f} % (SpO2)")
    print(f"SDNN (HRV)      : {sdnn:.2f} ms")
    print(f"RMSSD (HRV)     : {rmssd:.2f} ms")
    print("-" * 40)

    # 6. Vẽ biểu đồ kiểm tra
    plt.figure(figsize=(12, 6))
    plt.plot(ir_f, color='blue', label='IR Filtered', alpha=0.8)
    plt.plot(peaks, ir_f[peaks], "x", color='red', label='Đỉnh mạch')
    plt.title(f'Phân tích PPG - HR: {hr:.1f} | SpO2: {spo2:.1f}%')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    calculate_full_metrics(file_path)
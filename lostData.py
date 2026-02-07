# import pandas as pd
# import matplotlib.pyplot as plt

# data_fame = pd.read_csv("D:\Esp-idf\Mysource\sph0645_test\data_text\data_test400Hz_3rd.csv")
# x = range(len(data_fame))
# plt.plot(x, data_fame, marker="x", linestyle='-')

# plt.xlabel('Chỉ số dòng')
# plt.ylabel('Biên độ')
# plt.title('Biểu đồ dữ liệu từ file CSV')

# plt.show()  
import pandas as pd
import matplotlib.pyplot as plt

file_path = r"D:\Code_ESP-IDF\PPG1\data\400.csv"
data_frame = pd.read_csv(file_path, header=None)

# Lấy cột 1 (index = 0)
y = data_frame.iloc[:, 0]
x = range(len(y))

plt.figure(figsize=(10, 4))
plt.plot(x, y, linestyle='-')
plt.xlabel('Chỉ số mẫu')
plt.ylabel('Biên độ')
plt.title('Tín hiệu cột 1 từ file CSV')
plt.grid(True)
plt.tight_layout()
plt.show()

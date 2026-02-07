# import pandas as pd
# import matplotlib.pyplot as plt
# import os

# FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-01-31 19-44-38-601.csv"

# # Đọc CSV
# data = pd.read_csv(FILE_INPUT, header=0)

# # Lấy 3 cột đầu tiên
# y1 = data.iloc[:, 0]
# y2 = data.iloc[:, 1]
# y3 = data.iloc[:, 2]

# # Trục X = sample index
# x = range(len(y1))

# # Vẽ
# plt.figure(figsize=(12, 6))
# plt.plot(x, y1, linewidth=1, label=data.columns[0])
# plt.plot(x, y2, linewidth=1, label=data.columns[1])
# plt.plot(x, y3, linewidth=1, label=data.columns[2])

# plt.xlabel("Sample Index")
# plt.ylabel("Value")
# plt.title(os.path.basename(FILE_INPUT))  # tên biểu đồ = tên file
# plt.grid(True)
# plt.legend()

# plt.tight_layout()
# plt.show()
import pandas as pd
import matplotlib.pyplot as plt
import os

FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-02-06 00-15-12-639.csv"
# ====== ĐẶT TÊN BIỂU ĐỒ ======
TITLE_1 = "Raw Red Signal"
TITLE_2 = "Raw IR Signal"
#TITLE_3 = "Filtered IR Signal"
# ============================

# Đọc CSV
data = pd.read_csv(FILE_INPUT, header=0)

# Lấy 3 cột
y1 = data.iloc[:, 0]
y2 = data.iloc[:, 1]
#y3 = data.iloc[:, 2]

# Trục X = sample index
x = range(len(y1))

# Tạo 3 biểu đồ con (3 hàng, 1 cột)
fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)


# Biểu đồ 1
axes[0].plot(x, y1, linewidth=1)
axes[0].set_title(TITLE_1)
axes[0].set_ylabel(data.columns[0])
axes[0].grid(True)

# Biểu đồ 2
axes[1].plot(x, y2, linewidth=1)
axes[1].set_title(TITLE_2)
axes[1].set_ylabel(data.columns[1])
axes[1].grid(True)

# Biểu đồ 3
# axes[2].plot(x, y3, linewidth=1)
# axes[2].set_title(TITLE_3)
# axes[2].set_xlabel("Sample Index")
# axes[2].set_ylabel(data.columns[2])
# axes[2].grid(True)

# axes[0].plot(x, y1, color='red')
# axes[1].plot(x, y2, color='blue')
# axes[2].plot(x, y3, color='green')


# Tên chung (tên file)
# fig.suptitle(os.path.basename(FILE_INPUT), fontsize=12)

plt.tight_layout()
plt.show()


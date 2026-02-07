import pandas as pd
import matplotlib.pyplot as plt
import os

# =======================
# Kalman Filter 1D
# =======================
class KalmanFilter1D:
    def __init__(self, Q=0.001, R=0.5):
        self.Q = Q      # Process noise
        self.R = R      # Measurement noise
        self.x = 0.0    # Estimated value
        self.P = 1.0    # Estimation error

    def update(self, z):
        # Prediction
        self.P = self.P + self.Q

        # Kalman gain
        K = self.P / (self.P + self.R)

        # Update
        self.x = self.x + K * (z - self.x)
        self.P = (1 - K) * self.P

        return self.x


# =======================
# Load CSV
# =======================
FILE_INPUT = r"D:\Code_ESP-IDF\PPG1\data\CoolTerm Capture (Untitled_0) 2026-01-31 21-19-52-824.csv"
data = pd.read_csv(FILE_INPUT)

# =======================
# Lấy IR raw (cột 1)
# =======================
ir_raw = data.iloc[:, 0]
x = range(len(ir_raw))

# =======================
# Kalman filtering
# =======================
kf = KalmanFilter1D(Q=0.01, R=5)
ir_kalman = [kf.update(z) for z in ir_raw]

# =======================
# Vẽ biểu đồ so sánh
# =======================
plt.figure(figsize=(12, 8))

# ---- Biểu đồ 1: IR raw ----
plt.subplot(2, 1, 1)
plt.plot(x, ir_raw, linewidth=1, color='gray')
plt.title("Biểu đồ 1: IR raw signal (cột 1)")
plt.xlabel("Sample Index")
plt.ylabel("IR Value")
plt.grid(True)

# ---- Biểu đồ 2: IR sau Kalman ----
plt.subplot(2, 1, 2)
plt.plot(x, ir_kalman, linewidth=1, color='red')
plt.title("Biểu đồ 2: IR signal after Kalman Filter")
plt.xlabel("Sample Index")
plt.ylabel("IR Value")
plt.grid(True)

plt.tight_layout()
plt.show()
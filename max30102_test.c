// #include <stdio.h>
// #include <inttypes.h>
// #include <freertos/FreeRTOS.h>
// #include <freertos/task.h>
// #include <string.h>
// #include "driver/i2c.h"
// #include "max30102.h"
// #include "esp_log.h" // Thêm thư viện log
// #include "filter.h"     // Thêm thư viện bộ lọc tín hiệu số (User đã đổi tên từ dsp_filter)
// #include "pulse_calc.h" // Thêm thư viện tính toán BPM/SpO2

// // --- CẤU HÌNH CHO ESP32-C3 ---
// #define I2C_SDA_GPIO    8   // Chân SDA chuẩn của C3
// #define I2C_SCL_GPIO    9   // Chân SCL chuẩn của C3
// #define I2C_PORT        I2C_NUM_0

// // --- CẤU HÌNH CẢM BIẾN ---

// #define powerLed        UINT8_C(0x1F) // 6.4mA - Đủ dùng trong nhà
// #define sampleAverage   4             // Trung bình cộng 4 mẫu
// #define ledMode         2             // 2 = Red + IR (SpO2 Mode)
// #define sampleRate      400           // 400Hz (An toàn hơn 500Hz với I2C 400kHz)
// #define pulseWidth      411           // 18 bit resolution
// #define adcRange        16384         // Dải đo rộng nhất

// /**** MAX30102 Variables ****/
// i2c_dev_t dev;  
// struct max30102_record record;
// TaskHandle_t readMAXTask_handle = NULL;

// static const char *TAG = "MAX30102_APP";

// // Khai báo các biến bộ lọc toàn cục
// // Chúng ta cần 2 bộ lọc DC (cho Red và IR) và 2 bộ lọc Mean (cho Red và IR)
// dc_filter_t dc_red, dc_ir;
// mean_filter_t mean_red, mean_ir;

// //  Khai báo đối tượng máy đo nhịp tim/SpO2
// pulse_oximeter_t oximeter;

// esp_err_t max30102_configure(void){
//     // 1. Xóa sạch cấu hình cũ
//     memset(&dev, 0, sizeof(i2c_dev_t));
//     memset(&record, 0, sizeof(struct max30102_record));

//     // 2. Khởi tạo Descriptor
//     ESP_ERROR_CHECK(max30102_initDesc(&dev, I2C_PORT, I2C_SDA_GPIO, I2C_SCL_GPIO));

//     // --- [QUAN TRỌNG] CƯỠNG ÉP CẤU HÌNH TỐC ĐỘ TẠI ĐÂY ---
//     // Dòng này sẽ đè lên bất cứ lỗi nào trong thư viện
//     dev.cfg.master.clk_speed = 100000; // Chạy 100kHz cho ổn định (ESP32-C3 rất nhạy cảm với 400kHz)
//     // -----------------------------------------------------

//     // 3. Kiểm tra kết nối
//     if(max30102_readPartID(&dev) == ESP_OK) {
//         ESP_LOGI(TAG, "Tim thay MAX30102!");
//     }
//     else {
//         ESP_LOGE(TAG, "Khong tim thay MAX30102 (Loi I2C hoac day noi)");
//         // Không return lỗi vội, cứ thử init xem sao
//     }

//     // 4. Gửi lệnh cấu hình chi tiết
//     ESP_ERROR_CHECK(max30102_init(powerLed, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange, &record, &dev));
    
//     // 5. Xóa FIFO
//     max30102_clearFIFO(&dev);
    
//     return ESP_OK;
// }

// void readMAX30102_task(void *pvParameter){
//     ESP_LOGI(TAG, "Task Reading Started...");
    
//     // Khởi tạo giá trị ban đầu cho các bộ lọc trước khi vào vòng lặp
//     // Bước này quan trọng để xóa các giá trị rác trong RAM
//     dc_filter_init(&dc_red);
//     dc_filter_init(&dc_ir);
//     mean_filter_init(&mean_red);
//     mean_filter_init(&mean_ir);
    
//     //  Khởi tạo thuật toán tính toán BPM/SpO2
//     pulse_calc_init(&oximeter);

//     uint32_t raw_red, raw_ir;        // Biến lưu dữ liệu thô (Raw)
//     float ac_red, ac_ir;             // Biến lưu tín hiệu sau khi khử DC (AC)
//     float filtered_red, filtered_ir; // Biến lưu tín hiệu cuối cùng (đã làm mịn)

//     while(1){
//         // Kiểm tra và đọc dữ liệu từ cảm biến nạp vào struct record
//         max30102_check(&record, &dev); 

//         // Lấy dữ liệu từ struct record ra xử lý
//         while (max30102_available(&record)){
//             // 1. Lấy dữ liệu thô từ bộ đệm FIFO
//             raw_red = max30102_getFIFORed(&record);
//             raw_ir = max30102_getFIFOIR(&record);
            
//             // 2.  Giai đoạn 1: Khử DC (DC Removal)
//             // Loại bỏ thành phần một chiều (da, thịt, xương), giữ lại dao động nhịp tim
//             // Input: uint32_t -> Output: float (dao động quanh 0)
//             ac_red = -dc_removal((float)raw_red, &dc_red); // Đã có dấu trừ để đảo chiều
//             ac_ir = -dc_removal((float)raw_ir, &dc_ir);    // Đã có dấu trừ để đảo chiều

//             // 3. Giai đoạn 2: Làm mịn (Mean Filter)
//             // Loại bỏ các gai nhiễu tần số cao để đường sóng trơn tru
//             filtered_red = mean_filter(ac_red, &mean_red);
//             filtered_ir = mean_filter(ac_ir, &mean_ir);
            
//             // ---  TÍNH TOÁN BPM VÀ SPO2 ---
//             // Gọi hàm update từ thư viện pulse_calc.
//             // Hàm này trả về 'true' nếu vừa phát hiện một nhịp tim (BEAT)
//             bool beatDetected = pulse_calc_update(&oximeter, filtered_ir, filtered_red, raw_ir, raw_red);

//             if (beatDetected) {
//                 // Nếu bắt được nhịp tim, in kết quả ra Log Monitor
//                 ESP_LOGI(TAG, "NHIP TIM! BPM: %lu | SpO2: %d %%", oximeter.avg_bpm, oximeter.spo2);
//             }
//             // ----------------------------------------
            
//             // Format in ra Serial Plotter (Python/Arduino) để kiểm tra thuật toán
//             // Cấu trúc: Filtered_IR, Dynamic_Threshold, Beat_Marker
//             // - Filtered_IR: Tín hiệu nhịp tim
//             // - Dynamic_Threshold: Ngưỡng động (để xem thuật toán bám theo tín hiệu thế nào)
//             // - Beat_Marker: Tạo một xung vuông (0 hoặc 500) để đánh dấu vị trí bắt được nhịp
//             printf("%.2f,%.2f,%d\n", filtered_ir, oximeter.threshold, beatDetected ? 500 : 0);
            
//             // Chuyển sang mẫu tiếp theo trong bộ đệm
//             max30102_nextSample(&record);
//         }

//         // Delay 10ms để nhường CPU cho các tác vụ khác (Wifi, Bluetooth...)
//         // Với SampleRate 400Hz, 10ms sẽ tích được khoảng 4 mẫu.
//         // YÊU CẦU: Sửa STORAGE_SIZE trong max30102.h lên ít nhất 16
//         vTaskDelay(pdMS_TO_TICKS(10)); 
//     }
// }

// void app_main(void){
//     // 1. Khởi tạo thư viện I2C Helper
//     ESP_ERROR_CHECK(i2cdev_init()); 
    
//     // 2. Cấu hình MAX30102
//     if(max30102_configure() != ESP_OK){
//         ESP_LOGE(TAG, "Setup Failed. System halted.");
//         while(1) vTaskDelay(100); // Dừng chương trình nếu lỗi
//     }
    
//     ESP_LOGI(TAG, "Setup Complete. Starting Task...");
    
//     // 3. Tạo Task
//     // ESP32-C3 chỉ có 1 lõi (Core 0), nên dùng xTaskCreate hoặc xTaskCreatePinnedToCore với CoreID = 0 đều được.
//     xTaskCreatePinnedToCore(readMAX30102_task, "max30102_task", 4096, NULL, 5, &readMAXTask_handle, 0);
// }
// 
// #include <stdio.h>
// #include <inttypes.h>
// #include <freertos/FreeRTOS.h>
// #include <freertos/task.h>
// #include <string.h>
// #include "driver/i2c.h"
// #include "max30102.h"
// #include "esp_log.h"
// #include "i2cdev.h" // Đảm bảo include thư viện này

// static const char *TAG = "MAX30102_TEST";

// // --- CẤU HÌNH CHO ESP32-C3 ---
// #define I2C_SDA_GPIO    8   
// #define I2C_SCL_GPIO    9   
// #define I2C_PORT        I2C_NUM_0

// // Lưu ý: Không define lại I2C_FREQ_HZ ở đây để tránh warning
// // Thư viện max30102.h của bạn đã define nó là 100000 rồi.

// /**** MAX30102 Variables ****/
// i2c_dev_t dev;  
// struct max30102_record record; // Struct lưu dữ liệu của thư viện bạn

// void max30102_task(void *pvParameter){
//     // 1. Khởi tạo cấu trúc I2C
//     memset(&dev, 0, sizeof(i2c_dev_t));
//     memset(&record, 0, sizeof(struct max30102_record));

//     // SỬA LỖI 1: Tên hàm đúng là max30102_initDesc (chữ D viết hoa)
//     ESP_ERROR_CHECK(max30102_initDesc(&dev, I2C_PORT, I2C_SDA_GPIO, I2C_SCL_GPIO));

//     ESP_LOGI(TAG, "Khoi tao MAX30102...");

//     // SỬA LỖI 2 & 3: Hàm max30102_init của bạn đòi hỏi truyền tham số trực tiếp
//     // (Power, Average, Mode, Rate, PulseWidth, Range, Record, Dev)
//     // Các tham số này khớp với log lỗi bạn gửi
//     if (max30102_init(0x1F, 4, 2, 400, 411, 16384, &record, &dev) != ESP_OK) {
//         ESP_LOGE(TAG, "Khong tim thay MAX30102!");
//         // Vẫn cho chạy tiếp để debug dây nối
//     } else {
//         ESP_LOGI(TAG, "Da tim thay va cau hinh MAX30102");
//     }

//     uint32_t red, ir;

//     while(1){
//         // 2. Kiểm tra dữ liệu mới (Hàm check này sẽ đọc I2C và nạp vào struct record)
//         max30102_check(&record, &dev); 

//         // 3. Lặp qua bộ đệm để lấy dữ liệu
//         // (Thư viện này có bộ đệm FIFO, cần hàm available để check)
//         while (max30102_available(&record)){
            
//             // SỬA LỖI 7: Dùng hàm getFIFORed/IR thay vì truy cập trực tiếp
//             red = max30102_getFIFORed(&record);
//             ir = max30102_getFIFOIR(&record);
            
//             // In ra Serial Plotter
//             printf("%lu,%lu\n", red, ir);
            
//             // Chuyển sang mẫu tiếp theo trong hàng đợi
//             max30102_nextSample(&record);
//         }

//         // Delay ngắn để không chiếm dụng CPU nhưng vẫn đủ nhanh để check
//         vTaskDelay(pdMS_TO_TICKS(10)); 
//     }
// }

// void app_main(void){
//     // Khởi tạo I2C Helper
//     ESP_ERROR_CHECK(i2cdev_init()); 
    
//     // Tạo Task
//     xTaskCreatePinnedToCore(max30102_task, "max30102_task", 4096, NULL, 5, NULL, 0);
// }
// #include <stdio.h>
// #include <string.h>
// #include <freertos/FreeRTOS.h>
// #include <freertos/task.h>
// #include "driver/i2c.h"
// #include "esp_log.h"
// #include "max30102.h"

// // --- CẤU HÌNH CHO ESP32-C3 ---
// #define I2C_SDA_GPIO    8   // Chân SDA của C3
// #define I2C_SCL_GPIO    9   // Chân SCL của C3
// #define I2C_PORT        I2C_NUM_0

// // --- CẤU HÌNH CẢM BIẾN (Dành cho việc đo Raw) ---
// #define powerLed        UINT8_C(0x24) // Dòng khoảng 7.6mA cho LED
// #define sampleAverage   1             // Không lấy trung bình để thấy dữ liệu thô nhất
// #define ledMode         2             // 2 = Red + IR
// #define sampleRate      100           // 100Hz là đủ để quan sát dạng sóng thô
// #define pulseWidth      411           // 18 bit
// #define adcRange        16384 

// static const char *TAG = "MAX30102_RAW";
// i2c_dev_t dev;  
// struct max30102_record record;

// void read_raw_task(void *pvParameter) {
//     uint32_t raw_red, raw_ir;
    
//     ESP_LOGI(TAG, "Bắt đầu đọc dữ liệu RAW...");
    
//     while(1) {
//         // Kiểm tra xem có dữ liệu mới từ FIFO không
//         max30102_check(&record, &dev); 

//         while (max30102_available(&record)) {
//             // Lấy dữ liệu thô trực tiếp
//             raw_red = max30102_getFIFORed(&record);
//             raw_ir = max30102_getFIFOIR(&record);

//             // In ra định dạng Serial Plotter để vẽ biểu đồ
//             // Cấu trúc: Red, IR
//             printf("%lu,%lu\n", raw_red, raw_ir);
            
//             max30102_nextSample(&record);
//         }
        
//         // Delay ngắn để tránh chiếm dụng CPU
//         vTaskDelay(pdMS_TO_TICKS(10)); 
//     }
// }

// esp_err_t init_max30102_raw(void) {
//     memset(&dev, 0, sizeof(i2c_dev_t));
//     memset(&record, 0, sizeof(struct max30102_record));

//     // Khởi tạo I2C Descriptor
//     ESP_ERROR_CHECK(max30102_initDesc(&dev, I2C_PORT, I2C_SDA_GPIO, I2C_SCL_GPIO));

//     // ESP32-C3 hoạt động ổn định hơn ở 100kHz I2C
//     dev.cfg.master.clk_speed = 100000; 

//     // Kiểm tra Part ID để chắc chắn I2C đã thông
//     if(max30102_readPartID(&dev) != ESP_OK) {
//         ESP_LOGE(TAG, "LỖI: Không tìm thấy MAX30102. Kiểm tra dây và nguồn 3.3V!");
//         return ESP_FAIL;
//     }

//     // Cấu hình cảm biến
//     ESP_ERROR_CHECK(max30102_init(powerLed, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange, &record, &dev));
    
//     max30102_clearFIFO(&dev);
//     return ESP_OK;
// }

// void app_main(void) {
//     // 1. Khởi tạo driver I2C
//     ESP_ERROR_CHECK(i2cdev_init()); 
    
//     // 2. Khởi tạo MAX30102
//     if(init_max30102_raw() == ESP_OK) {
//         ESP_LOGI(TAG, "Khởi tạo thành công!");
//         // 3. Tạo task đọc dữ liệu trên Core 0
//         xTaskCreatePinnedToCore(read_raw_task, "raw_task", 4096, NULL, 5, NULL, 0);
//     } else {
//         ESP_LOGE(TAG, "Khởi tạo thất bại.");
//     }
// }
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "driver/i2c.h"
#include "driver/gpio.h"
#include "driver/i2s_std.h" // Dành cho ESP-IDF v5.x
#include "esp_log.h"
#include "esp_timer.h"

// --- THƯ VIỆN CỦA BẠN ---
#include "i2cdev.h"
#include "max30102.h"

static const char *TAG = "HEALTH_MONITOR";

// ================= 1. CẤU HÌNH PHẦN CỨNG (Theo README) =================
// I2C (OLED + MAX30102)
#define I2C_SDA_PIN     8
#define I2C_SCL_PIN     9
#define I2C_PORT        I2C_NUM_0
#define I2C_FREQ_HZ     100000 // 100kHz (An toàn)

// MAX30102 Interrupt
#define MAX_INT_PIN     3

// I2S Microphone (INMP441)
#define I2S_SCK_PIN     6
#define I2S_WS_PIN      5
#define I2S_SD_PIN      4
#define I2S_SAMPLE_RATE 16000

// ================= 2. CẤU TRÚC DỮ LIỆU & RTOS =================
typedef struct {
    float heart_rate;   // BPM
    float spo2;         // %
    float respiration;  // RPM (Reps Per Minute)
} system_data_t;

// Đối tượng FreeRTOS
SemaphoreHandle_t xI2CMutex;      // Bảo vệ I2C Bus (OLED vs MAX30102)
SemaphoreHandle_t xMaxReadySem;   // Cờ báo ngắt từ MAX30102
QueueHandle_t     xDataQueue;     // Hàng đợi gửi dữ liệu sang màn hình

// ================= 3. BỘ LỌC DSP (Đơn giản hóa) =================
// Bộ lọc DC Removal (Khử trôi đường nền)
typedef struct {
    float w;
    float alpha;
} dc_filter_t;

void dc_filter_init(dc_filter_t *f, float alpha) {
    f->w = 0;
    f->alpha = alpha;
}

float dc_filter_process(dc_filter_t *f, float input) {
    float output = input - f->w;
    f->w = input + f->alpha * output; // IIR Filter
    return output;
}

// Bộ lọc Mean (Làm mượt)
#define MEAN_FILTER_SIZE 4
typedef struct {
    float buffer[MEAN_FILTER_SIZE];
    uint8_t index;
    float sum;
} mean_filter_t;

void mean_filter_init(mean_filter_t *f) {
    memset(f, 0, sizeof(mean_filter_t));
}

float mean_filter_process(mean_filter_t *f, float input) {
    f->sum -= f->buffer[f->index];
    f->buffer[f->index] = input;
    f->sum += input;
    f->index++;
    if(f->index >= MEAN_FILTER_SIZE) f->index = 0;
    return f->sum / MEAN_FILTER_SIZE;
}

// ================= 4. HÀM NGẮT (ISR) =================
// Khi MAX30102 đo xong, chân INT kéo xuống thấp -> Hàm này chạy
void IRAM_ATTR max30102_isr_handler(void* arg) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    // Đánh thức Task Tim
    xSemaphoreGiveFromISR(xMaxReadySem, &xHigherPriorityTaskWoken);
    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
}

// ================= 5. TASK: ĐO NHỊP TIM (EVENT-DRIVEN) =================
void heart_rate_task(void *pvParam) {
    i2c_dev_t dev;
    struct max30102_record record;
    memset(&dev, 0, sizeof(i2c_dev_t));
    memset(&record, 0, sizeof(struct max30102_record));

    // Khởi tạo DSP Filters
    dc_filter_t dc_red, dc_ir;
    mean_filter_t mean_red;
    dc_filter_init(&dc_red, 0.95);
    mean_filter_init(&mean_red);

    // Cấu hình I2C & Cảm biến (Dùng Mutex vì I2C là tài nguyên chung)
    xSemaphoreTake(xI2CMutex, portMAX_DELAY);
    ESP_ERROR_CHECK(max30102_initDesc(&dev, I2C_PORT, I2C_SDA_PIN, I2C_SCL_PIN));
    
    // Cấu hình: Power=0x1F, Avg=4, Mode=2(HR+SPO2), Rate=400Hz, Pulse=411, Range=16k
    if (max30102_init(0x1F, 4, 2, 400, 411, 16384, &record, &dev) != ESP_OK) {
        ESP_LOGE(TAG, "MAX30102 Init Failed!");
    }
    
    // Bật ngắt trên cảm biến (Quan trọng: Enable Interrupt A_FULL/PPG_RDY)
    // Lưu ý: Thư viện của bạn mặc định có thể chưa bật ngắt, 
    // cần đảm bảo thanh ghi Enable Interrupt được set đúng.
    // Ở đây giả định thư viện đã cấu hình hoặc mặc định polling.
    
    xSemaphoreGive(xI2CMutex);

    system_data_t sys_data = {0};
    uint32_t raw_red;
    float ac_red, filtered_red;

    while(1) {
        // [EVENT-DRIVEN] Ngủ chờ ngắt, không tốn CPU
        if (xSemaphoreTake(xMaxReadySem, portMAX_DELAY)) {
            
            xSemaphoreTake(xI2CMutex, portMAX_DELAY);
            max30102_check(&record, &dev); // Đọc I2C
            
            while (max30102_available(&record)) {
                raw_red = max30102_getFIFORed(&record);
                max30102_nextSample(&record); // Next

                // --- PIPELINE XỬ LÝ TÍN HIỆU ---
                // 1. DC Removal
                ac_red = dc_filter_process(&dc_red, (float)raw_red);
                
                // 2. Invert Signal (Đảo dấu để đỉnh sóng đúng nhịp tim)
                ac_red = -ac_red;

                // 3. Mean Filter
                filtered_red = mean_filter_process(&mean_red, ac_red);

                // 4. Peak Detection (Giả lập tính toán BPM đơn giản)
                // Trong thực tế, bạn sẽ dùng thuật toán đếm đỉnh ở đây
                // Code demo: Gửi tín hiệu đã lọc ra Serial Plotter
                printf("RAW:%lu,FILTERED:%.2f\n", raw_red, filtered_red);
            }
            xSemaphoreGive(xI2CMutex);

            // Cập nhật BPM giả định (Placeholder cho thuật toán đếm đỉnh)
            sys_data.heart_rate = 75.0; 
            
            // Gửi sang Task Display (Overwrite để luôn lấy mới nhất)
            xQueueOverwrite(xDataQueue, &sys_data);
        }
    }
}

// ================= 6. TASK: ĐO NHỊP THỞ (I2S DMA) =================
void respiration_task(void *pvParam) {
    // Cấu hình I2S Standard Mode (ESP-IDF v5.x)
    i2s_chan_handle_t rx_handle;
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    i2s_new_channel(&chan_cfg, NULL, &rx_handle);
    
    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(I2S_SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_SCK_PIN,
            .ws = I2S_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din = I2S_SD_PIN,
        },
    };
    i2s_channel_init_std_mode(rx_handle, &std_cfg);
    i2s_channel_enable(rx_handle);

    int32_t i2s_buffer[256];
    size_t bytes_read;
    float envelope = 0;
    system_data_t sys_data;

    while(1) {
        if (i2s_channel_read(rx_handle, i2s_buffer, sizeof(i2s_buffer), &bytes_read, 100) == ESP_OK) {
            // Xử lý Audio -> Nhịp thở
            float sum_energy = 0;
            for (int i = 0; i < bytes_read / 4; i++) {
                // 1. Rectification (Chỉnh lưu)
                float sample = abs((i2s_buffer[i] >> 14)); 
                // 2. Envelope Detection (Đường bao)
                envelope = 0.01 * sample + 0.99 * envelope; 
                sum_energy += envelope;
            }
            
            // Logic Schmitt Trigger đếm nhịp thở (Rút gọn)
            // ... (Code đếm nhịp thở ở đây) ...
            
            // Cập nhật Queue (Peek để lấy BPM cũ, ghi đè RPM mới)
            if(xQueuePeek(xDataQueue, &sys_data, 0)) {
                sys_data.respiration = 18.5; // Giả định
                xQueueOverwrite(xDataQueue, &sys_data);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(50)); // Lấy mẫu ngắt quãng
    }
}

// ================= 7. TASK: HIỂN THỊ (OLED) =================
void display_task(void *pvParam) {
    // Khởi tạo OLED (Giả lập - bạn thay bằng SSD1306 driver của bạn)
    // xSemaphoreTake(xI2CMutex, portMAX_DELAY);
    // ssd1306_init();
    // xSemaphoreGive(xI2CMutex);

    system_data_t recv_data;
    char buffer[32];

    while(1) {
        if (xQueueReceive(xDataQueue, &recv_data, portMAX_DELAY)) {
            // Chiếm quyền I2C để vẽ lên màn hình
            if (xSemaphoreTake(xI2CMutex, portMAX_DELAY)) {
                
                // SSD1306_Fill(0);
                // sprintf(buffer, "BPM: %.1f", recv_data.heart_rate);
                // SSD1306_GotoXY(0,0); SSD1306_Puts(buffer);
                
                // sprintf(buffer, "RPM: %.1f", recv_data.respiration);
                // SSD1306_GotoXY(0,20); SSD1306_Puts(buffer);
                
                // SSD1306_UpdateScreen();
                
                xSemaphoreGive(xI2CMutex);
            }
            
            // Log ra console để debug (Thay thế OLED nếu chưa lắp)
            // ESP_LOGI("DISPLAY", "BPM: %.1f | RPM: %.1f", recv_data.heart_rate, recv_data.respiration);
        }
        // Refresh rate màn hình ~10Hz
        vTaskDelay(pdMS_TO_TICKS(100)); 
    }
}

// ================= 8. MAIN APPLICATION =================
void app_main(void) {
    // 1. Khởi tạo Thư viện Helper
    ESP_ERROR_CHECK(i2cdev_init());
    
    // 2. Tạo các RTOS Objects
    xI2CMutex = xSemaphoreCreateMutex();
    xDataQueue = xQueueCreate(1, sizeof(system_data_t)); // Queue độ dài 1 (chỉ cần data mới nhất)
    xMaxReadySem = xSemaphoreCreateBinary(); // Semaphore Ngắt

    // 3. Cấu hình Ngắt GPIO cho MAX30102
    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_NEGEDGE, // Ngắt cạnh xuống
        .pin_bit_mask = (1ULL << MAX_INT_PIN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = 1
    };
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(MAX_INT_PIN, max30102_isr_handler, NULL);

    // 4. Tạo Tasks (Phân phối ưu tiên)
    // Task Tim quan trọng nhất -> Priority cao
    xTaskCreatePinnedToCore(heart_rate_task, "HeartTask", 4096, NULL, 5, NULL, 0);
    // Task Phổi (I2S DMA tự chạy nền nên task nhẹ hơn)
    xTaskCreatePinnedToCore(respiration_task, "BreathTask", 4096, NULL, 4, NULL, 0);
    // Task Hiển thị thấp nhất
    xTaskCreatePinnedToCore(display_task, "DispTask", 3072, NULL, 3, NULL, 0);

    ESP_LOGI(TAG, "System Started. Waiting for interrupts...");
}
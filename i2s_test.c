
// #include <stdio.h>
// #include "freertos/FreeRTOS.h"
// #include "freertos/task.h"
// #include "driver/i2s_std.h"
// #include "driver/uart.h"

// // --- CẤU HÌNH GPIO (ESP32-C3) ---
// #define I2S_SCK_PIN 6
// #define I2S_WS_PIN  5
// #define I2S_SD_PIN  4

// // --- CẤU HÌNH ÂM THANH ---
// #define SAMPLE_RATE 16000 
// #define BLOCK_SIZE  512   

// void i2s_mic_init(i2s_chan_handle_t *rx_handle) {
//     i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
//     ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, rx_handle));

//     i2s_std_config_t std_cfg = {
//         .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
//         .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_STEREO),
//         .gpio_cfg = {
//             .mclk = I2S_GPIO_UNUSED,
//             .bclk = I2S_SCK_PIN,
//             .ws = I2S_WS_PIN,
//             .dout = I2S_GPIO_UNUSED,
//             .din = I2S_SD_PIN,
//         },
//     };
//     std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_BOTH; 

//     ESP_ERROR_CHECK(i2s_channel_init_std_mode(*rx_handle, &std_cfg));
//     ESP_ERROR_CHECK(i2s_channel_enable(*rx_handle));
// }

// void audio_wave_task(void *arg) {
//     i2s_chan_handle_t rx_handle;
//     i2s_mic_init(&rx_handle);

//     int32_t raw_buffer[BLOCK_SIZE]; 
//     size_t bytes_read = 0;

//     while (1) {
//         // 1. Đọc dữ liệu từ Micro
//         if (i2s_channel_read(rx_handle, raw_buffer, sizeof(raw_buffer), &bytes_read, 1000) == ESP_OK) {
            
//             int samples_read = bytes_read / 4;

//             // 2. Trích xuất và in dữ liệu dao động
//             for (int i = 0; i < samples_read; i += 2) {
                
//                 // Lấy dữ liệu kênh Left (32-bit)
//                 int32_t raw_val = raw_buffer[i]; 
                
//                 /* GIẢI THÍCH DỊCH BIT:
//                    Dữ liệu INMP441 là 24-bit có dấu. Khi nhận ở chế độ 32-bit, 
//                    nó nằm ở các bit cao (MSB). Ta dịch phải 14 bit để đưa về 
//                    phạm vi 16-bit (từ -32768 đến 32767) giúp đồ thị dễ nhìn hơn.
//                 */
//                 int16_t wave_sample = (int16_t)(raw_val >> 14);

//                 // 3. In ra Serial (Cột 1: Giá trị sóng, Cột 2: Mốc 0 cố định)
//                 // Downsampling: Chỉ in mỗi mẫu thứ 8 để tránh nghẽn UART ở Baudrate thấp
//                 if (i % 8 == 0) {
//                     printf("%d,0\n", wave_sample);
//                 }
//             }
            
//             // Task delay nhỏ để CPU xử lý việc khác (Tránh lỗi WDT)
//             vTaskDelay(pdMS_TO_TICKS(1)); 
//         }
//     }
// }

// void app_main() {
//     // Tăng tốc độ UART để vẽ đồ thị mượt hơn
//     uart_set_baudrate(UART_NUM_0, 115200);
    
//     xTaskCreate(audio_wave_task, "audio_wave_task", 4096, NULL, 5, NULL);
// }
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_std.h"
#include "driver/uart.h"

#define I2S_SCK_PIN 6
#define I2S_WS_PIN  5
#define I2S_SD_PIN  4

#define SAMPLE_RATE 16000 
#define BLOCK_SIZE  1024  // Tăng buffer để đọc mượt hơn

void i2s_mic_init(i2s_chan_handle_t *rx_handle) {
    i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, rx_handle));

    i2s_std_config_t std_cfg = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        // Sử dụng MONO và chuẩn Philips để khớp với INMP441
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = I2S_SCK_PIN,
            .ws = I2S_WS_PIN,
            .dout = I2S_GPIO_UNUSED,
            .din = I2S_SD_PIN,
        },
    };
    std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT; 

    ESP_ERROR_CHECK(i2s_channel_init_std_mode(*rx_handle, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(*rx_handle));
}

void audio_high_speed_task(void *arg) {
    i2s_chan_handle_t rx_handle;
    i2s_mic_init(&rx_handle);

    int32_t raw_buffer[BLOCK_SIZE]; 
    size_t bytes_read = 0;
    uint32_t seq_num = 0;

    while (1) {
        if (i2s_channel_read(rx_handle, raw_buffer, sizeof(raw_buffer), &bytes_read, 1000) == ESP_OK) {
            int samples_read = bytes_read / 4;
            for (int i = 0; i < samples_read; i++) {
                // In định dạng ngắn nhất: seq,val
                // Ví dụ: 1,2500
                printf("%lu,%d\n", (unsigned long)seq_num++, (int)(raw_buffer[i] >> 14));
            }
        }
        // Không sử dụng vTaskDelay ở đây nếu không cần thiết để tránh nghẽn I2S buffer
    }
}

void app_main() {
    // THIẾT LẬP QUAN TRỌNG: Baudrate 2 triệu
    uart_set_baudrate(UART_NUM_0, 2000000);
    
    // Ưu tiên Task cao (10) để ưu tiên xử lý dữ liệu âm thanh
    xTaskCreate(audio_high_speed_task, "audio_task", 4096, NULL, 10, NULL);
}
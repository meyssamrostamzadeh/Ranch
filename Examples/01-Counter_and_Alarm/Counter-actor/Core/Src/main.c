/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "string.h"
#include "stdio.h"
#include "stm32f1xx_hal.h"

#define BUFFER_SIZE 128  // Circular buffer size
#define FIFO_SIZE 8

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;
// Message identifiers
#define MSG_INC 1

// a struct to store message number and sender ID
typedef struct {
    uint8_t sender_id;   // 1 for USART1, 2 for USART2
    uint8_t message_number;
} fifo_item_t;

fifo_item_t fifo_queue[FIFO_SIZE];

uint8_t fifo_head = 0, fifo_tail = 0;


uint8_t usart1_rx_buffer[BUFFER_SIZE];
uint8_t usart2_rx_buffer[BUFFER_SIZE];
uint8_t usart1_tx_buffer[BUFFER_SIZE];
uint8_t usart2_tx_buffer[BUFFER_SIZE];

volatile uint16_t usart1_rx_head = 0;
volatile uint16_t usart1_rx_tail = 0;
volatile uint16_t usart2_rx_head = 0;
volatile uint16_t usart2_rx_tail = 0;

volatile uint8_t usart1_new_message_flag = 0;
volatile uint8_t usart2_new_message_flag = 0;

// Flag variables
volatile uint8_t a_notify_flag = 0;

volatile uint8_t msgsrv_inc_flag = 0;

char usart1_buffer[20];
char usart2_buffer[20];

uint8_t accum;
uint8_t sender;


void send_usart_message(UART_HandleTypeDef* huart, const char* message);
uint8_t check_for_new_message(uint8_t* buffer, volatile uint16_t* head, volatile uint16_t* tail, volatile uint8_t* new_message_flag);
uint8_t circular_buffer_read(uint8_t* buffer, volatile uint16_t* tail);
fifo_item_t fifo_dequeue();
void fifo_enqueue(uint8_t sender_id, uint8_t message_number);

int is_fifo_empty();

void check_send_flags() {
    if (a_notify_flag) {
        send_usart_message(&huart1, "notify");
        a_notify_flag = 0;
    }
}

void check_USART_1_routine() {
    if (check_for_new_message(usart1_rx_buffer, &usart1_rx_head, &usart1_rx_tail, &usart1_new_message_flag)) {
        char message[BUFFER_SIZE];
        for (int i = 0; i < BUFFER_SIZE; i++) {
            message[i] = circular_buffer_read(usart1_rx_buffer, &usart1_rx_tail);
            if (message[i] == '\n') break;
        }
        if (strcmp((const char *)message, "inc") == 0) {
            fifo_enqueue(1,MSG_INC);
        }
    }
}

void check_USART_2_routine() {
    if (check_for_new_message(usart2_rx_buffer, &usart2_rx_head, &usart2_rx_tail, &usart2_new_message_flag)) {
        char message[BUFFER_SIZE];
        for (int i = 0; i < BUFFER_SIZE; i++) {
            message[i] = circular_buffer_read(usart2_rx_buffer, &usart2_rx_tail);
            if (message[i] == '\n') break;
        }
    }
}

void check_FIFO_queue() {
    if (msgsrv_inc_flag) return;

    if (!is_fifo_empty()) {
        fifo_item_t item = fifo_dequeue();
        sender = item.sender_id;
        if (item.message_number == MSG_INC) {
            msgsrv_inc_flag = 1;
        }
    }
}

void fifo_enqueue(uint8_t sender_id, uint8_t message_number) {
    fifo_queue[fifo_head].sender_id = sender_id;
    fifo_queue[fifo_head].message_number = message_number;
    fifo_head = (fifo_head + 1) % FIFO_SIZE;
}

fifo_item_t fifo_dequeue() {
    fifo_item_t item = fifo_queue[fifo_tail];
    fifo_tail = (fifo_tail + 1) % FIFO_SIZE;
    return item;
}

int is_fifo_empty() {
    return fifo_head == fifo_tail;
}


const char* add_crlf(const char* str) {
    static char buffer[BUFFER_SIZE];
    snprintf(buffer, BUFFER_SIZE, "%s\r\n", str);
    return buffer;
}

void send_usart_message(UART_HandleTypeDef* huart, const char* message) {
    const char* msg_with_crlf = add_crlf(message);
    HAL_UART_Transmit_IT(huart, (uint8_t*)msg_with_crlf, strlen(msg_with_crlf));
}

// Circular buffer write for receiving data
void circular_buffer_write(uint8_t* buffer, volatile uint16_t* head, uint8_t data) {
    buffer[*head] = data;
    *head = (*head + 1) % BUFFER_SIZE;
}

uint8_t circular_buffer_read(uint8_t* buffer, volatile uint16_t* tail) {
    uint8_t data = buffer[*tail];
    *tail = (*tail + 1) % BUFFER_SIZE;
    return data;
}

// Function to check if a complete message has been received (CRLF)
uint8_t check_for_new_message(uint8_t* buffer, volatile uint16_t* head, volatile uint16_t* tail, volatile uint8_t* new_message_flag) {
    if (*new_message_flag) {
        *new_message_flag = 0;
        return 1;
    }
    return 0;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef* huart) {
    uint8_t received_byte;

    if (huart->Instance == USART1) {
        received_byte = huart->pRxBuffPtr[0];  // Received byte from USART1
        circular_buffer_write(usart1_rx_buffer, &usart1_rx_head, received_byte);

        // Check if last two bytes are CR (13) and LF (10)
        uint16_t prev_index = (usart1_rx_head + BUFFER_SIZE - 2) % BUFFER_SIZE;
        if (usart1_rx_buffer[prev_index] == 13 && usart1_rx_buffer[usart1_rx_head - 1] == 10) {
            usart1_new_message_flag = 1;  // Set new message flag
        }
        // Ready to receive the next byte
        HAL_UART_Receive_IT(&huart1, &received_byte, 1);
    }
    else if (huart->Instance == USART2) {
        received_byte = huart->pRxBuffPtr[0];
        circular_buffer_write(usart2_rx_buffer, &usart2_rx_head, received_byte);

        uint16_t prev_index = (usart2_rx_head + BUFFER_SIZE - 2) % BUFFER_SIZE;
        if (usart2_rx_buffer[prev_index] == 13 && usart2_rx_buffer[usart2_rx_head - 1] == 10) {
            usart2_new_message_flag = 1;
        }
        HAL_UART_Receive_IT(&huart2, &received_byte, 1);
    }
}
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  uint8_t temp_byte;
  HAL_UART_Receive_IT(&huart1, &temp_byte, 1);
  HAL_UART_Receive_IT(&huart2, &temp_byte, 1);
  while (1)
  {
      check_USART_1_routine();
      check_USART_2_routine();
      check_send_flags();
      check_FIFO_queue();
      asm("nop \n"
    		  ".global accum \n"
    		  ".global sender \n"
    		  ".global msgsrv_inc_flag \n"
    		  ".global a_notify_flag \n"
    		  "ldr r2, =msgsrv_inc_flag \n"
    		  "ldr r3, [r2] \n"
    		  "cmp r3, #1 \n"
    		  "beq msgsrv_inc \n"
    		  "b label_end \n"
    		  "msgsrv_inc: \n"
    		  "mov r0, #0 \n"
    		  "ldr r1, =msgsrv_inc_flag \n"
    		  "str r0, [r1] \n"
    		  "ldr r2, =accum \n"
    		  "ldr r3, [r2] \n"
    		  "mov r4, #1 \n"
    		  "cmp r3, r4 \n"
    		  "beq else_label1 \n"
    		  "mov r0, #0 \n"
    		  "ldr r1, =accum \n"
    		  "str r0, [r1] \n"
    		  "b end_label1 \n"
    		  "else_label1: \n"
    		  "mov r0, #1 \n"
    		  "ldr r1, =accum \n"
    		  "str r0, [r1] \n"
    		  "mov r0, #1 \n"
    		  "ldr r1, =a_notify_flag \n"
    		  "str r0, [r1] \n"
    		  "end_label1: \n"
    		  "mov r0, #1 \n"
    		  "ldr r1, =msgsrv_inc_flag \n"
    		  "str r0, [r1] \n"
    		  "bx lr \n"
    		  "label_end: \n");
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 9600;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_2;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 9600;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_2;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : LED_Pin */
  GPIO_InitStruct.Pin = LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : PB12 */
  GPIO_InitStruct.Pin = GPIO_PIN_12;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

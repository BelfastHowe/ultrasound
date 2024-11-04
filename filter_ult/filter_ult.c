#include "filter_ult.h"

static char dataIndex = 0;
static int sliding_window[ARRAY_SIZE];

int average_of_array(int *array)
{
    int sum = 0;
    for (int i = 0; i < ARRAY_SIZE; i++) 
    {
        sum += array[i];
    }
    int average = sum / ARRAY_SIZE;
    return average;
}

void countInRanges(int *arr, int *less_than_1200, int *between_1200_and_2000, int *greater_than_2000) 
{
    *less_than_1200 = 0;
    *between_1200_and_2000 = 0;
    *greater_than_2000 = 0;

    for (int i = 0; i < ARRAY_SIZE; i++) 
    {
        if (arr[i] < 1200) 
        {
            (*less_than_1200)++;
        } 
        else if (arr[i] >= 1200 && arr[i] < 2000) 
        {
            (*between_1200_and_2000)++;
        } 
        else 
        {
            (*greater_than_2000)++;
        }
    }
}

int calculateStdDev(int *arr) 
{
    double sum = 0.0;
    double mean = 0.0;
    double sum_of_squares = 0.0;
    double std_dev = 0.0;

    // 计算所有元素的和
    for (int i = 0; i < ARRAY_SIZE; i++) 
    {
        sum += arr[i];
    }

    // 计算平均值
    mean = sum / ARRAY_SIZE;

    // 计算平方差的和
    for (int i = 0; i < ARRAY_SIZE; i++) 
    {
        sum_of_squares += pow(arr[i] - mean, 2);
    }

    // 计算总体标准差
    std_dev = sqrt(sum_of_squares / ARRAY_SIZE);

    return (int)(std_dev + 0.5);
}

char filter_main(int* data_array)
{
    int classification[3];
    int average = 0;
    int std_dev = 0;
    char result = previous_status;

    // 计算分类计数
    countInRanges(data_array, &classification[0], &classification[1], &classification[2]);
        
    // 计算平均值
    average = average_of_array(data_array);
        
    // 计算标准差
    std_dev = calculateStdDev(data_array);

    if (average > threshold && classification[2] >= 2) 
    {
        result = 1;
        carpet_buffer = 0;
    } 
    else if (average < (threshold - 400) && classification[1] == 0 && classification[2] == 0 && std_dev <= 500) 
    {
        if (carpet_buffer == 1) 
        {
            result = 2;
        } 
        else 
        {
            result = previous_status;
            carpet_buffer = 1;
        }
    } 
    else 
    {
        result = previous_status;
        carpet_buffer = 0;
    }

    return result;
}

char filter_ult(short data)
{
    if(previous_status == 0)
    {
        if(data >= threshold)
        {
            previous_status = 1;
        }
        else
        {
            previous_status = 2;
        }
    }

    sliding_window[dataIndex++] = (int)data;

    if (dataIndex == ARRAY_SIZE) 
    {
        previous_status = filter_main(sliding_window);
        dataIndex = 0;
    }

    return previous_status;
}

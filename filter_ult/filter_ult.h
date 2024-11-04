#pragma once

#ifndef ULT_FILTER_QUEUE_H
#define ULT_FILTER_QUEUE_H

#ifdef __cplusplus
extern "C" {
#endif

    #define ARRAY_SIZE 15

    static int  threshold = 1200;
    static char previous_status = 0;
    static char carpet_buffer = 0;
    
    char filter_ult(short data);

#ifdef __cplusplus
}
#endif

#endif // ULT_FILTER_QUEUE_H

from .NJIT import NJIT
import time
from typing import Callable

def time_func(func: Callable, *args, n=1, **kwargs):
    if n <= 1:
        start = time.time()
        func(*args, **kwargs)
        return time.time() - start
    else:
        total = 0
        for _ in range(n):
            total += time_func(func, *args, n=1, **kwargs)
        return total / n

print(f'[Schedule: Get Sections]: {time_func(NJIT.get_sections, "202410", "CS"):.4f}s')
print(f'[Schedule: Get Subjects]: {time_func(NJIT.get_subjects, "202410"):.4f}s')
print()
print(f'[Course: Get Description]: {time_func(NJIT.get_course_desc, "BME 430"):.4f}s')
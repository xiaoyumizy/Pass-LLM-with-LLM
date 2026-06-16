"""
单调栈 / 单调队列 练习题
"""
import sys
from collections import deque


# ============================================================
# 每日温度（下一个更大元素）
# 模式：单调栈 | I/O：单组测试用例
# ============================================================

def solve_daily_temperatures():
    """
    输入格式：
        第一行 n
        第二行 n 个整数表示每天的温度
    输出格式：
        一行 n 个整数：需要等几天才能等到更高温度（等不到为 0）

    核心思路：
        单调递减栈，存下标
        遍历数组，若当前温度 > 栈顶温度，弹出并计算天数差
    """
    input = sys.stdin.readline

    n = int(input())
    temps = list(map(int, input().split()))

    # ============================================================
    # Algorithm：单调栈
    # ============================================================
    result = [0] * n
    stack = []  # 存下标，维护单调递减

    for i in range(n):
        while stack and temps[i] > temps[stack[-1]]:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)

    # ============================================================
    # Output
    # ============================================================
    print(" ".join(map(str, result)))


# ============================================================
# 柱状图中最大的矩形
# 模式：单调栈 | I/O：单组测试用例
# ============================================================

def solve_largest_rectangle():
    """
    输入格式：
        第一行 n
        第二行 n 个整数表示柱子高度
    输出格式：
        一行：最大矩形面积

    核心思路：
        单调递增栈，对每根柱子找左右第一个比它矮的柱子
        面积 = height * (right - left - 1)
    """
    input = sys.stdin.readline

    n = int(input())
    heights = list(map(int, input().split()))

    # ============================================================
    # Algorithm：单调栈
    # ============================================================
    stack = []  # 存下标，维护单调递增
    max_area = 0

    for i in range(n + 1):
        curr_h = heights[i] if i < n else 0
        while stack and curr_h < heights[stack[-1]]:
            h = heights[stack.pop()]
            left = stack[-1] if stack else -1
            right = i
            area = h * (right - left - 1)
            max_area = max(max_area, area)
        stack.append(i)

    # ============================================================
    # Output
    # ============================================================
    print(max_area)


# ============================================================
# 滑动窗口最大值（单调队列）
# 模式：单调队列 | I/O：单组测试用例
# ============================================================

def solve_sliding_window_max():
    """
    输入格式：
        第一行 n k
        第二行 n 个整数
    输出格式：
        一行：每个窗口的最大值

    核心思路：
        单调递减双端队列，存下标
        队头维护窗口最大值，过期下标从队头弹出
        维护单调性从队尾弹出较小元素
    """
    input = sys.stdin.readline

    n, k = map(int, input().split())
    nums = list(map(int, input().split()))

    # ============================================================
    # Algorithm：单调队列
    # ============================================================
    dq = deque()  # 存下标，维护单调递减
    result = []

    for i in range(n):
        # 队头过期：下标超出窗口左边界 [防错] i - k + 1 是左边界
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # 队尾维护单调性：弹出所有 <= 当前值的元素
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # 窗口形成后输出
        if i >= k - 1:
            result.append(str(nums[dq[0]]))

    # ============================================================
    # Output
    # ============================================================
    print(" ".join(result))


if __name__ == "__main__":
    solve_sliding_window_max()

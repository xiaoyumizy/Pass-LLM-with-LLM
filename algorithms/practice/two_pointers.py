"""
双指针 练习题
"""
import sys


# ============================================================
# 两数之和（排序版）
# 模式：双指针 | I/O：单组测试用例
# ============================================================

def solve_two_sum_sorted():
    """
    输入格式：
        第一行 n target
        第二行 n 个整数（已排序）
    输出格式：
        一行：两个元素的下标（1-based），无解输出 -1

    核心思路：
        左右双指针，和太大则右指针左移，和太小则左指针右移
    """
    input = sys.stdin.readline

    n, target = map(int, input().split())
    nums = list(map(int, input().split()))

    # ============================================================
    # Algorithm：双指针
    # ============================================================
    left, right = 0, n - 1
    while left < right:
        curr = nums[left] + nums[right]
        if curr == target:
            print(f"{left + 1} {right + 1}")
            return
        elif curr < target:
            left += 1
        else:
            right -= 1

    # ============================================================
    # Output
    # ============================================================
    print("-1")


# ============================================================
# 删除排序数组中的重复项
# 模式：快慢双指针 | I/O：单组测试用例
# ============================================================

def solve_remove_duplicates():
    """
    输入格式：
        第一行 n
        第二行 n 个整数（已排序）
    输出格式：
        一行：去重后的数组长度
        第二行：去重后的数组

    核心思路：
        快指针遍历，慢指针指向下一个要写入的位置
        快指针发现新元素时写入慢指针位置
    """
    input = sys.stdin.readline

    n = int(input())
    nums = list(map(int, input().split()))

    if n == 0:
        print(0)
        print("")
        return

    # ============================================================
    # Algorithm：快慢双指针
    # ============================================================
    slow = 0
    for fast in range(1, n):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]

    length = slow + 1

    # ============================================================
    # Output
    # ============================================================
    print(length)
    print(" ".join(map(str, nums[:length])))


# ============================================================
# 盛最多水的容器
# 模式：双指针 | I/O：单组测试用例
# ============================================================

def solve_container_with_most_water():
    """
    输入格式：
        第一行 n
        第二行 n 个非负整数表示柱子高度
    输出格式：
        一行：能容纳的最大水量

    核心思路：
        左右双指针，面积 = min(h[left], h[right]) * (right - left)
        移动较矮的那根柱子（移动较高的不会增大面积）
    """
    input = sys.stdin.readline

    n = int(input())
    heights = list(map(int, input().split()))

    # ============================================================
    # Algorithm：双指针
    # ============================================================
    left, right = 0, n - 1
    max_area = 0

    while left < right:
        area = min(heights[left], heights[right]) * (right - left)
        max_area = max(max_area, area)

        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    # ============================================================
    # Output
    # ============================================================
    print(max_area)


if __name__ == "__main__":
    solve_container_with_most_water()

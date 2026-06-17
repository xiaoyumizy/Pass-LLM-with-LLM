"""
字符串匹配 练习题（KMP / Rabin-Karp / 回文）
"""
import sys


# ============================================================
# KMP 模式匹配
# 模式：字符串匹配 | I/O：单组测试用例
# ============================================================

def solve_kmp():
    """
    输入格式：
        第一行 text
        第二行 pattern
    输出格式：
        一行：所有匹配位置的起始下标（0-based），无匹配输出 -1

    核心思路：
        构建 next 数组（前缀函数）：nxt[i] = pattern[:i+1] 的最长相等前后缀长度
        匹配时利用 next 数组跳过不必要的比较
    """
    input = sys.stdin.readline

    text = input().strip()
    pattern = input().strip()
    n, m = len(text), len(pattern)

    # ============================================================
    # Preprocess：构建 next 数组（前缀函数）
    # ============================================================
    nxt = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = nxt[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        nxt[i] = j

    # ============================================================
    # Algorithm：KMP 匹配
    # ============================================================
    j = 0
    positions = []
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = nxt[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = nxt[j - 1]  # [防错] 继续搜索下一个匹配

    # ============================================================
    # Output
    # ============================================================
    print(" ".join(map(str, positions)) if positions else "-1")


# ============================================================
# Rabin-Karp 字符串匹配
# 模式：字符串匹配（哈希）| I/O：单组测试用例
# ============================================================

def solve_rabin_karp():
    """
    输入格式：
        第一行 text
        第二行 pattern
    输出格式：
        一行：所有匹配位置的起始下标（0-based），无匹配输出 -1

    核心思路：
        对 pattern 和 text 的每个长度为 m 的子串计算滚动哈希
        哈希匹配时逐字符验证（防冲突）
    """
    input = sys.stdin.readline

    text = input().strip()
    pattern = input().strip()
    n, m = len(text), len(pattern)

    if m > n:
        print("-1")
        return

    # ============================================================
    # Preprocess：计算 pattern 的哈希和 text 第一个窗口的哈希
    # ============================================================
    BASE = 256
    MOD = 10**9 + 7

    # 预计算 BASE^(m-1) % MOD
    base_pow = pow(BASE, m - 1, MOD)

    # pattern 哈希
    ph = 0
    for c in pattern:
        ph = (ph * BASE + ord(c)) % MOD

    # text 第一个窗口哈希
    th = 0
    for i in range(m):
        th = (th * BASE + ord(text[i])) % MOD

    # ============================================================
    # Algorithm：滑动窗口 + 滚动哈希
    # ============================================================
    positions = []
    for i in range(n - m + 1):
        if th == ph:
            if text[i:i + m] == pattern:
                positions.append(i)

        # 滚动到下一个窗口
        if i < n - m:
            th = (th - ord(text[i]) * base_pow) * BASE + ord(text[i + m])
            th %= MOD

    # ============================================================
    # Output
    # ============================================================
    print(" ".join(map(str, positions)) if positions else "-1")


# ============================================================
# 最长回文子串（中心扩展）
# 模式：字符串处理 | I/O：单组测试用例
# ============================================================

def solve_longest_palindrome():
    """
    输入格式：
        一行字符串 s
    输出格式：
        一行：最长回文子串

    核心思路：
        枚举中心（共 2n-1 个：n 个奇数长度 + n-1 个偶数长度）
        从中心向两侧扩展，直到不是回文
    """
    input = sys.stdin.readline

    s = input().strip()
    n = len(s)
    if n == 0:
        print("")
        return

    # ============================================================
    # Algorithm：中心扩展
    # ============================================================
    best_start, best_len = 0, 1

    def expand(left, right):
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - left - 1

    for i in range(n):
        # 奇数长度回文
        start, length = expand(i, i)
        if length > best_len:
            best_start, best_len = start, length

        # 偶数长度回文
        start, length = expand(i, i + 1)
        if length > best_len:
            best_start, best_len = start, length

    # ============================================================
    # Output
    # ============================================================
    print(s[best_start:best_start + best_len])


if __name__ == "__main__":
    solve_longest_palindrome()

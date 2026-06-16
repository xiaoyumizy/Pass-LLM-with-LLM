# Algorithm Skeleton Templates

Replace the Algorithm phase in the standard skeleton with the matching template below.
See `SKILL.md` section 3 (Template Selection) for how to choose.

## 3a. BFS — Grid Shortest Path

**Trigger keywords**: shortest path, maze, grid, 0/1 matrix, reachable, min steps

```python
    # ============================================================
    # Algorithm: BFS grid shortest path
    # ============================================================
    xs, ys, xt, yt = map(int, input().split())
    xs -= 1; ys -= 1; xt -= 1; yt -= 1

    grid = [list(input().strip()) for _ in range(n)]

    dist = [[-1] * m for _ in range(n)]
    dist[xs][ys] = 0
    q = deque([(xs, ys)])

    while q:
        x, y = q.popleft()
        if x == xt and y == yt:
            break
        for dx, dy in DIR4:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] == "." and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))

    ans = dist[xt][yt]
    print(ans if ans != -1 else -1)
```

**Complexity**: O(n*m) time, O(n*m) space.

## 3b. DFS — Iterative (Stack-Based)

**Trigger keywords**: connected components, traversal, graph, reachability, flood fill

```python
    # ============================================================
    # Algorithm: Iterative DFS
    # ============================================================
    n = int(input())
    m = int(input())
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u, v = map(int, input().split())
        u -= 1; v -= 1
        graph[u].append(v)
        graph[v].append(u)

    seen = set()
    stack = [0]
    seen.add(0)
    while stack:
        u = stack.pop()
        for v in graph[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
```

**Complexity**: O(n + m) time, O(n) space.

## 3c. DSU (Union-Find)

**Trigger keywords**: merge, connected components, disjoint sets, union, connected query

```python
    # ============================================================
    # Algorithm: DSU
    # ============================================================
    n = int(input())

    parent = list(range(n))
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        return True

    m = int(input())
    for _ in range(m):
        a, b = map(int, input().split())
        a -= 1; b -= 1
        union(a, b)
```

**Complexity**: O(m * α(n)) time, O(n) space. Iterative find avoids Python recursion limit.

## 3d. Heap / Top-K

**Trigger keywords**: top K, largest K, smallest K, kth largest, priority queue

```python
    # ============================================================
    # Algorithm: Heap / Top-K
    # ============================================================
    n, k = map(int, input().split())
    nums = list(map(int, input().split()))

    heap = []
    for x in nums:
        if len(heap) < k:
            heappush(heap, x)
        elif x > heap[0]:
            heappop(heap)
            heappush(heap, x)

    ans = sorted(heap, reverse=True)
    print(ans)
```

**Complexity**: O(n log k) time, O(k) space.

## 3e. Dijkstra

**Trigger keywords**: weighted shortest path, min cost, min distance, Dijkstra, non-negative edges

```python
    # ============================================================
    # Algorithm: Dijkstra
    # ============================================================
    n = int(input())
    graph = [[] for _ in range(n)]
    m = int(input())
    for _ in range(m):
        u, v, w = map(int, input().split())
        u -= 1; v -= 1
        graph[u].append((v, w))
    start = int(input()) - 1

    INF = 10 ** 30
    dist = [INF] * n
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, u = heappop(heap)
        if d != dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heappush(heap, (nd, v))
    ans = dist
    print(ans)
```

**Complexity**: O((n+m) log n) time, O(n+m) space.
**Pitfall**: stale heap entry — always skip with `if d != dist[u]: continue`.

## 3f. Prefix Sum

**Trigger keywords**: range sum, subarray sum, interval query, cumulative sum

```python
    # ============================================================
    # Algorithm: Prefix sum
    # ============================================================
    n = int(input())
    nums = list(map(int, input().split()))
    pre = [0]
    for x in nums:
        pre.append(pre[-1] + x)

    q = int(input())
    out = []
    for _ in range(q):
        l, r = map(int, input().split())
        out.append(str(pre[r] - pre[l]))
    print("\n".join(out))
```

**Complexity**: O(n+q) time, O(n) space.
**Pitfall**: confirm query uses 0-based or 1-based indexing — prefix array is 1-based internally.

## 3g. Sliding Window (max/min variant)

**Trigger keywords**: subarray, window, max/min of length k, fixed-length window

```python
    # ============================================================
    # Algorithm: Sliding window
    # ============================================================
    n, k = map(int, input().split())
    nums = list(map(int, input().split()))

    cur = sum(nums[:k])
    ans = cur
    for i in range(k, n):
        cur += nums[i] - nums[i - k]
        ans = max(ans, cur)
    print(ans)
```

**Complexity**: O(n) time, O(1) space (fixed window).
**Pitfall**: for variable-length window, use a deque for monotonic max/min; this template is for fixed-length sum only.

## 3h. Binary Search

**Trigger keywords**: find minimum/maximum satisfying condition, boundary, monotonic function, answer in range

```python
    # ============================================================
    # Algorithm: Binary search
    # ============================================================
    n = int(input())
    a = list(map(int, input().split()))
    a.sort()

    def lower_bound(x):
        l, r = 0, n
        while l < r:
            m = (l + r) // 2
            if a[m] >= x:
                r = m
            else:
                l = m + 1
        return l

    def upper_bound(x):
        l, r = 0, n
        while l < r:
            m = (l + r) // 2
            if a[m] > x:
                r = m
            else:
                l = m + 1
        return l

    def check(x):
        # return True/False based on whether x satisfies the condition
        return True

    lo, hi = 0, 10 ** 9
    while lo < hi:
        mid = (lo + hi) // 2
        if check(mid):
            hi = mid
        else:
            lo = mid + 1
    ans = lo
    print(ans)
```

**Complexity**: O(n log n + check * log(range)). Lower/upper bound are O(log n) each.
**Pitfall**: `lo < hi` is half-open interval; `mid = (lo + hi) // 2` with `lo = mid + 1` avoids infinite loop.

## 3i. 1D Dynamic Programming

**Trigger keywords**: dp[i], climbing stairs, house robber, subsequence, longest increasing, fibonacci, 最长递增, 不相邻

```python
    # ============================================================
    # Algorithm: 1D DP
    # ============================================================
    n = int(input())
    nums = list(map(int, input().split()))

    # dp[i] = 前 i 个元素的最优解
    dp = [0] * (n + 1)

    # ============================================================
    # Base case
    # ============================================================
    dp[0] = 0            # TODO: 根据题意设定 base case
    # dp[1] = nums[0]    # TODO: 第一个元素单独处理

    # ============================================================
    # State transition
    # ============================================================
    for i in range(1, n + 1):
        # TODO: 根据题意填写状态转移
        # dp[i] = max(dp[i-1], dp[i-2] + nums[i-1])  # 不相邻最大和
        # dp[i] = dp[i-1] + 1                          # 最长递增子序列
        pass

    ans = dp[n]
    print(ans)
```

**Complexity**: O(n) time, O(n) space (可滚动数组优化到 O(1) space).
**Pitfall**: 边界 dp[0] / dp[1] 容易遗漏；滚动优化时注意顺序（1D 只需两个变量）。

## 3j. 2D Dynamic Programming (Grid Path / Knapsack)

**Trigger keywords**: grid path, knapsack, edit distance, dp[i][j], 二维 DP, 背包, 网格路径

```python
    # ============================================================
    # Algorithm: 2D DP
    # ============================================================
    n, m = map(int, input().split())
    grid = [list(map(int, input().split())) for _ in range(n)]

    # dp[i][j] = 从 (0,0) 到 (i,j) 的最优解
    dp = [[0] * m for _ in range(n)]

    # ============================================================
    # Base case
    # ============================================================
    dp[0][0] = grid[0][0]  # TODO: 根据题意设定
    for j in range(1, m):
        dp[0][j] = dp[0][j-1] + grid[0][j]   # TODO: 第一行初始化
    for i in range(1, n):
        dp[i][0] = dp[i-1][0] + grid[i][0]   # TODO: 第一列初始化

    # ============================================================
    # State transition
    # ============================================================
    for i in range(1, n):
        for j in range(1, m):
            # TODO: 根据题意填写
            # dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]  # 网格最小路径
            # dp[i][j] = dp[i-1][j] + dp[i][j-1]                    # 路径计数
            pass

    ans = dp[n-1][m-1]
    print(ans)
```

**Complexity**: O(n*m) time, O(n*m) space (可滚动数组优化到 O(m) space).
**Pitfall**: 第一行/第一列的初始化不能省略；滚动数组降维时，若依赖 dp[i-1][j-1] 需正序遍历。

## 3k. Monotonic Stack

**Trigger keywords**: next greater element, next smaller, histogram area, temperature, 单调栈, 柱状图

```python
    # ============================================================
    # Algorithm: Monotonic stack
    # ============================================================
    n = int(input())
    nums = list(map(int, input().split()))

    # next_greater[i] = 右侧第一个比 nums[i] 大的元素下标，不存在为 -1
    next_greater = [-1] * n
    stack = []  # 存下标，维护单调递减栈

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            next_greater[i] = idx   # TODO: 根据题意决定赋值方向
        stack.append(i)

    print(next_greater)
```

**Complexity**: O(n) time, O(n) space.
**Pitfall**: 栈中存下标而非值；while 条件是 `nums[i] > nums[stack[-1]]`（严格大于/大于等于按题意调整）。

## 3l. Monotonic Deque (Sliding Window Max/Min)

**Trigger keywords**: sliding window max, sliding window min, variable window, 单调队列, 滑动窗口最值

```python
    # ============================================================
    # Algorithm: Monotonic deque
    # ============================================================
    n, k = map(int, input().split())
    nums = list(map(int, input().split()))

    from collections import deque
    dq = deque()  # 存下标，维护单调递减队列（队头是窗口最大值下标）
    out = []

    for i in range(n):
        # 队头过期：下标超出窗口左边界
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # 队尾维护单调性：弹出所有 <= 当前值的元素
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # 窗口形成后输出
        if i >= k - 1:
            out.append(str(nums[dq[0]]))

    print(" ".join(out))
```

**Complexity**: O(n) time, O(k) space.
**Pitfall**: 过期元素必须从队头弹出（`dq[0] < i - k + 1`）；维护单调性从队尾弹出。

## 3m. Greedy

**Trigger keywords**: activity selection, interval scheduling, 贪心, 局部最优, 能力观赏, 分发糖果

```python
    # ============================================================
    # Algorithm: Greedy
    # ============================================================
    n = int(input())
    intervals = []
    for _ in range(n):
        s, e = map(int, input().split())
        intervals.append((s, e))

    # ============================================================
    # Step 1: 排序（贪心的关键前提）
    # ============================================================
    intervals.sort(key=lambda x: x[1])  # 按结束时间升序

    # ============================================================
    # Step 2: 贪心选择
    # ============================================================
    count = 0
    last_end = -1
    for s, e in intervals:
        if s >= last_end:       # TODO: 根据题意调整判断条件
            count += 1
            last_end = e

    print(count)
```

**Complexity**: O(n log n) time (排序主导), O(1) space (不算排序).
**Pitfall**: 贪心前必须先排序；选择标准（按开始/结束/持续时间）需要有贪心证明。

## 3n. Difference Array

**Trigger keywords**: range add, interval increment, 差分, 区间加, 差分还原

```python
    # ============================================================
    # Algorithm: Difference array
    # ============================================================
    n, q = map(int, input().split())
    a = list(map(int, input().split()))

    # ============================================================
    # Step 1: 构建差分数组
    # ============================================================
    diff = [0] * (n + 1)
    for _ in range(q):
        l, r, val = map(int, input().split())
        l -= 1; r -= 1           # 转为 0-based
        diff[l] += val
        diff[r + 1] -= val       # [防错] r+1 可能越界，diff 长度为 n+1

    # ============================================================
    # Step 2: 前缀和还原
    # ============================================================
    result = [0] * n
    result[0] = a[0] + diff[0]
    for i in range(1, n):
        diff[i] += diff[i-1]     # 累加差分
        result[i] = a[i] + diff[i]

    print(" ".join(map(str, result)))
```

**Complexity**: O(n + q) time, O(n) space.
**Pitfall**: `diff[r+1] -= val` 中 r+1 可能 = n，diff 数组需开 n+1；还原时 diff[i] += diff[i-1] 不能漏。

## 3o. Bit Manipulation

**Trigger keywords**: XOR, bitmask, subset enumeration, 奇偶, 位运算, 只出现一次

```python
    # ============================================================
    # Algorithm: Bit manipulation
    # ============================================================
    n = int(input())
    nums = list(map(int, input().split()))

    # ============================================================
    # XOR: 找只出现一次的数（其他出现两次）
    # ============================================================
    xor_all = 0
    for x in nums:
        xor_all ^= x
    print(xor_all)

    # ============================================================
    # Bitmask subset enumeration (if needed)
    # ============================================================
    # for mask in range(1 << n):
    #     subset = [nums[i] for i in range(n) if mask & (1 << i)]
    #     # TODO: process subset
```

**Complexity**: O(n) for XOR, O(n * 2^n) for subset enumeration.
**Pitfall**: `1 << n` 是 2^n（不包括 0）；`mask & (1 << i)` 检查第 i 位；XOR 满足交换律和结合律。

## 3p. String Processing (KMP / Rabin-Karp)

**Trigger keywords**: pattern matching, substring search, substring, 回文, KMP, 字符串匹配

```python
    # ============================================================
    # Algorithm: KMP pattern matching
    # ============================================================
    text = input().strip()
    pattern = input().strip()
    n, m = len(text), len(pattern)

    # ============================================================
    # Step 1: 构建 next 数组（前缀函数）
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
    # Step 2: KMP 匹配
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
            j = nxt[j - 1]

    print(positions if positions else [-1])
```

**Complexity**: O(n + m) time, O(m) space for next array.
**Pitfall**: next 数组构建时 `j = nxt[j-1]` 不能漏；匹配时找到后 `j = nxt[j-1]` 继续搜索。

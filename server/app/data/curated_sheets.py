"""
Curated Sheets Catalog for Debug Dojo / CursedCode.
Contains standardized problem blueprints from:
1. Striver's A2Z DSA Sheet (Step 1-4 Core & Advanced DSA)
2. CP-31 Sheet (800 - 1000 Rating Competitive Programming Foundations)
"""

CURATED_SHEETS = {
    "strivers-a2z": {
        "name": "Striver's A2Z DSA Sheet",
        "description": "The quintessential comprehensive Data Structures & Algorithms sheet by Take U Forward.",
        "badge": "DSA MASTERCLASS",
        "categories": ["Arrays", "Two Pointers", "Hashing", "Binary Search", "Strings"],
        "problems": [
            {
                "id": "set-matrix-zeroes",
                "title": "Set Matrix Zeroes",
                "difficulty": "Medium",
                "category": "Arrays",
                "grade": "Grade 3",
                "tags": ["Arrays", "Matrix"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ m, n ≤ 200; -2³¹ ≤ matrix[i][j] ≤ 2³¹ − 1",
                "time_complexity": "O(m · n)",
                "statement": "Write a function `set_matrix_zeroes(matrix)` that modifies the given m x n matrix in-place such that if an element is 0, its entire row and column are set to 0. Return the modified matrix.",
                "function_signature": "def set_matrix_zeroes(matrix):",
                "starter_code": "def set_matrix_zeroes(matrix):\n    # Modify matrix in-place and return it\n    if not matrix:\n        return matrix\n    rows, cols = len(matrix), len(matrix[0])\n    # Implement row and column zeroing\n    return matrix\n",
                "example": {
                    "call": "set_matrix_zeroes([[1, 1, 1], [1, 0, 1], [1, 1, 1]])",
                    "expected": "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]",
                    "explanation": "Matrix row 1 and column 1 both contain 0, so they become all zeroes."
                }
            },
            {
                "id": "pascals-triangle",
                "title": "Pascal's Triangle",
                "difficulty": "Easy",
                "category": "Arrays",
                "grade": "Grade 4",
                "tags": ["Arrays", "Math"],
                "time_limit_ms": 1000,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ numRows ≤ 30",
                "time_complexity": "O(numRows²)",
                "statement": "Write a function `generate_pascals_triangle(num_rows)` that returns the first `num_rows` of Pascal's triangle as a list of lists of integers.",
                "function_signature": "def generate_pascals_triangle(num_rows):",
                "starter_code": "def generate_pascals_triangle(num_rows):\n    # Return num_rows rows of Pascal's triangle\n    triangle = []\n    for i in range(num_rows):\n        row = [1] * (i + 1)\n        for j in range(1, i):\n            row[j] = triangle[i-1][j-1] + triangle[i-1][j]\n        triangle.append(row)\n    return triangle\n",
                "example": {
                    "call": "generate_pascals_triangle(5)",
                    "expected": "[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]",
                    "explanation": "Each element is the sum of the two elements directly above it."
                }
            },
            {
                "id": "kadanes-algorithm",
                "title": "Maximum Subarray (Kadane's Algorithm)",
                "difficulty": "Medium",
                "category": "Arrays",
                "grade": "Grade 3",
                "tags": ["Arrays", "Dynamic Programming"],
                "time_limit_ms": 300,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ len(nums) ≤ 10⁵; -10⁴ ≤ nums[i] ≤ 10⁴",
                "time_complexity": "O(n)",
                "statement": "Write a function `max_sub_array(nums)` that finds the subarray within `nums` (containing at least one number) which has the largest sum, and returns its sum.",
                "function_signature": "def max_sub_array(nums):",
                "starter_code": "def max_sub_array(nums):\n    # Kadane's algorithm\n    max_sum = nums[0]\n    current_sum = 0\n    for x in nums:\n        current_sum = max(x, current_sum + x)\n        max_sum = max(max_sum, current_sum)\n    return max_sum\n",
                "example": {
                    "call": "max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4])",
                    "expected": "6",
                    "explanation": "The subarray [4, -1, 2, 1] has the largest sum = 6."
                }
            },
            {
                "id": "sort-colors-012",
                "title": "Sort Colors (0s, 1s, 2s)",
                "difficulty": "Medium",
                "category": "Arrays",
                "grade": "Grade 3",
                "tags": ["Two Pointers", "Sorting"],
                "time_limit_ms": 300,
                "memory_limit_mb": 64,
                "input_constraints": "n == len(nums); 1 ≤ n ≤ 300; nums[i] ∈ {0, 1, 2}",
                "time_complexity": "O(n)",
                "statement": "Write a function `sort_colors(nums)` that sorts an array containing only numbers 0, 1, and 2 in ascending order in-place using the Dutch National Flag algorithm. Return the sorted list.",
                "function_signature": "def sort_colors(nums):",
                "starter_code": "def sort_colors(nums):\n    # Sort 0s, 1s, and 2s in-place (Dutch National Flag)\n    low, mid, high = 0, 0, len(nums) - 1\n    while mid <= high:\n        if nums[mid] == 0:\n            nums[low], nums[mid] = nums[mid], nums[low]\n            low += 1\n            mid += 1\n        elif nums[mid] == 1:\n            mid += 1\n        else:\n            nums[mid], nums[high] = nums[high], nums[mid]\n            high -= 1\n    return nums\n",
                "example": {
                    "call": "sort_colors([2, 0, 2, 1, 1, 0])",
                    "expected": "[0, 0, 1, 1, 2, 2]",
                    "explanation": "All 0s precede 1s, which precede 2s."
                }
            },
            {
                "id": "stock-buy-and-sell",
                "title": "Best Time to Buy and Sell Stock",
                "difficulty": "Easy",
                "category": "Arrays",
                "grade": "Grade 4",
                "tags": ["Arrays", "Greedy"],
                "time_limit_ms": 300,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ len(prices) ≤ 10⁵; 0 ≤ prices[i] ≤ 10⁴",
                "time_complexity": "O(n)",
                "statement": "Write a function `max_profit(prices)` that returns the maximum profit you can achieve from a single stock transaction (buy once, sell once on a future day). If no profit is possible, return 0.",
                "function_signature": "def max_profit(prices):",
                "starter_code": "def max_profit(prices):\n    # Return maximum single-transaction profit\n    if not prices:\n        return 0\n    min_price = float('inf')\n    max_prof = 0\n    for p in prices:\n        if p < min_price:\n            min_price = p\n        elif p - min_price > max_prof:\n            max_prof = p - min_price\n    return max_prof\n",
                "example": {
                    "call": "max_profit([7, 1, 5, 3, 6, 4])",
                    "expected": "5",
                    "explanation": "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6 - 1 = 5."
                }
            },
            {
                "id": "rotate-matrix-90",
                "title": "Rotate Image / Matrix by 90°",
                "difficulty": "Medium",
                "category": "Arrays",
                "grade": "Grade 3",
                "tags": ["Matrix", "Math"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "n == len(matrix) == len(matrix[i]); 1 ≤ n ≤ 20; -1000 ≤ matrix[i][j] ≤ 1000",
                "time_complexity": "O(n²)",
                "statement": "Write a function `rotate_matrix(matrix)` that rotates an n x n 2D matrix by 90 degrees clockwise in-place and returns the modified matrix.",
                "function_signature": "def rotate_matrix(matrix):",
                "starter_code": "def rotate_matrix(matrix):\n    # Rotate n x n matrix 90 degrees clockwise\n    n = len(matrix)\n    # Transpose\n    for i in range(n):\n        for j in range(i, n):\n            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n    # Reverse each row\n    for row in matrix:\n        row.reverse()\n    return matrix\n",
                "example": {
                    "call": "rotate_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
                    "expected": "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]",
                    "explanation": "Row [1, 2, 3] becomes the rightmost column [1, 2, 3]."
                }
            },
            {
                "id": "merge-intervals",
                "title": "Merge Overlapping Intervals",
                "difficulty": "Medium",
                "category": "Arrays",
                "grade": "Grade 3",
                "tags": ["Arrays", "Sorting"],
                "time_limit_ms": 400,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ len(intervals) ≤ 10⁴; intervals[i].length == 2; 0 ≤ startᵢ ≤ endᵢ ≤ 10⁴",
                "time_complexity": "O(n log n)",
                "statement": "Write a function `merge_intervals(intervals)` that merges all overlapping intervals from a list of `[start, end]` pairs and returns the non-overlapping intervals.",
                "function_signature": "def merge_intervals(intervals):",
                "starter_code": "def merge_intervals(intervals):\n    if not intervals:\n        return []\n    intervals.sort(key=lambda x: x[0])\n    merged = [intervals[0]]\n    for current in intervals[1:]:\n        prev = merged[-1]\n        if current[0] <= prev[1]:\n            prev[1] = max(prev[1], current[1])\n        else:\n            merged.append(current)\n    return merged\n",
                "example": {
                    "call": "merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])",
                    "expected": "[[1, 6], [8, 10], [15, 18]]",
                    "explanation": "Intervals [1, 3] and [2, 6] overlap and become [1, 6]."
                }
            },
            {
                "id": "longest-consecutive-sequence",
                "title": "Longest Consecutive Sequence",
                "difficulty": "Medium",
                "category": "Hashing",
                "grade": "Grade 3",
                "tags": ["HashSet", "Arrays"],
                "time_limit_ms": 300,
                "memory_limit_mb": 64,
                "input_constraints": "0 ≤ len(nums) ≤ 10⁵; -10⁹ ≤ nums[i] ≤ 10⁹",
                "time_complexity": "O(n)",
                "statement": "Write a function `longest_consecutive(nums)` that returns the length of the longest consecutive elements sequence in an unsorted array of integers in O(n) time.",
                "function_signature": "def longest_consecutive(nums):",
                "starter_code": "def longest_consecutive(nums):\n    num_set = set(nums)\n    longest = 0\n    for num in num_set:\n        if num - 1 not in num_set:\n            current_num = num\n            current_streak = 1\n            while current_num + 1 in num_set:\n                current_num += 1\n                current_streak += 1\n            longest = max(longest, current_streak)\n    return longest\n",
                "example": {
                    "call": "longest_consecutive([100, 4, 200, 1, 3, 2])",
                    "expected": "4",
                    "explanation": "The longest consecutive sequence is [1, 2, 3, 4], length 4."
                }
            }
        ]
    },
    "cp-31": {
        "name": "CP-31 Sheet (Ladder 800-1000)",
        "description": "The battle-tested 31-problem competitive programming ladder curated by TLE Eliminators.",
        "badge": "CP ARENA",
        "categories": ["Greedy", "Implementation", "Math", "Strings"],
        "problems": [
            {
                "id": "can-divide-watermelon",
                "title": "Watermelon (CF 4A)",
                "difficulty": "Easy",
                "category": "Math",
                "grade": "Grade 4",
                "tags": ["Math", "Parity"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ w ≤ 100",
                "time_complexity": "O(1)",
                "statement": "Pete and Billy want to divide a watermelon weighing `w` kilos into two parts, each weighing an even positive integer number of kilos. Write `can_divide_watermelon(w)` that returns `True` if possible, otherwise `False`.",
                "function_signature": "def can_divide_watermelon(w):",
                "starter_code": "def can_divide_watermelon(w):\n    # Return True if w can be divided into two positive even integers\n    return w > 2 and w % 2 == 0\n",
                "example": {
                    "call": "can_divide_watermelon(8)",
                    "expected": "True",
                    "explanation": "8 can be split into 2 and 6, or 4 and 4, both of which are even."
                }
            },
            {
                "id": "way-too-long-words",
                "title": "Way Too Long Words (CF 71A)",
                "difficulty": "Easy",
                "category": "Strings",
                "grade": "Grade 4",
                "tags": ["Strings", "Implementation"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ len(word) ≤ 100",
                "time_complexity": "O(n)",
                "statement": "A word is considered 'too long' if its length is strictly more than 10 characters. Replace such words with an abbreviation formed by its first letter, the count of characters between first and last, and the last letter. Write `abbreviate_word(word)`.",
                "function_signature": "def abbreviate_word(word):",
                "starter_code": "def abbreviate_word(word):\n    # If length > 10, abbreviate\n    if len(word) > 10:\n        return word[0] + str(len(word) - 2) + word[-1]\n    return word\n",
                "example": {
                    "call": "abbreviate_word('localization')",
                    "expected": "'l10n'",
                    "explanation": "'localization' has 12 chars; first is 'l', last is 'n', and 10 in between."
                }
            },
            {
                "id": "bit-plus-plus",
                "title": "Bit++ (CF 282A)",
                "difficulty": "Easy",
                "category": "Implementation",
                "grade": "Grade 4",
                "tags": ["Implementation", "Strings"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ len(statements) ≤ 150",
                "time_complexity": "O(n)",
                "statement": "The language Bit++ has one variable x (initially 0) and two operations: ++ (increments x by 1) and -- (decrements x by 1). Given a list of operations, return the final value of x via `execute_bit_statements(statements)`.",
                "function_signature": "def execute_bit_statements(statements):",
                "starter_code": "def execute_bit_statements(statements):\n    x = 0\n    for stmt in statements:\n        if '+' in stmt:\n            x += 1\n        elif '-' in stmt:\n            x -= 1\n    return x\n",
                "example": {
                    "call": "execute_bit_statements(['++X', 'X++', '--X'])",
                    "expected": "1",
                    "explanation": "0 -> 1 -> 2 -> 1. Final value is 1."
                }
            },
            {
                "id": "domino-piling",
                "title": "Domino Piling (CF 50A)",
                "difficulty": "Easy",
                "category": "Math",
                "grade": "Grade 4",
                "tags": ["Math", "Greedy"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ m, n ≤ 10⁹",
                "time_complexity": "O(1)",
                "statement": "Given a rectangular board of M x N squares and dominoes of size 2 x 1, find the maximum number of dominoes that can be placed on the board without overlapping. Write `max_dominoes(m, n)`.",
                "function_signature": "def max_dominoes(m, n):",
                "starter_code": "def max_dominoes(m, n):\n    # Return maximum 2x1 dominoes on m x n board\n    return (m * n) // 2\n",
                "example": {
                    "call": "max_dominoes(3, 3)",
                    "expected": "4",
                    "explanation": "A 3x3 board has 9 squares; each domino takes 2 squares, so floor(9/2) = 4."
                }
            },
            {
                "id": "beautiful-matrix",
                "title": "Beautiful Matrix (CF 263A)",
                "difficulty": "Easy",
                "category": "Matrix",
                "grade": "Grade 4",
                "tags": ["Matrix", "Math"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "matrix is 5×5 with exactly one 1 and 24 zeros",
                "time_complexity": "O(25)",
                "statement": "You are given a 5 x 5 matrix containing 24 zeroes and a single one. Write `min_moves_to_center(matrix)` that calculates the minimum number of row/column swaps needed to move the number one to the center (row index 2, column index 2).",
                "function_signature": "def min_moves_to_center(matrix):",
                "starter_code": "def min_moves_to_center(matrix):\n    # Find position of 1 and compute Manhattan distance to (2, 2)\n    for r in range(5):\n        for c in range(5):\n            if matrix[r][c] == 1:\n                return abs(r - 2) + abs(c - 2)\n    return 0\n",
                "example": {
                    "call": "min_moves_to_center([[0, 0, 0, 0, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])",
                    "expected": "3",
                    "explanation": "One is at (1, 4). Manhattan distance to (2, 2) is |1 - 2| + |4 - 2| = 1 + 2 = 3 moves."
                }
            },
            {
                "id": "elephant-steps",
                "title": "Elephant (CF 617A)",
                "difficulty": "Easy",
                "category": "Math",
                "grade": "Grade 4",
                "tags": ["Math", "Greedy"],
                "time_limit_ms": 500,
                "memory_limit_mb": 64,
                "input_constraints": "1 ≤ x ≤ 10⁹",
                "time_complexity": "O(1)",
                "statement": "An elephant wants to visit his friend at coordinate x (start at 0). In one step, the elephant can move 1, 2, 3, 4, or 5 positions forward. Write `min_steps_to_friend(x)` to find the minimum number of steps to reach x.",
                "function_signature": "def min_steps_to_friend(x):",
                "starter_code": "def min_steps_to_friend(x):\n    # Greedy step of size 5\n    return (x + 4) // 5\n",
                "example": {
                    "call": "min_steps_to_friend(12)",
                    "expected": "3",
                    "explanation": "The elephant can take steps 5, 5, 2 (3 steps total)."
                }
            }
        ]
    }
}

"""
Seed challenges and test cases matching client/src/data/challenges.js.
Ensures both frontend and backend are aligned on challenge IDs, statements, tests, and progressive hints.
"""

SEED_CHALLENGES = [
    {
        "id": "last-k-total",
        "title": "Last K Total",
        "description": "Return the total of the final k values in a list of numbers.",
        "statement": "Write a function named `last_k_total(numbers, k)` that takes a list of integers `numbers` and an integer `k`. It returns the sum of the last `k` integers in the list. If `k` is 0, return 0.",
        "grade": "Grade 4",
        "difficulty": "Easy",
        "tags": ["Lists", "Slicing"],
        "estimatedTime": "10 min",
        "starterCode": "def last_k_total(numbers, k):\n    # Return the total of the last k values in numbers.\n    if k == 0:\n        return 0\n    return sum(numbers[-k:])\n",
        "example": {
            "call": "last_k_total([3, 8, 2, 5], 2)",
            "expected": "7",
            "explanation": "The last 2 elements are 2 and 5. Their sum is 7."
        },
        "visibleTests": [
            {"call": "last_k_total([3, 8, 2, 5], 2)", "expected": "7"},
            {"call": "last_k_total([10, 20, 30], 1)", "expected": "30"},
            {"call": "last_k_total([4, 6, 8], 0)", "expected": "0"}
        ],
        "hiddenTests": [
            {"call": "last_k_total([1, 2, 3, 4, 5], 5)", "expected": "15"},
            {"call": "last_k_total([], 0)", "expected": "0"},
            {"call": "last_k_total([-5, -10, 20], 2)", "expected": "10"},
            {"call": "last_k_total([100], 1)", "expected": "100"},
            {"call": "last_k_total([7, 3, 1, 9, 4], 3)", "expected": "14"}
        ],
        "hints": [
            "Check what happens when k is 0. Python's slice `numbers[-0:]` will take the entire list from index 0!",
            "Consider slicing with negative indices `numbers[-k:]` only when k > 0.",
            "Make sure you handle cases where k is greater than the length of the list.",
            "Use `numbers[-k:] if k > 0 else []` to safely slice the last k elements, then return `sum(...)`."
        ]
    },
    {
        "id": "countpasses",
        "title": "Count Passes",
        "description": "Count the number of test scores that are 40 or more.",
        "statement": "Write a function named `count_passes(marks)` that takes a list of integer `marks` and returns how many of them are 40 or more.",
        "grade": "Grade 4",
        "difficulty": "Easy",
        "tags": ["Loops", "Comparison"],
        "estimatedTime": "10 min",
        "starterCode": "def count_passes(marks):\n    # Count marks that are 40 or more\n    count = 0\n    for mark in marks:\n        if mark >= 40:\n            count += 1\n    return count\n",
        "example": {
            "call": "count_passes([30, 40, 50])",
            "expected": "2",
            "explanation": "Marks 40 and 50 are 40 or more, so the count is 2."
        },
        "visibleTests": [
            {"call": "count_passes([30, 40, 50])", "expected": "2"},
            {"call": "count_passes([10, 20, 30])", "expected": "0"},
            {"call": "count_passes([40, 40, 40])", "expected": "3"}
        ],
        "hiddenTests": [
            {"call": "count_passes([])", "expected": "0"},
            {"call": "count_passes([39, 40, 41])", "expected": "2"},
            {"call": "count_passes([39])", "expected": "0"},
            {"call": "count_passes([100, 5, 40, 0, 41])", "expected": "3"},
            {"call": "count_passes([0])", "expected": "0"},
            {"call": "count_passes([40, 39])", "expected": "1"}
        ],
        "hints": [
            "Check the boundary: does a mark exactly equal to 40 count?",
            "Remember '40 or more' means use `>=`, not `>`.",
            "Start your counter at 0 before the loop, then return it after the loop ends.",
            "Loop through each mark with `for mark in marks:` and check `if mark >= 40:`."
        ]
    },
    {
        "id": "first-n-squares",
        "title": "First N Squares",
        "description": "Build and return a list containing the squares of numbers from 1 through n.",
        "statement": "Write a function named `first_n_squares(n)` that receives a positive integer `n` and returns a list containing the squares of integers from 1 up to and including `n` in ascending order.",
        "grade": "Grade 4",
        "difficulty": "Easy",
        "tags": ["Loops", "Lists"],
        "estimatedTime": "10 min",
        "starterCode": "def first_n_squares(n):\n    # Build list of squares from 1 up to n\n    return [i * i for i in range(1, n + 1)]\n",
        "example": {
            "call": "first_n_squares(4)",
            "expected": "[1, 4, 9, 16]",
            "explanation": "The first 4 positive integers squared are 1, 4, 9, and 16."
        },
        "visibleTests": [
            {"call": "first_n_squares(4)", "expected": "[1, 4, 9, 16]"},
            {"call": "first_n_squares(1)", "expected": "[1]"},
            {"call": "first_n_squares(0)", "expected": "[]"}
        ],
        "hiddenTests": [
            {"call": "first_n_squares(5)", "expected": "[1, 4, 9, 16, 25]"},
            {"call": "first_n_squares(2)", "expected": "[1, 4]"},
            {"call": "first_n_squares(3)", "expected": "[1, 4, 9]"},
            {"call": "first_n_squares(6)", "expected": "[1, 4, 9, 16, 25, 36]"},
            {"call": "first_n_squares(10)", "expected": "[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]"}
        ],
        "hints": [
            "Remember that range in Python is exclusive at the stop index.",
            "To include n, your range stop value must be n + 1.",
            "If n is 0 or negative, the result should be an empty list [].",
            "A list comprehension `[i ** 2 for i in range(1, n + 1)]` handles all cases cleanly."
        ]
    },
    {
        "id": "middlethree",
        "title": "Middle Three",
        "description": "Extract and return the middle three items from an odd-length sequence.",
        "statement": "Write a function named `middle_three(items)` that receives an odd-length list with at least 3 elements. Return a new list containing the exact 3 items situated at the center of the list.",
        "grade": "Grade 3",
        "difficulty": "Medium",
        "tags": ["Lists", "Indexing"],
        "estimatedTime": "15 min",
        "starterCode": "def middle_three(items):\n    # Return the three middle items of an odd-length list\n    mid = len(items) // 2\n    return items[mid - 1 : mid + 2]\n",
        "example": {
            "call": "middle_three([1, 2, 3, 4, 5])",
            "expected": "[2, 3, 4]",
            "explanation": "The center element is 3. The middle 3 items are 2, 3, 4."
        },
        "visibleTests": [
            {"call": "middle_three([1, 2, 3, 4, 5])", "expected": "[2, 3, 4]"},
            {"call": "middle_three(['a', 'b', 'c'])", "expected": "['a', 'b', 'c']"},
            {"call": "middle_three([10, 20, 30, 40, 50, 60, 70])", "expected": "[30, 40, 50]"}
        ],
        "hiddenTests": [
            {"call": "middle_three([9, 8, 7, 6, 5])", "expected": "[8, 7, 6]"},
            {"call": "middle_three([1, 2, 3, 4, 5, 6, 7, 8, 9])", "expected": "[4, 5, 6]"},
            {"call": "middle_three([0, 0, 1, 0, 0])", "expected": "[0, 1, 0]"},
            {"call": "middle_three(['x', 'y', 'z'])", "expected": "['x', 'y', 'z']"},
            {"call": "middle_three([100, 200, 300, 400, 500])", "expected": "[200, 300, 400]"}
        ],
        "hints": [
            "Find the middle index using integer division: `mid = len(items) // 2`.",
            "The element directly before the center is at `mid - 1`, and the element after is at `mid + 1`.",
            "Remember that slice end index is exclusive in Python, so `mid + 2` includes `mid + 1`.",
            "Return `items[mid - 1 : mid + 2]`."
        ]
    },
    {
        "id": "word-boundary",
        "title": "Word Boundary",
        "description": "Determine whether a sentence starts or ends with a specific target keyword.",
        "statement": "Write a function named `is_at_boundary(sentence, keyword)` that checks if the given `sentence` either begins with or concludes with the exact string `keyword` (case-sensitive).",
        "grade": "Grade 3",
        "difficulty": "Medium",
        "tags": ["Strings", "Comparison"],
        "estimatedTime": "15 min",
        "starterCode": "def is_at_boundary(sentence, keyword):\n    # Check if sentence starts or ends with keyword\n    return sentence.startswith(keyword) or sentence.endswith(keyword)\n",
        "example": {
            "call": "is_at_boundary(\"curse energy flows\", \"curse\")",
            "expected": "True",
            "explanation": "The sentence starts with 'curse'."
        },
        "visibleTests": [
            {"call": "is_at_boundary(\"curse energy flows\", \"curse\")", "expected": "True"},
            {"call": "is_at_boundary(\"the quiet realm\", \"realm\")", "expected": "True"},
            {"call": "is_at_boundary(\"inside the barrier now\", \"barrier\")", "expected": "False"}
        ],
        "hiddenTests": [
            {"call": "is_at_boundary(\"infinite void\", \"void\")", "expected": "True"},
            {"call": "is_at_boundary(\"hollow purple\", \"hollow\")", "expected": "True"},
            {"call": "is_at_boundary(\"sukuna\", \"sukuna\")", "expected": "True"},
            {"call": "is_at_boundary(\"domain expansion\", \"expand\")", "expected": "False"},
            {"call": "is_at_boundary(\"\", \"curse\")", "expected": "False"}
        ],
        "hints": [
            "Python strings have built-in methods `.startswith()` and `.endswith()`.",
            "Make sure the check is case-sensitive as requested.",
            "Combine both conditions using the logical `or` operator.",
            "`return sentence.startswith(keyword) or sentence.endswith(keyword)` covers all edge cases."
        ]
    },
    {
        "id": "pair-sum",
        "title": "Pair Sum",
        "description": "Find two distinct numbers in an array whose sum equals the specified target value.",
        "statement": "Write a function named `has_pair_sum(numbers, target)` that returns `True` if any two distinct entries in the list `numbers` sum to `target`, otherwise `False`.",
        "grade": "Grade 3",
        "difficulty": "Medium",
        "tags": ["Loops", "Lists"],
        "estimatedTime": "20 min",
        "starterCode": "def has_pair_sum(numbers, target):\n    # Return True if two numbers sum to target\n    seen = set()\n    for num in numbers:\n        if (target - num) in seen:\n            return True\n        seen.add(num)\n    return False\n",
        "example": {
            "call": "has_pair_sum([2, 7, 11, 15], 9)",
            "expected": "True",
            "explanation": "2 + 7 equals 9."
        },
        "visibleTests": [
            {"call": "has_pair_sum([2, 7, 11, 15], 9)", "expected": "True"},
            {"call": "has_pair_sum([3, 5, 1], 10)", "expected": "False"},
            {"call": "has_pair_sum([5], 10)", "expected": "False"}
        ],
        "hiddenTests": [
            {"call": "has_pair_sum([1, 2, 3, 4], 7)", "expected": "True"},
            {"call": "has_pair_sum([5, 5], 10)", "expected": "True"},
            {"call": "has_pair_sum([], 5)", "expected": "False"},
            {"call": "has_pair_sum([10, -2, 3], 8)", "expected": "True"},
            {"call": "has_pair_sum([1, 2, 4], 8)", "expected": "False"}
        ],
        "hints": [
            "Be careful not to add a number to itself unless it appears twice in the list.",
            "A hash set allows O(1) lookup of the needed complement `(target - num)`.",
            "For each number, check if `target - num` is already in your `seen` set before adding `num`.",
            "If the loop ends without finding a complement, return `False`."
        ]
    },
    {
        "id": "mirror-check",
        "title": "Mirror Check",
        "description": "Verify if a string reads the same forwards and backwards, ignoring case.",
        "statement": "Write a function named `is_mirror(text)` that returns `True` if `text` is a palindrome when comparing lowercase characters only, otherwise `False`.",
        "grade": "Grade 3",
        "difficulty": "Medium",
        "tags": ["Strings", "Indexing"],
        "estimatedTime": "15 min",
        "starterCode": "def is_mirror(text):\n    # Check if text is a palindrome, case-insensitive\n    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())\n    return cleaned == cleaned[::-1]\n",
        "example": {
            "call": "is_mirror(\"Level\")",
            "expected": "True",
            "explanation": "\"level\" reads identically in reverse."
        },
        "visibleTests": [
            {"call": "is_mirror(\"Level\")", "expected": "True"},
            {"call": "is_mirror(\"sorcery\")", "expected": "False"},
            {"call": "is_mirror(\"A man a plan a canal Panama\")", "expected": "True"}
        ],
        "hiddenTests": [
            {"call": "is_mirror(\"racecar\")", "expected": "True"},
            {"call": "is_mirror(\"hello\")", "expected": "False"},
            {"call": "is_mirror(\"\")", "expected": "True"},
            {"call": "is_mirror(\"No 'x' in Nixon\")", "expected": "True"},
            {"call": "is_mirror(\"12321\")", "expected": "True"}
        ],
        "hints": [
            "Ignore non-alphanumeric characters (spaces, punctuation) using `.isalnum()`.",
            "Convert all characters to lowercase using `.lower()` before checking.",
            "Compare the cleaned string with its reverse `cleaned[::-1]`.",
            "An empty string is trivially a palindrome and should return `True`."
        ]
    },
    {
        "id": "common-start",
        "title": "Common Start",
        "description": "Identify the longest common starting prefix shared across a list of strings.",
        "statement": "Write a function named `common_start(words)` that returns the longest string prefix shared by every word in the given list. If there is no common prefix, return `\"\"`.",
        "grade": "Grade 2",
        "difficulty": "Hard",
        "tags": ["Strings", "Loops"],
        "estimatedTime": "25 min",
        "starterCode": "def common_start(words):\n    # Find longest shared prefix\n    if not words:\n        return \"\"\n    prefix = words[0]\n    for word in words[1:]:\n        while not word.startswith(prefix):\n            prefix = prefix[:-1]\n            if not prefix:\n                return \"\"\n    return prefix\n",
        "example": {
            "call": "common_start([\"domain\", \"domino\", \"domestic\"])",
            "expected": "\"dom\"",
            "explanation": "All three words start with 'dom'."
        },
        "visibleTests": [
            {"call": "common_start([\"domain\", \"domino\", \"domestic\"])", "expected": "\"dom\""},
            {"call": "common_start([\"flash\", \"spark\", \"bolt\"])", "expected": "\"\""},
            {"call": "common_start([\"curse\", \"cursed\", \"curiosity\"])", "expected": "\"cur\""}
        ],
        "hiddenTests": [
            {"call": "common_start([\"black\", \"blackout\", \"blacksmith\"])", "expected": "\"black\""},
            {"call": "common_start([\"a\"])", "expected": "\"a\""},
            {"call": "common_start([])", "expected": "\"\""},
            {"call": "common_start([\"same\", \"same\", \"same\"])", "expected": "\"same\""},
            {"call": "common_start([\"prefix\", \"prefer\", \"prepare\"])", "expected": "\"pre\""}
        ],
        "hints": [
            "Start by checking if `words` is empty. If so, return `\"\"` immediately.",
            "Initialize your prefix candidate to the first word in the list.",
            "Iterate through subsequent words; while the word doesn't start with the prefix, shorten prefix by one character: `prefix = prefix[:-1]`.",
            "If prefix becomes empty, no common prefix exists; return `\"\"`."
        ]
    },
    {
        "id": "missing-step",
        "title": "Missing Step",
        "description": "Find the single missing value in an otherwise contiguous arithmetic progression.",
        "statement": "Write a function named `find_missing_step(sequence)` that receives an arithmetic sequence of numbers where one number is missing. Return that missing number.",
        "grade": "Grade 2",
        "difficulty": "Hard",
        "tags": ["Lists", "Comparison"],
        "estimatedTime": "20 min",
        "starterCode": "def find_missing_step(sequence):\n    # Find the missing element in arithmetic sequence\n    n = len(sequence)\n    diff = (sequence[-1] - sequence[0]) // n\n    for i in range(n - 1):\n        if sequence[i + 1] - sequence[i] != diff:\n            return sequence[i] + diff\n    return sequence[0]\n",
        "example": {
            "call": "find_missing_step([2, 4, 8, 10])",
            "expected": "6",
            "explanation": "The common difference is 2; 6 is the missing step."
        },
        "visibleTests": [
            {"call": "find_missing_step([2, 4, 8, 10])", "expected": "6"},
            {"call": "find_missing_step([10, 7, 1])", "expected": "4"},
            {"call": "find_missing_step([1, 3, 5, 9])", "expected": "7"}
        ],
        "hiddenTests": [
            {"call": "find_missing_step([10, 20, 40])", "expected": "30"},
            {"call": "find_missing_step([5, 10, 15, 25])", "expected": "20"},
            {"call": "find_missing_step([100, 90, 70])", "expected": "80"},
            {"call": "find_missing_step([0, 3, 9])", "expected": "6"},
            {"call": "find_missing_step([2, 6, 8])", "expected": "4"}
        ],
        "hints": [
            "In an arithmetic sequence of length n with 1 missing term, the total step count is n.",
            "Calculate expected difference: `diff = (sequence[-1] - sequence[0]) // len(sequence)`.",
            "Loop through adjacent pairs; if `sequence[i + 1] - sequence[i] != diff`, the missing number is `sequence[i] + diff`.",
            "This approach handles both increasing and decreasing progressions correctly."
        ]
    },
    {
        "id": "balanced-brackets",
        "title": "Balanced Brackets",
        "description": "Check whether all brackets in a string have matching and correctly nested closers.",
        "statement": "Write a function named `is_balanced(expr)` that returns `True` if all parentheses `()`, square brackets `[]`, and curly braces `{}` are correctly paired and nested.",
        "grade": "Grade 2",
        "difficulty": "Hard",
        "tags": ["Strings", "Loops"],
        "estimatedTime": "25 min",
        "starterCode": "def is_balanced(expr):\n    # Check if brackets are balanced and properly nested\n    stack = []\n    pairs = {')': '(', ']': '[', '}': '{'}\n    for ch in expr:\n        if ch in pairs.values():\n            stack.append(ch)\n        elif ch in pairs:\n            if not stack or stack.pop() != pairs[ch]:\n                return False\n    return len(stack) == 0\n",
        "example": {
            "call": "is_balanced(\"{[()]}\")",
            "expected": "True",
            "explanation": "All brackets are properly closed in correct order."
        },
        "visibleTests": [
            {"call": "is_balanced(\"{[()]}\")", "expected": "True"},
            {"call": "is_balanced(\"([)]\")", "expected": "False"},
            {"call": "is_balanced(\"({[\")", "expected": "False"}
        ],
        "hiddenTests": [
            {"call": "is_balanced(\"\")", "expected": "True"},
            {"call": "is_balanced(\"((()))\")", "expected": "True"},
            {"call": "is_balanced(\"][\")", "expected": "False"},
            {"call": "is_balanced(\"(()\")", "expected": "False"},
            {"call": "is_balanced(\"{[]}\")", "expected": "True"}
        ],
        "hints": [
            "Use a stack (a Python list with `.append()` and `.pop()`).",
            "When encountering an opening bracket, push it onto the stack.",
            "When encountering a closing bracket, check if the stack is non-empty and the top matches.",
            "At the end of the string, the stack must be completely empty: `return len(stack) == 0`."
        ]
    },
    {
        "id": "frequency-count",
        "title": "Character Frequency",
        "description": "Count occurrences of each unique character and return character counts.",
        "statement": "Write a function named `char_frequency(text)` that returns a dictionary mapping each distinct lowercase character in `text` to its total frequency count. Ignore spaces.",
        "grade": "Grade 3",
        "difficulty": "Medium",
        "tags": ["Strings", "Lists"],
        "estimatedTime": "15 min",
        "starterCode": "def char_frequency(text):\n    # Return count of each character, excluding whitespace\n    freq = {}\n    for ch in text.lower():\n        if not ch.isspace():\n            freq[ch] = freq.get(ch, 0) + 1\n    return freq\n",
        "example": {
            "call": "char_frequency(\"seal\")",
            "expected": "{'s': 1, 'e': 1, 'a': 1, 'l': 1}",
            "explanation": "Each character appears once."
        },
        "visibleTests": [
            {"call": "char_frequency(\"seal\")", "expected": "{'s': 1, 'e': 1, 'a': 1, 'l': 1}"},
            {"call": "char_frequency(\"banana\")", "expected": "{'b': 1, 'a': 3, 'n': 2}"},
            {"call": "char_frequency(\"a a\")", "expected": "{'a': 2}"}
        ],
        "hiddenTests": [
            {"call": "char_frequency(\"curse\")", "expected": "{'c': 1, 'u': 1, 'r': 1, 's': 1, 'e': 1}"},
            {"call": "char_frequency(\"\")", "expected": "{}"},
            {"call": "char_frequency(\"GoJo\")", "expected": "{'g': 1, 'o': 2, 'j': 1}"},
            {"call": "char_frequency(\"xyz\")", "expected": "{'x': 1, 'y': 1, 'z': 1}"},
            {"call": "char_frequency(\"  \")", "expected": "{}"}
        ],
        "hints": [
            "Convert each character to lowercase with `.lower()`.",
            "Skip spaces using `if not ch.isspace():`.",
            "Use dictionary `.get(ch, 0) + 1` to increment counts safely.",
            "Return the dictionary directly."
        ]
    },
    {
        "id": "streak-counter",
        "title": "Longest Streak",
        "description": "Calculate the maximum length of consecutive true or matching conditions in a list.",
        "statement": "Write a function named `longest_streak(values, target)` that returns the maximum number of consecutive times `target` appears in the sequence `values`.",
        "grade": "Grade 4",
        "difficulty": "Easy",
        "tags": ["Loops", "Comparison"],
        "estimatedTime": "10 min",
        "starterCode": "def longest_streak(values, target):\n    # Return max consecutive occurrences of target\n    max_streak = current = 0\n    for val in values:\n        if val == target:\n            current += 1\n            if current > max_streak:\n                max_streak = current\n        else:\n            current = 0\n    return max_streak\n",
        "example": {
            "call": "longest_streak([1, 1, 0, 1, 1, 1, 0], 1)",
            "expected": "3",
            "explanation": "The longest contiguous run of 1s has length 3."
        },
        "visibleTests": [
            {"call": "longest_streak([1, 1, 0, 1, 1, 1, 0], 1)", "expected": "3"},
            {"call": "longest_streak([0, 0, 0], 1)", "expected": "0"},
            {"call": "longest_streak(['a', 'a', 'b', 'a'], 'a')", "expected": "2"}
        ],
        "hiddenTests": [
            {"call": "longest_streak([1, 2, 2, 2, 2, 1], 2)", "expected": "4"},
            {"call": "longest_streak([], 5)", "expected": "0"},
            {"call": "longest_streak([7, 7, 7, 7], 7)", "expected": "4"},
            {"call": "longest_streak([1, 0, 1, 0], 1)", "expected": "1"},
            {"call": "longest_streak([4, 5, 6], 10)", "expected": "0"}
        ],
        "hints": [
            "Keep two tracking variables: `current_streak` and `max_streak`.",
            "When `val == target`, increment `current_streak` and update `max_streak = max(max_streak, current_streak)`.",
            "When `val != target`, reset `current_streak = 0`.",
            "After checking all elements, return `max_streak`."
        ]
    }
]

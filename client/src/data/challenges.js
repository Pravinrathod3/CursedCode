export const CHALLENGES = [
  {
    id: 'last-k-total',
    title: 'Last K Total',
    description: 'Return the total of the final k values in a list of numbers.',
    statement: 'Write a function named `last_k_total(numbers, k)` that takes a list of integers `numbers` and an integer `k`. It returns the sum of the last `k` integers in the list. If `k` is 0, return 0.',
    grade: 'Grade 4',
    difficulty: 'Easy',
    tags: ['Lists', 'Slicing'],
    status: 'New',
    estimatedTime: '10 min',
    starterCode: `def last_k_total(numbers, k):
    # Return the total of the last k values in numbers.
    if k == 0:
        return 0
    return sum(numbers[-k:])
`,
    example: {
      call: 'last_k_total([3, 8, 2, 5], 2)',
      expected: '7',
      explanation: 'The last 2 elements are 2 and 5. Their sum is 7.'
    },
    visibleTests: [
      { test: 1, call: 'last_k_total([3, 8, 2, 5], 2)', expected: '7' },
      { test: 2, call: 'last_k_total([10, 20, 30], 1)', expected: '30' },
      { test: 3, call: 'last_k_total([4, 6, 8], 0)', expected: '0' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'countpasses',
    title: 'Count Passes',
    description: 'Count the number of test scores that are 40 or more.',
    statement: 'Write a function named `count_passes(marks)` that takes a list of integer `marks` and returns how many of them are 40 or more.',
    grade: 'Grade 4',
    difficulty: 'Easy',
    tags: ['Loops', 'Comparison'],
    status: 'Attempted',
    estimatedTime: '10 min',
    starterCode: `def count_passes(marks):
    # Count marks that are 40 or more
    count = 0
    for mark in marks:
        if mark >= 40:
            count += 1
    return count
`,
    example: {
      call: 'count_passes([30, 40, 50])',
      expected: '2',
      explanation: 'Marks 40 and 50 are 40 or more, so the count is 2.'
    },
    visibleTests: [
      { test: 1, call: 'count_passes([30, 40, 50])', expected: '2' },
      { test: 2, call: 'count_passes([10, 20, 30])', expected: '0' },
      { test: 3, call: 'count_passes([40, 40, 40])', expected: '3' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'first-n-squares',
    title: 'First N Squares',
    description: 'Build and return a list containing the squares of numbers from 1 through n.',
    statement: 'Write a function named `first_n_squares(n)` that receives a positive integer `n` and returns a list containing the squares of integers from 1 up to and including `n` in ascending order.',
    grade: 'Grade 4',
    difficulty: 'Easy',
    tags: ['Loops', 'Lists'],
    status: 'Solved',
    estimatedTime: '10 min',
    starterCode: `def first_n_squares(n):
    # Build list of squares from 1 up to n
    return [i * i for i in range(1, n + 1)]
`,
    example: {
      call: 'first_n_squares(4)',
      expected: '[1, 4, 9, 16]',
      explanation: 'The first 4 positive integers squared are 1, 4, 9, and 16.'
    },
    visibleTests: [
      { test: 1, call: 'first_n_squares(4)', expected: '[1, 4, 9, 16]' },
      { test: 2, call: 'first_n_squares(1)', expected: '[1]' },
      { test: 3, call: 'first_n_squares(0)', expected: '[]' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'middlethree',
    title: 'Middle Three',
    description: 'Extract and return the middle three items from an odd-length sequence.',
    statement: 'Write a function named `middle_three(items)` that receives an odd-length list with at least 3 elements. Return a new list containing the exact 3 items situated at the center of the list.',
    grade: 'Grade 3',
    difficulty: 'Medium',
    tags: ['Lists', 'Indexing'],
    status: 'New',
    estimatedTime: '15 min',
    starterCode: `def middle_three(items):
    # Return the three middle items of an odd-length list
    mid = len(items) // 2
    return items[mid - 1 : mid + 2]
`,
    example: {
      call: 'middle_three([1, 2, 3, 4, 5])',
      expected: '[2, 3, 4]',
      explanation: 'The center element is 3. The middle 3 items are 2, 3, 4.'
    },
    visibleTests: [
      { test: 1, call: 'middle_three([1, 2, 3, 4, 5])', expected: '[2, 3, 4]' },
      { test: 2, call: 'middle_three(["a", "b", "c"])', expected: "['a', 'b', 'c']" },
      { test: 3, call: 'middle_three([10, 20, 30, 40, 50, 60, 70])', expected: '[30, 40, 50]' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'word-boundary',
    title: 'Word Boundary',
    description: 'Determine whether a sentence starts or ends with a specific target keyword.',
    statement: 'Write a function named `is_at_boundary(sentence, keyword)` that checks if the given `sentence` either begins with or concludes with the exact string `keyword` (case-sensitive).',
    grade: 'Grade 3',
    difficulty: 'Medium',
    tags: ['Strings', 'Comparison'],
    status: 'New',
    estimatedTime: '15 min',
    starterCode: `def is_at_boundary(sentence, keyword):
    # Check if sentence starts or ends with keyword
    return sentence.startswith(keyword) or sentence.endswith(keyword)
`,
    example: {
      call: 'is_at_boundary("curse energy flows", "curse")',
      expected: 'True',
      explanation: 'The sentence starts with "curse".'
    },
    visibleTests: [
      { test: 1, call: 'is_at_boundary("curse energy flows", "curse")', expected: 'True' },
      { test: 2, call: 'is_at_boundary("the quiet realm", "realm")', expected: 'True' },
      { test: 3, call: 'is_at_boundary("inside the barrier now", "barrier")', expected: 'False' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'pair-sum',
    title: 'Pair Sum',
    description: 'Find two distinct numbers in an array whose sum equals the specified target value.',
    statement: 'Write a function named `has_pair_sum(numbers, target)` that returns `True` if any two distinct entries in the list `numbers` sum to `target`, otherwise `False`.',
    grade: 'Grade 3',
    difficulty: 'Medium',
    tags: ['Loops', 'Lists'],
    status: 'Attempted',
    estimatedTime: '20 min',
    starterCode: `def has_pair_sum(numbers, target):
    # Return True if two numbers sum to target
    seen = set()
    for num in numbers:
        if (target - num) in seen:
            return True
        seen.add(num)
    return False
`,
    example: {
      call: 'has_pair_sum([2, 7, 11, 15], 9)',
      expected: 'True',
      explanation: '2 + 7 equals 9.'
    },
    visibleTests: [
      { test: 1, call: 'has_pair_sum([2, 7, 11, 15], 9)', expected: 'True' },
      { test: 2, call: 'has_pair_sum([3, 5, 1], 10)', expected: 'False' },
      { test: 3, call: 'has_pair_sum([5], 10)', expected: 'False' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'mirror-check',
    title: 'Mirror Check',
    description: 'Verify if a string reads the same forwards and backwards, ignoring case.',
    statement: 'Write a function named `is_mirror(text)` that returns `True` if `text` is a palindrome when comparing lowercase characters only, otherwise `False`.',
    grade: 'Grade 3',
    difficulty: 'Medium',
    tags: ['Strings', 'Indexing'],
    status: 'New',
    estimatedTime: '15 min',
    starterCode: `def is_mirror(text):
    # Check if text is a palindrome, case-insensitive
    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]
`,
    example: {
      call: 'is_mirror("Level")',
      expected: 'True',
      explanation: '"level" reads identically in reverse.'
    },
    visibleTests: [
      { test: 1, call: 'is_mirror("Level")', expected: 'True' },
      { test: 2, call: 'is_mirror("sorcery")', expected: 'False' },
      { test: 3, call: 'is_mirror("A man a plan a canal Panama")', expected: 'True' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'common-start',
    title: 'Common Start',
    description: 'Identify the longest common starting prefix shared across a list of strings.',
    statement: 'Write a function named `common_start(words)` that returns the longest string prefix shared by every word in the given list. If there is no common prefix, return `""`.',
    grade: 'Grade 2',
    difficulty: 'Hard',
    tags: ['Strings', 'Loops'],
    status: 'New',
    estimatedTime: '25 min',
    starterCode: `def common_start(words):
    # Find longest shared prefix
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        while not word.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix
`,
    example: {
      call: 'common_start(["domain", "domino", "domestic"])',
      expected: '"dom"',
      explanation: 'All three words start with "dom".'
    },
    visibleTests: [
      { test: 1, call: 'common_start(["domain", "domino", "domestic"])', expected: '"dom"' },
      { test: 2, call: 'common_start(["flash", "spark", "bolt"])', expected: '""' },
      { test: 3, call: 'common_start(["curse", "cursed", "curiosity"])', expected: '"cur"' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'missing-step',
    title: 'Missing Step',
    description: 'Find the single missing value in an otherwise contiguous arithmetic progression.',
    statement: 'Write a function named `find_missing_step(sequence)` that receives an arithmetic sequence of numbers where one number is missing. Return that missing number.',
    grade: 'Grade 2',
    difficulty: 'Hard',
    tags: ['Lists', 'Comparison'],
    status: 'New',
    estimatedTime: '20 min',
    starterCode: `def find_missing_step(sequence):
    # Find the missing element in arithmetic sequence
    n = len(sequence)
    diff = (sequence[-1] - sequence[0]) // n
    for i in range(n - 1):
        if sequence[i + 1] - sequence[i] != diff:
            return sequence[i] + diff
    return sequence[0]
`,
    example: {
      call: 'find_missing_step([2, 4, 8, 10])',
      expected: '6',
      explanation: 'The common difference is 2; 6 is the missing step.'
    },
    visibleTests: [
      { test: 1, call: 'find_missing_step([2, 4, 8, 10])', expected: '6' },
      { test: 2, call: 'find_missing_step([10, 7, 1])', expected: '4' },
      { test: 3, call: 'find_missing_step([1, 3, 5, 9])', expected: '7' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'balanced-brackets',
    title: 'Balanced Brackets',
    description: 'Check whether all brackets in a string have matching and correctly nested closers.',
    statement: 'Write a function named `is_balanced(expr)` that returns `True` if all parentheses `()`, square brackets `[]`, and curly braces `{}` are correctly paired and nested.',
    grade: 'Grade 2',
    difficulty: 'Hard',
    tags: ['Strings', 'Loops'],
    status: 'New',
    estimatedTime: '25 min',
    starterCode: `def is_balanced(expr):
    # Check if brackets are balanced and properly nested
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for ch in expr:
        if ch in pairs.values():
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return len(stack) == 0
`,
    example: {
      call: 'is_balanced("{[()]}()")',
      expected: 'True',
      explanation: 'All brackets are properly closed in correct order.'
    },
    visibleTests: [
      { test: 1, call: 'is_balanced("{[()]}()")', expected: 'True' },
      { test: 2, call: 'is_balanced("([)]")', expected: 'False' },
      { test: 3, call: 'is_balanced("({[")}', expected: 'False' }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'frequency-count',
    title: 'Character Frequency',
    description: 'Count occurrences of each unique character and return character counts.',
    statement: 'Write a function named `char_frequency(text)` that returns a dictionary mapping each distinct lowercase character in `text` to its total frequency count. Ignore spaces.',
    grade: 'Grade 3',
    difficulty: 'Medium',
    tags: ['Strings', 'Lists'],
    status: 'Solved',
    estimatedTime: '15 min',
    starterCode: `def char_frequency(text):
    # Return count of each character, excluding whitespace
    freq = {}
    for ch in text.lower():
        if not ch.isspace():
            freq[ch] = freq.get(ch, 0) + 1
    return freq
`,
    example: {
      call: 'char_frequency("seal")',
      expected: "{'s': 1, 'e': 1, 'a': 1, 'l': 1}",
      explanation: 'Each character appears once.'
    },
    visibleTests: [
      { test: 1, call: 'char_frequency("seal")', expected: "{'s': 1, 'e': 1, 'a': 1, 'l': 1}" },
      { test: 2, call: 'char_frequency("banana")', expected: "{'b': 1, 'a': 3, 'n': 2}" },
      { test: 3, call: 'char_frequency("a a")', expected: "{'a': 2}" }
    ],
    hiddenTestCount: 5
  },
  {
    id: 'streak-counter',
    title: 'Longest Streak',
    description: 'Calculate the maximum length of consecutive true or matching conditions in a list.',
    statement: 'Write a function named `longest_streak(values, target)` that returns the maximum number of consecutive times `target` appears in the sequence `values`.',
    grade: 'Grade 4',
    difficulty: 'Easy',
    tags: ['Loops', 'Comparison'],
    status: 'New',
    estimatedTime: '10 min',
    starterCode: `def longest_streak(values, target):
    # Return max consecutive occurrences of target
    max_streak = current = 0
    for val in values:
        if val == target:
            current += 1
            if current > max_streak:
                max_streak = current
        else:
            current = 0
    return max_streak
`,
    example: {
      call: 'longest_streak([1, 1, 0, 1, 1, 1, 0], 1)',
      expected: '3',
      explanation: 'The longest contiguous run of 1s has length 3.'
    },
    visibleTests: [
      { test: 1, call: 'longest_streak([1, 1, 0, 1, 1, 1, 0], 1)', expected: '3' },
      { test: 2, call: 'longest_streak([0, 0, 0], 1)', expected: '0' },
      { test: 3, call: 'longest_streak(["a", "a", "b", "a"], "a")', expected: '2' }
    ],
    hiddenTestCount: 5
  }
];

export const GRADE_SCALE = [
  { grade: 'Grade 4', difficulty: 'Easy', order: 1 },
  { grade: 'Grade 3', difficulty: 'Medium', order: 2 },
  { grade: 'Grade 2', difficulty: 'Hard', order: 3 },
  { grade: 'Semi-Grade 1', difficulty: 'Advanced', order: 4 },
  { grade: 'Grade 1', difficulty: 'Expert', order: 5 },
  { grade: 'Special Grade', difficulty: 'Master', order: 6 }
];

export const CONCEPTS = [
  'Lists',
  'Loops',
  'Strings',
  'Slicing',
  'Indexing',
  'Comparison'
];

export const STATUSES = [
  'New',
  'Attempted',
  'Solved'
];

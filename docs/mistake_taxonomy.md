# Debug Dojo — Mistake Taxonomy & Detection Specification

Per the **DI-01 Problem Statement (Requirement 7)**, every failed submission is analyzed and tagged with distinct mistake categories. A mistake category is marked as **recurring** when it is detected across at least 2 distinct challenges for a learner.

---

## The 5 Core Categories & Detection Logic

### 1. `off_by_one`
* **Description**: The loop boundary or slice index misses by $\pm 1$ element (e.g. `range(len(arr) - 1)` or `range(1, n)` instead of `range(1, n + 1)`).
* **Detection Rule**:
  - The submission passes all tests with $k=0$ or mid-range inputs, but consistently fails the exact boundary element test (e.g., last element missing or extra iteration).
  - AST inspection reveals `range(...)` or slice expressions differing by 1 from the required length/upper bound.

### 2. `unhandled_short_input`
* **Description**: Code crashes (`IndexError`) or calculates incorrect output on empty lists (`[]`), single-element lists, or cases where parameter $k$ exceeds list length ($k > \text{len}(\text{numbers})$).
* **Detection Rule**:
  - Code passes standard length inputs ($N \ge 3$), but fails on inputs with $N = 0, 1$ or $k > N$.
  - Traces indicate unhandled `IndexError` or negative slice index overflows (e.g. `len(marks) - k` going negative).

### 3. `print_not_return`
* **Description**: The student uses `print(...)` inside the function rather than `return ...`, resulting in the caller receiving `None`.
* **Detection Rule**:
  - The function execution outcome is `wrong_output` with `got: None` or `"None"`.
  - The AST of the function contains `ast.Print` or `ast.Call` to `print`, and does not have a non-empty `ast.Return`.

### 4. `boundary_comparison`
* **Description**: Comparison operator error at strict vs non-strict thresholds (e.g. using `<` instead of `≤`, or `>` instead of `≥`).
* **Detection Rule**:
  - The solution passes tests with values strictly above or below the threshold, but fails specifically on test cases where input values equal the threshold value (e.g. `passing_mark = 40` with score `40`).

### 5. `mutates_input`
* **Description**: The function modifies the input arguments in-place (`list.pop()`, `list.sort()`, `list.reverse()`, or `list[i] = ...`) when a pure function is expected, corrupting subsequent assertions.
* **Detection Rule**:
  - Pre-execution copy of input is compared with post-execution state: `deepcopy(input) != input`.
  - AST detection of mutating methods (`.append()`, `.pop()`, `.sort()`, `.extend()`).

---

## Recurring Mistake Progression
* When a mistake tag appears across $\ge 2$ different challenges, it is flagged as **recurring** in the learner profile (`GET /api/learner/{learner_id}`).
* The recommendation engine automatically dispatches the next challenge that exercises that specific concept and weakness.

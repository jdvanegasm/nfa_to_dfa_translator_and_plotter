# NFA Plotter – NFA to DFA Translator

Desktop Python application for:

1. entering a regular expression over the alphabet `{0,1}`
2. constructing an NFA using Thompson’s algorithm
3. converting that NFA into a DFA using the subset construction method
4. visualizing the step-by-step process and the generated automata

## Scope

The project supports regular expressions with:

- symbols `0` and `1`
- union `|`
- implicit concatenation
- Kleene star `*`
- grouping with parentheses `(` `)`

## Stack

- Python
- Poetry
- PySide6
- Graphviz
- pdoc
- pytest

## General Structure

```text
src/nfa_plotter/
├── algorithms/
├── domain/
├── gui/
├── regex/
├── visualization/
├── main.py
└── __main__.py
```

## Installation

### System Dependency

Install Graphviz on Linux:

```bash
sudo apt update
sudo apt install -y graphviz
```

### Project Dependencies

```bash
poetry install
```

## Run

```bash
poetry run python -m nfa_plotter
```

## Running Tests

```bash
poetry run pytest
```

## Documentation Generation

```bash
poetry run pdoc ./src/nfa_plotter -o ./docs/site
```

## Usage Flow

1. enter a regular expression
    
2. validate and parse it
    
3. generate the NFA
    
4. convert NFA → DFA
    
5. review the subset construction table
    
6. review the state mapping `K0`, `K1`, `K2`, ...
    
7. visualize the final DFA
    

## Constraints

- the alphabet is limited to `{0,1}`
    
- user input is textual, not manual drawing
    
- the NFA → DFA conversion is implemented from scratch
    
- the graphical interface is used only for input, visualization, and process explanation

---

# Manual Test Plan

## Objective

Verify that the software:

- correctly validates regular expressions
- builds the corresponding NFA
- correctly converts the NFA into a DFA
- displays the step-by-step subset construction method
- renders both automata without errors

## Test Cases

### Case 1: Simple symbol

**Input:** `0`

**Expected result:**

- valid regex
- NFA with 2 states
- DFA generated correctly
- table with transitions for `0` and `1`
- appearance of a sink state

---

### Case 2: Simple concatenation

**Input:** `01`

**Expected result:**

- valid regex
- normalization to `0.1`
- correct postfix form
- NFA with sequential transition
- equivalent DFA without errors

---

### Case 3: Union

**Input:** `0|1`

**Expected result:**

- valid regex
- NFA with epsilon transitions for union
- DFA with deterministic transitions
- at least one accepting state

---

### Case 4: Kleene star

**Input:** `(0|1)*`

**Expected result:**

- valid regex
- NFA with epsilon cycles
- DFA generated correctly
- accepting initial state

---

### Case 5: Composite expression

**Input:** `(0|010)*`

**Expected result:**

- valid regex
- correct NFA construction
- subset construction table visible
- state mapping `K0`, `K1`, `K2`, ...
- final DFA rendered

---

### Case 6: Error due to initial operator

**Input:** `|0`

**Expected result:**

- invalid regex
- visible error message
- no NFA or DFA should be generated

---

### Case 7: Error due to empty parentheses

**Input:** `()`

**Expected result:**

- invalid regex
- visible error message
- table and images cleared

---

### Case 8: Error due to double operator

**Input:** `0||1`

**Expected result:**

- invalid regex
- clear error message
- previous results should not be displayed

## Acceptance Criteria

The software is considered correct if:

1. valid expressions generate NFAs and DFAs without exceptions
2. invalid expressions display clear error messages
3. the DFA contains deterministic transitions
4. the subset construction table matches the observed behavior
5. the visualizations correspond to the textual summary
# CompilerDesign_grammar-to-ll1-parser-generator
A web-based Compiler Design project that automates the conversion of a Context-Free Grammar (CFG) into an LL(1) predictive parser.

## 📌 Project Overview

The **Grammar to LL(1) Parser Generator** provides an interactive way to analyze a Context-Free Grammar and generate the components required for LL(1) predictive parsing.

The system performs grammar transformations, computes FIRST and FOLLOW sets, constructs the LL(1) parsing table, detects conflicts, and demonstrates the predictive parsing process for a user-provided input string.

## 🎯 Objectives

- Convert a Context-Free Grammar into an LL(1) predictive parser.
- Eliminate left recursion.
- Perform left factoring.
- Compute FIRST and FOLLOW sets.
- Generate the LL(1) parsing table.
- Detect conflicts in the parsing table.
- Demonstrate predictive parsing using a user-provided input string.
- Display the parsing process in an interactive manner.

## ⚙️ System Workflow

```text
Context-Free Grammar
        ↓
Grammar Analysis
        ↓
Left Recursion Elimination
        ↓
Left Factoring
        ↓
FIRST Set Computation
        ↓
FOLLOW Set Computation
        ↓
LL(1) Parsing Table
        ↓
Conflict Detection
        ↓
Input String
        ↓
Predictive Parsing
        ↓
Accepted / Rejected

import streamlit as st
from collections import defaultdict

EPS = "ε"
END = "$"

def parse_grammar(text):
    grammar = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or "->" not in line:
            continue
        lhs, rhs = line.split("->", 1)
        lhs = lhs.strip()
        alternatives = [a.strip() for a in rhs.split("|")]
        grammar[lhs] = []
        for alt in alternatives:
            if alt in ("", "epsilon", "ε"):
                grammar[lhs].append([EPS])
            else:
                # Supports space-separated symbols; also recognizes common compact forms.
                grammar[lhs].append(alt.split())
    return grammar

def fresh_name(base, grammar):
    name = base + "'"
    while name in grammar:
        name += "'"
    return name

def eliminate_left_recursion(grammar):
    g = {k: [p[:] for p in v] for k, v in grammar.items()}
    nts = list(g.keys())

    for i, A in enumerate(nts):
        # Substitute earlier nonterminals.
        new_prods = []
        for prod in g[A]:
            if prod and prod[0] in nts[:i]:
                B = prod[0]
                for bprod in g[B]:
                    if bprod == [EPS]:
                        new_prods.append(prod[1:] or [EPS])
                    else:
                        new_prods.append(bprod + prod[1:])
            else:
                new_prods.append(prod)
        g[A] = new_prods

        alpha, beta = [], []
        for prod in g[A]:
            if prod and prod[0] == A:
                alpha.append(prod[1:])
            else:
                beta.append(prod)

        if alpha:
            Aprime = fresh_name(A, g)
            g[A] = []
            for b in beta:
                g[A].append(([EPS] if b == [EPS] else b) + [Aprime])
            g[Aprime] = [a + [Aprime] for a in alpha] + [[EPS]]
            nts.insert(i + 1, Aprime)
    return g

def left_factor(grammar):
    g = {k: [p[:] for p in v] for k, v in grammar.items()}
    changed = True
    while changed:
        changed = False
        for A in list(g.keys()):
            prods = g[A]
            groups = defaultdict(list)
            for p in prods:
                if p != [EPS]:
                    groups[p[0]].append(p)
            target = next((k for k, v in groups.items() if len(v) > 1), None)
            if target is None:
                continue
            candidates = groups[target]
            prefix = candidates[0][:]
            for p in candidates[1:]:
                j = 0
                while j < len(prefix) and j < len(p) and prefix[j] == p[j]:
                    j += 1
                prefix = prefix[:j]
            if not prefix:
                continue
            Aprime = fresh_name(A, g)
            remaining = [p for p in prods if p not in candidates]
            remaining.append(prefix + [Aprime])
            g[A] = remaining
            suffixes = []
            for p in candidates:
                suffixes.append(p[len(prefix):] or [EPS])
            g[Aprime] = suffixes
            changed = True
            break
    return g

def first_of_sequence(seq, first):
    result = set()
    nullable = True
    for sym in seq:
        if sym == EPS:
            result.add(EPS)
            continue
        if sym not in first:
            result.add(sym)
            nullable = False
            break
        result |= (first[sym] - {EPS})
        if EPS not in first[sym]:
            nullable = False
            break
    if nullable:
        result.add(EPS)
    return result

def compute_first(grammar):
    nts = set(grammar)
    first = {A: set() for A in nts}
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                before = len(first[A])
                first[A] |= first_of_sequence(prod, first)
                if len(first[A]) > before:
                    changed = True
    return first

def compute_follow(grammar, first):
    nts = set(grammar)
    follow = {A: set() for A in nts}
    start = next(iter(grammar))
    follow[start].add(END)
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                for i, B in enumerate(prod):
                    if B not in nts:
                        continue
                    beta = prod[i+1:]
                    fb = first_of_sequence(beta, first) if beta else {EPS}
                    before = len(follow[B])
                    follow[B] |= (fb - {EPS})
                    if EPS in fb:
                        follow[B] |= follow[A]
                    if len(follow[B]) > before:
                        changed = True
    return follow

def build_table(grammar, first, follow):
    table = {}
    conflicts = []
    for A, prods in grammar.items():
        for prod in prods:
            f = first_of_sequence(prod, first)
            targets = f - {EPS}
            if EPS in f:
                targets |= follow[A]
            for t in targets:
                key = (A, t)
                if key in table and table[key] != prod:
                    conflicts.append((A, t, table[key], prod))
                else:
                    table[key] = prod
    return table, conflicts

def symbols(grammar):
    nts = set(grammar)
    ts = set()
    for prods in grammar.values():
        for p in prods:
            ts.update(x for x in p if x not in nts and x != EPS)
    return ts

def parse_input(grammar, table, text):
    tokens = text.strip().split() if text.strip() else []
    tokens.append(END)
    stack = [END, next(iter(grammar))]
    i = 0
    steps = []
    while stack:
        top = stack[-1]
        current = tokens[i] if i < len(tokens) else END
        steps.append((" ".join(stack), " ".join(tokens[i:]), ""))
        if top == current == END:
            steps[-1] = (steps[-1][0], steps[-1][1], "ACCEPT")
            return steps, True
        if top not in grammar:
            if top == current:
                stack.pop()
                i += 1
                steps[-1] = (steps[-1][0], steps[-1][1], f"Match {current}")
            else:
                steps[-1] = (steps[-1][0], steps[-1][1], f"ERROR: expected {top}")
                return steps, False
        else:
            prod = table.get((top, current))
            if prod is None:
                steps[-1] = (steps[-1][0], steps[-1][1], f"ERROR: no rule for ({top}, {current})")
                return steps, False
            stack.pop()
            if prod != [EPS]:
                for s in reversed(prod):
                    stack.append(s)
            steps[-1] = (steps[-1][0], steps[-1][1], f"{top} → {' '.join(prod)}")
    return steps, False

def grammar_text(g):
    return "\n".join(f"{A} -> " + " | ".join(" ".join(p) for p in prods) for A, prods in g.items())

st.set_page_config(page_title="Grammar to LL(1) Parser Generator", page_icon="🔤", layout="wide")
st.title("🔤 Grammar to LL(1) Parser Generator")
st.caption("CFG → Grammar Transformation → FIRST/FOLLOW → LL(1) Table → Predictive Parsing")

default = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""

grammar_input = st.text_area("Enter Context-Free Grammar", default, height=170,
                             help="Use spaces between symbols. Example: E -> E + T | T")

if st.button("🚀 Generate LL(1) Parser", type="primary"):
    try:
        original = parse_grammar(grammar_input)
        if not original:
            st.error("Please enter a valid grammar.")
            st.stop()

        transformed = eliminate_left_recursion(original)
        transformed = left_factor(transformed)
        first = compute_first(transformed)
        follow = compute_follow(transformed, first)
        table, conflicts = build_table(transformed, first, follow)

        st.session_state.data = (transformed, first, follow, table, conflicts)
    except Exception as e:
        st.error(f"Could not process grammar: {e}")

if "data" in st.session_state:
    transformed, first, follow, table, conflicts = st.session_state.data

    st.subheader("1. Transformed Grammar")
    st.code(grammar_text(transformed))

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("2. FIRST Sets")
        for A in transformed:
            st.write(f"**FIRST({A})** = {{ {', '.join(sorted(first[A]))} }}")
    with c2:
        st.subheader("3. FOLLOW Sets")
        for A in transformed:
            st.write(f"**FOLLOW({A})** = {{ {', '.join(sorted(follow[A]))} }}")

    st.subheader("4. LL(1) Parsing Table")
    terms = sorted(symbols(transformed) | {END})
    header = ["Non-Terminal"] + terms
    rows = []
    for A in transformed:
        row = [A]
        for t in terms:
            p = table.get((A, t))
            row.append(f"{A} → {' '.join(p)}" if p else "")
        rows.append(row)
    st.table([header] + rows)

    if conflicts:
        st.error("⚠️ Grammar has LL(1) conflicts.")
        for A, t, p1, p2 in conflicts:
            st.write(f"Conflict at ({A}, {t}): {' '.join(p1)} / {' '.join(p2)}")
    else:
        st.success("✅ No LL(1) conflicts detected.")

    st.subheader("5. Predictive Parsing")
    input_text = st.text_input("Enter input string (space-separated)", "id + id * id")
    if st.button("▶ Parse Input"):
        steps, accepted = parse_input(transformed, table, input_text)
        st.dataframe(
            [{"Step": i+1, "Stack": s, "Input": inp, "Action": act}
             for i, (s, inp, act) in enumerate(steps)],
            use_container_width=True,
            hide_index=True
        )
        if accepted:
            st.success("🎉 Input ACCEPTED")
        else:
            st.error("❌ Input REJECTED")

"""2. feladat: véges automata determinizálása (részhalmaz-konstrukció).

Ezt a fájlt a python-starter/project/problems/ mappába kell tenni.
"""
import argparse
import sys

from project.problem import Problem


class AutomatonError(Exception):
    pass


def parse_automaton(text):
    lines = [l.rstrip("\r") for l in text.split("\n")]
    if len(lines) < 4:
        raise AutomatonError("A bemenet legalább 4 sort kell tartalmazzon.")

    states = lines[0].split()
    alphabet = lines[1].split()
    start_list = lines[2].split()
    finals = lines[3].split()

    if len(start_list) != 1:
        raise AutomatonError("Pontosan egy kezdőállapotnak kell szerepelnie.")
    start = start_list[0]
    state_set = set(states)
    alpha_set = set(alphabet)

    if start not in state_set:
        raise AutomatonError(f"Ismeretlen kezdőállapot: {start}")
    for f in finals:
        if f not in state_set:
            raise AutomatonError(f"Ismeretlen végállapot: {f}")

    delta = {}
    for no, line in enumerate(lines[4:], start=5):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 3:
            raise AutomatonError(f"Hibás átmenet a(z) {no}. sorban: '{line}'")
        src, sym, dst = parts
        if src not in state_set:
            raise AutomatonError(f"Ismeretlen állapot a(z) {no}. sorban: {src}")
        if sym not in alpha_set:
            raise AutomatonError(f"Ismeretlen jel a(z) {no}. sorban: {sym}")
        if dst not in state_set:
            raise AutomatonError(f"Ismeretlen állapot a(z) {no}. sorban: {dst}")
        delta.setdefault((src, sym), set()).add(dst)

    return states, alphabet, start, set(finals), delta


def determinize(alphabet, start, finals, delta):
    start_set = frozenset([start])
    ids = {start_set: 0}
    order = [start_set]
    transitions = []
    symbols = sorted(set(alphabet))

    i = 0
    while i < len(order):
        cur = order[i]
        for sym in symbols:
            target = frozenset(t for q in cur for t in delta.get((q, sym), ()))
            if not target:
                continue
            if target not in ids:
                ids[target] = len(order)
                order.append(target)
            transitions.append((i, sym, ids[target]))
        i += 1

    new_finals = [k for k, s in enumerate(order) if s & finals]
    transitions.sort(key=lambda t: (t[0], t[1], t[2]))
    return len(order), new_finals, transitions


def format_output(alphabet, n, new_finals, transitions):
    out = [
        " ".join(f"s{i}" for i in range(n)),
        " ".join(alphabet),
        "s0",
        " ".join(f"s{i}" for i in new_finals),
    ]
    out += [f"s{a} {sym} s{b}" for a, sym, b in transitions]
    return "\n".join(out) + "\n"


class Determinize(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        # Az --input és --output már fel van véve a Main osztályban.
        parser.add_argument('--det', action='store_true',
                            help='determinize the automaton')

    def is_chosen_problem(self, args):
        return bool(getattr(args, 'det', False))

    def run(self, args):
        if not args.input or not args.output:
            print("Hiba: az --input és --output megadása kötelező.",
                  file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input, encoding="utf-8") as f:
                text = f.read()
            _states, alphabet, start, finals, delta = parse_automaton(text)
            n, new_finals, transitions = determinize(alphabet, start, finals, delta)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(format_output(alphabet, n, new_finals, transitions))
        except (AutomatonError, OSError) as e:
            print(f"Hiba: {e}", file=sys.stderr)
            sys.exit(1)
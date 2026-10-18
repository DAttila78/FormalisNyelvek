"""1. feladat: determinisztikus véges automata (DFA) szimulációja.

Ezt a fájlt a python-starter/project/problems/ mappába kell tenni.
Használat: python -m project --input <fájl> --output <fájl> --check szo1,szo2,...
"""
import argparse
import sys

from project.problem import Problem


def load_dfa(path):
    """Beolvassa a DFA-t: (kezdőállapot, végállapotok, átmenettábla)."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    # A 4 fejlécsor pozíció szerint számít (a végállapot-sor lehet üres is).
    while len(lines) < 4:
        lines.append("")

    start = lines[2].strip()
    finals = set(lines[3].split())

    delta = {}
    for line in lines[4:]:
        parts = line.split()
        if len(parts) != 3:
            continue
        src, sym, dst = parts
        delta[(src, sym)] = dst
    return start, finals, delta


def accepts(start, finals, delta, word):
    state = start
    for ch in word:
        state = delta.get((state, ch))
        if state is None:  # nincs átmenet (vagy ismeretlen jel) -> elutasít
            return False
    return state in finals


class CheckProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        # Az --input és --output már fel van véve a Main osztályban.
        if '--check' not in parser._option_string_actions:
            parser.add_argument('--check', default=None,
                                help='comma separated words to check')

    def is_chosen_problem(self, args):
        return getattr(args, 'check', None) is not None

    def run(self, args):
        if not args.input or not args.output:
            print("Hiba: az --input és --output megadása kötelező.",
                  file=sys.stderr)
            sys.exit(1)
        try:
            start, finals, delta = load_dfa(args.input)
            words = args.check.split(',')
            results = ["IGEN" if accepts(start, finals, delta, w) else "NEM"
                       for w in words]
            with open(args.output, "w", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(results) + "\n")
        except OSError as e:
            print(f"Hiba: {e}", file=sys.stderr)
            sys.exit(1)
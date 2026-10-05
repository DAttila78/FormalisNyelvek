from project.problem import Problem
import argparse
import sys

# Beépített példák (a feladat PDF-jéből): ezeket futtatja a program,
# ha kapcsolók nélkül, csak "python -m project" paranccsal indítjuk.
DEMOS = [
    {
        "automaton": (
            "q0 q1 q2\n"
            "0 1\n"
            "q0\n"
            "q0\n"
            "q0 0 q2\nq0 1 q1\n"
            "q1 0 q2\nq1 1 q0\n"
            "q2 0 q1\nq2 1 q2\n"
        ),
        "words": ["10101", "111", "111110111010101", "001", "0021"],
    },
    {
        "automaton": (
            "q0 q1 q2\n"
            "a b\n"
            "q0\n"
            "q1 q2\n"
            "q0 a q1\nq1 a q1\nq1 b q2\nq2 b q2\n"
        ),
        "words": ["a", "aa", "abab", "bbb", "aaaaaaaaaaaab",
                  "aaaaabbbbb", "aaaabbbbba", "c"],
    },
    {
        "automaton": (
            "q0 q1 q2\n"
            "0 1 2\n"
            "q0\n"
            "q0\n"
            "q0 0 q0\nq0 1 q1\nq0 2 q2\n"
            "q1 0 q1\nq1 1 q2\nq1 2 q0\n"
            "q2 0 q2\nq2 1 q0\nq2 2 q1\n"
        ),
        "words": ["0", "1", "2", "12", "111", "0021", "102", "1122", "3", "210"],
    },
]


class DFAProblem(Problem):
    """1. feladat: determinisztikus véges automata (DFA) szimulációja."""

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument(
            '--check',
            help='comma separated words to check (e.g. a,ab,abc)'
        )

    def is_chosen_problem(self, args):
        """
        Chosen if --check is given, or if the program was started
        without any arguments (built-in demo mode).
        """
        return args.check is not None or len(sys.argv) == 1

    def run(self, args):
        """
        Run the program
        """
        if args.check is None:
            self.run_demo()
            return

        automaton = self.parse_automaton(self.read_file(args.input))
        results = self.check_words(automaton, args.check.split(','))
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))

    def run_demo(self):
        """
        No arguments: run the built-in automata, print results to the terminal
        """
        for i, demo in enumerate(DEMOS, start=1):
            automaton = self.parse_automaton(demo["automaton"])
            results = self.check_words(automaton, demo["words"])
            print(f"{i}. automata:")
            for word, result in zip(demo["words"], results):
                print(f"  {word:<18}{result}")

    @staticmethod
    def read_file(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            return f.read()

    @staticmethod
    def parse_automaton(text):
        """
        Parse: states, alphabet, start state, final states, transitions
        """
        lines = text.splitlines()
        # Az első négy sor fix helyen van (a végállapotok sora lehet üres is)
        while len(lines) < 4:
            lines.append("")

        alphabet = set(lines[1].split())
        start = lines[2].strip()
        finals = set(lines[3].split())

        transitions = {}  # {(állapot, jel): új állapot}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, symbol, dst = parts
                transitions[(src, symbol)] = dst
        return alphabet, start, finals, transitions

    @staticmethod
    def check_words(automaton, words):
        alphabet, start, finals, transitions = automaton
        results = []
        for word in words:
            state = start
            for ch in word:
                state = transitions.get((state, ch)) if ch in alphabet else None
                if state is None:
                    break
            results.append("IGEN" if state in finals else "NEM")
        return results
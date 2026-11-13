"""4. feladat: reguláris kifejezések egy Android logcat állományon.

A keresésekhez kizárólag reguláris kifejezéseket használunk.
"""
import argparse
import re
import sys

from project.problem import Problem

# A feladatleírásban megadott, egy logsort felbontó kifejezés.
#   1: teljes időbélyeg  2: dátum+idő  3: PID  4: TID
#   5: szint (I D V E F A W)  6: tag  7: üzenet (opcionális)
LOG_LINE = re.compile(
    r"(([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)"
)

NEWLINE = re.compile(r"\r?\n")

# 1. feladat: az alpontok kifejezései (soronként illesztve, a sor elejétől).
SUB_PATTERNS = [
    # 10. hónap 15-én létrejött sorok
    re.compile(r"10-15 "),
    # 10-15 10:18:51 -kor létrejött sorok
    re.compile(r"10-15 10:18:51\b"),
    # bármely 51. másodpercben létrejött sor (perc és óra mindegy)
    re.compile(r"[0-9-]+ [0-9]{2}:[0-9]{2}:51\b"),
    # lowmemorykiller tag
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] lowmemorykiller:"),
    # 10:18:51-kor keletkező, 221-es PID-ű sorok
    re.compile(r"[0-9-]+ 10:18:51\b[0-9.]* +221 +[0-9]+ [IDVEFAW] "),
    # hibák
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E "),
    # PackageManager warningok
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ W PackageManager:"),
    # ExoPlayer debug sorok
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ D [^:]*ExoPlayer[^:]*:"),
    # java állomány pozíciót tartalmazó hibák és warningok
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [EW] .*\.java:"),
    # Thread szó az üzenet részben (a tag után)
    re.compile(
        r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] [^:]+:(?: .*)?Thread"
    ),
]

# 2. feladat: Valami.java, ahogy a stack trace-ben szerepel.
JAVA_FILE = re.compile(r"([A-Za-z0-9_$-]+\.java):[0-9]+")


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    lines = NEWLINE.split(text)
    # a záró sortörés utáni üres elem nem sor
    if lines and not lines[-1]:
        lines.pop()
    return lines


def solve_1(lines):
    return [
        str(sum(1 for line in lines if pattern.match(line)))
        for pattern in SUB_PATTERNS
    ]


def solve_2(lines):
    """Minden hibasorból (és annak törzséből) kigyűjti a .java állományokat."""
    result = []
    in_error = False
    for line in lines:
        header = LOG_LINE.match(line)
        if header:
            in_error = header.group(5) == "E"
        elif not in_error:
            continue
        if in_error:
            result.extend(JAVA_FILE.findall(line))
    return result


def parse(lines):
    return [m for m in (LOG_LINE.match(line) for line in lines) if m]


def solve_3(lines):
    seen = {}
    for m in parse(lines):
        seen.setdefault(m.group(3), None)
    return list(seen)


def solve_4(lines):
    counts = {}
    for m in parse(lines):
        if m.group(5) == "E":
            counts[m.group(3)] = counts.get(m.group(3), 0) + 1
    if not counts:
        return []
    # döntetlennél az először előforduló PID nyer (a dict megőrzi a sorrendet)
    pid = max(counts, key=counts.get)
    return [f"PID={pid} ({counts[pid]} errors)"]


def solve_5(lines):
    return [str(sum(
        1 for m in parse(lines)
        if m.group(5) == "E" and m.group(3) == m.group(4)
    ))]


SOLVERS = {1: solve_1, 2: solve_2, 3: solve_3, 4: solve_4, 5: solve_5}


class Rgx(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--rgx', type=int, metavar='TASK',
                            help='regex task number (1-5)')

    def is_chosen_problem(self, args):
        return getattr(args, 'rgx', None) is not None

    def run(self, args):
        if not args.input or not args.output:
            print("Hiba: az --input és --output megadása kötelező.",
                  file=sys.stderr)
            sys.exit(1)
        solver = SOLVERS.get(args.rgx)
        if solver is None:
            print(f"Hiba: ismeretlen feladatszám: {args.rgx}", file=sys.stderr)
            sys.exit(1)
        try:
            lines = read_lines(args.input)
            result = solver(lines)
            with open(args.output, "w", encoding="utf-8", newline="\n") as f:
                f.write("".join(item + "\n" for item in result))
        except OSError as e:
            print(f"Hiba: {e}", file=sys.stderr)
            sys.exit(1)

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
    # 1. az összes sort, amelyik 10. hónap 15-én jött létre
    re.compile(r"(?:[0-9]{4}-)?10-15 "),
    # 2. az összes sort, amelyik 10. hónap 15-én 10 óra 18 perc és 51 másodperckor jött létre
    re.compile(r"(?:[0-9]{4}-)?10-15 10:18:51\b"),
    # 3. az összes sort, amelyik 51 másodperckor jött létre (mindegy a perc)
    re.compile(r"[0-9-]+ [0-9]{2}:[0-9]{2}:51\b"),
    # 4. az összes lowmemorykiller taget tartalmazó sor
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] lowmemorykiller:"),
    # 5. az összes 10:18:51 kor keletkező 221-es process id-jú sort
    re.compile(r"[0-9-]+ 10:18:51\b[0-9.]* +221 +[0-9]+ [IDVEFAW] "),
    # 6. az összes hibát tartalmazó sort (E)
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E "),
    # 7. az összes warningot (W) amit a PackageManager küld
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ W PackageManager:"),
    # 8. az összes ExoPlayer-es debug (D) infót
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ D .*ExoPlayer"),
    # 9. az összes java állomány pozíciót tartalmazó hibát és warningot (EW.java:)
    re.compile(r"[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [EW] .*\.java:"),
    # 10. az összes olyan sort, ami tartalmazza a Thread szót a message részben (nem a tagben)
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
    if lines and not lines[-1]:
        lines.pop()
    return lines


def _parse_logs_with_continuation(lines):
    """
    Segédfüggvény, amely kezeli a több soros logokat (pl. stack trace sorok,
    melyek nem kezdődnek új log headerrel), így a 2. feladat és a folytatólagos
    ellenőrzések pontosan illeszkednek.
    """
    parsed_entries = []
    current_entry = None

    for line in lines:
        match = LOG_LINE.match(line)
        if match:
            if current_entry:
                parsed_entries.append(current_entry)
            full_header, dt, pid, tid, level, tag, message = match.groups()
            current_entry = {
                'pid': pid,
                'tid': tid,
                'level': level,
                'tag': tag.strip(),
                'message': message if message else "",
                'raw': line,
                'continuation': []
            }
        else:
            if current_entry:
                current_entry['continuation'].append(line)
    
    if current_entry:
        parsed_entries.append(current_entry)
    return parsed_entries


def solve_1(lines):
    # Az 1. feladat pontról pontra soronként vizsgálja a SUB_PATTERNS elemeit
    return [
        str(sum(1 for line in lines if pattern.match(line)))
        for pattern in SUB_PATTERNS
    ]


def solve_2(lines):
    """Minden hibasorból (és a hozzá tartozó folytatósorokból/stack trace-ből) kigyűjti a .java állományokat."""
    entries = _parse_logs_with_continuation(lines)
    result = []
    for entry in entries:
        if entry['level'] == 'E':
            text_to_check = entry['message'] + ' ' + ' '.join(entry['continuation'])
            matches = JAVA_FILE.findall(text_to_check)
            result.extend(matches)
    return result


def parse(lines):
    return [m for m in (LOG_LINE.match(line) for line in lines) if m]


def solve_3(lines):
    # A 3. feladat az összes különböző PID-t kigyűri az előfordulási sorrendjükben
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
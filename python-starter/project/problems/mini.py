"""3. feladat: véges automata minimalizálása."""
import argparse
import sys

from project.problem import Problem


class AutomatonError(Exception):
    pass


def parse_automaton(text):
    lines = text.splitlines()
    if len(lines) < 4:
        raise AutomatonError("A bemenet legalább 4 sort kell tartalmazzon.")

    states = lines[0].split()
    alphabet = lines[1].split()
    start_list = lines[2].split()
    finals = lines[3].split()

    if not states:
        raise AutomatonError("Legalább egy állapotot meg kell adni.")
    if len(states) != len(set(states)):
        raise AutomatonError("Az állapotok között nem szerepelhet ismétlődés.")
    if len(alphabet) != len(set(alphabet)):
        raise AutomatonError("Az ábécé elemei között nem szerepelhet ismétlődés.")
    if len(start_list) != 1:
        raise AutomatonError("Pontosan egy kezdőállapotnak kell szerepelnie.")

    state_set = set(states)
    alpha_set = set(alphabet)
    start = start_list[0]
    if start not in state_set:
        raise AutomatonError(f"Ismeretlen kezdőállapot: {start}")
    for final in finals:
        if final not in state_set:
            raise AutomatonError(f"Ismeretlen végállapot: {final}")

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

        key = (src, sym)
        if key in delta and delta[key] != dst:
            raise AutomatonError(
                f"Nem determinisztikus átmenet a(z) {no}. sorban: {src} {sym}"
            )
        delta[key] = dst

    return states, alphabet, start, set(finals), delta


def minimize(states, alphabet, start, finals, delta):
    state_order = {state: index for index, state in enumerate(states)}
    reachable = []
    seen = {start}
    pending = [start]
    while pending:
        state = pending.pop()
        reachable.append(state)
        for symbol in alphabet:
            target = delta.get((state, symbol))
            if target is not None and target not in seen:
                seen.add(target)
                pending.append(target)
    reachable.sort(key=state_order.__getitem__)

    sink = object()
    partition_states = reachable + [sink]
    blocks = []
    final_block = [state for state in partition_states if state in finals]
    nonfinal_block = [state for state in partition_states if state not in finals]
    if final_block:
        blocks.append(final_block)
    if nonfinal_block:
        blocks.append(nonfinal_block)

    while True:
        block_for = {
            state: block_index
            for block_index, block in enumerate(blocks)
            for state in block
        }
        refined = []
        changed = False
        for block in blocks:
            groups = {}
            for state in block:
                signature = tuple(
                    block_for[
                        sink if state is sink
                        else delta.get((state, symbol), sink)
                    ]
                    for symbol in alphabet
                )
                groups.setdefault(signature, []).append(state)
            refined.extend(groups.values())
            changed |= len(groups) > 1
        blocks = refined
        if not changed:
            break

    state_block = {
        state: block_index
        for block_index, block in enumerate(blocks)
        for state in block
    }
    representatives = {
        state_block[state]: min(
            state_order[item]
            for item in blocks[state_block[state]]
            if item is not sink
        )
        for state in reachable
    }
    labels = {
        block_index: f"s{state_index}"
        for block_index, state_index in representatives.items()
    }
    output_states = [
        labels[block_index]
        for block_index in sorted(representatives, key=representatives.__getitem__)
    ]
    output_start = labels[state_block[start]]
    output_finals = sorted(
        {labels[state_block[state]] for state in reachable if state in finals},
        key=lambda label: int(label[1:]),
    )

    transitions = set()
    for state in reachable:
        src_block = state_block[state]
        for symbol in alphabet:
            target = delta.get((state, symbol))
            if target is None:
                continue
            target_block = state_block[target]
            if target_block not in labels:
                continue
            transitions.add((labels[src_block], symbol, labels[target_block]))
    transitions = sorted(
        transitions,
        key=lambda item: (int(item[0][1:]), item[1], int(item[2][1:])),
    )
    return output_states, output_start, output_finals, transitions


def format_output(alphabet, states, start, finals, transitions):
    out = [
        " ".join(states),
        " ".join(alphabet),
        start,
        " ".join(finals),
    ]
    out.extend(f"{src} {symbol} {dst}" for src, symbol, dst in transitions)
    return "\n".join(out) + "\n"


class Minimize(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', action='store_true',
                            help='minimize the automaton')

    def is_chosen_problem(self, args):
        return bool(getattr(args, 'mini', False))

    def run(self, args):
        if not args.input or not args.output:
            print("Hiba: az --input és --output megadása kötelező.",
                  file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input, encoding="utf-8") as f:
                text = f.read()
            states, alphabet, start, finals, delta = parse_automaton(text)
            new_states, new_start, new_finals, transitions = minimize(
                states, alphabet, start, finals, delta
            )
            with open(args.output, "w", encoding="utf-8", newline="\n") as f:
                f.write(format_output(
                    alphabet, new_states, new_start, new_finals, transitions
                ))
        except (AutomatonError, OSError) as e:
            print(f"Hiba: {e}", file=sys.stderr)
            sys.exit(1)

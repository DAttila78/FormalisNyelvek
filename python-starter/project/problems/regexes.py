import re
from project.problem import Problem

class RegexProblem(Problem):
    """
    4. feladat: Android logcat logfájlok elemzése reguláris kifejezésekkel.
    """
    def initialize_parser(self, parser):
        # Az --input és --output már definiálva van a fő keretrendszerben, 
        # ezért itt csak a saját --rgx argumentumunkat adjuk hozzá:
        parser.add_argument('--rgx', type=int, required=True, help='A feladat sorszáma (1-5)')

    def is_chosen_problem(self, args) -> bool:
        return hasattr(args, 'rgx') and args.rgx in [1, 2, 3, 4, 5]

    def run(self, args) -> int:
        input_filename = args.input
        output_filename = args.output
        task_num = args.rgx

        try:
            with open(input_filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.rstrip('\r\n') for line in f]
        except Exception as e:
            print(f"Hiba a bemeneti fájl olvasásakor: {e}")
            return 1

        results = []
        if task_num == 1:
            results = self._solve_task_1(lines)
        elif task_num == 2:
            results = self._solve_task_2(lines)
        elif task_num == 3:
            results = self._solve_task_3(lines)
        elif task_num == 4:
            results = self._solve_task_4(lines)
        elif task_num == 5:
            results = self._solve_task_5(lines)

        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                for res in results:
                    f.write(str(res) + '\n')
        except Exception as e:
            print(f"Hiba a kimeneti fájl írásakor: {e}")
            return 1

        return 0

    def _parse_logs(self, lines):
        log_pattern = re.compile(r'^(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([IDVEFAW])\s+([^:]+):\s*(.*)$')
        
        parsed_entries = []
        current_entry = None

        for line in lines:
            match = log_pattern.match(line)
            if match:
                if current_entry:
                    parsed_entries.append(current_entry)
                date, time, pid, tid, level, tag, message = match.groups()
                current_entry = {
                    'date': date,
                    'time': time,
                    'pid': pid,
                    'tid': tid,
                    'level': level,
                    'tag': tag.strip(),
                    'message': message,
                    'raw': line,
                    'continuation': []
                }
            else:
                if current_entry:
                    current_entry['continuation'].append(line)
        
        if current_entry:
            parsed_entries.append(current_entry)
        return parsed_entries

    def _solve_task_1(self, lines):
        entries = self._parse_logs(lines)
        c1 = c2 = c3 = c4 = c5 = c6 = c7 = c8 = c9 = c10 = 0
        java_pattern = re.compile(r'\.java:')

        for entry in entries:
            date = entry['date']
            time = entry['time']
            pid = entry['pid']
            level = entry['level']
            tag = entry['tag']
            message = entry['message']
            continuation = entry['continuation']

            if date == '10-15':
                c1 += 1
            if date == '10-15' and time.startswith('10:18:51'):
                c2 += 1
            if re.match(r'^\d{2}:\d{2}:51\.', time):
                c3 += 1
            if 'lowmemorykiller' in tag.lower():
                c4 += 1
            if time.startswith('10:18:51') and pid == '221':
                c5 += 1
            if level == 'E':
                c6 += 1
            if level == 'W' and tag == 'PackageManager':
                c7 += 1
            if level == 'D' and ('ExoPlayer' in tag or 'ExoPlayer' in message):
                c8 += 1
            if level in ('E', 'W'):
                if java_pattern.search(message) or any(java_pattern.search(cl) for cl in continuation):
                    c9 += 1
            if 'Thread' in message:
                c10 += 1

        return [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

    def _solve_task_2(self, lines):
        entries = self._parse_logs(lines)
        java_file_pattern = re.compile(r'([a-zA-Z0-9_]+\.java):\d+')
        results = []

        for entry in entries:
            if entry['level'] == 'E':
                text_to_check = entry['message'] + ' ' + ' '.join(entry['continuation'])
                matches = java_file_pattern.findall(text_to_check)
                results.extend(matches)

        return results

    def _solve_task_3(self, lines):
        entries = self._parse_logs(lines)
        seen = set()
        pids = []
        for entry in entries:
            pid = entry['pid']
            if pid not in seen:
                seen.add(pid)
                pids.append(pid)
        return pids

    def _solve_task_4(self, lines):
        entries = self._parse_logs(lines)
        error_counts = {}
        for entry in entries:
            if entry['level'] == 'E':
                pid = entry['pid']
                error_counts[pid] = error_counts.get(pid, 0) + 1

        if not error_counts:
            return ["Nincs hiba"]

        max_pid = max(error_counts, key=error_counts.get)
        max_count = error_counts[max_pid]
        return [f"{max_pid}={max_count} ({max_count} errors)"]

    def _solve_task_5(self, lines):
        entries = self._parse_logs(lines)
        count = 0
        for entry in entries:
            if entry['level'] == 'E' and entry['pid'] == entry['tid']:
                count += 1
        return [count]
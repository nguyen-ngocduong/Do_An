#!/usr/bin/env python3
"""Giao một task FE cho AGY; Codex đọc diff và tự quyết định nghiệm thu."""

import argparse
import difflib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / '.agent-runs'
TEXT_SUFFIXES = {'.md', '.py', '.ts', '.tsx', '.mjs', '.mts', '.css', '.json',
                 '.html', '.toml', '.yml', '.yaml', '.sh', '.txt', '.ipynb'}


def allowed_path(value):
    path = (ROOT / value).resolve()
    relative = path.relative_to(ROOT)
    if not relative.parts or relative.parts[0] not in {'FE', 'work_dir'}:
        raise ValueError('Chỉ giao quyền ghi trong FE/ hoặc work_dir/.')
    if any(part.startswith('.env') or part in {'node_modules', '.next', '.git'}
           for part in relative.parts):
        raise ValueError('Không giao quyền ghi credentials, dependencies hoặc cache.')
    return relative.as_posix()


def inside(path, boundaries):
    return any(path == boundary or path.startswith(boundary + '/')
               for boundary in boundaries)


def snapshot():
    # Bao gồm source chưa git add; git diff đơn thuần sẽ bỏ sót FE hiện chưa track.
    result = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    names = {name for name in result.decode().split('\0') if name}
    # JSON source và work_dir có thể bị bỏ qua bởi .gitignore.
    for source in [ROOT / 'FE', ROOT / 'work_dir']:
        for directory, folders, filenames in os.walk(source):
            folders[:] = [name for name in folders if name not in
                          {'node_modules', '.next', '__pycache__', 'results'}]
            names.update((Path(directory) / name).relative_to(ROOT).as_posix()
                         for name in filenames)
    files = {}
    for name in sorted(names):
        if name.startswith('.agent-runs/'):
            continue
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            continue
        if name.endswith(('.tsbuildinfo', '.pyc')):
            continue
        if (not name.startswith(('FE/', 'work_dir/'))
                and path.suffix not in TEXT_SUFFIXES
                and path.name not in {'.gitignore', '.gitattributes'}):
            continue
        if any(part.startswith('.env') for part in path.parts):
            continue
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def settings(boundaries, read_paths=None):
    # Overrides chỉ có hiệu lực cho lượt CLI này, không sửa cấu hình tài khoản.
    protected = ['BE', 'output', 'notebook', '.git', '.codex', 'AGENTS.md',
                 'README.md', 'docs', 'scripts', '.gemini']
    secret_paths = [ROOT / 'BE/.env', ROOT / 'BE/runtime', ROOT / 'FE/.env',
                    ROOT / 'FE/.env.local', ROOT / 'FE/.env.production',
                    Path.home() / '.ssh', Path.home() / '.aws',
                    Path.home() / '.codex', Path.home() / '.gemini/antigravity-cli']
    return {'permissions': {
        'allow': ['write_file(' + str(ROOT / path) + ')' for path in boundaries]
                 + ['read_file(' + str(path) + ')' for path in (read_paths or [])],
        'deny': ['write_file(' + str(ROOT / path) + ')' for path in protected]
                + ['read_file(' + str(path) + ')' for path in secret_paths]
                + ['write_file(' + str(ROOT / 'FE/node_modules') + ')',
                   'write_file(' + str(ROOT / 'FE/.next') + ')',
                   'command(*)', 'unsandboxed(*)', 'mcp(*)', 'read_url(*)', 'execute_url(*)'],
        'ask': [],
    }}


def run(args):
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != 'duong':
        raise ValueError('Task hệ thống chỉ được chạy trên nhánh duong.')
    if not shutil.which('agy'):
        raise ValueError('Chưa có agy trong PATH; xem docs-md/CODEX_AGY_WORKFLOW.md.')
    boundaries = [allowed_path(path) for path in args.allow_write]
    expected = [allowed_path(path) for path in args.expect]
    if any(not inside(path, boundaries) for path in expected):
        raise ValueError('--expect phải nằm trong --allow-write.')
    read_paths = [Path(path).resolve() for path in getattr(args, 'allow_read', [])]
    for path in read_paths:
        if not path.is_file() or any(part.startswith('.env') for part in path.parts):
            raise ValueError('--allow-read chỉ nhận file tài liệu cụ thể, không nhận .env hoặc thư mục.')
    task = Path(args.task).resolve().read_text()
    RUNS.mkdir(mode=0o700, exist_ok=True)
    with (RUNS / 'frontend.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Một task AGY khác đang chạy; chờ hoàn thành trước khi sửa chung file.') from None
        folder = RUNS / (time.strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid()))
        folder.mkdir(mode=0o700)
        before = snapshot()
        for name in before:
            path = ROOT / name
            if inside(name, boundaries):
                copy = folder / 'before' / name
                copy.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, copy)
        profile = folder / 'settings.json'
        profile.write_text(json.dumps(settings(boundaries, read_paths), indent=2))
        prompt = f'''Bạn là Antigravity, người triển khai FE do Codex điều phối.
Đọc AGENTS.md, FE/PLAN.md, FE/design/DESIGN.md và FE/design/SURFACE.md theo nhu cầu task.
Chỉ ghi các đường dẫn: {', '.join(boundaries)}.
Dùng công cụ file (view_file/list_dir/grep_search/write_to_file/replace_file_content).
Không chạy terminal hoặc nhờ agent khác chạy terminal. Codex sẽ chạy lint/test/build.
Không tự gọi agy, không tạo agent con, không sửa AGENTS.md, BE, model hoặc dữ liệu chạy.
Không đọc .env/credentials/config tài khoản; không commit/push, restart server hoặc thao tác browser.
Giữ kiến trúc/API hiện có và code đơn giản cho sinh viên. Chỉ làm task bên dưới.
Nếu thiếu quyền/căn cứ, báo rõ; không tuyên bố đã làm khi chưa có file thực tế.
Kết thúc báo file đã sửa, hành vi, việc chưa làm và các kiểm tra thực sự đã chạy.

TASK:
{task}
'''
        (folder / 'prompt.md').write_text(prompt)
        command = ['agy', '-p', prompt, '--mode', 'accept-edits', '--settings', str(profile),
                   '--output-format', 'json', '--print-timeout', f'{args.timeout}s']
        if args.conversation:
            command += ['--conversation', args.conversation]
        print('AGY đang chạy; bằng chứng:', folder.relative_to(ROOT), flush=True)
        started = time.monotonic()
        timed_out = False
        with (folder / 'stdout.json').open('w') as stdout, (folder / 'stderr.log').open('w') as stderr:
            process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                returncode = process.wait(timeout=args.timeout + 20)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    returncode = process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    returncode = process.wait()
        try:
            response = json.loads((folder / 'stdout.json').read_text())
        except json.JSONDecodeError:
            response = {}
        if not isinstance(response, dict):
            response = {}
        after = snapshot()
        changed = [name for name in sorted(before.keys() | after.keys())
                   if before.get(name) != after.get(name)]
        outside = [name for name in changed if not inside(name, boundaries)]
        missing = [name for name in expected if name not in changed or not (ROOT / name).is_file()]
        stderr_text = (folder / 'stderr.log').read_text()
        permission_notice = any(word in stderr_text.lower() for word in
                                ['denied', 'soft denied', 'requires approval', 'requires permission',
                                 'not allowed', 'not permitted', 'permission required'])
        successful = (returncode == 0 and response.get('status') == 'SUCCESS' and changed
                      and not outside and not missing and not timed_out and not permission_notice)
        report = {'cli_exit': returncode, 'status': response.get('status', 'NO_JSON_RESULT'),
                  'conversation_id': response.get('conversation_id'),
                  'elapsed_seconds': round(time.monotonic() - started, 2),
                  'timed_out': timed_out, 'permission_notice': permission_notice,
                  'allowed_writes': boundaries, 'allowed_reads': [str(path) for path in read_paths],
                  'changed_files': changed,
                  'outside_scope': outside, 'missing_expected_changes': missing,
                  'ready_for_codex_review': bool(successful),
                  'note': 'Chưa nghiệm thu: Codex cần đọc response/diff, kiểm tra code và chạy checks.'}
        (folder / 'source-hashes.json').write_text(json.dumps({'before': before, 'after': after}, indent=2) + '\n')
        (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        with (folder / 'changes.diff').open('w') as output:
            for name in changed:
                old = folder / 'before' / name
                new = ROOT / name
                try:
                    previous = old.read_text().splitlines(keepends=True) if old.exists() else []
                    current = new.read_text().splitlines(keepends=True) if new.is_file() else []
                except UnicodeDecodeError:
                    output.write(f'Binary file changed: {name} (xem hash trong snapshot).\n')
                    continue
                output.writelines(difflib.unified_diff(previous, current, fromfile='before/' + name, tofile='after/' + name))
        print(json.dumps({**report, 'changed_files': changed[:30], 'outside_scope': outside[:30],
                          'report_file': str((folder / 'report.json').relative_to(ROOT))},
                         ensure_ascii=False, indent=2))
        return 0 if successful else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', help='File Markdown chứa task cụ thể.')
    parser.add_argument('--allow-write', action='append', required=True, help='File/thư mục FE hoặc work_dir được sửa; lặp lại được.')
    parser.add_argument('--allow-read', action='append', default=[], help='File tài liệu cụ thể ngoài workspace cần quyền đọc; lặp lại được.')
    parser.add_argument('--expect', action='append', default=[], help='File bắt buộc được tạo/sửa trong lượt này.')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--conversation', help='ID chính xác từ report trước để giao task sửa tiếp.')
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error('--timeout phải lớn hơn 0.')
    try:
        return run(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

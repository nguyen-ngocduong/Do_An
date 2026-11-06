"""Kiểm tra runner bằng CLI giả; không gọi model, không sửa repo người dùng."""

import argparse
import contextlib
import fcntl
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('agy_frontend', Path(__file__).parents[1] / 'agy_frontend.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        subprocess.run(['git', 'init', '-q', '-b', 'duong', str(self.root)], check=True)
        (self.root / '.gitignore').write_text('.agent-runs/\nwork_dir/\n*.json\n')
        (self.root / 'FE/src').mkdir(parents=True)
        (self.root / 'work_dir').mkdir()
        (self.root / 'task.md').write_text('Task fixture')
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'agy'
        cli.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
mode = os.environ['AGY_TEST_ACTION']
if mode != 'no_changes':
    Path('FE/src/probe.json').write_text('{"brand":"NIDR"}')
if mode == 'outside':
    Path('README.md').write_text('Out of scope')
if mode == 'denied':
    print('Tool run_command: permission denied', file=sys.stderr)
if mode == 'binary':
    Path('FE/src/probe.png').write_bytes(bytes([137, 80, 78, 71, 0]))
if mode == 'invalid':
    print('[]')
else:
    print(json.dumps({'status': 'SUCCESS', 'conversation_id': 'fixture', 'response': 'Done'}))
''')
        cli.chmod(0o755)
        self.paths = patch.multiple(runner, ROOT=self.root, RUNS=self.root / '.agent-runs')
        self.paths.start()
        self.environment = patch.dict(os.environ, {'PATH': str(binary) + os.pathsep + os.environ['PATH'],
                                                  'AGY_TEST_ACTION': 'success'})
        self.environment.start()
        self.args = argparse.Namespace(task=str(self.root / 'task.md'), allow_write=['FE/src'],
                                       expect=['FE/src/probe.json'], timeout=3, conversation=None)

    def tearDown(self):
        self.environment.stop()
        self.paths.stop()
        self.temporary.cleanup()

    def execute(self, action):
        with patch.dict(os.environ, {'AGY_TEST_ACTION': action}), contextlib.redirect_stdout(io.StringIO()):
            code = runner.run(self.args)
        report_path = next((self.root / '.agent-runs').glob('*/report.json'))
        return code, json.loads(report_path.read_text()), report_path.parent

    def test_success_sees_ignored_untracked_json_and_diff(self):
        code, report, folder = self.execute('success')
        self.assertEqual(code, 0)
        self.assertEqual(report['changed_files'], ['FE/src/probe.json'])
        self.assertTrue(report['ready_for_codex_review'])
        self.assertIn('+{"brand":"NIDR"}', (folder / 'changes.diff').read_text())
        policy = json.loads((folder / 'settings.json').read_text())
        self.assertIn('command(*)', policy['permissions']['deny'])

    def test_zero_exit_success_without_changes_is_rejected(self):
        code, report, _ = self.execute('no_changes')
        self.assertEqual(code, 2)
        self.assertEqual(report['missing_expected_changes'], ['FE/src/probe.json'])

    def test_soft_denied_is_rejected_even_if_file_changed(self):
        code, report, _ = self.execute('denied')
        self.assertEqual(code, 2)
        self.assertTrue(report['permission_notice'])

    def test_outside_scope_source_change_is_not_accepted_or_rolled_back(self):
        code, report, _ = self.execute('outside')
        self.assertEqual(code, 2)
        self.assertEqual(report['outside_scope'], ['README.md'])
        self.assertEqual((self.root / 'README.md').read_text(), 'Out of scope')

    def test_binary_asset_is_detected_without_garbage_text_diff(self):
        code, report, folder = self.execute('binary')
        self.assertEqual(code, 0)
        self.assertIn('FE/src/probe.png', report['changed_files'])
        self.assertIn('Binary file changed: FE/src/probe.png', (folder / 'changes.diff').read_text())

    def test_invalid_json_envelope_is_rejected(self):
        code, report, _ = self.execute('invalid')
        self.assertEqual(code, 2)
        self.assertEqual(report['status'], 'NO_JSON_RESULT')

    def test_branch_guard(self):
        subprocess.run(['git', 'checkout', '-q', '-b', 'main'], cwd=self.root, check=True)
        with self.assertRaisesRegex(ValueError, 'duong'):
            runner.run(self.args)

    def test_paths_cannot_escape_scope_or_include_credentials(self):
        for value in ['.', 'BE/main.py', '../outside', 'FE/.env.local', 'FE/.next/test']:
            with self.subTest(path=value), self.assertRaises(ValueError):
                runner.allowed_path(value)
        (self.root / 'FE/link').symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            runner.allowed_path('FE/link/escape.ts')

    def test_lock_prevents_parallel_handoff(self):
        runner.RUNS.mkdir()
        with (runner.RUNS / 'frontend.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'đang chạy'):
                runner.run(self.args)


if __name__ == '__main__':
    unittest.main()

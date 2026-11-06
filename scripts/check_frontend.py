#!/usr/bin/env python3
"""Chạy checks FE trong bản sao tạm, giữ cache Next dev đang hoạt động."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    node = shutil.which('node')
    npm = shutil.which('npm')
    if not node or not npm:
        raise RuntimeError('Cần Node.js 22.12+ thuộc dòng22 và npm trong PATH: nvm use 22.')
    version = subprocess.check_output([node, '--version'], text=True).strip().lstrip('v').split('.')
    if int(version[0]) != 22 or int(version[1]) < 12:
        raise RuntimeError('Chạy nvm use 22 trước khi kiểm tra FE.')
    if not (ROOT / 'FE/node_modules').is_dir():
        raise RuntimeError('Cần npm ci trong FE trước khi kiểm tra.')
    with tempfile.TemporaryDirectory(prefix='nidr-fe-check-') as temporary:
        frontend = Path(temporary) / 'FE'
        ignored = shutil.ignore_patterns('node_modules', '.next', '.env*', '*.tsbuildinfo',
                                        'results', '__pycache__')
        shutil.copytree(ROOT / 'FE', frontend, ignore=ignored)
        # Bản sao dependencies giữ traced files nằm trong gốc build standalone.
        shutil.copytree(ROOT / 'FE/node_modules', frontend / 'node_modules', symlinks=True)
        environment = dict(os.environ)
        environment['NEXT_TELEMETRY_DISABLED'] = '1'
        for check in ['lint', 'typecheck', 'test', 'build']:
            print(f'Kiểm tra {check} trong bản sao tạm.', flush=True)
            subprocess.run([npm, 'run', check], cwd=frontend, env=environment, check=True)
    print('Đạt lint/typecheck/test/build; không sửa FE/.next đang dev.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)

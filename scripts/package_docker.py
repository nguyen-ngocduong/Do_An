#!/usr/bin/env python3
"""Build and export NIDR images. Producer only; recipients need Docker alone."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='1.0.0')
    parser.add_argument('--skip-build', action='store_true')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', args.version):
        parser.error('Invalid image version')
    paths = json.loads((ROOT / 'deploy/docker/artifacts.json').read_text())
    checksums = {}
    for relative in paths:
        path = ROOT / relative
        checksums[relative] = digest(path)
        if path.name != 'output_checksums.json':
            folder = path.parent.parent if path.parent.name == 'frozen_models' else path.parent
            manifest = json.loads((folder / 'output_checksums.json').read_text())
            relative_name = path.relative_to(folder).as_posix()
            if relative_name in manifest and checksums[relative] != manifest[relative_name]:
                raise RuntimeError(f'Artifact checksum mismatch: {relative}')
    images = []
    for target in ['backend', 'frontend', 'gateway']:
        name = f'nidr-{target}:{args.version}'
        images.append(name)
        if not args.skip_build:
            subprocess.run(['docker', 'build', '--platform', 'linux/amd64', '--target', target, '-t', name, '.'], cwd=ROOT, check=True)
    image_records = []
    for name in images:
        record = json.loads(subprocess.check_output(['docker', 'image', 'inspect', name]))[0]
        if record['Architecture'] != 'amd64' or record['Os'] != 'linux':
            raise RuntimeError(f'Wrong image platform: {name}')
        image_records.append({key: record[key] for key in ['Id', 'RepoTags', 'Architecture', 'Os', 'Size']})
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / f'nidr-{args.version}-linux-amd64.zip'
    if destination.exists():
        raise FileExistsError(f'Release already exists: {destination}; choose a new version/output')
    with tempfile.TemporaryDirectory(prefix='nidr-release-') as temporary:
        bundle = Path(temporary)
        archive = bundle / 'nidr-images.tar'
        subprocess.run(['docker', 'save', '--output', str(archive), *images], check=True)
        for relative in ['docker-compose.yml', 'docker-compose.prod.yml', '.env.docker.example', 'deploy/docker/nginx.prod.conf']:
            path = bundle / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, path)
        template = (bundle / '.env.docker.example').read_text().replace('NIDR_VERSION=1.0.0', 'NIDR_VERSION=' + args.version)
        (bundle / '.env.docker.example').write_text(template)
        shutil.copyfile(ROOT / 'deploy/docker/README.md', bundle / 'README.md')
        (bundle / 'samples').mkdir()
        shutil.copyfile(ROOT / 'output/integration_runs/integration_20261022_075217_0b67d48f/input_features.csv', bundle / 'samples/integration_input_50.csv')
        manifest = {'version': args.version, 'platform': 'linux/amd64', 'images': image_records, 'artifact_sha256': checksums,
                    'files': {p.relative_to(bundle).as_posix(): digest(p) for p in bundle.rglob('*') if p.is_file()}}
        (bundle / 'release-manifest.json').write_text(json.dumps(manifest, indent=2))
        partial = destination.with_suffix('.zip.part')
        try:
            with zipfile.ZipFile(partial, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=3) as output:
                for path in sorted(bundle.rglob('*')):
                    if path.is_file():
                        output.write(path, path.relative_to(bundle))
            partial.replace(destination)
        finally:
            partial.unlink(missing_ok=True)
    destination.with_suffix('.zip.sha256').write_text(digest(destination) + '  ' + destination.name + '\n')
    print(destination)

if __name__ == '__main__':
    main()

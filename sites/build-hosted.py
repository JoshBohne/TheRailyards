"""Build the public site from one verified current-scene media release.

No archived V12/V13 model assets are substituted. Prepare the release with
package-current-media.py after the native renders and replay export finish.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import struct
from pathlib import Path

def split_venue(output):
    """Keep the existing Draco geometry, splitting its buffer for static hosting."""
    model = output / "replay/model/venue.glb"
    data = model.read_bytes()
    magic, version, total = struct.unpack_from("<III", data)
    if magic != 0x46546C67 or version != 2 or total != len(data):
        raise ValueError("Invalid venue GLB")
    json_length = struct.unpack_from("<I", data, 12)[0]
    scene = json.loads(data[20:20 + json_length])
    binary = data[28 + json_length:]
    chunks = [bytearray()]
    for view in scene["bufferViews"]:
        if view.get("buffer", 0) != 0:
            raise ValueError("Expected one embedded venue buffer")
        start = view.get("byteOffset", 0)
        payload = binary[start:start + view["byteLength"]]
        if len(payload) != view["byteLength"]:
            raise ValueError("Incomplete venue buffer view")
        if len(chunks[-1]) + len(payload) + 3 > 12 * 1024 * 1024:
            chunks.append(bytearray())
        chunk = chunks[-1]
        chunk.extend(b"\0" * (-len(chunk) % 4))
        view["buffer"] = len(chunks) - 1
        view["byteOffset"] = len(chunk)
        chunk.extend(payload)
    scene["buffers"] = []
    for index, chunk in enumerate(chunks):
        name = f"venue-{index}.bin"
        (model.parent / name).write_bytes(chunk)
        scene["buffers"].append({"uri": name, "byteLength": len(chunk)})
    model.with_suffix(".gltf").write_text(json.dumps(scene, separators=(",", ":")))
    model.unlink()
    replacements = 0
    for script in (output / "replay/assets").glob("*.js"):
        source = script.read_text()
        replacements += source.count("model/venue.glb")
        script.write_text(source.replace("model/venue.glb", "model/venue.gltf"))
    if replacements != 1:
        raise ValueError(f"Expected one venue URL, found {replacements}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--templates', type=Path, default=Path(__file__).resolve().parent / 'public')
    parser.add_argument('--release-root', type=Path, required=True)
    parser.add_argument('--replay-dist', type=Path, default=Path(__file__).resolve().parent / 'replay/dist')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'runtime/dist/client')
    parser.add_argument('--site-url', default='https://therailyards.jbohne.chatgpt.site')
    args = parser.parse_args()
    release = args.release_root.resolve()
    receipt = json.loads((release / 'release.json').read_text())
    if receipt['sceneVersion'] != 14:
        raise ValueError('Expected the current V14 release')
    for item in receipt['files']:
        path = release / item['path']
        if not path.resolve().is_relative_to(release):
            raise ValueError('Invalid release path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Release checksum mismatch: {path}')
    replay = json.loads((release / 'model/replay.json').read_text())
    if replay['sourceStaticSha256'] != receipt['sourceStaticSha256']:
        raise ValueError('Replay and rendered scene disagree')
    if not (args.replay_dist / 'index.html').is_file():
        raise FileNotFoundError(args.replay_dist / 'index.html')
    output = args.output.resolve()
    for source in [args.templates.resolve(), release, Path.cwd()]:
        if source == output or source.is_relative_to(output):
            raise ValueError('Output must be separate from source')
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(release / 'media', output / 'media')
    shutil.copytree(args.replay_dist, output / 'replay', ignore=shutil.ignore_patterns('model'))
    shutil.copytree(release / 'model', output / 'replay/model')
    split_venue(output)
    for source in args.templates.iterdir():
        if not source.is_file() or source.suffix not in ('.html', '.css', '.js', '.svg'):
            continue
        target = output / source.name
        if source.suffix == '.html':
            target.write_text(source.read_text().replace('{{SITE_URL}}', args.site_url.rstrip('/')))
        else:
            shutil.copy2(source, target)
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    files = [{'path': str(p.relative_to(output)), 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(output.rglob('*')) if p.is_file()]
    oversized = [p['path'] for p in files if p['bytes'] >= 25 * 1024 * 1024]
    if oversized:
        raise ValueError(f'Files exceed hosting limit: {oversized}')
    manifest = {'commit': revision, 'sceneVersion': 14, 'sourceStaticSha256': receipt['sourceStaticSha256'],
                'sourceAnimatedSha256': receipt['sourceAnimatedSha256'], 'seatCount': replay['seatCount'],
                'releaseSha256': hashlib.sha256((release / 'release.json').read_bytes()).hexdigest(), 'files': files}
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"Built {len(files)} files from the verified V14 release in {output}")


if __name__ == '__main__':
    main()

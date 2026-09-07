"""Build the public site from templates and checksum-pinned V11 release media."""
import argparse
import hashlib
import json
import shutil
import subprocess
import struct
import urllib.request
import zipfile
from pathlib import Path

RELEASE = "https://github.com/JoshBohne/TheRailyards/releases/download/v11-circulation/"
ARCHIVES = {
    "public": "a2be2ae15cbc16f82fe78ec2ef71152f6a3df9a33d0314ea0d32133e8b56172d",
    "review": "cf99f94fe9ee93f8709507fa90c7cb500ecf92b91a7318b08dcd169e54e1d3af",
}


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
    parser.add_argument("--templates", type=Path, default=Path("templates"))
    parser.add_argument("--output", type=Path, default=Path("dist"))
    parser.add_argument("--assets", type=Path, default=Path(".cache"))
    parser.add_argument("--site-url", default="")
    args = parser.parse_args()
    args.assets.mkdir(parents=True, exist_ok=True)
    output = args.output.resolve()
    if output == args.templates.resolve() or output == Path.cwd():
        raise ValueError("Output must be separate from source")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for kind, expected in ARCHIVES.items():
        name = f"railyards-v11-{kind}-site.zip"
        archive = args.assets / name
        if not archive.exists():
            with urllib.request.urlopen(RELEASE + name, timeout=60) as response:
                archive.write_bytes(response.read())
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Release checksum mismatch: {name}")
        with zipfile.ZipFile(archive) as source:
            for item in source.infolist():
                path = Path(item.filename)
                if item.is_dir() or path.is_absolute() or ".." in path.parts:
                    continue
                relative = path.relative_to(kind)
                if kind == "public" and relative.parts[0] in ("media", "replay"):
                    target = output / relative
                elif kind == "review" and str(relative) in (
                    "media/source-south.jpg", "media/source-bridge.jpg",
                    "media/v11-south.jpg", "media/v11-bridge.jpg",
                ):
                    target = output / str(relative).replace("v11-", "model-")
                else:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read(item))
    split_venue(output)
    replay_page = output / "replay/index.html"
    replay_html = replay_page.read_text().replace('href="../"', 'href="../index.html" target="_top"')
    replay_html = replay_html.replace('href="../index.html" target="_top">Watch the rendered films',
                                      'href="../gallery.html#films" target="_top">Watch the rendered films')
    replay_page.write_text(replay_html)
    for source in args.templates.iterdir():
        if source.is_file() and source.suffix in (".html", ".css", ".js", ".svg"):
            target = output / source.name
            if source.suffix == ".html":
                text = source.read_text()
                if args.site_url:
                    text = text.replace("{{SITE_URL}}", args.site_url.rstrip("/"))
                else:
                    text = "\n".join(line for line in text.splitlines() if "{{SITE_URL}}" not in line)
                target.write_text(text)
            else:
                shutil.copy2(source, target)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    manifest = {"commit": commit, "sceneVersion": 11, "releaseChecksums": ARCHIVES,
                "files": [{"path": str(p.relative_to(output)), "bytes": p.stat().st_size,
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(output.rglob("*")) if p.is_file()]}
    (output / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Built {len(manifest['files'])} files in {output}")


if __name__ == "__main__":
    main()

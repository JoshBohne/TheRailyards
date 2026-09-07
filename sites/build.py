"""Build self-contained public and review sites from saved-scene artifacts.

Run:
    uv run --with imageio-ffmpeg==0.6.0 python sites/build.py --encode --replay

Outputs live under ``work/web-dist`` and do not require the Blender UI.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "railyards-v4"


def git_state() -> tuple[str | None, bool | None]:
    """Return build provenance when running inside a Git checkout."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
        return commit, dirty
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, None


def public_url(raw: str | None) -> str | None:
    if not raw:
        return None
    value = raw.strip()
    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"
    return value.rstrip("/")


def write_discovery_files(destination: Path, site_url: str, include_replay: bool) -> None:
    urls = [f"{site_url}/", f"{site_url}/process.html"]
    if include_replay:
        urls.append(f"{site_url}/replay/")
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%s
</urlset>
""" % "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
    (destination / "sitemap.xml").write_text(sitemap)
    (destination / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encode", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--scene-version", type=int, default=11, help="Rendered scene version to publish")
    parser.add_argument("--site-url", help="Canonical public URL used for social metadata")
    args = parser.parse_args()

    site_url = public_url(
        args.site_url
        or os.environ.get("RAILYARDS_SITE_URL")
        or os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
        or os.environ.get("VERCEL_URL")
    )
    current = MODEL / f"review/v{args.scene_version}"

    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    movies = current / "movies"
    movies.mkdir(exist_ok=True)

    if args.encode:
        for name, count in [("arrival", 192), ("left_center", 192), ("boat", 192), ("river", 168)]:
            folder = current / name
            missing = [f"{frame:04d}.png" for frame in range(count) if not (folder / f"{frame:04d}.png").is_file()]
            if missing:
                raise FileNotFoundError(f"{name}: missing {len(missing)} rendered frames; first {missing[0]}")
            target = movies / f"{name}.mp4"
            newest_frame = max((folder / f"{frame:04d}.png").stat().st_mtime for frame in range(count))
            if target.exists() and target.stat().st_mtime > newest_frame:
                continue
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-loglevel",
                    "error",
                    "-framerate",
                    "24",
                    "-i",
                    str(folder / "%04d.png"),
                    "-frames:v",
                    str(count),
                    "-c:v",
                    "libx264",
                    "-crf",
                    "18",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    str(target),
                ],
                check=True,
            )

    if args.replay:
        subprocess.run(["pnpm", "--dir", str(ROOT / "sites/replay"), "build"], check=True)

    images = {name: current / f"{name}.png" for name in ["arrival", "left_center", "boat", "skyline_west", "skyline_east"]}
    images["river-poster"] = current / "river/0110.png"
    images["v8-left_center"] = MODEL / "review/v8-experiences/left_center.png"
    for name in ["willis", "regis", "pru"]:
        for version in ["before", "after"]:
            images[f"{name}-{version}"] = MODEL / f"review/v9/forms/{name}-{version}.png"

    sources = {
        "north": "aecom-north-aerial.png",
        "south": "aecom-south-aerial.jpg",
        "bridge": "user-bridge-view.png",
    }
    for name, filename in sources.items():
        images[f"source-{name}"] = ROOT / "reconstruction-references" / filename
        images[f"v9-{name}"] = MODEL / f"v9-{name}.png"
        images[f"v8-{name}"] = MODEL / f"final-{name}.png"
        images[f"v3-{name}"] = ROOT / f"railyards-v3/final-{name}.png"

    if args.scene_version != 9:
        for name in sources:
            images[f"v{args.scene_version}-{name}"] = MODEL / f"v{args.scene_version}-{name}.png"

    # Version-specific review evidence is optional so a newly rendered version can
    # publish before its diagnostic gallery has the exact same file set as V11.
    for name, filename in {
        "entrance-before": "entrance-before.png",
        "entrance-after": "C_entrance_landing.png",
        "riverwalk-before": "riverwalk-before.png",
        "riverwalk-after": "F_riverwalk_under_deck.png",
        "corner-stair": "I_corner_stair_close.png",
        "lf-stair": "M_lf_stair_side.png",
        "rf-stair": "K_rf_stair.png",
    }.items():
        candidate = current / filename
        if candidate.is_file():
            images[name] = candidate

    for name in sources:
        images[f"model-{name}"] = images[f"v{args.scene_version}-{name}"]

    commit, dirty = git_state()
    public_assets = {
        "arrival",
        "left_center",
        "boat",
        "skyline_west",
        "skyline_east",
        "river-poster",
        "source-north",
        "model-north",
        "source-south",
        "model-south",
        "source-bridge",
        "model-bridge",
    }

    for kind in ["public", "review"]:
        destination = ROOT / "work/web-dist" / kind
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True, exist_ok=True)
        for file in (ROOT / "sites" / kind).iterdir():
            if file.is_file():
                shutil.copy2(file, destination / file.name)

        if kind == "public":
            for html in destination.glob("*.html"):
                text = html.read_text()
                if site_url:
                    text = text.replace("{{SITE_URL}}", site_url)
                else:
                    text = "\n".join(line for line in text.splitlines() if "{{SITE_URL}}" not in line) + "\n"
                html.write_text(text)
            if site_url:
                write_discovery_files(destination, site_url, args.replay)

        media = destination / "media"
        media.mkdir(exist_ok=True)
        chosen = images if kind == "review" else {key: value for key, value in images.items() if key in public_assets}
        for name, source in chosen.items():
            if not source.is_file():
                raise FileNotFoundError(source)
            target = media / f"{name}.jpg"
            if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
                subprocess.run(
                    [
                        ffmpeg,
                        "-y",
                        "-loglevel",
                        "error",
                        "-i",
                        str(source),
                        "-vf",
                        "scale=min(1600\\,iw):-2",
                        "-frames:v",
                        "1",
                        "-q:v",
                        "3",
                        str(target),
                    ],
                    check=True,
                )

        for name in ["arrival", "left_center", "boat", "river"]:
            source = movies / f"{name}.mp4"
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copy2(source, media / source.name)

        if kind == "public" and args.replay:
            replay_destination = destination / "replay"
            if replay_destination.exists():
                shutil.rmtree(replay_destination)
            shutil.copytree(ROOT / "sites/replay/dist", replay_destination)

        manifest = {
            "site": kind,
            "sceneVersion": args.scene_version,
            "commit": commit,
            "workingTreeDirty": dirty,
            "files": [
                {
                    "path": str(path.relative_to(destination)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                }
                for path in sorted(destination.rglob("*"))
                if path.is_file() and path.name != "build-manifest.json"
            ],
        }
        (destination / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f'{kind}: {destination} ({len(manifest["files"])} files)')


if __name__ == "__main__":
    main()

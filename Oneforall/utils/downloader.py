from os import path
import traceback
import yt_dlp

ytdl = yt_dlp.YoutubeDL({"extractor_args": {"youtube": {"player_client": ["mweb"]}},
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "format": "bestaudio/best",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "cookiefile": "/root/Unique-/youtube.txt",
    "js_runtimes": {"node": {"path": "/usr/bin/node"}},
    "remote_components": ["ejs:github"],
})


def download(url: str, my_hook) -> str:
    # 👉 name support
    if not url.startswith("http"):
        url = f"ytsearch1:{url}"

    ydl_optssx = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "cookiefile": "/root/Unique-/youtube.txt",
        "js_runtimes": {"node": {"path": "/usr/bin/node"}},
        "remote_components": ["ejs:github"],
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb"],
            }
        },
        "quiet": True,
        "no_warnings": True,
    }

    try:
        x = yt_dlp.YoutubeDL(ydl_optssx)
        x.add_progress_hook(my_hook)

        # 🔥 extract + download together
        info = x.extract_info(url, download=True)

        # 👉 search case handle
        if "entries" in info:
            info = info["entries"][0]

    except Exception as y_e:
        print("YT-DLP ERROR:", repr(y_e))
        traceback.print_exc()
        return None

    # ✅ correct file path
    xyz = x.prepare_filename(info)
    return xyz

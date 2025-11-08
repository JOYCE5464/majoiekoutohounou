#!/usr/bin/env python3

"""
Generate a 60-second vertical video with dynamic motion design for Majoie, SEO consultant.

The script uses MoviePy to build animated typographic scenes that mirror the provided narrative.
Prerequisites:
  - Python 3.9+
  - moviepy >= 1.0.3
  - ImageMagick (required by TextClip) or use the `--use_gizeh` option of moviepy
  - ffmpeg available on PATH

Usage:
  pip install moviepy
  python generate_majoie_video.py

The output file is `majoie_seo_motion.mp4` in the current directory. Adjust fonts, colours,
or timings in the SCENES configuration to taste.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

from moviepy.editor import ColorClip, CompositeVideoClip, TextClip
from moviepy.video.fx import all as vfx

VIDEO_SIZE: Tuple[int, int] = (1080, 1920)  # Vertical format (9:16)
VIDEO_DURATION = 60
FPS = 30

# Configure fonts available on your system. Provide full font names installed on the machine.
HEADLINE_FONT = "Poppins-Bold"
BODY_FONT = "Poppins-Regular"
ACCENT_FONT = "Poppins-SemiBold"

PALETTE: Dict[str, Tuple[int, int, int]] = {
    "midnight": (15, 23, 42),
    "deep_blue": (24, 35, 68),
    "sky": (76, 139, 245),
    "violet": (146, 83, 234),
    "neo_green": (45, 226, 190),
    "warm_white": (243, 246, 255),
    "soft_gray": (195, 206, 223),
}


def ease_out_cubic(x: float) -> float:
    """Cubic easing for fluid motion."""
    x = max(0.0, min(1.0, x))
    return 1 - pow(1 - x, 3)


def clip_progress(t: float, start_time: float, duration: float) -> float:
    """Return eased progress percentage for a clip at absolute time t."""
    if t <= start_time:
        return 0.0
    if t >= start_time + duration:
        return 1.0
    raw = (t - start_time) / duration
    return ease_out_cubic(raw)


def normalized_to_pixels(coord: Tuple[float, float]) -> Tuple[float, float]:
    """Convert normalized coordinates (0-1) into absolute pixel positions."""
    return coord[0] * VIDEO_SIZE[0], coord[1] * VIDEO_SIZE[1]


def animated_position(
    start_px: Tuple[float, float],
    end_px: Tuple[float, float],
    start_time: float,
    move_duration: float,
) -> Callable[[float], Tuple[float, float]]:
    """Create a position callable for MoviePy based on eased interpolation."""

    def position(t: float) -> Tuple[float, float]:
        progress = clip_progress(t, start_time, move_duration)
        return (
            start_px[0] + (end_px[0] - start_px[0]) * progress,
            start_px[1] + (end_px[1] - start_px[1]) * progress,
        )

    return position


def build_text_clip(
    *,
    text: str,
    font: str,
    fontsize: int,
    color: Tuple[int, int, int],
    start_time: float,
    duration: float,
    start_pos: Tuple[float, float],
    end_pos: Tuple[float, float],
    move_duration: float,
    line_height: int | None = None,
    stroke_width: int = 0,
    stroke_color: Tuple[int, int, int] | None = None,
    background_opacity: float = 0.0,
) -> TextClip:
    """Create an animated TextClip with smooth entrance and gentle float."""

    text_clip = TextClip(
        text,
        font=font,
        fontsize=fontsize,
        color=_rgb_to_hex(color),
        method="caption",
        align="center",
        size=(int(VIDEO_SIZE[0] * 0.84), None),
        interline=line_height,
        stroke_color=_rgb_to_hex(stroke_color) if stroke_color else None,
        stroke_width=stroke_width,
    )

    if background_opacity > 0:
        text_clip = text_clip.margin(30, color=_rgb_to_hex((0, 0, 0))).set_opacity(background_opacity)

    clip = (
        text_clip.set_start(start_time)
        .set_duration(duration)
        .set_position(
            animated_position(
                normalized_to_pixels(start_pos),
                normalized_to_pixels(end_pos),
                start_time,
                move_duration,
            )
        )
        .crossfadein(min(0.8, move_duration))
        .crossfadeout(0.6)
    )

    # Apply a subtle scale pulse for added dynamism
    pulse_strength = 0.02

    def scale_pulse(t: float) -> float:
        local_t = max(0.0, t - start_time)
        return 1 + pulse_strength * math.sin(2 * math.pi * local_t / max(duration, 0.01))

    return clip.resize(scale_pulse)


def build_accent_clip(
    *,
    color: Tuple[int, int, int],
    width: float,
    height: float,
    start_time: float,
    duration: float,
    start_pos: Tuple[float, float],
    end_pos: Tuple[float, float],
    move_duration: float,
    opacity: float = 1.0,
    rotation: float = 0.0,
) -> ColorClip:
    """Create a geometric accent block that moves gently to add depth."""
    clip = (
        ColorClip(size=(int(width), int(height)), color=color)
        .set_start(start_time)
        .set_duration(duration)
        .set_position(
            animated_position(
                normalized_to_pixels(start_pos),
                normalized_to_pixels(end_pos),
                start_time,
                move_duration,
            )
        )
        .set_opacity(opacity)
    )

    if rotation:
        clip = clip.rotate(rotation, resample="bilinear")

    return clip.crossfadein(min(0.6, move_duration)).crossfadeout(0.8)


def _rgb_to_hex(color: Tuple[int, int, int] | None) -> str:
    if color is None:
        return "#FFFFFF"
    return "#{:02x}{:02x}{:02x}".format(*color)


SCENES: List[Dict] = [
    {
        "name": "Problème",
        "start": 0.0,
        "duration": 10.0,
        "background": PALETTE["deep_blue"],
        "texts": [
            {
                "text": "Votre site web est une jolie vitrine...\nqui n'attire aucun client ?",
                "font": HEADLINE_FONT,
                "fontsize": 88,
                "color": PALETTE["warm_white"],
                "start_offset": 0.2,
                "duration": 6.8,
                "start_pos": (-0.6, 0.18),
                "end_pos": (0.08, 0.18),
                "move_duration": 1.1,
            },
            {
                "text": "Vous vous sentez invisible sur Google malgré tous vos efforts ?",
                "font": BODY_FONT,
                "fontsize": 60,
                "color": PALETTE["neo_green"],
                "start_offset": 3.0,
                "duration": 6.0,
                "start_pos": (1.2, 0.42),
                "end_pos": (0.08, 0.44),
                "move_duration": 1.0,
            },
        ],
        "accents": [
            {
                "color": PALETTE["violet"],
                "width": VIDEO_SIZE[0] * 0.65,
                "height": VIDEO_SIZE[1] * 0.18,
                "start_offset": 0.0,
                "duration": 10.0,
                "start_pos": (0.7, -0.18),
                "end_pos": (0.65, 0.05),
                "move_duration": 2.0,
                "opacity": 0.12,
                "rotation": -12,
            },
            {
                "color": PALETTE["neo_green"],
                "width": VIDEO_SIZE[0] * 0.08,
                "height": VIDEO_SIZE[1] * 0.4,
                "start_offset": 1.0,
                "duration": 9.0,
                "start_pos": (0.85, 1.2),
                "end_pos": (0.82, 0.72),
                "move_duration": 1.8,
                "opacity": 0.18,
                "rotation": 8,
            },
        ],
    },
    {
        "name": "Solution",
        "start": 10.0,
        "duration": 15.0,
        "background": PALETTE["midnight"],
        "texts": [
            {
                "text": "Moi c'est Majoie, consultante SEO.",
                "font": HEADLINE_FONT,
                "fontsize": 82,
                "color": PALETTE["neo_green"],
                "start_offset": 0.4,
                "duration": 6.5,
                "start_pos": (-0.5, 0.16),
                "end_pos": (0.08, 0.18),
                "move_duration": 1.0,
            },
            {
                "text": "J'aide les entreprises à transformer leur site en véritable aimant à prospects, grâce à un audit complet de votre référencement.",
                "font": BODY_FONT,
                "fontsize": 54,
                "color": PALETTE["warm_white"],
                "start_offset": 2.4,
                "duration": 10.0,
                "start_pos": (1.1, 0.46),
                "end_pos": (0.08, 0.44),
                "move_duration": 1.2,
                "line_height": -5,
            },
        ],
        "accents": [
            {
                "color": PALETTE["sky"],
                "width": VIDEO_SIZE[0] * 0.9,
                "height": VIDEO_SIZE[1] * 0.02,
                "start_offset": 1.0,
                "duration": 14.0,
                "start_pos": (-0.4, 0.35),
                "end_pos": (0.05, 0.36),
                "move_duration": 1.5,
                "opacity": 0.6,
            },
            {
                "color": PALETTE["violet"],
                "width": VIDEO_SIZE[0] * 0.12,
                "height": VIDEO_SIZE[1] * 0.12,
                "start_offset": 0.6,
                "duration": 12.0,
                "start_pos": (0.85, 0.12),
                "end_pos": (0.78, 0.18),
                "move_duration": 2.2,
                "opacity": 0.35,
            },
        ],
    },
    {
        "name": "Résultat",
        "start": 25.0,
        "duration": 15.0,
        "background": PALETTE["deep_blue"],
        "texts": [
            {
                "text": "L'objectif ? Que la page 1 de Google vous envoie chaque mois un flux régulier de visiteurs qualifiés.",
                "font": HEADLINE_FONT,
                "fontsize": 72,
                "color": PALETTE["warm_white"],
                "start_offset": 0.3,
                "duration": 8.0,
                "start_pos": (1.2, 0.18),
                "end_pos": (0.08, 0.2),
                "move_duration": 1.0,
            },
            {
                "text": "Des prospects prêts à devenir vos clients, sans publicité coûteuse.",
                "font": BODY_FONT,
                "fontsize": 58,
                "color": PALETTE["neo_green"],
                "start_offset": 2.6,
                "duration": 9.5,
                "start_pos": (-0.6, 0.5),
                "end_pos": (0.08, 0.5),
                "move_duration": 1.2,
            },
        ],
        "accents": [
            {
                "color": PALETTE["neo_green"],
                "width": VIDEO_SIZE[0] * 0.14,
                "height": VIDEO_SIZE[1] * 0.5,
                "start_offset": 0.0,
                "duration": 14.5,
                "start_pos": (0.05, 1.1),
                "end_pos": (0.04, 0.6),
                "move_duration": 2.0,
                "opacity": 0.16,
                "rotation": -6,
            },
            {
                "color": PALETTE["violet"],
                "width": VIDEO_SIZE[0] * 0.2,
                "height": VIDEO_SIZE[1] * 0.2,
                "start_offset": 1.2,
                "duration": 12.0,
                "start_pos": (0.78, 0.65),
                "end_pos": (0.7, 0.58),
                "move_duration": 1.6,
                "opacity": 0.25,
            },
        ],
    },
    {
        "name": "Appel à l'action",
        "start": 40.0,
        "duration": 20.0,
        "background": PALETTE["midnight"],
        "texts": [
            {
                "text": "Si le sujet vous parle, envoyez-moi un message avec « AUDIT »",
                "font": HEADLINE_FONT,
                "fontsize": 78,
                "color": PALETTE["neo_green"],
                "start_offset": 0.2,
                "duration": 9.5,
                "start_pos": (-0.5, 0.2),
                "end_pos": (0.08, 0.22),
                "move_duration": 1.0,
            },
            {
                "text": "Je vous renvoie les 3 points clés à analyser sur votre site.",
                "font": BODY_FONT,
                "fontsize": 58,
                "color": PALETTE["warm_white"],
                "start_offset": 2.4,
                "duration": 11.0,
                "start_pos": (1.1, 0.4),
                "end_pos": (0.08, 0.42),
                "move_duration": 1.4,
            },
            {
                "text": "Majoie • Consultante SEO",
                "font": ACCENT_FONT,
                "fontsize": 64,
                "color": PALETTE["soft_gray"],
                "start_offset": 8.5,
                "duration": 11.0,
                "start_pos": (0.5, 0.78),
                "end_pos": (0.5, 0.75),
                "move_duration": 1.8,
            },
        ],
        "accents": [
            {
                "color": PALETTE["sky"],
                "width": VIDEO_SIZE[0] * 0.92,
                "height": VIDEO_SIZE[1] * 0.015,
                "start_offset": 0.4,
                "duration": 19.0,
                "start_pos": (1.05, 0.32),
                "end_pos": (0.04, 0.32),
                "move_duration": 1.2,
                "opacity": 0.7,
            },
            {
                "color": PALETTE["violet"],
                "width": VIDEO_SIZE[0] * 0.16,
                "height": VIDEO_SIZE[1] * 0.16,
                "start_offset": 4.0,
                "duration": 16.0,
                "start_pos": (0.12, 0.08),
                "end_pos": (0.15, 0.12),
                "move_duration": 3.0,
                "opacity": 0.28,
            },
        ],
    },
]


def make_video(output_path: str = "majoie_seo_motion.mp4") -> None:
    """Build and export the full composite video."""
    clips = []

    for scene in SCENES:
        scene_start = scene["start"]
        scene_duration = scene["duration"]

        # Background block for the scene
        background = (
            ColorClip(size=VIDEO_SIZE, color=scene["background"])
            .set_start(scene_start)
            .set_duration(scene_duration)
        )
        clips.append(background)

        for accent in scene.get("accents", []):
            clips.append(
                build_accent_clip(
                    color=accent["color"],
                    width=accent["width"],
                    height=accent["height"],
                    start_time=scene_start + accent.get("start_offset", 0.0),
                    duration=accent["duration"],
                    start_pos=accent["start_pos"],
                    end_pos=accent["end_pos"],
                    move_duration=accent["move_duration"],
                    opacity=accent.get("opacity", 1.0),
                    rotation=accent.get("rotation", 0.0),
                )
            )

        for text_cfg in scene["texts"]:
            clips.append(
                build_text_clip(
                    text=text_cfg["text"],
                    font=text_cfg["font"],
                    fontsize=text_cfg["fontsize"],
                    color=text_cfg["color"],
                    start_time=scene_start + text_cfg["start_offset"],
                    duration=text_cfg["duration"],
                    start_pos=text_cfg["start_pos"],
                    end_pos=text_cfg["end_pos"],
                    move_duration=text_cfg["move_duration"],
                    line_height=text_cfg.get("line_height"),
                    stroke_width=text_cfg.get("stroke_width", 0),
                    stroke_color=text_cfg.get("stroke_color"),
                    background_opacity=text_cfg.get("background_opacity", 0.0),
                )
            )

    composite = CompositeVideoClip(clips, size=VIDEO_SIZE).set_duration(VIDEO_DURATION)

    composite = composite.fx(vfx.fadein, 0.6).fx(vfx.fadeout, 0.8)
    composite.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        preset="medium",
        bitrate="6000k",
        audio=False,
        threads=4,
    )


if __name__ == "__main__":
    make_video()

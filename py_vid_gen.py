import os
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips
)

from moviepy.audio.AudioClip import CompositeAudioClip

from .const import (
    COLOR_MAPS,
    FONT,
    FONT_SIZE,
    H,
    W
)


def get_asset_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


BEEP_PATH = get_asset_path("beep.mp3")
ALARM_PATH = get_asset_path("beep.mp3")


def get_color(color_name):
    if color_name in COLOR_MAPS:
        return COLOR_MAPS[color_name]
    return (0, 0, 0)


def generate_beeps(total_time, interval_list):
    beeps = []
    i = 0
    t = interval_list[i][1]
    while t < total_time:
        beep = AudioFileClip(BEEP_PATH).with_start(t)
        beeps.append(beep)
        i += 1 if i < len(interval_list) else 0
        t += interval_list[i][1]
    return beeps


def generate_timer_video(
    video_name="test_timer",
    total_video_length=130,  # 2:10 in seconds
    with_prepare=True,
    prepare_duration=10,
    prepare_text="PREPARE",
    intervals=True,
    interval_list=[("go", 30, "green"), ("no", 30, "red")],
    intervals_repeat=2
):
    clips = []

    if with_prepare:
        prepare_clip = ColorClip(
            (W, H),
            color=get_color("orange"),
            duration=prepare_duration
        )
        prepare_text = TextClip(
            text=prepare_text, font_size=FONT_SIZE, color="black", font=FONT
        ).with_position("center").with_duration(prepare_duration)
        prepare = CompositeVideoClip([prepare_clip, prepare_text])
        clips.append(prepare)

    main_duration = total_video_length - 10
    if interval_list:
        interval_clips = []
        total_time = 0
        current_repeat = 0

        while total_time < main_duration and current_repeat < intervals_repeat:
            for text, sec, bg_color in interval_list:
                if total_time >= main_duration:
                    break
                clip_duration = min(sec, main_duration - total_time)
                bg = ColorClip(
                    (W, H),
                    color=get_color(bg_color),
                    duration=clip_duration
                )
                label = TextClip(
                    text=text.upper(),
                    font_size=FONT_SIZE,
                    color="white",
                    font=FONT
                ).with_position("center").with_duration(clip_duration)
                interval_clips.append(
                    CompositeVideoClip([bg, label]).with_start(total_time)
                )
                total_time += clip_duration
            current_repeat += 1

        beeps = generate_beeps(total_time, interval_list)

        base = concatenate_videoclips(interval_clips)
        if beeps:
            audio_clips = [
                clip for clip in [base.audio] + beeps
                if clip is not None
            ]
            full_audio = CompositeAudioClip(audio_clips)
            base = base.with_audio(full_audio)
        clips.append(base)

    final_video = concatenate_videoclips(clips)

    alarms = [
        AudioFileClip(
            ALARM_PATH
        ).with_start(total_video_length - 1 + i * 0.5) for i in range(3)
    ]
    final_audio = CompositeAudioClip(
        [final_video.audio] + alarms if final_video.audio else alarms
    )
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        video_name + ".mp4", fps=24, codec="libx264", audio_codec="aac"
    )

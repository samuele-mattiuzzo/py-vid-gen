import os
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    concatenate_videoclips,
)
from moviepy.audio.AudioClip import CompositeAudioClip
from const import COLOR_MAPS, FONT, FONT_SIZE, H, W


def get_asset_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


BEEP_PATH = ALARM_PATH = get_asset_path("beep.mp3")


def get_color(color_name):
    return COLOR_MAPS.get(color_name.lower(), (0, 0, 0))


def countdown_text_clip(interval_duration, interval_text, round_info=""):
    clips = []
    for t in range(interval_duration, 0, -1):
        mins, secs = divmod(t, 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

        text = f"{interval_text}\n{time_str}"
        if round_info:
            text = f"{interval_text}\n{time_str}\n{round_info}"

        countdown_clip = (
            TextClip(
                text=text,
                font=FONT,
                font_size=FONT_SIZE,
                color="white",
                size=(W, H),
                method="caption",
            )
            .with_position("center")
            .with_duration(1)
        )
        clips.append(countdown_clip)
    return concatenate_videoclips(clips)


def generate_timer_video(
    video_name="test_timer",
    total_video_length=145,
    with_prepare=True,
    prepare_duration=10,
    prepare_text="PREPARE",
    interval_list=[("WORK", "green", 45), ("REST", "red", 45)],
    intervals_repeat=2,
):
    clips = []

    if with_prepare:
        bg = ColorClip((W, H), color=get_color("orange"), duration=prepare_duration)
        txt = (
            TextClip(
                text=prepare_text,
                font=FONT,
                font_size=FONT_SIZE,
                color="black",
                size=(W, H),
                method="caption",
            )
            .with_position("center")
            .with_duration(prepare_duration)
        )
        clips.append(CompositeVideoClip([bg, txt]))
        prepare_beep = AudioFileClip(BEEP_PATH).with_start(prepare_duration - 1)
    else:
        prepare_beep = None

    main_duration = total_video_length - (prepare_duration if with_prepare else 0)

    if interval_list:
        interval_clips = []
        total_time = 0
        current_repeat = 0

        while total_time < main_duration and current_repeat < intervals_repeat:
            for text, bg_color, sec in interval_list:
                if total_time >= main_duration:
                    break

                sec = int(sec)
                clip_duration = min(sec, main_duration - total_time)

                bg = ColorClip(
                    (W, H), color=get_color(bg_color), duration=clip_duration
                )

                round_info = (
                    f"Round {current_repeat + 1} / {intervals_repeat}"
                    if intervals_repeat > 1
                    else ""
                )
                countdown = countdown_text_clip(clip_duration, text.upper(), round_info)

                interval_clips.append(
                    CompositeVideoClip([bg, countdown]).with_start(total_time)
                )

                total_time += clip_duration
            current_repeat += 1

        base = concatenate_videoclips(interval_clips)

        beeps = [
            AudioFileClip(BEEP_PATH).with_start(clip.start + clip.duration - 1)
            for clip in interval_clips
        ]
        if prepare_beep:
            beeps.insert(0, prepare_beep)

        audio_clips = [clip for clip in [base.audio] + beeps if clip is not None]
        base = base.with_audio(CompositeAudioClip(audio_clips))
        clips.append(base)

    final_video = concatenate_videoclips(clips)

    alarms = [
        AudioFileClip(ALARM_PATH).with_start(total_video_length - 1 + i * 0.5)
        for i in range(3)
    ]
    final_audio = CompositeAudioClip(
        [final_video.audio] + alarms if final_video.audio else alarms
    )
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        video_name + ".mp4", fps=24, codec="libx264", audio_codec="aac"
    )

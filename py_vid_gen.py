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
    """Get absolute path to an asset in the same folder as this file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


BEEP_PATH = ALARM_PATH = get_asset_path("beep.mp3")


def get_color(color_name):
    """Return RGB tuple for a color name, default black."""
    return COLOR_MAPS.get(color_name.lower(), (0, 0, 0))


def generate_beeps(total_time, interval_list):
    """Generate beep audio clips at the end of each interval."""
    beeps = []
    if not os.path.isfile(BEEP_PATH):
        return beeps

    current_time = 0
    for text, _, sec in interval_list:
        sec = int(sec)
        if current_time + sec > total_time:
            break
        beep = AudioFileClip(BEEP_PATH).with_start(current_time + sec - 1)
        beeps.append(beep)
        current_time += sec
    return beeps


def generate_timer_video(
    video_name="test_timer",
    total_video_length=145,
    with_prepare=True,
    prepare_duration=10,
    prepare_text="PREPARE",
    interval_list=[("go", 45, "green"), ("rest", 45, "red")],
    intervals_repeat=2,
):
    clips = []

    if with_prepare:
        prepare_clip = ColorClip(
            (W, H), color=get_color("orange"), duration=prepare_duration
        )
        prepare_text_clip = (
            TextClip(text=prepare_text, font_size=FONT_SIZE, color="black", font=FONT)
            .with_position("center")
            .with_duration(prepare_duration)
        )
        clips.append(CompositeVideoClip([prepare_clip, prepare_text_clip]))

    main_duration = total_video_length - (prepare_duration if with_prepare else 0)

    if interval_list:
        interval_clips = []
        total_time = 0
        current_repeat = 0

        while total_time < main_duration and current_repeat < intervals_repeat:
            for text, bg_color, sec in interval_list:
                if total_time >= main_duration:
                    break
                clip_duration = min(int(sec), int(main_duration) - int(total_time))
                bg = ColorClip(
                    (W, H), color=get_color(bg_color), duration=clip_duration
                )
                label = (
                    TextClip(
                        text=text.upper(), font_size=FONT_SIZE, color="white", font=FONT
                    )
                    .with_position("center")
                    .with_duration(clip_duration)
                )
                interval_clips.append(
                    CompositeVideoClip([bg, label]).with_start(total_time)
                )
                total_time += clip_duration
            current_repeat += 1

        beeps = generate_beeps(total_time, interval_list)
        base = concatenate_videoclips(interval_clips)
        if beeps:
            audio_clips = [clip for clip in [base.audio] + beeps if clip is not None]
            base = base.with_audio(CompositeAudioClip(audio_clips))
        clips.append(base)

    final_video = concatenate_videoclips(clips)

    # Final 3 alarms at the end
    alarms = [
        AudioFileClip(ALARM_PATH).with_start(total_video_length - 1 + i * 0.5)
        for i in range(3)
    ]
    final_audio = CompositeAudioClip(
        [final_video.audio] + alarms if final_video.audio is not None else alarms
    )
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        video_name + ".mp4", fps=24, codec="libx264", audio_codec="aac"
    )

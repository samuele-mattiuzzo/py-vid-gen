import os
from moviepy.editor import (
    ColorClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    concatenate_videoclips,
)
from moviepy.config import change_settings

# IMPORTANT: Set the path to your ImageMagick binary.
# If you don't have it, you can download it from:
# https://imagemagick.org/script/download.php
# After installation, find the path and paste it here.
# Example for Windows:
# change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe"})
# Example for macOS/Linux:
# change_settings({"IMAGEMAGICK_BINARY": "/usr/local/bin/magick"})

# --- Configuration ---
INPUT_FILE = "timers.txt"
OUTPUT_DIR = "videos"
FINAL_SOUND_FILE = "alarm.mp3"  # You must provide a short audio file here.
WIDTH = 1920
HEIGHT = 1080
FPS = 30
FONT_COLOR = "white"
BACKGROUND_COLOR = (18, 18, 18)  # Dark grey/black
FINAL_SCREEN_DURATION = 5  # seconds


def parse_timers(file_path):
    """
    Parses the timers from a text file.
    The file format is:
    [category]
    timer_name,minutes,seconds
    timer_name,minutes,seconds
    """
    timers = {}
    current_category = None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("[") and line.endswith("]"):
                    current_category = line[1:-1].strip().replace(" ", "_").lower()
                    if current_category not in timers:
                        timers[current_category] = []
                elif current_category and "," in line:
                    parts = line.split(",")
                    if len(parts) == 3:
                        name = parts[0].strip()
                        try:
                            minutes = int(parts[1].strip())
                            seconds = int(parts[2].strip())
                            timers[current_category].append(
                                {"name": name, "minutes": minutes, "seconds": seconds}
                            )
                        except ValueError:
                            print(
                                f"Skipping malformed line: '{line}' in category '{current_category}'"
                            )
    except FileNotFoundError:
        print(f"Error: The input file '{file_path}' was not found.")
        return None
    return timers


def format_time(total_seconds):
    """Formats seconds into MM:SS or H:MM:SS format."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def create_timer_video(timer_data, output_path, final_sound_path):
    """
    Creates a single timer video with a countdown.
    """
    timer_name = timer_data["name"]
    total_seconds = (timer_data["minutes"] * 60) + timer_data["seconds"]

    print(f"Creating video for '{timer_name}' ({format_time(total_seconds)})")

    # Create a black background clip
    background = ColorClip(
        (WIDTH, HEIGHT),
        color=BACKGROUND_COLOR,
        duration=total_seconds + FINAL_SCREEN_DURATION,
    )

    # Create the title clip that stays throughout the countdown
    title_clip = TextClip(
        timer_name,
        fontsize=100,
        color=FONT_COLOR,
        font="Arial-Bold",
        size=(WIDTH, None),
    ).set_position(("center", 200))

    # Create the countdown clock clips
    time_clips = []
    for t in range(total_seconds, -1, -1):
        time_text = format_time(t)
        clip = (
            TextClip(time_text, fontsize=300, color=FONT_COLOR, font="Arial-Bold")
            .set_position(("center", "center"))
            .set_duration(1)
        )
        time_clips.append(clip)

    countdown_video = concatenate_videoclips(time_clips, method="compose")

    # Create the final "Timer Complete!" screen
    final_text_clip = (
        TextClip(
            "Timer Complete!",
            fontsize=120,
            color="red",
            font="Arial-Bold",
            size=(WIDTH, None),
        )
        .set_position(("center", "center"))
        .set_duration(FINAL_SCREEN_DURATION)
    )

    # Combine all video clips
    final_video = concatenate_videoclips([countdown_video, final_text_clip])

    # Composite the title over the final video and add the sound effect
    try:
        # Load the final sound effect and set it to play at the end
        final_sound_clip = AudioFileClip(final_sound_path).set_start(total_seconds)

        final_clip = CompositeVideoClip(
            [background.set_duration(final_video.duration), title_clip, final_video]
        ).set_audio(final_sound_clip)

    except Exception as e:
        print(
            f"Warning: Could not load audio file '{final_sound_path}'. Proceeding without sound. Error: {e}"
        )
        final_clip = CompositeVideoClip(
            [background.set_duration(final_video.duration), title_clip, final_video]
        )

    # Write the output file
    final_clip.write_videofile(output_path, fps=FPS, codec="libx264", audio_codec="aac")
    print(f"Video saved to '{output_path}'")


def main():
    """
    Main function to orchestrate the video generation process.
    """
    print("Starting video generation process...")

    # Create the main output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timers = parse_timers(INPUT_FILE)
    if not timers:
        print("No timers found or file could not be read. Exiting.")
        return

    for category, timer_list in timers.items():
        category_dir = os.path.join(OUTPUT_DIR, category)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)

        print(f"\nProcessing category: '{category}'")
        for timer in timer_list:
            safe_name = (
                timer["name"].replace(" ", "_").replace("/", "").replace(":", "")
            )
            output_path = os.path.join(
                category_dir,
                f"{safe_name}_{timer['minutes']:02d}m{timer['seconds']:02d}s.mp4",
            )
            create_timer_video(timer, output_path, FINAL_SOUND_FILE)

    print("\nVideo generation complete!")


if __name__ == "__main__":
    # Create a dummy timers.txt file and an alarm.mp3 file for demonstration
    # You will need to replace these with your actual files.
    with open("timers.txt", "w", encoding="utf-8") as f:
        f.write("# This is the timers configuration file\n\n")
        f.write("[food_timers]\n")
        f.write("Pasta,10,0\n")
        f.write("Steak (rare),3,30\n")
        f.write("Boiled Eggs,7,0\n\n")
        f.write("[workout_timers]\n")
        f.write("Tabata (20s/10s),4,0\n")
        f.write("Sprint (30s),0,30\n")
        f.write("Plank Challenge,1,30\n\n")
        f.write("[white_noise]\n")
        f.write("Sleep (6 hours),360,0\n")
        f.write("Sleep (8 hours),480,0\n")
        f.write("Meditation,15,0\n")

    # Create a dummy audio file using pydub (requires ffmpeg)
    # This is just so the script can run without a user-provided file.
    try:
        from pydub import AudioSegment

        print("Creating a dummy alarm sound...")
        # Create a simple 2-second sine wave tone at 440 Hz (A4)
        simple_tone = AudioSegment.from_mono_audiosegments(
            AudioSegment.silent(duration=1900),
            AudioSegment.silent(duration=100)
            .set_frame_rate(44100)
            .high_pass_filter(440, 0.001),
        ).fade_out(100)
        simple_tone.export("alarm.mp3", format="mp3")
        print("Dummy 'alarm.mp3' created.")
    except ImportError:
        print("\nPydub is not installed. Please install it with 'pip install pydub'")
        print(
            "Then provide your own 'alarm.mp3' file or the script will run without sound."
        )
    except Exception as e:
        print(
            f"\nCould not create dummy audio file. Please provide your own 'alarm.mp3'. Error: {e}"
        )

    main()

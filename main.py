import ast
import shutil
import os

from py_vid_gen import generate_timer_video


CSVS = [
    # ("test_timers.csv", "pasta"),
    # ("workout_timers.csv", 'workout'),
    ("pasta_timers.csv", "pasta")
    # "white_noise_sleep_timers.csv
]


def batch_generate_from_csv(csv_path="test_timers.csv", move_folder=None):
    """
    Generate videos from a CSV file.
    Expects interval_list as Python-style list: "[('WORK','green',60), ...]"
    """
    import csv

    def to_video_name(title):
        return title.lower().replace(" ", "_").replace(",", "_").replace('"', "")

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print("Generating video for:", row["name"])
            interval_list = ast.literal_eval(row["interval_list"])
            generate_timer_video(
                video_name=to_video_name(row["name"]),
                total_video_length=int(row["total_video_length"]),
                prepare_duration=int(row["prepare_duration"]),
                with_prepare=True,
                intervals_repeat=int(row["intervals_repeat"]),
                interval_list=interval_list,
            )
            print("Video generated:", row["name"])
            if move_folder:
                video_name = to_video_name(row["name"]) + ".mp4"
                dest_path = os.path.join(os.getcwd(), "output", move_folder, video_name)
                shutil.move(os.path.join(os.getcwd(), video_name), dest_path)
                print(f"Moved {video_name} to {move_folder}")


if __name__ == "__main__":
    for csv_name, move_folder in CSVS:
        print(f"Processing {csv_name}...")
        batch_generate_from_csv(csv_name, move_folder)

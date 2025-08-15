import ast
from py_vid_gen import generate_timer_video

TEST = False  # Set to False to enable batch CSV-based generation


def batch_generate_from_csv(csv_path="timers.csv"):
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


if __name__ == "__main__":
    if TEST:
        generate_timer_video()
    else:
        batch_generate_from_csv()

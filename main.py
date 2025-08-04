from py_vid_gen import generate_timer_video

TEST = True  # Set to False to enable batch CSV-based generation


def batch_generate_from_csv(csv_path="timers.csv"):
    # Placeholder for future CSV-based batch generator
    pass


if __name__ == "__main__":
    if TEST:
        generate_timer_video()
    else:
        batch_generate_from_csv()

import os
from pathlib import Path
from time import sleep

from dotenv import load_dotenv

import src.notepad_driver as note
import src.screen as sc
import src.window_validator as win
from config import ANNOTATION_DIR, PROJECT_DIR
from src.builder import build_client, build_clients, build_strategy
from src.data_source import fetch_posts
from src.grounder.roles.grounder import Grounder, TargetNotVisibleError

load_dotenv()


def process_post(
    post: dict,
    output_dir: Path,
):
    clients = build_clients([("openrouter", None)])
    grounder = build_strategy("direct", Grounder(clients))
    note.ensure_clean_launch()
    sleep(1)
    sc.navigateToDesktop()
    sleep(0.6)
    screenshot = sc.captureScreenshot()
    work_area = sc.get_work_area_viewport()
    cropped = sc.crop_to_viewport(screenshot, work_area)
    target_description = "Notepad text editor application icon, a small image shows lines and a note used to launch Microsoft Notepad"
    try:
        result = grounder.ground(cropped, target_description)
        local_bbox = result.bbox
    except TargetNotVisibleError:
        print("[main] Notepad icon not on desktop — launching directly")
        note.launch_directly()
    else:
        bbox = work_area.to_screen(local_bbox)
        sc.save_annotated_screenshot(
            screenshot,
            bbox,
            ANNOTATION_DIR / f"post_{post['id']}_annotated.png",
        )
        x, y = bbox.center

        sc.moveTo(x, y, 0.3)
        sc.doubleClick()
    if not win.isAppFoused(("Untitled", "Notepad")):
        print("Error Notepad is not opened")

    sleep(0.5)
    note.type_post_content(post["title"], post["body"])
    sleep(1)
    filename = f"post_{post['id']}.txt"
    note.save_as(filename, output_dir)
    note.close(filename)


def main():
    posts = fetch_posts(10)
    for post in posts:
        process_post(post, PROJECT_DIR)
        sleep(5)
        # take screenshot
        # ground the notepad
        # doubleclick on the notepad
        # validate notepad window
        # format post
        # write the post
        # save the file
        # close notepad


if __name__ == "__main__":
    main()

from datetime import datetime
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
import yaml
import typer

import subprocess
import os
import tempfile
import uuid

CONFIG_FILE = "config.yml"

PROJECT = "project"
URL = "url"
ID = "id"
LABEL = "Download .zip file"

USER = "user"
EMAIL = "email"
PASSWORD = "password"

BACKUP = "backup"

DOWNLOAD = "download"
PATH = "path"

GIT = "git"

RSYNC = "rsync"
SERVER = "server"
PORT = "port"
DESTINATION = "destination"

app = typer.Typer()


def read_config():
    with open(CONFIG_FILE, "r") as f:
        config_content = yaml.load(f, Loader=yaml.FullLoader)
    return config_content


def _helper(path: str):
    if path.endswith("/"):
        path = path[:-1]
    url = config[PROJECT][URL]
    if url.endswith("/"):
        url = url[:-1]
    project_id = config[PROJECT][ID]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.locator('input[name="email"]').fill(config[USER][EMAIL])
        page.locator('input[name="password"]').fill(config[USER][PASSWORD])
        page.locator('button[type="submit"]').click()
        page.wait_for_url(f"{url}/project")

        with page.expect_download() as download_info:
            selector = f'td:has(input[data-project-id="{project_id}"]) ~ td button[aria-label="{LABEL}"]'
            page.locator(selector).click()
        _download = download_info.value
        result = f"{path}/{datetime.now().strftime('%Y%m%d%H%M%S')}-{_download.suggested_filename}"
        _download.save_as(result)
        browser.close()
    return result


@app.command()
def download():
    typer.echo("Downloading...")
    _helper(config[BACKUP][DOWNLOAD][PATH])
    typer.echo("Download successfully!")


@app.command()
def git():
    typer.echo("Backup using Git...")
    git_path = config[BACKUP][GIT][PATH]
    result = _helper(git_path)
    with ZipFile(result, "r") as zip_ref:
        zip_ref.extractall(git_path)
    os.remove(result)
    subprocess.run(["git", "add", "."], cwd=git_path)
    subprocess.run(["git", "commit", "-m", "Backup"], cwd=git_path)
    subprocess.run(["git", "push"], cwd=git_path)
    typer.echo("Backup using Git successfully!")


@app.command()
def rsync():
    typer.echo("Backup using rsync...")
    rsync_path = tempfile.gettempdir()
    result = _helper(rsync_path)
    extract_path = f"{rsync_path}/overleaf-{uuid.uuid4()}"
    with ZipFile(result, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(result)
    subprocess.run(
        [
            "rsync",
            "-rvz",
            "-e",
            f"ssh -p {config[BACKUP][RSYNC][PORT]}",
            extract_path + "/",
            f"{config[BACKUP][RSYNC][SERVER]}:{config[BACKUP][RSYNC][DESTINATION]}",
        ],
    )
    os.remove(extract_path)
    typer.echo("Backup using rsync successfully!")


if __name__ == "__main__":
    config = read_config()
    app()

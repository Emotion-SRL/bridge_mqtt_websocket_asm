import datetime
import subprocess
from subprocess import Popen

import click

image_name = "service-mqtt-bridge"


@click.command()
@click.option('--latest', is_flag=True, help="build image with latest tag")
@click.option(
    "--tag",
    type=str,
    default="none",
    help="The tag of image.",
)
def docker_build(latest=False, tag="none"):
    version_name = Popen("git rev-parse --abbrev-ref HEAD & git rev-parse --short HEAD", shell=True, stdout=subprocess.PIPE).communicate()[0].decode().strip()
    version_name = version_name.replace("\n", "-")
    modified = Popen("git status --porcelain", shell=True, stdout=subprocess.PIPE).communicate()[0].decode().strip()
    if modified != "":
        version_name += "-Modified"
    today = datetime.date.today()
    tag_daily = f"{today.year}{today.month}{today.day}"
    daily_tag = tag_daily
    tag_latest_or_test = "latest" if latest else "test"
    extra_tag = tag if tag != "none" else ""
    click.echo(
        f"Build image with tag: {daily_tag}, {tag_latest_or_test}, {extra_tag}")
    if extra_tag != "":
        extra_tag = f"-t emotionsrl/{image_name}:{extra_tag} "
    Popen(f"docker buildx build --platform linux/amd64 --build-arg GIT_COMMIT_VERSION={version_name} " +
          f"-t emotionsrl/{image_name}:{daily_tag} " +
          f"-t emotionsrl/{image_name}:{tag_latest_or_test} " +
          f"{extra_tag} " + "-f scripts/Dockerfile --push .",
          shell=True,
          ).wait()


if __name__ == "__main__":
    docker_build()

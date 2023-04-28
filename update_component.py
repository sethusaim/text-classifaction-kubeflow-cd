import os

import yaml

new_tag = os.environ["DOCKERTAG"]

file_name = os.path.join("manifests", "components", os.environ["COMP_FILE"])


def update_yaml():
    try:
        with open(file_name, "r") as f:
            content = yaml.safe_load(f)

        old_image = content["spec"]["steps"][0]["image"]

        tagless_image = old_image.split(":")[0]

        new_image = tagless_image + ":" + str(new_tag)

        content["spec"]["steps"][0]["image"] = new_image

        with open(file_name, "w") as fp:
            yaml.safe_dump(content, fp, sort_keys=False)

    except Exception as e:
        raise e


if __name__ == "__main__":
    update_yaml()

import os
import uuid
import shutil


def save_upload_file(upload_file):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    filename = (
        f"uploads/{uuid.uuid4()}.jpg"
    )

    with open(
        filename,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            upload_file.file,
            buffer
        )

    return filename
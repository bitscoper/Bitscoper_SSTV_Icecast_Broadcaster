#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# By Abdullah As-Sadeed

if __name__ == "__main__":
    from tempfile import NamedTemporaryFile
    import io
    import os
    import subprocess
    import sys
    import time

    if len(sys.argv) != 5:
        print(
            "Usage: python main.py <image_path> <icecast_host> <icecast_port> <icecast_password>"
        )
        sys.exit(1)

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print("FFmpeg is available.")

    except subprocess.CalledProcessError:
        print("FFmpeg could not be checked!")
        sys.exit(1)

    except FileNotFoundError:
        print("FFmpeg has not been found in the PATH!")
        sys.exit(1)

    required_packages = ["Pillow", "pydub", "pysstv"]

    def install_package(package):
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    def safe_import(package_name):
        try:
            if package_name == "Pillow":
                package = __import__("PIL")
            else:
                package = __import__(package_name)

            print(f"The {package_name} package is available.")
            return package

        except ImportError:
            print(f"Could not find the {package_name} package. Installing ...")
            install_package(package_name)

            if package_name == "Pillow":
                package = __import__("PIL")
            else:
                package = __import__(package_name)

            print(f"The {package_name} package has been installed and is available.")
            return package

    PIL = safe_import("Pillow")
    pysstv = safe_import("pysstv")
    AudioSegment = safe_import("pydub").AudioSegment

    from PIL import Image

    from pysstv.color import (
        MartinM1,
        MartinM2,
        PD120,
        PD160,
        PD180,
        PD240,
        PD290,
        PD90,
        PasokonP3,
        PasokonP5,
        PasokonP7,
        Robot36,
        ScottieDX,
        ScottieS1,
        ScottieS2,
        WraaseSC2120,
        WraaseSC2180,
    )
    from pysstv.grayscale import Robot8BW, Robot24BW

    SSTV_MODES = [
        MartinM1,
        MartinM2,
        PD120,
        PD160,
        PD180,
        PD240,
        PD290,
        PD90,
        PasokonP3,
        PasokonP5,
        PasokonP7,
        Robot24BW,
        Robot36,
        Robot8BW,
        ScottieDX,
        ScottieS1,
        ScottieS2,
        WraaseSC2120,
        WraaseSC2180,
    ]

    image_path = sys.argv[1]
    icecast_host = sys.argv[2]
    icecast_port = sys.argv[3]
    icecast_password = sys.argv[4]

    try:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f'Could not find the "{image_path}" file!')
            sys.exit(1)

        image = Image.open(image_path)
        print(f"Opened the image: {image_path}")

    except FileNotFoundError as error:
        print(error)
        sys.exit(1)

    except OSError as error:
        print(error)
        sys.exit(1)

    SAMPLES_PER_SECOND = 48000
    BITS_PER_SAMPLE = 16
    CHANNELS = 1
    VOX_ENABLED = True

    progress = 0

    for mode_class in SSTV_MODES:
        mode_name = mode_class.__name__
        print(f"Generating {mode_name} ...")

        wav_buffer = io.BytesIO()
        sstv = mode_class(
            image=image, samples_per_sec=SAMPLES_PER_SECOND, bits=BITS_PER_SAMPLE
        )
        sstv.nchannels = CHANNELS
        sstv.vox_enabled = VOX_ENABLED
        sstv.write_wav(wav_buffer)

        wav_buffer.seek(0)
        audio_segment = AudioSegment.from_wav(wav_buffer)

        print(f"Streaming {mode_name} ...")

        with NamedTemporaryFile(suffix=".ogg", delete=True) as temporary_file:
            audio_segment.export(temporary_file.name, format="opus")
            stream_command = [
                "ffmpeg",
                "-re",
                "-i",
                temporary_file.name,
                "-c:a",
                "libopus",
                "-content_type",
                "audio/ogg",
                "-f",
                "opus",
                "-vbr",
                "on",
                "-vn",
                f"icecast://source:{icecast_password}@{icecast_host}:{icecast_port}/{mode_name}_{int(time.time())}",
                "-loglevel",
                "info",
            ]

            result = subprocess.run(stream_command)

            if result.returncode != 0:
                print(
                    f"Error streaming {mode_name}. FFmpeg returned code {result.returncode}."
                )
                break

            progress += 1

    print(f"\nDone with {progress} SSTV modes.")

<div align="center">

# Bitscoper SSTV Icecast Broadcaster

A Python project that transmits images using 19 SSTV (Slow Scan Television) modes with VOX functionality through Icecast in Ogg Opus format with dynamic mount points.

</div>

## SSTV Modes

- MartinM1
- MartinM2
- PD120
- PD160
- PD180
- PD240
- PD290
- PD90
- PasokonP3
- PasokonP5
- PasokonP7
- Robot24BW
- Robot36
- Robot8BW
- ScottieDX
- ScottieS1
- ScottieS2
- WraaseSC2120
- WraaseSC2180

## Usage

```
python main.py <image_path> <icecast_host> <icecast_port> <icecast_password>
```

## Dependencies

- [FFmpeg](https://github.com/FFmpeg/FFmpeg)
- [Pillow](https://github.com/python-pillow/Pillow)
- [PySSTV](https://github.com/dnet/pySSTV)
- [pydub](https://github.com/jiaaro/pydub)

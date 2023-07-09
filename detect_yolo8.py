import argparse
import json
import logging
import sys
import textwrap
from pathlib import Path
from typing import List, NamedTuple, Optional

import pandas as pd
import ultralytics

import utils


LOGGER = logging.getLogger('detect_yolo8')

ultralytics.hub.utils.events.enabled = False  # disable telemetry


class ProgramOptions(NamedTuple):
    images_dir: Path
    output_dir: Path
    model_path: Path
    confidence: float
    iou: float
    image_size: int
    device: Optional[str]


class Label(NamedTuple):
    image: str
    label: int
    xc: float
    yc: float
    w: float
    h: float
    score: float


class Times(NamedTuple):
    image: str
    total: float


def show_progress(stopwatch: utils.Stopwatch, processed_images: int, total_images: int, detected_persons: int):
    if sys.stdout.isatty():
        utils.set_console_title(
            'YOLO8 | Image: {0} / {1} ( {2:.2f}% ) | Detected: {3} | Elapsed: {4} | Remaining: {5}'.format(
                processed_images,
                total_images,
                processed_images / total_images * 100,
                detected_persons,
                stopwatch.elapsed(seconds_rounding=int),
                utils.remaining_time(stopwatch, processed_images, total_images, seconds_rounding=int)))


def predict(options: ProgramOptions):
    LOGGER.info('Enumerate images...')
    images = sorted(utils.enum_images(options.images_dir))

    LOGGER.info(f'Image count: {len(images)}')

    LOGGER.info('Save image names to "images.txt"...')
    (options.output_dir / 'images.txt').write_text(
        '\n'.join(image.relative_to(options.images_dir).as_posix() for image in images),
        encoding='utf-8')

    metadata = {
        'task': 'detect',
        'mode': 'predict',
        'model': 'yolo8',
        'model_path': str(options.model_path),
        'images_dir': str(options.images_dir),
        'output_dir': str(options.output_dir),
        'model_parameters': {
            'confidence': options.confidence,
            'iou': options.iou,
            'image_size': options.image_size,
            },
        'device': options.device,
        }

    LOGGER.info('Save metadata to "experiment.json"...')
    (options.output_dir / 'experiment.json').write_text(
        json.dumps(metadata, indent=4), encoding='utf-8')

    labels: List[Label] = []
    times: List[Times] = []

    LOGGER.info('Load model...')
    model = ultralytics.YOLO(options.model_path)

    stopwatch = utils.Stopwatch()
    person_count = 0

    for image_num, path in enumerate(images):
        LOGGER.info(f'Process image: {path}')

        relative_path = path.relative_to(options.images_dir).as_posix()

        image_stopwatch = utils.Stopwatch()
        results = model.predict(source=path, conf=options.confidence, iou=options.iou, imgsz=options.image_size,
                                device=options.device, classes=0, verbose=False)

        times.append(Times(
            image=relative_path,
            total=image_stopwatch.elapsed_seconds()))

        for result in results:
            for ((xc, yc, w, h), conf) in zip(result.boxes.xywhn.tolist(), result.boxes.conf.tolist()):
                labels.append(Label(image=relative_path, label=0,
                                    xc=xc, yc=yc, w=w, h=h, score=conf))
                LOGGER.debug(f'Detected: box=[{xc:.4f}, {yc:.4f}, {w:.4f}, {h:.4f}] conf={conf:.4f}')
                person_count += 1

        show_progress(stopwatch, image_num + 1, len(images), person_count)

    LOGGER.info('Save labels to "labels.csv"...')
    columns = ['image', 'label', 'xc', 'yc', 'w', 'h', 'score']
    pd.DataFrame(labels, columns=columns).to_csv(options.output_dir / 'labels.csv', index=False)

    LOGGER.info('Save processing times to "times.csv"...')
    pd.DataFrame(times, columns=['image', 'total']).to_csv(options.output_dir / 'times.csv', index=False)


def configure_logging(logger: logging.Logger, output_path: Path):
    formatter = logging.Formatter('%(asctime)s [%(levelname)5s] %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(output_path, 'wt', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    logger.setLevel(1) # min level


def parse_command_line_options() -> ProgramOptions:
    parser = argparse.ArgumentParser(
        description='Detect humans using YOLOv8 model.',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--model', dest='model_path', type=Path,
                        help='path to the model (default: %(default)s)')

    parser.add_argument('--confidence', dest='confidence', type=float,
                        help='confidence treshold (default: %(default)s)')

    parser.add_argument('--iou', dest='iou', type=float,
                        help='intersection over union (IoU) threshold for NMS (default: %(default)s)')

    parser.add_argument('--image-size', dest='image_size', type=int,
                        help='size of input images (default: %(default)s)')

    parser.add_argument('--device', dest='device', type=str,
                        help='device to run on, i.e. device=cuda or device=0,1,2,3 or device=cpu')

    parser.add_argument('images_dir', type=Path,
                        help='path to the input directory with images')

    parser.add_argument('output_dir', type=Path,
                        help='path to the output directory')

    parser.set_defaults(confidence=0.1, iou=0.1, image_size=1280, model_path='yolov8x.pt')

    args = parser.parse_args()

    if not args.model_path.exists() and args.model_path.is_absolute():
        parser.error(f'argument --model: path "{args.model_path}" not found')

    if not args.images_dir.exists():
        parser.error(f'argument images_dir: path "{args.images_dir}" not found')

    return ProgramOptions(**vars(args))


def main():
    options = parse_command_line_options()

    options.output_dir.mkdir(exist_ok=True, parents=True)

    configure_logging(LOGGER, options.output_dir / 'detect.log')

    LOGGER.info('Program options:\n' + textwrap.indent(
        '\n'.join(f'{name} = {options[i]}' for i, name in enumerate(options._fields)), '  '))

    predict(options)


if __name__ == '__main__':
    main()

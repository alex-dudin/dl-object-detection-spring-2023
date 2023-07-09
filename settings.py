from pathlib import Path
import yaml


def load_settings():
    path = Path(__file__).absolute().parent / 'rescue-app.yaml'
    return yaml.safe_load(path.read_text())


_settings = load_settings()


APP_DIR = Path(__file__).absolute().parent
STORAGE_DIR = Path(_settings['storage_dir'])

YOLO8_IMAGE_SIZE = _settings['yolo8']['image_size']
YOLO8_DEVICE = _settings['yolo8']['device']
YOLO8_IOU_THRESHOLD = _settings['yolo8']['iou_threshold']
YOLO8_CONF_THRESHOLD = _settings['yolo8']['conf_threshold']

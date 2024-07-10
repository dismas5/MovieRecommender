from os import path

ROOT_FOLDER = path.abspath(path.join(__file__, '..', '..'))
DATASET_FOLDER_PATH = path.join(ROOT_FOLDER, 'dataset')
RECOMMENDATION_MODEL_PATH = path.join(ROOT_FOLDER, 'models', 'recommendation_model')
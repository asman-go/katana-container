import boto3
import logging
import pathlib
import pydantic
import subprocess


class Config(pydantic.BaseSettings):
    KATANA_S3_ENDPOINT: str
    KATANA_BUCKET_NAME: str
    KATANA_BUCKET_INPUT_FILE: str
    KATANA_BUCKET_OUTPUT_FILE: str

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def download_folder(bucket, directory: str, config: Config):
    for obj in bucket.objects.filter(Prefix=directory):
        target = pathlib.Path(directory, obj.key)
        if not target.parent.exists():
            target.parent.mkdir(parents=True)
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    config = Config()
    INPUT_FILE_PATH = pathlib.Path('files', 'input.txt')

    s3 = boto3.client(
        's3',
        endpoint_url=config.KATANA_S3_ENDPOINT,
        aws_access_key_id=config.S3_ACCESS_KEY,
        aws_secret_access_key=config.S3_SECRET_KEY,
    )
    # bucket = s3.Bucket(config.KATANA_BUCKET_NAME)
    s3.download_file(
        config.KATANA_BUCKET_NAME,
        config.KATANA_BUCKET_INPUT_FILE,
        INPUT_FILE_PATH
    )
    if INPUT_FILE_PATH.exists():
        with INPUT_FILE_PATH.open(mode='r') as input_stream:
            logger.info(f'Downloaded input list: {input_stream.readlines()}')

    logger.info('Starting Katana')
    subprocess.check_output(['katana', '-config', pathlib.Path('katana.yaml')])
    logger.info('Katana has finished')

    output_file = pathlib.Path('output.txt')
    if output_file.exists():
        logger.info('Starting upload output file to s3 bucket')
        s3.upload_file(output_file, config.KATANA_BUCKET_NAME, config.KATANA_BUCKET_OUTPUT_FILE)
        logger.info('Output file was uploaded')
    else:
        logger.error('Output file was not created')
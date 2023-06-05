import boto3
from fastapi import FastAPI
import logging
import pathlib
import pydantic
import subprocess
import uvicorn


INPUT_FILE_NAME = 'input.txt'
OUTPUT_FILE_NAME = 'output.txt'
CONFIG_FILE_NAME = 'katana.yaml'


class Config(pydantic.BaseSettings):
    KATANA_S3_ENDPOINT: str
    KATANA_BUCKET_NAME: str

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    PORT: int

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


async def run_campaigh(campaign: str, config: Config):
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    INPUT_FILE_PATH = pathlib.Path('files', INPUT_FILE_NAME)

    s3 = boto3.client(
        's3',
        endpoint_url=config.KATANA_S3_ENDPOINT,
        aws_access_key_id=config.S3_ACCESS_KEY,
        aws_secret_access_key=config.S3_SECRET_KEY,
    )

    # bucket = s3.Bucket(config.KATANA_BUCKET_NAME)
    s3.download_file(
        config.KATANA_BUCKET_NAME,
        f'{campaign}/{INPUT_FILE_NAME}',
        INPUT_FILE_PATH
    )
    if INPUT_FILE_PATH.exists():
        with INPUT_FILE_PATH.open(mode='r') as input_stream:
            logger.info(f'Downloaded input list: {input_stream.readlines()}')

    logger.info('Starting Katana')
    subprocess.check_output(['katana', '-config', pathlib.Path(CONFIG_FILE_NAME)])
    logger.info('Katana has finished')

    output_file = pathlib.Path(OUTPUT_FILE_NAME)
    if output_file.exists():
        logger.info('Starting upload output file to s3 bucket')
        s3.upload_file(output_file, config.KATANA_BUCKET_NAME, f'{campaign}/{OUTPUT_FILE_NAME}')
        logger.info('Output file was uploaded')
        return True
    else:
        logger.error('Output file was not created')
        return False


app = FastAPI()
config = Config()


@app.get("/healthcheck")
async def healthcheck():
    return {"Status": "OK"}


@app.get("/run")
async def read_root(campaigh: str):
    result = await run_campaigh(campaigh, config)

    return {"Status": result}


if __name__ == '__main__':
    uvicorn.run("main:app", port=config.PORT, host='0.0.0.0', log_level="info")

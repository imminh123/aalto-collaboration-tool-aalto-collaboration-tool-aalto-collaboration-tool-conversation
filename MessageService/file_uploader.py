from minio import Minio
from minio.error import S3Error
from io import BytesIO
from fastapi.responses import StreamingResponse

minio_client = Minio(
    "localhost:9000",
    access_key="wtOy3zjCkI60kwXuJNSm",
    secret_key="PrmTcotzh4rqALxwAcD0Hlb0EsamnzuoSvBOQk11",
    secure=False,
)

BUCKET_NAME = "collaboration-tool"

class FileManager:
    def __init__(self) -> None:

        # Make the bucket if it doesn't exist.
        found = minio_client.bucket_exists(BUCKET_NAME)
        if not found:
            minio_client.make_bucket(BUCKET_NAME)
            print("Created bucket", BUCKET_NAME)
        else:
            print("Bucket", BUCKET_NAME, "already exists")

    # List all buckets
    def list_buckets():
        try:
            buckets = minio_client.list_buckets()
            for bucket in buckets:
                print(bucket.name)
        except S3Error as err:
            print(err)

    # Create a new bucket
    def create_bucket(self, bucket_name):
        try:
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully.")
            else:
                print(f"Bucket '{bucket_name}' already exists.")
        except S3Error as err:
            print(err)

    def upload_file(self, object_name, file_data, bucket_name=BUCKET_NAME):
        try:

            # Convert file_data to BytesIO object
            file_data_stream = BytesIO(file_data.file.read())
            print(file_data)
            print("file_data_stream",file_data_stream)
            print(file_data.file)
            # Upload the file using put_object
            minio_client.put_object(
                bucket_name,
                object_name,
                file_data_stream,
                length=file_data.size,
            )

            print(f"File '{object_name}' uploaded successfully.")
        except S3Error as err:
            print(err)
        except Exception as e:
            print(e)

    # Download a file from a bucket
    def download_file(self, object_name, bucket_name=BUCKET_NAME):
        try:
            file_stream = minio_client.get_object(bucket_name, object_name)
            print(f"File '{object_name}' downloaded successfully.")
            return StreamingResponse(BytesIO(file_stream.read()), media_type='application/octet-stream')
        except S3Error as err:
            print(err)
        finally:
            file_stream.close()
            file_stream.release_conn()

    # List objects in a bucket
    def list_objects(self, bucket_name=BUCKET_NAME):
        try:
            objects = minio_client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                print(obj.object_name)
        except S3Error as err:
            print(err)

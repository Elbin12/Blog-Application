import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect

region_name = settings.AWS_S3_REGION_NAME
bucket_name = settings.AWS_STORAGE_BUCKET_NAME

s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=region_name)

def upload_fileobj_to_s3(file_obj, object_name):
    """Upload a file object to an S3 bucket"""

    try:
        s3.upload_fileobj(file_obj, bucket_name, object_name, ExtraArgs={ 'ContentType': file_obj.content_type})
        print("Upload Successful")
        image_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}"
        return image_url
    except ClientError as e:
        return False
    
def create_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name=region_name)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return None

    # The response contains the presigned URL
    return response


def token_generation_and_set_in_cookie(user):
    refresh = RefreshToken.for_user(user)
    refresh["email"] = str(user.email)

    if user.is_superuser:
        response = HttpResponseRedirect('/admin/home/')
    else:
        response = HttpResponseRedirect('/')
    response.set_cookie(
            key = settings.SIMPLE_JWT['AUTH_COOKIE'],
            value = str(refresh.access_token),
            secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
    response.set_cookie(
        key = 'refresh_token',
        value = str(refresh),
        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],    
        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    return response
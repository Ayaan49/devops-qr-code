from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import boto3
import os
from io import BytesIO
from botocore.exceptions import ClientError
import logging

app = FastAPI()

# Allowing CORS for local testing and production
origins = [
    "http://localhost:3000",
    "https://dev.qr-app.devfun.me"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 Configuration
try:
    s3 = boto3.client('s3')
    logger.info("Successfully created S3 client")
    # Test S3 connection
    s3.list_buckets()
    logger.info("Successfully connected to S3")
except Exception as e:
    logger.error(f"Failed to create S3 client or connect to S3: {str(e)}")
    raise

# Get bucket name from environment variable
bucket_name = os.getenv('S3_BUCKET_NAME')
if not bucket_name:
    logger.error("S3_BUCKET_NAME environment variable is not set")
    raise ValueError("S3_BUCKET_NAME environment variable is not set")
logger.info(f"Using S3 bucket: {bucket_name}")

@app.get("/")
async def root():
    return {"message": "QR Code Generator API is running"}

@app.post("/generate-qr/")
async def generate_qr(url: str):
    logger.info(f"Received request to generate QR code for URL: {url}")
    
    try:
        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        logger.info("QR code image generated successfully")

        # Save QR Code to BytesIO object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        logger.info("QR code image saved to BytesIO")

        # Generate file name for S3
        file_name = f"qr_codes/{url.split('//')[-1]}.png"
        logger.info(f"Generated S3 file name: {file_name}")

        # Upload to S3
        try:
            logger.info(f"Attempting to upload file {file_name} to bucket {bucket_name}")
            response = s3.put_object(
                Bucket=bucket_name, 
                Key=file_name, 
                Body=img_byte_arr, 
                ContentType='image/png', 
                ACL='public-read'
            )
            logger.info(f"Successfully uploaded QR code to S3: {file_name}")
            logger.info(f"S3 response: {response}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"S3 upload failed. Error code: {error_code}, Message: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {error_message}")

        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        logger.info(f"Generated S3 URL: {s3_url}")
        
        return {"qr_code_url": s3_url}
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

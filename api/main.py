from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import boto3
import logging
from io import BytesIO

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000",
    "http://dev.qr-app.devfun.me"
	"https://dev.qr-app.devfun.me"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 Configuration
s3 = boto3.client('s3')
bucket_name = 'new-bucket666'  # Add your bucket name here

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@app.post("/api/generate-qr/")
async def generate_qr(url: str):
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

    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name for S3
    file_name = f"qr_codes/{url.split('//')[-1]}.png"

    try:
        # Upload to S3
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=img_byte_arr, ContentType='image/png', ACL='public-read')

        # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        logger.info(f"Successfully uploaded QR code to S3: {s3_url}")

        return {"qr_code_url": s3_url}

    except Exception as e:
        logger.error(f"Failed to upload QR code to S3: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error generating QR code")

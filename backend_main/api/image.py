import os, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.disease_service import predict_disease

router = APIRouter()
BASE_URL = "http://50.19.164.128:8000" 
@router.post("/predict")
async def predict_image(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image file")

    os.makedirs("temp/images", exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    path = f"temp/images/{file_id}{ext}"

    with open(path, "wb") as f:
        f.write(await image.read())

    try:
        top_predictions = predict_disease(path, top_k=3)
        best = top_predictions[0]
        print(f"Predictions for {image.filename}: {top_predictions} {best}")
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "image_id": file_id,
        "image_path": path,    
        "image_url": f"{BASE_URL}/static/images/{file_id}{ext}",      
        "predictions": top_predictions,
        "best_prediction": best,
    }
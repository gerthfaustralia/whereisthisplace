from fastapi import APIRouter, UploadFile, File
from ml import scene_classifier, retrieval, fuse

router = APIRouter()

@router.post("/predict")
async def predict(photo: UploadFile = File(...)):
    image_bytes = await photo.read()
    scene = scene_classifier.predict_topk(image_bytes, k=5)
    retrieval_results = retrieval.search(image_bytes, k=5)
    (lat, lon), confidence = fuse.fuse(scene=scene, retrieval=retrieval_results)
    return {"latitude": lat, "longitude": lon, "confidence": confidence}

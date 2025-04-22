import uvicorn
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
if __name__ == "__main__":
    uvicorn.run("face_detection.api.main:app", host="0.0.0.0", port=8000, reload=True)

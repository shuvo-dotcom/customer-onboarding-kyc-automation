try:
    import fastapi
    import pydantic
    import sklearn
    import cv2
    import sqlalchemy
    import streamlit
    print("All packages imported successfully!")
except ImportError as e:
    print(f"Error importing packages: {e}") 
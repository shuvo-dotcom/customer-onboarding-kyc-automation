import os
import requests
import json

def batch_finger_extraction(dataset_dir, api_url, output_json='finger_extraction_results.json'):
    results = []
    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(dataset_dir, filename)
            with open(file_path, 'rb') as f:
                files = {'image': (filename, f, 'image/jpeg')}
                try:
                    response = requests.post(api_url, files=files)
                    if response.ok:
                        data = response.json()
                        print(f"{filename}: {data['num_fingers']} fingers detected")
                        results.append({'filename': filename, 'num_fingers': data['num_fingers']})
                    else:
                        print(f"{filename}: Error {response.status_code}")
                        results.append({'filename': filename, 'error': response.status_code})
                except Exception as e:
                    print(f"{filename}: Exception {e}")
                    results.append({'filename': filename, 'exception': str(e)})
    # Save results
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_json}")

if __name__ == "__main__":
    # Update this path to the location of your 11K Hands dataset images
    DATASET_DIR = 'datasets/11khands/images'
    # Update this URL if your backend is running elsewhere
    API_URL = 'http://localhost:8000/api/v1/fingerprint/extract-fingers'
    batch_finger_extraction(DATASET_DIR, API_URL)

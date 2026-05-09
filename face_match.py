import cv2
import numpy as np
import sys
import json
import os

# -----------------------------
# GET IMAGE PATHS
# -----------------------------

img1_path = sys.argv[1]
img2_path = sys.argv[2]

# -----------------------------
# LOAD IMAGES
# -----------------------------

img1 = cv2.imread(img1_path)
img2 = cv2.imread(img2_path)

if img1 is None or img2 is None:
    print(json.dumps({
        "error": "Unable to read one or both images"
    }))
    sys.exit()

# -----------------------------
# CREATE RESULT DIRECTORY
# -----------------------------

os.makedirs("public/result_pic", exist_ok=True)

# -----------------------------
# RESIZE IMAGES
# -----------------------------

img1 = cv2.resize(img1, (600, 700))
img2 = cv2.resize(img2, (600, 700))

gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# -----------------------------
# LOAD FACE DETECTOR
# -----------------------------

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -----------------------------
# DETECT FACES
# -----------------------------

faces1 = face_cascade.detectMultiScale(
    gray1,
    scaleFactor=1.05,
    minNeighbors=3,
    minSize=(60, 60)
)

faces2 = face_cascade.detectMultiScale(
    gray2,
    scaleFactor=1.05,
    minNeighbors=3,
    minSize=(60, 60)
)

# -----------------------------
# CHECK FACE DETECTION
# -----------------------------

if len(faces1) == 0:
    print(json.dumps({
        "error": "No face detected in first image"
    }))
    sys.exit()

if len(faces2) == 0:
    print(json.dumps({
        "error": "No face detected in second image"
    }))
    sys.exit()

# -----------------------------
# SELECT LARGEST FACE
# -----------------------------

faces1 = sorted(faces1, key=lambda f: f[2] * f[3], reverse=True)
faces2 = sorted(faces2, key=lambda f: f[2] * f[3], reverse=True)

x1, y1, w1, h1 = faces1[0]
x2, y2, w2, h2 = faces2[0]

# -----------------------------
# EXTRACT FACE REGIONS
# -----------------------------

face1 = gray1[y1:y1+h1, x1:x1+w1]
face2 = gray2[y2:y2+h2, x2:x2+w2]

# Normalize size
face1 = cv2.resize(face1, (300, 300))
face2 = cv2.resize(face2, (300, 300))

# -----------------------------
# REGION SCORE FUNCTION
# -----------------------------

def region_score(region):

    edges = cv2.Canny(region, 50, 150)

    density = np.sum(edges > 0) / region.size

    return min(100, density * 400)

# -----------------------------
# FEATURE EXTRACTION
# -----------------------------

def extract_features(face):

    h, w = face.shape

    regions = {

        "Eyes": face[
            int(0.18*h):int(0.38*h),
            int(0.15*w):int(0.85*w)
        ],

        "Nose": face[
            int(0.38*h):int(0.60*h),
            int(0.35*w):int(0.65*w)
        ],

        "Lips": face[
            int(0.62*h):int(0.80*h),
            int(0.28*w):int(0.72*w)
        ],

        "Hair": face[
            0:int(0.18*h),
            :
        ],

        "Jaw": face[
            int(0.78*h):h,
            int(0.20*w):int(0.80*w)
        ]
    }

    scores = {}

    for key, region in regions.items():

        score = region_score(region)

        scores[key] = round(score, 2)

    return scores

# -----------------------------
# GET FEATURE SCORES
# -----------------------------

scores1 = extract_features(face1)
scores2 = extract_features(face2)

# -----------------------------
# MATCH SCORES
# -----------------------------

match_scores = {}

for key in scores1:

    diff = abs(scores1[key] - scores2[key])

    similarity = max(0, 100 - diff)

    match_scores[key] = round(similarity, 2)

# -----------------------------
# OVERALL MATCH
# -----------------------------

overall_match = round(
    sum(match_scores.values()) / len(match_scores),
    2
)

# -----------------------------
# DRAW FACE BOXES
# -----------------------------

cv2.rectangle(
    img1,
    (x1, y1),
    (x1 + w1, y1 + h1),
    (0, 255, 0),
    3
)

cv2.rectangle(
    img2,
    (x2, y2),
    (x2 + w2, y2 + h2),
    (0, 255, 0),
    3
)

# -----------------------------
# PERSON LABELS
# -----------------------------

cv2.putText(
    img1,
    "Person 1",
    (x1, y1 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 0),
    3
)

cv2.putText(
    img2,
    "Person 2",
    (x2, y2 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 0),
    3
)

# -----------------------------
# FEATURE TEXT
# -----------------------------

y_offset1 = y1 + h1 + 30

for key, value in scores1.items():

    cv2.putText(
        img1,
        f"{key}: {value}%",
        (x1, y_offset1),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    y_offset1 += 35

y_offset2 = y2 + h2 + 30

for key, value in scores2.items():

    cv2.putText(
        img2,
        f"{key}: {value}%",
        (x2, y_offset2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    y_offset2 += 35

# -----------------------------
# COMBINE IMAGES
# -----------------------------

combined = np.hstack((img1, img2))

# -----------------------------
# OVERALL MATCH TEXT
# -----------------------------

cv2.putText(
    combined,
    f"OVERALL FACE MATCH: {overall_match}%",
    (250, 50),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.2,
    (0, 0, 255),
    4
)

# -----------------------------
# SAVE RESULT IMAGE
# -----------------------------

output_path = "public/result_pic/result.jpg"

cv2.imwrite(output_path, combined)

# -----------------------------
# RETURN JSON RESULT
# -----------------------------

result = {
    "overall_match": overall_match,
    "details": match_scores,
    "image": "result_pic/result.jpg"
}

print(json.dumps(result))
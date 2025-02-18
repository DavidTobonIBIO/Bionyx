import easyocr
import cv2
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 36})

reader = easyocr.Reader(['en'])

image_paths = ['B14.jpg', 'D70.jpeg', 'H54.jpeg']

predictions = []

for image_path in image_paths:
    # (detail=0 retorna solo es texto)
    results = reader.readtext(image_path, detail=0)
    predictions.append(results)

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

for ax, image_path, prediction in zip(axes, image_paths, predictions):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    ax.imshow(image)
    
    ax.set_title("Prediction: " + " ".join(prediction), fontsize=10)
    
    ax.axis('off')

plt.tight_layout()
plt.show()

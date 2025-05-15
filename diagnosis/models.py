import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

class SkinDiseaseModel:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, 'trained_skin_disease_model.keras')

        self.model = tf.keras.models.load_model(model_path)

        self.class_names = [
            'Chàm (Eczema)',
            'U hắc tố ác tính (Melanoma)',
            'Viêm da cơ địa (Atopic Dermatitis)',
            'Ung thư biểu mô tế bào đáy (Basal Cell Carcinoma)',
            'Nốt ruồi sắc tố (Melanocytic Nevi)'
        ]


    def predict(self, image_path):
        img = load_img(image_path, target_size=(128, 128))
        input_arr = img_to_array(img)
        input_arr = np.expand_dims(input_arr, axis=0)
        predictions = self.model.predict(input_arr)
        result_index = np.argmax(predictions)
        return self.class_names[result_index]

from flask import *
from flask_restful import Api, Resource
import numpy as np
import os, pickle
from flask_cors import CORS
import tensorflow as tf
import tensorflow_hub as hub

app = Flask(__name__, static_folder='images')
app.secret_key='asdfrfrhbrirmanseje#48h'

cors = CORS(app)
api = Api(app)

class Rust_measure(Resource):
    def post(self):
        folder = 'images'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        if 'file' not in request.files:
            return {'message': 'No file part in the request'}, 400
        
        file = request.files['file']
        # print(file)
        if file.filename == '':
            return {'message': 'No file selected'}, 404
        
        file.save('images/'+file.filename)
        img_path = 'images/'+file.filename

        img = tf.keras.preprocessing.image.load_img(img_path, target_size=(224, 224, 3))
        img = tf.keras.preprocessing.image.img_to_array(img)
        img = img/255.
        img = np.expand_dims(img, axis=0)
        
        # with open('model/model.pkl', 'rb') as f:
        #     model_architecture, model_weights = pickle.load(f)
        #     loaded_model = tf.keras.models.model_from_json(model_architecture)
        #     loaded_model.set_weights(model_weights)
        #     pred_value = loaded_model.predict(img)
        #     prediction = pred_value[0][0]
        #     if prediction > 0.5:
        #         result = 'No Corrosion'
        #     else:
        #         result = 'Corrosion'
        #     return {'result': result, 'prediction': float(prediction)}, 200
        model = tf.keras.models.load_model('model/CNN.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        pred_value = model.predict(img)
        prediction = int(pred_value[0][0])
        
        return {'prediction': prediction}

api.add_resource(Rust_measure, '/v1/api/Rust')

import json
class Rust_calculation(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        if "filename" not in data['filename']:
            filename = data['filename']
        else:
            return {'error': 'Filename not specified'}, 500
        with open('result.json', 'r+') as file:
            jsonData = json.load(file)
            for i in jsonData:
                if i['Name_Image'].lower() in filename.lower():
                    print("final", i['Grading_Point'])
                    return {"prediction": int(i['Grading_Point'])}
            return {"error": "File not found"}, 300

api.add_resource(Rust_calculation, '/v1/api/rust_')

class Rust_Batch(Resource):
    def post(self):
        data =  request.get_json()
        if "filenames" not in data:
            return {'error': 'Missing filenames'}, 302
        else:
            filenames = data["filenames"]
        filenames = filenames.split(",")
        filenames = [i.lower() for i in filenames]
        result = {}
        with open('result.json', 'r+') as file:
            jsonData = json.load(file)
            for i in jsonData:
                for j in filenames:
                    if i['Name_Image'].lower() in j:
                        result[j] = int(i['Grading_Point'])
                        break
        return {'prediction': result}, 200

api.add_resource(Rust_Batch, '/v1/api/batch')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

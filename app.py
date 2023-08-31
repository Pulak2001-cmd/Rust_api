from flask import *
from flask_restful import Api, Resource
import numpy as np
import os, pickle
from flask_cors import CORS
import tensorflow as tf

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
        if file.filename == '':
            return {'message': 'No file selected'}, 404
        
        file.save('images/'+file.filename)
        img_path = 'images/'+file.filename

        img = tf.keras.preprocessing.image.load_img(img_path, target_size=(128, 128, 3))
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
        model = tf.keras.models.load_model('CNN.h5', custom_objects={'KerasLayer': hub.KerasLayer})
        pred_value = model.predict(img)
        prediction = pred_value[0][0]
        return {'prediction':prediction}

api.add_resource(Rust_measure, '/v1/api/Rust')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
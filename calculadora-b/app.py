
from flask import Flask, request, jsonify
from PIL import Image
import cv2
import easyocr
import pytesseract

import numpy as np
import re
from flask_cors import CORS  # Importa CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación
@app.route('/recognize', methods=['POST'])
def recognize():


    if 'file' not in request.files:
        return jsonify({'error': 'No se puede subir la imagen'}), 400

    file = request.files['file']
    image = Image.open(file)

    # Preprocesar la imagen
    image = image.convert('L')  # Convertir a escala de grises
    img_array = np.array(image)
    # Aplicar un desenfoque para eliminar ruido (FUNCIONO PARA RECONOCER LOS () )
    img_array = cv2.GaussianBlur(img_array, (5, 5), 0)

    # Aplicar un umbral adaptativo para mejorar la detección (FUNCIONO PARA RECONOCER LOS () )
    img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Convertir de nuevo a imagen
    image = Image.fromarray(img_array)

    # Usar Tesseract para reconocer texto en la imagen
    custom_config = r'--oem 3 --psm 6'  # Configuración personalizada
    text = pytesseract.image_to_string(image, config=custom_config)
    print(f'Texto reconocido: "{text}"')  # Imprimir texto reconocido

    # Validar el texto de Tesseract





    # Limpiar y validar la expresión
    text = re.sub(r'[^0-9+\-*/()x. ]', '', text)  # Elimina caracteres no válidos
    print(f'Texto limpio: "{text}"')  # Imprimir texto limpio

    # Reemplazos manuales si es necesario
    # Ajusta según lo que observes en el texto reconocido
    text = text.replace(' ', '*' )  # Ejemplo: si el espacio se interpreta como asterisco
    text = text.replace('x', '*')  # Reemplazar 'x' por asteriscos


    # Agregar asterisco entre paréntesis adyacentes
    text = re.sub(r'\)\s*\(', ')*(', text)  # Asegurarse de que los paréntesis estén separados
    text = text.replace(')(', ')*(')  # Reemplazar )( por )*(
    if not text.strip():
        return jsonify({'error': 'Cálculo inválido, expresión vacía'}), 400

    # Intentamos evaluar la expresión matemática reconocida
    try:
        calculation = eval(text)
    except Exception as e:
        return jsonify({'error': 'Cálculo inválido', 'details': str(e)}), 400

    return jsonify({'calculo': calculation, 'text': text})




@app.route('/convert-to-binary', methods=['POST'])
def convert_to_binary():
    if 'file' not in request.files:
        return jsonify({'Error': 'No se puede convertir la imagen'}),400

    file = request.files['file']
    image = Image.open(file)



    # Usar configuración para extraer solo dígitos
    text = pytesseract.image_to_string(image, config='outputbase digits')
    print(f'Texto reconocido: "{text}"')

    # Limpiar el texto y extraer el número decimal
    text = re.sub(r'[^0-9]', '',text).strip()# Solo números y el punto decimal
    print(f'texto limpio: "{text}"')

    if  text == '':
        return jsonify({'Error': 'Número invalido, expresion vacía'}),400

    try:
        decimal_number = int(text)
        binary_number = bin(decimal_number)[2:] #convierte a binario
    except ValueError as e:
        return  jsonify({'Error': 'Múmero inválido', 'detalles': str(e)}),400

    return jsonify({'binario': binary_number, 'text': text})


if __name__ == '__main__':
    app.run(debug=True)
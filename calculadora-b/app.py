
from flask import Flask, request, jsonify
from PIL import Image
import cv2
import easyocr
import pytesseract

import numpy as np
import re
from sympy import symbols, Eq, solve
from flask_cors import CORS  # Importa CORS
from sympy.core.backend import sympify

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación
@app.route('/sumas', methods=['POST'])
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





@app.route('/ecuacion', methods=['POST'])
def ecuacion():

    if 'file' not in request.files:
        return jsonify({'error': 'No se puede subir la imagen'}), 400

    file = request.files['file']
    image = Image.open(file)

    # PREPARAR LA IMAGEN
    image = image.convert('L')
    img_array = np.array(image)
    img_array = cv2.GaussianBlur(img_array, (5, 5), 0)
    img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    image = Image.fromarray(img_array)

    # USAR TESSERACT PARA RECONOCER TEXTO EN LA IMAGEN
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    print(f'Texto reconocido: "{text}"')

    # Limpiar y validar la expresión
    text = re.sub(r'[^0-9+\-*/()=xyXY.]', '', text)
    print(f'Texto limpio: "{text}"')


    #REMOVEMIS ESPACIOS INNCESARIOS ALREDDEDOR DE '='
    text = text.replace(' =', '='.replace('= ','='))

    if not text.strip():
        return jsonify({'error': 'Cálculo inválido, expresión vacía'}), 400

    # VERIFICA SI LA ECUACIÓN ES LINEAL
    if '=' in text:
        lhs, rhs = text.split('=')
        lhs = lhs.strip()
        rhs = rhs.strip()
    else:
        return jsonify({'error': 'La expresión no contiene una ecuación válida'}), 400

        # Reemplazar '4x' por '4*x' y similar
    lhs = re.sub(r'(\d)([xyXY])', r'\1*\2', lhs)
    rhs = re.sub(r'(\d)([xyXY])', r'\1*\2', rhs)

    #SE DEFINE LAS VARBLES PARA Sympy
    try:
        x = symbols('x')

        #USAR  Sympy PARA CONVERTIR LAS CADEDENAS EN EXPRESIONES DE Sympy
        lhs_expr = sympify(lhs)
        rhs_expr = sympify(rhs)

        #CREAR LA ECUACION
        equation = Eq(lhs_expr, rhs_expr)
        print(f'Ecuacion: {equation}')




        #RESOLVER LA ECUACION
        solutions = solve(equation,(x))
        print(f'Soluciones: {solutions}')  # Ver qué devuelve

        # Convertir las soluciones a tipos serializables
        if isinstance(solutions, list):
            # Si hay más de una solución, devuelve la lista
            solutions_serializable = [float(sol) if sol.is_real else str(sol) for sol in solutions]
        elif isinstance(solutions, dict):
            # Si hay un diccionario de soluciones
            solutions_serializable = {str(var): float(sol) if sol.is_real else str(sol) for var, sol in
                                      solutions.items()}
        else:
            solutions_serializable = solutions  # Cualquier otra forma se maneja aquí
    except Exception as e:
        return jsonify({'error': 'Error al resolver la ecuación', 'details': str(e)}), 500

    return jsonify({'ecuacion': solutions_serializable, 'texto': text})



if __name__ == '__main__':
    app.run(debug=True)
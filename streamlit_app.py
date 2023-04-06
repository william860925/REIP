#model import 
import math
import pandas as pd
import streamlit as st
from io import StringIO
import PIL
import time
import importlib
import matplotlib.pyplot as plt
from REIP.image_processing.remove_cs import convert_to_dfimage, adjust_gray_value, show_edited_image, from3d_array_image, convert_to_RGB3darray
from streamlit_drawable_canvas import st_canvas
from REIP.prediction.Prediction import prediction
import os
import cv2

@st.cache(allow_output_mutation=True)
def auto_load(methods):
    ml = eval(methods)
    return ml

#@st.cache(allow_output_mutation=True)
#def originimage(imagename):
    """
    originimage(filepath)
    """
#    origin_img = cv2.imread(imagename)
#    return origin_img

@st.cache(allow_output_mutation=True)
def resultimage(imagearray, model):
    result_img = model(imagearray)
    return result_img

from PIL import Image
from REIP.image_processing.restore_blur import img_processing, edsr, espcn, fsrcnn, lapsrn, uint_to_float, enhance_details, restore_again, blur_function_selection
#parameter settting
blur_method = ['Click here select method','img_processing', 'enhance_details', 'edsr', 'espcn', 'fsrcnn', 'lapsrn']
blur_description = ['Sharpen the edge area with automatically modifying contrast', 
                    'Sharpen the edge area', 'less memory needed, slow but thoroughly restoration', 
                    'Fast but roughly restoration', 'Similar to ESPCN, fast with roughly restoration', 
                    'Medium time consuming and medium restoration']
blur_list = pd.DataFrame({'method':blur_method[1:]})
blur_list_descrip = pd.DataFrame({'method':blur_method[1:],'Description':blur_description})
blur_list_descrip = blur_list_descrip.set_index('method')
##########
st.title('DIRECT Project')

'History'
st.write('The goal of this project is to develop a software to help new comer students to get familiar in specific microscope, including TEM, SEM and AFM etc. A common question for new comers is how to judge the quality of images. In this case, the software is developed to distinguish whether the image is noisy, well-exposed or suffer from unsharpness or blur with the function of image optimization. After the judgement from the software is been made, students decide whether spending time to optimize the image or not. Image restoration, such as denoting and inpainting, is included to optimize the picture in this software. Depending on the quality of the image, the restoration time varies. Receiving the final image, students are able to get the ideal images for their research.')

col1, col2, col3 = st.columns(3)
col1.metric('Team Member', 'Kim')
col2.metric('Team Member', 'William')
col3.metric('Team Member', 'Lilo')
col4, col5 = st.columns(2)
col4.metric('Team Member', 'Hsuan-Yu')
col5.metric('Team Member', 'Nick')

st.title('How this project works?')
'We aim to help you distinguish the quality of TEM photo. Upload your photo, this website is able to distinguish the defect types and help you to fine-tune the image!'

sc, blur = st.columns(2)
sc.subheader('Surface Charge Example')
ex_surface_charge = PIL.Image.open('./doc/images/498.tif')
sc.image(ex_surface_charge)

blur.subheader('Blur Charge Example')
ex_blur = PIL.Image.open('./doc/images/1386.tif')
blur.image(ex_blur)

temp='./temp/'

input_data = st.file_uploader('Upload your TEM experiment photo',type=['png','tif','jpg','jpg','tiff'])
realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)


def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join(temp,uploaded_file.name),'wb') as f:
            f.write(uploaded_file.getbuffer())
        return 1    
    except:
        return 0

if input_data is not None:
    if save_uploaded_file(input_data): 
        display_image = Image.open(input_data)
        st.image(display_image)
        prediction = prediction(os.path.join(temp,input_data.name))
        global classified_class
        global classified_image
        classified_class = prediction[0] 
        classified_image = prediction[1]
        st.header(classified_class)
        #os.remove(temp+input_data.name)
        
        if classified_class == 'It is predicted to be surface charge.':
            gray_level = st.sidebar.slider('Surface charge remove level', -10, 30, 9)
            st.subheader('Select the surface area')
            canvas_result = st_canvas(height = prediction[2].shape[0], width = prediction[2].shape[1], fill_color = 0 , 
                                          drawing_mode = 'rect', 
                                          stroke_width = 2, 
                                          background_image = from3d_array_image(prediction[2]))
            #canvas_result = st_canvas(fill_color = 0, 
                                          #drawing_mode = 'rect', 
                                          #stroke_width = 2, 
                                          #background_image = from3d_array_image(resize_array))
            if canvas_result.json_data is not None:  
                objects = pd.json_normalize(canvas_result.json_data["objects"])
                for col in objects.select_dtypes(include = ['object']).columns:
                    objects[col] = objects[col].astype('str')

                for i in range(len(objects)):
                    start_point = [objects['left'][i],objects['top'][i]] 
                    end_point = [objects['left'][i]+objects['width'][i], objects['top'][i]+objects['height'][i]]
                    df_image = convert_to_dfimage(from3d_array_image(prediction[2]))
                    df_copied = adjust_gray_value(df_image, start_point, end_point, level = gray_level)
                    after_sc_image = show_edited_image(df_copied)
                    RGBarray = convert_to_RGB3darray(after_sc_image)
                    st.subheader('After surface charge restoration')
                    st.image(after_sc_image)
                    Answer= st.selectbox('Further improve blur?', options=['Click here to select', 'Remain','Restore Blur'], index=0)
                    if Answer == 'Restore Blur':
                        methods= st.selectbox('Choose blur restoration method', options=blur_list, index=0)
                        if methods != 'Click here select method':

                            ml = eval(methods)
                            result_array = ml((RGBarray))
                            result_array_copied = result_array.copy()
                            after_sc_image = PIL.Image.fromarray(result_array_copied)
                            
                            #result_2img = cv2.resize(result_array_copied,(1280, 890))
                            #image = PIL.Image.fromarray(result_2img)
                            result_2img = cv2.resize(RGBarray, (1280,960))
                            st.image(result_2img)
                            remain_output = PIL.Image.fromarray(result_2img).save(temp+input_data.name)
                            with open(os.path.join(temp,input_data.name),'rb') as f:
                                btn = st.download_button(label="Download edited image", data=f, file_name=input_data.name, mime="image/tif")
                            os.remove(temp+input_data.name)
                    if Answer == 'Remain':

                       
                        #result_2img = cv2.resize(RGBarray,(1280, 890))
                        result_2img = cv2.resize(RGBarray, (1280,960))
                        remain_output = PIL.Image.fromarray(result_2img).save(temp+input_data.name)
                        with open(os.path.join(temp,input_data.name),'rb') as f:
                            btn = st.download_button(label="Download edited image", data=f, file_name=input_data.name, mime="image/tif")
                        os.remove(temp+input_data.name)


        elif prediction[0] == 'It is predicted to be blur.':
            st.text('Here is the list of feature in image proessing')
            st.table(blur_list_descrip)

            methods= st.selectbox('Choose the 1st restoration method', options=blur_list, index=0)
            #@st.cache(allow_output_mutation=True)
            #def auto_load(array_image, methods)
                #ml = eval(methods)
                #return ml
            #result_img = auto_load(methods)((classified_image)) 
            
            result_img = resultimage(classified_image, auto_load(methods))
            st.image(from3d_array_image(result_img))
            Answer= st.selectbox('Would you want to restore again', options=['Default','Yes','No'], index=0)
            if Answer == 'Yes':
                methods2= st.selectbox('Choose the restoration method (edsr is time-consuming)', options=blur_list, index=0)
                ml2 = eval(methods2)
                result_2img = ml2((result_img))
                st.image(result_2img)
                st.header('you are all set!')
                result_2img = cv2.resize(result_2img, (1280,960))
                image = PIL.Image.fromarray(result_2img)
                remain_output = image.save(temp+input_data.name)
                with open(os.path.join(temp,input_data.name),'rb') as f:
                    btn = st.download_button(label="Download edited image", data=f, file_name=input_data.name, mime="image/tif")
                os.remove(temp+input_data.name)
                
            elif Answer == 'No':
                result_2img = cv2.resize(result_img, (1280,960))
                image = PIL.Image.fromarray(result_2img)
                remain_output = image.save(temp+input_data.name)
                with open(os.path.join(temp,input_data.name),'rb') as f:
                    btn = st.download_button(label="Download edited image", data=f, file_name=input_data.name, mime="image/tif")
                os.remove(temp+input_data.name)

        elif prediction[0] == 'It is predicted to be clear.':
            st.header('Congrats! Perfect image!')
            st.balloons()

    else:
        st.write('saving image failed')
    


    
    
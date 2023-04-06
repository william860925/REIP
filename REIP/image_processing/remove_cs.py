import pandas as pd
import numpy as np
from numpy import asarray
import PIL


def convert_to_dfimage(image):
    converted = image.convert('L')
    image_nparray = asarray(converted)
    df = pd.DataFrame(image_nparray)
    return df

def adjust_gray_value(df, start_point, end_point, level = 9):
    """
    adjust_gray_value(df, start_point, end_point, level = 9)
    df = the image dataframe
    start point / end point = a list indicates the x, y
    level ( default = 4 ) the count adjust the gray level
    """
    df_copied = df.copy()
    df_copied.iloc[start_point[1]:end_point[1], start_point[0]:end_point[0]] = df.iloc[start_point[1]:end_point[1], start_point[0]:end_point[0]] + level
    
    return df_copied

def show_edited_image(df_copied):
    edited_image = PIL.Image.fromarray(df_copied.values)
    return edited_image


def from3d_array_image(array_image):
    image = PIL.Image.fromarray(array_image)
    converted = image.convert('L')
    image_nparray = asarray(converted)
    edited_image = PIL.Image.fromarray(image_nparray)
    return edited_image

def convert_to_RGB3darray(image):
    converted = image.convert('RGB')
    image_nparray = asarray(converted)
    copied_nparray = image_nparray.copy()
    return copied_nparray

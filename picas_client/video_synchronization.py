#!/usr/bin/env python
# coding: utf-8

#  <h1 style="text-align: center;">Camera Synchronization (Version 1.1)</h1>
#  <p style="text-align: center; font-size: 20px">This Jupyter Notebook has been prepared for Applied Data Group</p>

#  <h3 style="text-align: left;">Outline of the project</h3>
# 
# <ol>
#     <li>Importing Libraries</li>
#     <li>Frames Conversion (Video to Frames)</li>
#     <li>Cropping, Transformation and Detection</li>
#     <li>Check OCR Results and Fix</li>
#     <li>Check for Continuous Value</li>
#     <li>Add/Drop Frames</li>
#     <li>Video Construction</li>
# </ol>
# 




# <h3>1 - Importing Libraries  </h3>



# In[2]:


#Python libraries for importing, transfromation and detection
import os
import re
import sys
from os.path import isfile, join
import cv2
import csv
import easyocr
import tempfile
import pandas as pd
import numpy as np
import datetime
import random
import shutil
import subprocess as sp
import shlex
from tqdm import tqdm
from PIL import Image,ImageEnhance,ImageFilter
reader = easyocr.Reader(['en'])  

# <h3>Testing</h3>
# <h4> Edit the filename and Test_case number, Then Run All</h4>

# In[3]:


sp.check_call([sys.executable, '-m', 'pip', 'install',
'tqdm'])

# In[4]:


file_name = sys.argv[1]
test_case = sys.argv[2]
ffmpeg_path= 'ffmpeg.exe'

# In[5]:


file_name_to_run = './'+file_name
image_directory = './framestest'+str(test_case)+'/'
csv_filename = './digit_logt_test'+ str(test_case) + '.csv'
frames_path= image_directory
video_name = file_name+'updated.mp4'

# <h3>2 - Frames Conversion</h3>
# <p style="font-size: 15px">This section converts video to frames using cv2. It takes video's width, height, frame per second, frame count and convert it into frames. </p>

# In[6]:


# Function to convert video into frames while saving it in the frame folder
def convert_video(video_path, folder):
    i = 0
    vid = cv2.VideoCapture(video_path)
    print(f"Name:\t\t{video_path}")
    

    # Get frame details
    video_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps = vid.get(cv2.CAP_PROP_FPS)
    video_frame_cnt = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
    print('Video:\t\t', video_fps, video_frame_cnt, video_width, video_height)

    print('Video to Frames started')
    
    #Create folder frames
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Folder '{folder}' created successfully.")
    else:
        print(f"Folder '{folder}' already exists.")

    timestamp_array = []

    # Keep converting video into frames until finished
    print("Starting now with i = ",i)
    for i in tqdm(range(0,video_frame_cnt)):    
        success, frame = vid.read()
        
        #read
        if success:
            file_index = str(int(i))
            file_name = file_index + ".png"
            file_path = folder + file_name
            cv2.imwrite(file_path, frame)
            video_timestamp = vid.get(cv2.CAP_PROP_POS_MSEC)
            timestamp_dict = {
              "frame_index": file_index,
              "frame_timestamp": (video_timestamp/1000)%60
            }
            timestamp_array.append(timestamp_dict)
            

        else:
            print('Video to Frames completed')   
            break
    
    print("Ending now with i = ",i)
    
    return timestamp_array    


# In[7]:


current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

# For converting the video to frames and retuning dataframe with timestamp of each frame
timestamp_array = convert_video(file_name, image_directory)
timestamp_dataframe = pd.DataFrame(timestamp_array)


current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# <h3>3 - Cropping, Tranformation and Detection </h3>
# <p style="font-size: 15px">This section converts video to frames using cv2. It takes video's width, height, frame per second, frame count and convert it into frames. It then crops the all frames to get the last two digits (ss) of the timestamp.</p>
# <p style="font-size: 15px">It then tranforms the cropped images while using the following methods</p>
# <ul>
#     <li>Binarization</li>
#     <li>Upscaling</li>
#     <li>Dilating (commented)</li>
#     <li>Structuring (commented)</li>
# </ul>
# 
# <p style="font-size: 15px">After recognizing the transformed images and save the result in a CSV file for logging</p>

# In[8]:


# Class for saving image Score
class image_score:
    def __init__(self, filename, value, score):
        self.filename = filename
        self.value = value
        self.score = score
        

def detect_digit(image):
    
    """
    Function to detect images through OCR
    
    Args:
        image (string): The path of the image having digit that needs to be detected

    Returns:
        result: The result has the following columns.
            - 'result[0][1]': The detected value from the Easy_OCR
            - 'result[0][2]': The confidence score from the Easy_OCR for detection
    """
        
    # Perform OCR on the region using EasyOCR
    result = reader.readtext(image, allowlist ='0123456789')

    if result:
        
        # Return the OCR result
        return(result[0][1], result[0][2])

    else:
        return None, 0


# In[9]:


def transform(cropped_image, threshold):        
    # binarization
    bw_image = cropped_image.convert("L").point(lambda x: 0 if x < threshold else 255, mode='1')

    # grayscale
    grayscale_image = bw_image.convert("L")

    # filter
    filtered_image = grayscale_image.filter(ImageFilter.GaussianBlur(radius=1))

    # upscale 5x
    upscaled_image = filtered_image.resize((filtered_image.width * 5, filtered_image.height * 5), Image.NEAREST)

    # convert to numpy (for cv2)
    upscaled_image_np = np.array(upscaled_image)

    # Structure&Dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))
    dilated_image = cv2.dilate(upscaled_image_np, kernel)
    temp_path = tempfile.NamedTemporaryFile(suffix='.png').name
    
    cv2.imwrite(temp_path,dilated_image)
    extracted_value, score = detect_digit(temp_path)
    return (extracted_value, score)


def Alternate_transformation(cropped_image, threshold ):
    bw_image = cropped_image.convert("L").point(lambda x: 0 if x < threshold else 255, mode='1')
    filtered_image = grayscale_image.filter(ImageFilter.GaussianBlur(radius=1))
    upscaled_image = filtered_image.resize((filtered_image.width * 5, filtered_image.height * 5), Image.NEAREST)
    image_np = np.array(upscaled_image)
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 3))
    dlt = cv2.dilate(image_np, krn)
    updated_image_dlt = Image.fromarray(dlt)
    temp_path = tempfile.NamedTemporaryFile(suffix='.png').name

    cv2.imwrite(temp_path,updated_image_dlt)
    extracted_value, score = detect_digit(temp_path)

    return (extracted_value, score)


# In[10]:


def image_configure(frame_directory, csv_filename):
    
    """
    Function for cropping, transformation and detection

    Args:
        frame_directory (list): Contains the directory name where all the cropped images exist
        csv_filename (string): Contains the name of the csv filename

    Returns:
        image_array: The image_array has the following columns
            - 'filename': The filename of the image
            - 'value': The detected value from the Easy_OCR
            - 'score': The confidence score from the Easy_OCR for detection
    """
    # Check time for reference
    current_time = datetime.datetime.now().time()
    x = 1198
    y = 28
    width = 37
    height = 35
    image_array = []

    # Iterate through the image files in the directory
    image_files = os.listdir(image_directory)
    
    #Removing .png for sorting
    files_updated = [files.replace('.png', '') for files in image_files]
    
    #Sorting as per alphanumeric
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c.replace("_","")) for c in re.split('([0-9]+)', key) ]
    files_updated.sort( key=alphanum_key )
    png_string = ".png"
    image_files = [s + png_string for s in files_updated]
    
    # Specify the languages you want to recognize
    reader = easyocr.Reader(['en'])  
    threshold = 200
    cropped_image = []
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'value', 'score'])
        for filename in tqdm(image_files):
            image_path = os.path.join(image_directory, filename)
            
            if filename == 'deleted.png':
                continue
                
            # Load the image
            image = Image.open(image_path)

            # Crop and transform the region
            region = (x, y, x + width, y + height)
            cropped_image = image.crop(region)
            
            # Images are saved as Object
            extracted_value, score= transform(cropped_image, threshold)
            if extracted_value is None:
                extracted_value, score = transform(cropped_image, threshold = 230)
                if extracted_value is None:
                    extracted_value, score = transform(cropped_image, threshold = 150)
                    if extracted_value is None:
                        extracted_value, score = Alternate_transformation(cropped_image)
            # Image Scores are saved as Object
            image_chunk = image_score(image.filename, extracted_value, score)
            image_array.append(image_chunk)
            
            # Log the results in the CSV file
            writer.writerow([filename, extracted_value, score])
    current_time = datetime.datetime.now().time()
    return image_array


# In[11]:


print("Image Directory - ",image_directory)
print("CSV Filename - ",csv_filename)


# In[13]:


current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

# For applying cropping, transformation and detection to frames
image_array_updated = image_configure(image_directory, csv_filename)

current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# In[14]:


#image_array_updated is an array that contains object that has filename, value and score
dataframe_view = pd.DataFrame([{'filename': s.filename, 'value': s.value, 'score':s.score} for s in image_array_updated])


# In[15]:


# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create a file name using the formatted date and time
file_name = "Step_3_updated_dataframe_" + str(test_case) +f"_{formatted_datetime}.xlsx"

# Print the file name
print("saving data frame to", file_name)
dataframe_view.to_excel(file_name)


# <h3>4 - Check OCR Results and Fix</h3>

# In[16]:


#image_array_updated is an array that contains object that has filename, value and score
dataframe_view = pd.DataFrame([{'filename': s.filename, 'value': s.value, 'score':s.score} for s in image_array_updated])
dataframe = dataframe_view.replace(image_directory,'', regex=True)
dataframe['value1'] = dataframe['filename'].str.extract('(\d+)').astype(int)
dataframe = dataframe.sort_values(by='value1')
dataframe = dataframe.reset_index(drop=True)
dataframe = dataframe.drop(columns='value1')


# In[17]:


def fixing_function(output):
    
    """
    Function that fills in the missing values that are not 2 digit for possible scenerios
    # <missing value> (if neighbors are 1) -> 1
    # 003 -> 03
    # 1 -> 01

    Args:
       output: Dataframe containing filename, value and score

    Returns:
        output: The DataFrame has the following updated values in the columns:
            - 'filename': The filename of the image
            - 'value': The detected value from the Easy_OCR
            - 'score': The confidence score from the Easy_OCR for detection
            - 'value_fixed': The values are fixed by the fixing function
            - 'isDigit': Check if the value is 
            
            	filename	value	value_fixed	score	isDigit	fix_scenario
    """
    
    # Data preparation
    output.insert(output.columns.get_loc('value') + 1, 'value_fixed', output['value'])
    output['isDigit'] = output['value_fixed'].apply(lambda x: True if ( x !=None  ) and (len(x) == 2) else False)
    output.loc[np.where(output['isDigit'] == False)[0],'fix_scenario'] = 0

    # Starting part, if the there are one or more False in the begining of the serie, then give all of them the value of the first True
    if output['isDigit'][0] == False:
        index_first_true = np.where(output['isDigit'] == True)[0][0]
        output['value_fixed'][0:index_first_true] = output['value_fixed'][index_first_true]
        output['fix_scenario'][0:index_first_true] = 'start_end_normal'

        # if some of the distance between the False and the first True is larger than 15, then give them the value of the first True -1
            # (we assume that the index of the first ture will never be much bigger than 15, so the value-1 is the earliest time)
        if index_first_true > 14:
            j=0
            while(j<index_first_true):
                output['value_fixed'][j] = str(int(output['value_fixed'][index_first_true]) - 1)
                output['fix_scenario'][j] = 'start_end_far'
                j+=1

    #Engaging part, similarily
    if output['isDigit'].iloc[-1] == False:
        index_last_true = np.where(output['isDigit'] == True)[0][-1]
        output['value_fixed'][index_last_true:-1] = output['value_fixed'][index_last_true]
        output['fix_scenario'][index_last_true:-1] = 'start_end_normal'

        if (output.shape[0] - index_last_true) > 14:
            j=output.shape[0]
            while j>index_last_true:
                output['value_fixed'][j] = str(int(output['value_fixed'][index_last_true]) + 1)
                output['fix_scenario'][j] = 'start_end_far'
                j-=1

    # Middle part
    wrong_list=np.where(output['isDigit'] == False)[0].tolist()
    
    # Shuffle the list to make the fixing order more random, so we can rely on neighbor values
    wrong_list_shuffle = random.sample(wrong_list,len(wrong_list))

    for i in wrong_list_shuffle:
        k=1
        while k<=14:
            
            # If the two closest neighbors are True and the values are the same, then give it the same value
            if (i-k>=0) and (i+k <= output.shape[0]-1) and (output['isDigit'][i-k]) == True & (output['isDigit'][i+k]== True):
                if output['value_fixed'][i - k] == output['value_fixed'][i + k]:
                    output['value_fixed'][i] = output['value_fixed'][i-k]
                    output['fix_scenario'][i] = f'{k}_same_neighbor'
                    break
                    
                # If the two closest neighbors are True and the values are different, then give it the value of the first True (left biased)
                else:
                    output['value_fixed'][i] = output['value_fixed'][i-k]
                    output['fix_scenario'][i] = f'{k}_single_True_left_neighbor'
                    break
                    
            # If one of the two closest neighbors is True and another is False, then give it the value of the True
            elif (i-k>=0) and (output['isDigit'][i-k]) == True :
                    output['value_fixed'][i] = output['value_fixed'][i-k]
                    output['fix_scenario'][i] = f'{k}_left_neighbor'
                    break
            elif (i+k <= output.shape[0]-1) and (output['isDigit'][i+k] == True):
                    output['value_fixed'][i] = output['value_fixed'][i+k]
                    output['fix_scenario'][i] = f'{k}_right_neighbor'
                    break
            else:
                k+=1
            if k==15:
                output['value_fixed'][i] = 99
                output['fix_scenario'][i] = 'no_neighbor'
                break

    return output


# In[18]:


current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

updated_dataframe=fixing_function(dataframe)
updated_dataframe.loc[updated_dataframe['isDigit'] == False,:]

current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# In[19]:


# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create a file name using the formatted date and time
file_name = "Step_4_updated_dataframe_" + str(test_case) +f"_{formatted_datetime}.xlsx"

# Print the file name
print("saving data frame to", file_name)
updated_dataframe.to_excel(file_name)


# <h3>5 - Check for Continuous Value</h3>
# 

# In[20]:


def find_continuous_count(arr):
    """
    Finds the continuous count of each element in the given array

    Args:
        arr (list): The input array containing elements

    Returns:
        pandas.DataFrame: A DataFrame containing information about the continuous counts
            The DataFrame has the following columns:
            - 'number': The element in the array.
            - 'count': The count of the continuous occurrences of the element
            - 'Start Index': The start index of the continuous sequence in the array
            - 'End Index': The end index of the continuous sequence in the array
    """
    result = []
    count = 1
    start_index = 0
    
    for i in range(1, len(arr)):
        if arr[i] == arr[i-1]:
            count += 1
        else:
            result.append({'number': arr[i-1], 'count': count, 'Start Index': start_index, 'End Index': i-1})
            count = 1
            start_index = i
    
    # Handle the last number in the array
    result.append({'number': arr[-1], 'count': count, 'Start Index': start_index, 'End Index': len(arr)-1})
    
    return pd.DataFrame(result)

def retainIntegers(string):
    """
    Extracts and returns the integer value from a given string

    Args:
        string (str): The input string

    Returns:
        int: The extracted integer value from the string.
            If the string does not contain any integers or an error occurs during the extraction,
            the function returns 0.
    """

    try:
        
        # Matches any non-digit character
        pattern = r'\D'  
        
        # Removes all non-digit characters from the string
        result = re.sub(pattern, '', string)  
        
         # Converts the resulting string to an integer and returns it
        return int(result) 
    except (TypeError, ValueError):
        
        # Returns 0 if a TypeError or ValueError occurs during the conversion
        return 0  


def find_most_frequent_value(arr):
    """
    Finds the most frequent value in a given array

    Args:
        arr (list): The input array containing values and their corresponding counts

    Returns:
        Any: The most frequent value in the array
            If the array is empty, the function returns None
    """

    # Dictionary to store the counts of each value
    counts = {}  
    
    # Variable to keep track of the maximum count
    max_count = 0  
    
     # Variable to store the most frequent value
    most_frequent_value = None 
    
    for value, count in arr:
        if value in counts:
            
            # Increment the count if the value already exists in the dictionary
            counts[value] += count  
        else:
            
            # Add the value to the dictionary if it doesn't exist
            counts[value] = count  
        
        if counts[value] > max_count:
            
            # Update the maximum count
            max_count = counts[value]  
            
            # Update the most frequent value
            most_frequent_value = value  
    
     # Return the most frequent value
    return most_frequent_value 

def repeat_values(arr):
    """
    Repeats the values in a given array based on their corresponding counts

    Args:
        arr (list): The input array containing values and their corresponding counts

    Returns:
        list: A new array with repeated values based on their counts
            The order of the repeated values is determined by the order of the original array
            If the input array is empty, the function returns an empty array
    """

    # List to store the repeated values
    repeated_array = []  
    
    for value, count in arr:
        
         # Extend the repeated_array with the repeated values
        repeated_array.extend([value] * count) 
    
    # Return the new array with repeated values
    return repeated_array  


# In[21]:


current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

counts_df = find_continuous_count(updated_dataframe.value_fixed.tolist())


# In[22]:


final_value_counts = []  # List to store the final values and counts
index_to_ignore = []  # List to keep track of indices to ignore

 

# Iterate over each row in the 'counts_df' DataFrame
for index, row in counts_df.iterrows():
    curr_value = counts_df['number'].iloc[index]  # Get the 'number' value from the current row
    curr_count = counts_df['count'].iloc[index]  # Get the 'count' value from the current row
    total_count = curr_count  # Initialize the total count with the current count
    most_frequent_val = curr_value  # Initialize the most frequent value with the current value

    if index not in index_to_ignore:  # Check if the current index should be ignored
        if curr_count < 15:  # Check if the current count is less than 15
            array_which_is_added = []  # Initialize an array to store added values
            array_which_is_added.append([curr_value, curr_count])  # Add the current value and count to the array

            # Iterate up to 10 times to find additional values that satisfy the total count condition
            for i in range(10):

                #to ensure the count is not going more than 15
                try:
                    if counts_df['count'].iloc[index +i+ 1] >= 15:
                        break
                except:
                    pass

                try:
                    # Check if adding the count of the next row would exceed 15
                    if (total_count + counts_df['count'].iloc[index+1+i]) <= 15:
                        total_count += counts_df['count'].iloc[index+1+i]  # Update the total count
                        array_which_is_added.append([counts_df['number'].iloc[index+1+i], counts_df['count'].iloc[index+1+i]])  # Add the next value and count to the array
                        index_to_ignore.append(index+1+i)  # Add the next index to ignore list
                    if (total_count + counts_df['count'].iloc[index+1+i]) >= 15:
                        break
                except IndexError:
                    pass  # Ignore index errors if the next row doesn't exist

            most_frequent_val = find_most_frequent_value(array_which_is_added)  # Find the most frequent value in the array
        final_value_counts.append([most_frequent_val, total_count])  # Append the most frequent value and total count to the final list
    elif index in index_to_ignore:
        pass  # Ignore the current index if it should be ignored

new_values = repeat_values(final_value_counts)


# In[23]:


updated_dataframe['fix_continous'] = new_values
current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# In[24]:


# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the date and time as a string
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create a file name using the formatted date and time
file_name = "Step_5_updated_dataframe_" + str(test_case) +f"_{formatted_datetime}.xlsx"

# Print the file name
print("saving data frame to", file_name)
updated_dataframe.to_excel(file_name)


# <h3>6 - Add/Drop Frames</h3>

# In[25]:


def add_drop_frames(updated_dataframe):
        """
        Adds or drop frames in starting, middle and ending part of the video to keep 15 frames consistency

        Args:
            updated_dataframe (dataframe): The dataframe contain the update value for the column filename, value and score

        Returns:
            list: A new array with repeated values based on their counts
                The order of the repeated values is determined by the order of the original array
                If the input array is empty, the function returns an empty array
        """
        
        
        count = 0
        prev_text = None
        consecutive_count = 0
        
        # Flag to indicate whether to remove the first group
        should_remove = True  
        prev_frame = None
        
        # Store files to delete
        files_to_delete = []  
        detect_start = False
        
        # Iterate through the image files in the directory
        image_files = sorted(os.listdir(image_directory), key=lambda x: int(x.split('.')[0])) 
        deleted_folder = os.path.join(image_directory, "deleted")
        os.makedirs(deleted_folder, exist_ok=True)
        minutes =  '59' 

        # Get the last index of the files
        last_index = len(image_files) - 1  
        prev_text = None
        if not updated_dataframe.empty:
            
            # Display the OCR result
            for index, row in updated_dataframe.iterrows():
                #print(f"Text: {row.fix_continous}, prev_text: {prev_text}, consecutive count is {consecutive_count}")
                if int(row.fix_continous) != 0 and prev_text is None or index > 54000 and int(row.fix_continous) < 10:
                    source_file = os.path.join(image_directory, row.filename)
                    destination_file = os.path.join(deleted_folder, row.filename)
                    shutil.move(source_file, destination_file)if os.path.exists(source_file) else None
                    print("deleting frame at ", row.filename , minutes,":", row.fix_continous)  #added
                    prev_text = None
                    continue
                count +=1
                if int(count/60)<10:   
                    temp = (int(count/60))
                    minutes = '0' + str(temp)
                else:
                    minutes = int(count/60)

                # Count consecutive digits
                if prev_text is not None and int(row.fix_continous) == int(prev_text):
                    consecutive_count += 1
                    prev_frame = row.filename

                else:
                    if (consecutive_count < 15 and prev_text is not None):
                        for i in range(15 - consecutive_count):
                            print(f"Duplicated: {prev_frame} at   { minutes} : {prev_text}") #added
                            
                            # Duplicate the last frame until it reaches 5
                            source_file = os.path.join(image_directory, prev_frame)
                            updated_prev_frame = prev_frame.replace('.png', '')
                            print(f"{updated_prev_frame}_{i}.png")
                            destination_file = os.path.join(image_directory, f"{updated_prev_frame}_{i}.png")
                            shutil.copy2(source_file, destination_file)
                    if consecutive_count > 15:
                        for i in range(consecutive_count - 15):
                            deleted_added_frame = prev_frame.replace('.png', '')
                            deleted_added_frame = int(deleted_added_frame)
                            deleted_added_frame = deleted_added_frame + i
                            deleted_added_frame = f"{deleted_added_frame}.png"
                            print(f"Deleted: {deleted_added_frame} at  { minutes} : {prev_text}") #added
                            
                            # Store the filename to delete
                            files_to_delete.append(deleted_added_frame)  
                    consecutive_count = 1
                    
                # Log the results in the CSV file if important
                    prev_text = row.fix_continous
        if consecutive_count < 15:
            if  int(row.fix_continous) > 57:
                for i in range(15-consecutive_count):
                    print(f"Duplicate the last one: {row.filename} at  { minutes} : {row.fix_continous}")  #added
                    # Duplicate the last frame until it reaches 5
                    source_file = os.path.join(image_directory, row.filename)
                    updated_filename = row.filename.replace('.png', '')
                    destination_file = os.path.join(image_directory, f"{updated_filename}_{i}.png")
                    shutil.copy2(source_file, destination_file)

        for filename in files_to_delete:
            source_file = os.path.join(image_directory, filename)
            destination_file = os.path.join(deleted_folder,filename)
            print("Deleting frame ", filename)
            shutil.move(source_file, destination_file)if os.path.exists(source_file) else None
        print("Successfully synchronized")


# In[26]:


# Check time for reference
current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

add_drop_frames(updated_dataframe)

# Check time for reference
current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# <h3>7 - Video Construction</h3>
# <p style="font-size: 15px">Reading frames through CV2 and then using ffmpeg to make the video file while keeping HEVC-265 codec</p>

# In[27]:


def convert_frames_to_video(frames_path, video_name, ffmpeg_path):
    """
    Function for converting frames to video (HEVC-265)

    Args:
        frames_path (string): The location of folder containing the added and dropped frames
        video_name (string): The name of the video 
        ffmpeg_path(string): The path for the ffmped executable file

    """
    image_files_test = os.listdir(frames_path)

    #Make resolution 1280x720, and 15 fps
    width, height, fps = 1280, 720,  15 

    #ffmpeg is necessary part for HEVC-256 codec
    process = sp.Popen(shlex.split(f'ffmpeg -y -s {width}x{height} -pixel_format bgr24 -f rawvideo -r {fps} -i pipe: -vcodec libx265 -crf 24 {video_name}'), stdin=sp.PIPE)

    
    #Array for saving the frame that would be converted to video
    frame_array= []

   #Reading the frames from the folder
    files = [f for f in os.listdir(frames_path) if isfile(join(frames_path, f))]

    #Removing .png for sorting
    files_updated = [files.replace('.png', '') for files in files]
    
    #Sorting as per alphanumeric
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c.replace("_","")) for c in re.split('([0-9]+)', key) ]
    files_updated.sort( key=alphanum_key )
    png_string = ".png"
    files_updated_string = [s + png_string for s in files_updated]

    for i in tqdm(range(len(files_updated_string))):
        filename=frames_path + files_updated_string[i]
        #Reading each files
        image = cv2.imread(filename)
        image_np = np.array(image)

        # Write raw video frame to input stream of ffmpeg sub-process.
        process.stdin.write(image_np.tobytes())

    # Close and flush stdin
    process.stdin.close()

    # Wait for sub-process to finish
    process.wait()

    # Terminate the sub-process
    process.terminate()


# In[28]:


# Check time for reference
current_time = datetime.datetime.now().time()
print('Start Time= ', current_time)

convert_frames_to_video(frames_path, video_name, ffmpeg_path)    

# Check time for reference
current_time = datetime.datetime.now().time()
print('End Time= ', current_time)


# # Final check if the video created is 15 fps

# In[29]:


# Reading the file
vid = cv2.VideoCapture(video_name)
print(f"Name:\t\t{video_name}")

# Get frame details
video_width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = vid.get(cv2.CAP_PROP_FPS)
video_frame_cnt = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
print('Video:\t\t', video_fps, video_frame_cnt, video_width, video_height)


# In[ ]:





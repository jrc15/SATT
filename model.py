# model.py
# J. Cook
# Email: "jrc15@aber.ac.uk"
# This is the model part of the QT Application - balsam - extract & map

from shapely.geometry import LineString, Point
import exiftool as exiftool # need exiftool software in same directory as code (exiftool.exe) # ensure pyexiftool in installed via pip
from statistics import mean
import geopandas as gpd
import pandas as pd
import numpy as np
import math
import glob
import csv
import cv2
import sys
import os

 
class Model:
    def __init__( self ):
        '''
        Initializes the two members the class holds:
        the file name and its contents.
        '''
        self.fileName = None
        self.fileContent = ""


    def extractBalsam( self, dirPath, flwDir, outPath, results):
        print("In MODEL: Unpacking Results")
        # unpack results
        Lh, Ls, Lv, Uh, Us, Uv, Fshp, Fx, Fy, Os, Bbox = results
        print('In Model: ', Lh, Ls, Lv, Uh, Us, Uv, Fshp, Fx, Fy, Os, Bbox)
        
        ###### Automatic Threshold Extraction of Balsam Objects fom Oblique Images ######

        # create annotation file name
        vectorNames = dirPath.split("/")[-1]
        annotation_csv = outPath + '/' + vectorNames + '_annotations.csv'
        print(annotation_csv)
        print(outPath + '/' + vectorNames)

        # get list of images from directory
        imgList = glob.glob(dirPath + '\*.JPG')

        # empty list to hold feature vectors list per image
        flower_count = []

        # list of annotations, headers included in sublist
        _annotations = [['filename', 'width', 'height', 'class', 
                        'xmin', 'ymin', 'xmax', 'ymax']]

        # set progressbar ranges
        self.extractionBar.setRange(0, 100)

        # loop through each image,
        # pull out flowers and annotate
        for i, img in enumerate(imgList):
            #print("Processing: ",i, " of ", len(imgList), end=" \r")

            # emit signal
            progress = int(100*(i+1)/len(imgList))
            yield progress

            filename = img

            outImg = flwDir + img[len(dirPath):-4] + '_flowers.png'

            # read image with openCV
            img = cv2.imread(img)

            # convert image from rgb to bgr
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # blur image
            blur = cv2.GaussianBlur(img_bgr, (15, 15), 2)

            # convert to HSV,
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            h,s,v = cv2.split(hsv)

            # keep v channel constant
            zeros = np.zeros(hsv.shape[:2], dtype="uint8")

            # merge the image back together again
            merged = cv2.merge([h, s, zeros])

            # calculate avergae brightness value
            average = np.mean(v)              
            
            # define upper and lower boundaries for flowers
            lower_red = np.array([Lh, Ls, Lv]) # [110, 20, 0]   #100
            upper_red = np.array([Uh, Us, Uv]) # [255, 255, 0]   #255

            # create a mask of the flowers using range
            mask = cv2.inRange(merged, lower_red, upper_red)

            if Fshp == 'Ellipse':
                # create an ellipsed kernel
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (Fx, Fy))
            elif Fshp == 'Cross':
                # create an ellipsed kernel
                kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (Fx, Fy))
            elif Fshp == 'Rectangle':
                # create an ellipsed kernel
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (Fx, Fy))
            
            # remove noise
            opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

            #combine mask and image
            masked_img = cv2.bitwise_and(img, img, mask=opened_mask)

            # convert to grey scale ready to extract contours
            masked_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)

            # get external contours of objects in image
            image, contours, hier = cv2.findContours(masked_img, 
                                                     cv2.RETR_TREE, 
                                                     cv2.CHAIN_APPROX_SIMPLE)

            # get contours in area range, 
            # get annotation information
            cnts = []

            i = 1
            l = 1
            for n,c in enumerate(contours):
                area = cv2.contourArea(c)
                if area > 100 and area < 2000:

                    # get the bounding rect
                    x, y, w, h = cv2.boundingRect(c)

                    # draw a green rectangle to visualize the bounding rect
                    cv2.rectangle(img, (x, y), (x+w, y+h), Bbox, 2)

                    # add contours to be drawn to list
                    cnts.append(contours[n])                                    

                    # write annotation info to list
                    filename = filename.split('\\')[-1]
                    annotation = [filename, img.shape[1], img.shape[0], 'balsam', 
                                  math.floor(x), math.floor(y), 
                                  math.ceil(x+w), math.ceil(y+h)]

                    _annotations.append(annotation)

                    i = i+1
                l = l+1

            flower_count.append(len(cnts))

            # draw aqua coloured cnts on img
            cv2.drawContours(img, cnts, -1, (255, 255, 0), 1)

            # save and view image
            cv2.imwrite(outImg, img)

        # write annotations list out to csv
        with open(annotation_csv, "w", newline="") as f: 
            writer = csv.writer(f)
            writer.writerows(_annotations)

        print('Automatic Threshold Extraction Completed.')

        # if check box for 'Only CNN Training' is ticked end script
        if self.checkCNNBox.isChecked():
            sys.exit()




        ###### get mean of each flower  ######

        # NOTE: sometimes needs to be run twice???

        # read annotation csv as df
        df = pd.read_csv(annotation_csv)

        # get list of columns
        columns = df.columns

        # image width
        hoi, img_width = img.shape[:2]
        #img_width = 4864

        # segments
        segment_1 = img_width/5
        segment_2 = segment_1*2
        segment_4 = img_width - (segment_1*2)
        segment_5 = img_width - segment_1

        #### get pixel size of each flower in each image ####

        # lists
        seg_1_heights = []  # segment 1 flowers heights lists
        seg_5_heights = []  # segment 5 flowers heights lists
        flower_files = []   # list of image indexes that contain flowers
        mean_heights = []   # list of image mean heights
        count = []          # count of flowers


        #### get mean pixel size of flowers per image ####

        # get list of unique filenames
        filenames = df[columns[0]].unique()

        for n, x in enumerate(flower_count):
            if x != 0:
                flower_files.append(n)
                count.append(x)

        #print('flower files = ', len(flower_files))
        #print('filenames = ', len(filenames))

        flower_count = count

        # get list of filesnames containing flowers
        files = filenames

        # get mean balsam object heights
        for i, name in enumerate(filenames):

            #self.metricsBar.setValue(i+1)
            #print("Processing: ",i, " of ", len(filenames), end=" \r")

            new_df = df[df[columns[0]]==name]
            img_heights = []
            seg_1 = []
            seg_5 = []

            # loop through rows in df and get y min & max, and object height
            for ind in new_df.index:        
                xmin = new_df[columns[4]][ind]
                ymin = new_df[columns[5]][ind]
                xmax = new_df[columns[6]][ind]
                ymax = new_df[columns[7]][ind]
                height = ymax - ymin
                img_heights.append(height)

                # create list of flowers in left most image segment
                if xmin < segment_1 and xmax < segment_1:
                    seg_1.append(height)

                elif xmin < segment_2 and xmax < segment_2:
                    seg_1.append(height)

                # create list of flowers in right most image segment
                if xmin > segment_5 and xmax > segment_5:
                    seg_5.append(height)

                elif xmin > segment_4 and xmax > segment_4:
                    seg_5.append(height)


            mean_heights.append(mean(img_heights))

            # get average of largest 25% of flowers in seg_1
            n = int(round(len(seg_1)/4, 0))

            if n > 0:
                a = np.array(seg_1)
                ind = np.argpartition(a, -n)[-n:]
                seg_1_mean = mean(a[ind])
            else:
                seg_1_mean = -9999

            # get average of largest 25% of flowers in seg_5
            n = int(round(len(seg_5)/4, 0))

            if n > 0:
                a = np.array(seg_5)
                ind = np.argpartition(a, -n)[-n:]
                seg_5_mean = mean(a[ind])
            else:
                seg_5_mean = -9999

            # append to lists for later use
            seg_1_heights.append(seg_1_mean)
            seg_5_heights.append(seg_5_mean)

        print('Generated Height Metrics for Flowers Completed.')

        ###### calculate distance of flowers in image from image capture point ######

        # get list of files
        images = [imgList[n] for n in flower_files]
        
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(images[0])
            gimbal = et.get_tag_batch('GimbalYawDegree', images)
            flight= et.get_tag_batch('FlightYawDegree', images)
            long = et.get_tag_batch('GPSLongitude', images)
            lat = et.get_tag_batch('GPSLatitude', images)
            focal = et.get_tag_batch('FocalLength',images)
            image_height = et.get_tag_batch('ImageHeight',images)
            fov = et.get_tag_batch('FOV', images)

        #print(len(images), len(flower_count), len(seg_1_heights), len(seg_5_heights))
        
        adjusted_gimbal = []
        adjusted_flight = []
        orientation = []
        longitude = []

        # adjust gimbal values to 360 degrees
        for value in gimbal:
            value = float(value)
            if value < 0:
                value = float(value) + 360
                adjusted_gimbal.append(value)
            else:
                adjusted_gimbal.append(value)        

        # adjust flight values to 360 degrees
        for value in flight:
            value = float(value)
            if value < 0:
                value = float(value) + 360
                adjusted_flight.append(value)
            else:
                adjusted_flight.append(value)

        #get orientation values
        for n in range(0,len(adjusted_gimbal)):
            x = adjusted_gimbal[n] + adjusted_flight[n]
            if x > 360:
                x = x - 360
                orientation.append(x)
            else:
                orientation.append(x)

        # convert negative values to positive
        for value in long:
            lon = -abs(value)
            longitude.append(lon)

        # create new dataframe with the following variables    
        df = pd.DataFrame(
            {'image_name': images,
             'GimbalYawDegree': gimbal,
             'FlightYawDegree': flight,
             'adjusted_gimbal': adjusted_gimbal,
             'adjusted_flight': adjusted_flight,
             'long': longitude,
             'lat': lat,
             'orientation': orientation,
             'balsam_heights': mean_heights,
             'l_balsam_heights': seg_1_heights,
             'r_balsam_heights': seg_5_heights,
             'image_height': image_height,
             'flower_count': flower_count
            })

        #print(df.head())

        ### calculate distance for each image ###

        remove_ind = []
        distances = []
        lines = []
        capLines = []
        fov_lengths = []
        centre_lons = []
        centre_lats = []

        # open file in geopandas
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long, df.lat), crs="EPSG:4326")
        #print(gdf.head())

        # calculate object distance from coordinates in given orientation
        focal_length = focal[0]
        real_object_height = Os                               ####### Add as button/parameter in function/GUI #######
        sensor_height = 8.8

        #print('focal length = ', focal[0])
        for n in range(0,len(focal)):

            # image and object heights
            balsam_heights = df['balsam_heights'][n]
            img_height = df['image_height'][n]

            # object heights on left and right sides of image
            balsam_heights_l = df['l_balsam_heights'][n]
            balsam_heights_r = df['r_balsam_heights'][n]

            # central point distance  of image
            distance = ((focal_length*real_object_height*img_height)/(balsam_heights*sensor_height))/1000
            distances.append(distance)


            ###### Move points by distance(m) and bearing(degrees) for centre ######

            # Radius of the Earth
            r = 6378.1 

            # Bearing is converted to radians
            brng = math.radians(adjusted_gimbal[n])

            # Distance in m
            d = (distance/1000)

            # Centre Coordinates - Convert lat & lon to radians
            lat_rad = math.radians(lat[n])
            lon_rad = math.radians(longitude[n])

            # Calculate the latitudinal projection
            centreLat = math.asin(math.sin(lat_rad)*math.cos(d/r) + 
                                  math.cos(lat_rad)*math.sin(d/r)*math.cos(brng))

            # Calculate the longitudinal projection
            centreLon = lon_rad + math.atan2(math.sin(brng)*math.sin(d/r)*math.cos(lat_rad),
                                 math.cos(d/r)-math.sin(lat_rad)*math.sin(centreLat))

            # Convert lat & lon to degrees
            centreLat = math.degrees(centreLat)
            centreLon = math.degrees(centreLon)

            # append coords to lists
            centre_lats.append(centreLat)
            centre_lons.append(centreLon)


            ##### Create left image coordinates #####

            d_h = distance/math.cos(math.radians(fov[n]/2))/1000

            # Subtract half the camera field of view to give a bearing for the left side of the image
            lbrng = brng -(math.radians(fov[n]/2))

            # Calculate the lat & lon projection # was l_d
            leftLat = math.asin(math.sin(lat_rad)*math.cos(d_h/r) + 
                                math.cos(lat_rad)*math.sin(d_h/r)*math.cos(lbrng))

            leftLon = lon_rad + math.atan2(math.sin(lbrng)*math.sin(d_h/r)*math.cos(lat_rad),
                                           math.cos(d_h/r)-math.sin(lat_rad)*math.sin(leftLat))

            # Convert lat & lon to degrees
            leftLat = math.degrees(leftLat)
            leftLon = math.degrees(leftLon)


            ##### Create right image coordinates #####

            # Add half the camera field of view to give a bearing for the right side of the image
            rbrng = brng +(math.radians(fov[n]/2))

            # Calculate the lat & lon projection # was r_d
            rightLat = math.asin(math.sin(lat_rad)*math.cos(d_h/r) + 
                                math.cos(lat_rad)*math.sin(d_h/r)*math.cos(rbrng))

            rightLon = lon_rad + math.atan2(math.sin(rbrng)*math.sin(d_h/r)*math.cos(lat_rad),
                                           math.cos(d_h/r)-math.sin(lat_rad)*math.sin(rightLat))

            # Convert lat & lon to degrees
            rightLat = math.degrees(rightLat)
            rightLon = math.degrees(rightLon)

            # create linestring of each image
            line = LineString([Point(leftLon, leftLat), Point(rightLon, rightLat)])
            lines.append(line)

            capLine = LineString([Point(longitude[n], lat[n]), Point(centreLon, centreLat)])
            capLines.append(capLine)

            #print("\r" + str(n+1) + " of " + str(len(focal)) + "\r", end="")

        # add new column to df
        df['distances'] = distances

        # drop indice with no balsam values
        df_drop = df.drop(remove_ind)

        # create geodataframe, and write to file as lines:
        try:
            new_gdf = gpd.GeoDataFrame(df_drop, geometry=lines, crs = gdf.crs)
            new_gdf = new_gdf.to_crs("EPSG:27700")
            new_gdf['fov_width'] = new_gdf.geometry.length   
            new_gdf['flowers_per_m'] = new_gdf['flower_count']/new_gdf['fov_width']
            new_gdf.to_file(outPath + '/' + vectorNames + '_FOV_Lines.geojson', driver='GeoJSON')
            
        except Exception as e: print(e)
            
        #print(outPath + '/' + vectorNames + '_FOV_Lines.geojson')

        # and points:
        point_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(centre_lons, centre_lats), crs = gdf.crs)
        point_gdf['flowers_per_m'] = new_gdf['flowers_per_m']
        point_gdf = point_gdf.to_crs("EPSG:27700")
        point_gdf.to_file(outPath + '/' + vectorNames + '_Centre_points.geojson', driver='GeoJSON')

        # gps point of image capture fom drone
        capture_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(longitude, lat), crs = gdf.crs)
        capture_gdf = capture_gdf.to_crs("EPSG:27700")
        capture_gdf.to_file(outPath + '/' + vectorNames + '_Capture_Points.geojson', driver='GeoJSON')

        # draw line from capture point to centre line of image
        capture_dist = gpd.GeoDataFrame(df, geometry=capLines, crs = gdf.crs)
        capture_dist = capture_dist.to_crs("EPSG:27700")
        capture_dist.to_file(outPath + '/' + vectorNames + '_Capture_Lines.geojson', driver='GeoJSON')

        print('Completed Vector Generation')
        
        
    def processAdvance( self, filename, results):
    
        # unpack results
        Lh, Ls, Lv, Uh, Us, Uv, Fshp, Fx, Fy, Os, Bbox = results
        print('In Model: ', Lh, Ls, Lv, Uh, Us, Uv, Fshp, Fx, Fy)
        
        ###### Automatic Threshold Extraction of Balsam Objects fom Oblique Images ######
        #outImg = flwDir + img[len(dirPath):-4] + '_flowers.png'  might need to add a tmp folder to input folder and save localy to there.

        # read image with openCV
        img = cv2.imread(filename)

        # convert image from rgb to bgr
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # blur image
        blur = cv2.GaussianBlur(img_bgr, (15, 15), 2)

        # convert to HSV,
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)

        # keep v channel constant
        zeros = np.zeros(hsv.shape[:2], dtype="uint8")

        # merge the image back together again
        merged = cv2.merge([h, s, zeros])
        
        # define upper and lower boundaries for flowers
        lower_red = np.array([Lh, Ls, Lv]) # [110, 20, 0]   #100
        upper_red = np.array([Uh, Us, Uv]) # [255, 255, 0]   #255

        # create a mask of the flowers using range
        mask = cv2.inRange(merged, lower_red, upper_red)
        
        if Fshp == 'Ellipse':
            # create an ellipsed kernel
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (Fx, Fy))
        elif Fshp == 'Cross':
            # create an ellipsed kernel
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (Fx, Fy))
        elif Fshp == 'Rectangle':
            # create an ellipsed kernel
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (Fx, Fy))
        
        # remove noise
        opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        #combine mask and image
        masked_img = cv2.bitwise_and(img, img, mask=opened_mask)
        
        # return mask, and load to plot
        return masked_img
        
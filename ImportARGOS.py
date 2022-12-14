##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: 17 October 2022
## Author: eliza.carter@duke.edu (for ENV859)
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

# Set input variables (Hard-wired)
inputFolder = '../Data/ARGOSData'
inputFiles = os.listdir(inputFolder)
outputSR = arcpy.SpatialReference(54002)
outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"

arcpy.env.overwriteOutput = True

## Prepare a new feature class to which we'll add tracking points
# Create an empty feature class; requires the path and name as separate parameters
outPath,outName = os.path.split(outputFC)
arcpy.management.CreateFeatureclass(outPath, outName, "POINT","","","", outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.management.AddField(outputFC,"TagID","LONG")
arcpy.management.AddField(outputFC,"LC","TEXT")
arcpy.management.AddField(outputFC,"Date","DATE")

# Create the insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])

for i in inputFiles:
    if i == 'README.txt':
        continue
    
    #create a path for each object in the folder
    i = os.path.join(inputFolder, i)
    
    #Construct a while loop to iterate through all lines in the datafile
    # Open the ARGOS data file for reading
    inputFileObj = open(i,'r')
    
    # Get the first line of data, so we can use a while loop
    lineString = inputFileObj.readline()
    
    # Start the while loop
    while lineString:
        
        # Set code to run only if the line contains the string "Date: "
        if ("Date :" in lineString):
            
            # Parse the line into a list
            lineData = lineString.split()
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()        
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
          
            # Extract attributes from the datum header line
            tagID = lineData[0]
            obsDate = lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            # Print results to see how we're doing
            #print (tagID, "Date:"+obsDate, "Time:"+obsTime, "Location Class:"+obsLC, "Lat:"+obsLat,"Long:"+obsLon)
            
            
            #Try to convert the coordinates to numbers
            try:
                # Convert raw coordinate strings to numbers
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else:
                    obsLat = float(obsLat[:-1]) * -1
                if obsLon[-1] == 'E':
                    obsLon = float(obsLon[:-1])
                else:
                    obsLon = float(obsLon[:-1]) * -1
                    
                # Construct a point object from the feature class
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat
          
                # Convert the point to a point geometry object with spatial reference
                inputSR = arcpy.SpatialReference(4326)
                obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
                
                # Create a feature object
                feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") + " " + obsTime))
                
            #Handle any error
            except Exception as e:
                print(f"Error adding record {tagID} to the output: {e}") 
            
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()
        
    #Close the file object
    inputFileObj.close()
    
#Delete the cursor object
del cur
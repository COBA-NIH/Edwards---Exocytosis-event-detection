One-step protocol
  - ImageJ script
    - Input - timelapse movies (name and name_NH3 pairs)
    - Output - .csv file event x,y position and frame number, .tif label image and a .tif overlay

Automatic event detection using ImageJ and ImageJ plugin Event_detection_TrackMate

1.	Open " Event_detection_withGUI_overlay.py" script in Fiji or ImageJ
2.	Make sure the language selected is Python
3.	Hit Run
4.	Select the folder on your computer where all the movies are located
5.	Change any parameters that need changing and check the output folder where all results will be saved.
6.	From this point on the process is automatic
    - Each movie takes 2-5 min depending on the number of events and can be
    run unsupervised
Parameters that can be adjusted include

Setting	Default Setting	Description
Are files on tiff format?	Yes	Are files in a tif format or another format was used
if not, what format?	tif	File format the movies where saved as
Number of frames	100	length of time-lapse movie
Number of stimuli	8	number of stimuli
First stimuli frame	20	frame where first stimuli is given
Stimuli frame interval	6	rate of stimuli
Number of frames on NH3 movie	26	length of NH3 time-lapse movie
NH3 addition frame	22	frame NH3 was added
Spot diameter	5	Average size of the vesicles, will change based on the magnification used on the microscope
Threshold	100	threshold for the event detection larger values will result in less events detected, bright events being detected, smaller values will result in more event, but this might include false events
Link distance	2	this set the distance that an event can within a frame for static events this value should be set close to 0
  Gap distance	2	this set the distance that an event can move from frame to frame, for static events this value should be set close to 0
Output folder	output_path	Folder in your computer where result files will be saved

Description of result files

csv file event x,y position and frame number

A csv file will be saved for each stimuli, one for the whole stimuli movie and one for the NH3 movie

•	For each stimuli the file name will be as follows

o	(Name of movie)_img(stimuli number).csv

•	For the whole stimuli movie

o	(Name of movie)_whole.csv

•	For the NH3 movie

o	(Name of movie)_total.csv

.tif label image and a .tif overlay
•	For the whole stimuli movie

o	(Name of movie)_lblImg.tif – image of the detected events
o	(Name of movie)_overlay.tif – image of the detected events overlayed on the original image

•	For the NH3 movie

o	(Name of movie)_lblImg_NH3.tif – image of the detected events
o	(Name of movie)_overlay_NH3.tif – image of the detected events overlayed on the original image

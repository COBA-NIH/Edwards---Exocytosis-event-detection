### Step by Step protocol for vesicle fusion detection ###

This protocols is a two-step process
  - ImageJ script
    - Input - timelapse movie (.nd2 file)
    - Output - .csv file event x,y position and frame number, .tif timelapse
    and tif label image
  - Jupyter notebook
    - Input - .csv file, .tif timelapse and tif label image
    - Output - pdf with event graphs

The first part of the process is the automatic event detection using ImageJ
and ImageJ plugin Event_detection_TrackMate

  1. Open "Event_detection_TrackMate" script in Fiji or ImageJ
  1. Make sure the language selected is Python
  1. Change the input and output folders in line 27 and 28 of the script
    - The input folder should have all movies to be processed the script
    expects '.nd2' files but can be modified in line 39
    - If running the script in MacOs make sure you remove the DS file form
    this folder
  1. Hit Run from this point on the process is automatic
    - Each movie takes 5-10 min depending on the number of events and can be
    run unsupervised

Parameters that can be adjusted include
 - file_type - the file format that the movie is saved as.
 - frames - length of time-lapse movie
 - step_size - number of frames that are used to remove background fluorescence
 should be 2-3 times the duration of the longest event.
 - diameter - average diameter of the event in microns or pixels (if the movie
 no scale information)
 - threshold - threshold for event detection larger values will result in less
 events detected (bright events); smaller values will result in more event but
 this might include false events.
 - channel - trackmate can work on images that include more than one channel if
 that is the case select the channel were the events are being detected.
 - link_distance - distance that an event can shift whitin a frame, for static
 events this value should be set close to 0
 - gap_distance - distance that an event can move from frame to frame, for
 static events this value should be set close to 0
 - gap_frame - number of frames that can have no event detected between
 two event and still be considered the same event


The second part of the process is the filtering of false events and to determine
vesicle type

  1. Open "Event_filter_graph" script in Jupyter notebook (or any other python
  console)
  1. Change the input and output folders in line 27 and 28 of the script
    - The input folder should be the output folder of the previous Fiji script
  1. Execute the code, the process is completely automatic
    - Each movie takes between 10-15 min depending on the number of events.
    - At the end of the process several files are created
      1. TimeTrace file contains the intensity
      1. Measurements file with the x,y coordinates, start and end, baseline,
      post-event and vesicle type.
      1. Event graphs with start frame, x,y coordinates and vesicle type

Parameters
 - crop_size_begining - number of frames at the beginning that should be omitted
 - crop_size_end - number of frames at the beginning that should be omitted
 - max_event_frame - number of maximum event present at a single frame
 - event_ext - number of frame to extend the event for peak and baseline detection
 - pixel_size - pixel size of the events
 - event_min_intensity = 15
 - baseline_size - approximate frame number used for baseline and post event calculation
 - smooth_long - smooth size applied to long event for peak detection
 - smooth_mid - smooth size applied to mid length event for peak detection
 - smooth_short - smooth size applied to short events for peak detection

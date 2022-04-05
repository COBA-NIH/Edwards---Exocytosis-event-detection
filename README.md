# Edwards---Exocitosis-event-detection

Image analysis pipeline to detect exocytosis (vesicle fusion at plasma membrane) 
on TIRF microscopy timelapse images

This protocols is a two-step process
 - The first part of the process is the automatic event detection using ImageJ
 and ImageJ plugin TrackMate - Event_detection_TrackMate

 - The second part of the process is the filtering of false events
 and determination of the vesicle type, done in a Jupyter nNotebook - Event_filter_graph

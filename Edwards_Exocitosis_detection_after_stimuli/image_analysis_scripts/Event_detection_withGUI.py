import sys, os
import math

from ij import IJ, WindowManager, ImagePlus
from ij.io import DirectoryChooser
from ij.gui import WaitForUserDialog, GenericDialog
from ij.plugin import ImageCalculator, PlugIn
from ij.measure import Measurements, ResultsTable
from ij.plugin.frame import RoiManager

from fiji.plugin.trackmate import Model, Settings, TrackMate, SelectionModel, Logger, Spot, SpotCollection
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.sparselap import SimpleSparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
from fiji.plugin.trackmate.action import ExportAllSpotsStatsAction
from fiji.plugin.trackmate.action import LabelImgExporter
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
from fiji.plugin.trackmate.providers import SpotAnalyzerProvider
from fiji.plugin.trackmate.providers import EdgeAnalyzerProvider
from fiji.plugin.trackmate.providers import TrackAnalyzerProvider


dc=DirectoryChooser("Choose a folder")
input_dir=dc.getDirectory() #folder were all time-lapse images are saved
if input_dir is None:
    print("User Canceled")

else:
  gd=GenericDialog(input_dir)
  gd.addRadioButtonGroup("Are files on tiff format?", ["Yes", "No"], 1, 2, "Yes")
  gd.addStringField("if not, what format?", "nd2", 5)
  gd.addNumericField("Number of frames", 100, 0,)
  gd.addNumericField("Number of stimuli",8,0)
  gd.addNumericField("First stimuli frame",20,0)
  gd.addNumericField("Stimuli frame interval",6,0)
  gd.addNumericField("NH3 addition frame",22,0)
  gd.addNumericField("Spot diameter",5,2)
  gd.addNumericField("Threshold",100,1)
  gd.addNumericField("Link distance",2,1)
  gd.addNumericField("Gap distance",2,1)
  gd.addStringField("Output folder", "/Users/bdiazroh/Desktop/Projects/COBA/Edwards/Analysis/", 60)
  gd.showDialog()  
  if gd.wasCanceled():
    print("User canceled dialog!")
  else:
 #settings for image processing to improve signal/noise ratio
    is_tiff = gd.getNextRadioButton()
    file_type = gd.getNextString()
    frames = int(gd.getNextNumber()) #length of time-lapse movie
    stimuli = int(gd.getNextNumber()) #number of stimuli
    first_stimuli = int(gd.getNextNumber()) #frame where first stimuli is given
    step_size = int(gd.getNextNumber()) #rate of stimuli
    total_frame = int(gd.getNextNumber()) #frame NH3 was added 
    diameter = float(gd.getNextNumber())
    threshold = float(gd.getNextNumber()) #threshold for the event detection larger values will result in less events detected, bright events being detected,
                #smaller values will result in more event but this might include false events
    link_distance = int(gd.getNextNumber()) #this set the distance that an event can whitin a frame for static events this value should be set close to 0
    gap_distance = int(gd.getNextNumber()) #this set the distance that an event can move from frame to frame, for static events this value should be set close to 0\
    output_dir=gd.getNextString() #folder were files created will be saved
    

ic =  ImageCalculator();
reload(sys)
sys.setdefaultencoding('utf-8')


#Process each movie and return a label image with each event as a spot numbered based on the trackId as well as a .csv table with x,y and frame position for each event and the track it belongs too

movies = os.listdir(input_dir)
print (movies)
for eachobj in movies:
	name = eachobj.split(".")[0]
	subname = "NH3"
	if subname in name:
		name = eachobj.split("_")[0]
		if is_tiff=="No":
			IJ.run("Bio-Formats Windowless Importer","open="+os.path.join(input_dir,eachobj));
			IJ.saveAs("Tiff",os.path.join(output_dir,name+'.tif'));
		else:
			imp = IJ.openImage(os.path.join(input_dir,eachobj));
			imp.show();
		
#how the total movie is processed
		j = total_frame
		i = j - 1
		k = j + 1
		IJ.selectWindow(str(name)+"_NH3.tif");
		IJ.run("Make Substack...", "slices="+str(i));
		IJ.selectWindow(str(name)+"_NH3.tif");
		IJ.run("Make Substack...", "slices="+str(k)+"-26");
		imp1= WindowManager.getImage("Substack ("+ str(k)+"-26)");
		imp2= WindowManager.getImage("Substack ("+ str(i)+")");
		imp = ImageCalculator.run(imp1, imp2, "Subtract create stack");
		imp.show();
		imp.setTitle("img_for_TM");
		IJ.selectWindow("Substack ("+ str(i)+")");
		IJ.run ("Close");
		IJ.selectWindow("Substack ("+ str(k)+"-26)");
		IJ.run ("Close");
		
	#Trackmate model, detector, tracking and export of spots and tracks
		model = Model()
		settings = Settings(imp)
		radius = float(diameter)/2
	
		settings.detectorFactory = LogDetectorFactory()
		settings.detectorSettings = {
			'DO_SUBPIXEL_LOCALIZATION' : False,
			'RADIUS' : float(radius),
			'TARGET_CHANNEL' : 1,
			'THRESHOLD' : float(threshold),
			'DO_MEDIAN_FILTERING' : False,
			}
	
		settings.trackerFactory = SimpleSparseLAPTrackerFactory()
		settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
		settings.trackerSettings['LINKING_MAX_DISTANCE'] = float(link_distance)
		settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = float(gap_distance)
		settings.trackerSettings['MAX_FRAME_GAP'] = 0
		trackmate = TrackMate(model, settings)
	
		ok = trackmate.checkInput()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
	
		ok = trackmate.process()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
	
		selectionModel = SelectionModel(model)
	
		exportSpotsAsDots = False
		exportTracksOnly = True
		lblImg = LabelImgExporter.createLabelImagePlus( trackmate, exportSpotsAsDots, exportTracksOnly, False )
		lblImg.show()
		IJ.selectWindow('LblImg_img_for_TM');
		IJ.saveAs("Tiff",os.path.join(output_dir,name+'_lblImg_NH3.tif'));
		
		ds = DisplaySettingsIO.readUserDefault()
	
		fm = model.getFeatureModel()
	
		rt_exist = WindowManager.getWindow("TrackMate Results")
	
		if rt_exist==None or not isinstance(rt_exist, TextWindow):
			table= ResultsTable()
		else:
			table = rt_exist.getTextPanel().getOrCreateResultsTable()
		table.reset
	
		for id in model.getTrackModel().trackIDs(True):
			v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
			model.getLogger().log('')
			model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
			track = model.getTrackModel().trackSpots(id)
	
			for spot in track:
				sid = spot.ID()
				x=spot.getFeature('POSITION_X')
				y=spot.getFeature('POSITION_Y')
				t=spot.getFeature('FRAME')
				q=spot.getFeature('QUALITY')
				snr=spot.getFeature('SNR')
				mean=spot.getFeature('MEAN_INTENSITY')
				model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q))
				table.incrementCounter()
				table.addValue("TRACK_ID", id)
				table.addValue("SPOT_ID", sid)
				table.addValue("POSITION_X", x)
				table.addValue("POSITION_Y", y)
				table.addValue("FRAME", t)
				table.addValue("QUALITY", q)
		table.show("TrackMate Results")
		IJ.selectWindow('TrackMate Results');
		IJ.saveAs("Measurements",os.path.join(output_dir,name+'_total.csv'));
		IJ.selectWindow(name+'_total.csv');
		IJ.run ("Close");
		IJ.run ("Close All");
		
#how the original movie is processed		
	else:
		if is_tiff=="No":
			IJ.run("Bio-Formats Windowless Importer","open="+os.path.join(input_dir,eachobj));
			IJ.saveAs("Tiff",os.path.join(output_dir,name+'.tif'));
		else:
			imp = IJ.openImage(os.path.join(input_dir,eachobj));
			imp.show();
			
#image processing to improve spot detection
	
		for i in range (0, stimuli):
			j = first_stimuli + (i*step_size)
			k = j + step_size
			l = i+1
			IJ.selectWindow(str(name)+".tif");
			IJ.run("Make Substack...", "slices=" + str(j)+ "-"+str(k));
			IJ.selectWindow("Substack ("+ str(j)+ "-"+str(k)+")");
			IJ.run("Make Subset...", "slices=1 delete");
			img1= WindowManager.getImage("Substack ("+ str(j)+ "-"+str(k)+")");
			img2= WindowManager.getImage("Substack (1)");
			imp = ImageCalculator.run(img1, img2, "Subtract create stack");
			imp.show();
			imp.setTitle("img"+str(i));
			IJ.selectWindow("Substack ("+ str(j)+ "-"+str(k)+")");
			IJ.run ("Close");
			IJ.selectWindow("Substack (1)");
			IJ.run ("Close");
			
			
			model = Model()
			settings = Settings(imp)
			radius = float(diameter)/2
		
			settings.detectorFactory = LogDetectorFactory()
			settings.detectorSettings = {
				'DO_SUBPIXEL_LOCALIZATION' : False,
				'RADIUS' : float(radius),
				'TARGET_CHANNEL' : 1,
				'THRESHOLD' : float(threshold),
				'DO_MEDIAN_FILTERING' : False,
				}
		
			settings.trackerFactory = SimpleSparseLAPTrackerFactory()
			settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
			settings.trackerSettings['LINKING_MAX_DISTANCE'] = float(link_distance)
			settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = float(gap_distance)
			settings.trackerSettings['MAX_FRAME_GAP'] = 0
			trackmate = TrackMate(model, settings)
		
			ok = trackmate.checkInput()
			if not ok:
				sys.exit(str(trackmate.getErrorMessage()))
		
			ok = trackmate.process()
			if not ok:
				sys.exit(str(trackmate.getErrorMessage()))
		
			selectionModel = SelectionModel(model)
			
			exportSpotsAsDots = False
			exportTracksOnly = True
			lblImg = LabelImgExporter.createLabelImagePlus( trackmate, exportSpotsAsDots, exportTracksOnly, False )
			lblImg.show()
			IJ.selectWindow('LblImg_img'+str(i));
			IJ.saveAs("Tiff",os.path.join(output_dir,name+'_lblImg_img'+str(l)+'.tif'));
		
			ds = DisplaySettingsIO.readUserDefault()
		
			fm = model.getFeatureModel()
		
			rt_exist = WindowManager.getWindow("TrackMate Results")
		
			if rt_exist==None or not isinstance(rt_exist, TextWindow):
				table= ResultsTable()
			else:
				table = rt_exist.getTextPanel().getOrCreateResultsTable()
			table.reset
		
			for id in model.getTrackModel().trackIDs(True):
				v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
				model.getLogger().log('')
				model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
				track = model.getTrackModel().trackSpots(id)
		
				for spot in track:
					sid = spot.ID()
					x=spot.getFeature('POSITION_X')
					y=spot.getFeature('POSITION_Y')
					t=spot.getFeature('FRAME')
					q=spot.getFeature('QUALITY')
					snr=spot.getFeature('SNR')
					mean=spot.getFeature('MEAN_INTENSITY')
					model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q))
					table.incrementCounter()
					table.addValue("TRACK_ID", id)
					table.addValue("SPOT_ID", sid)
					table.addValue("POSITION_X", x)
					table.addValue("POSITION_Y", y)
					table.addValue("FRAME", t)
					table.addValue("QUALITY", q)
			table.show("TrackMate Results")
			IJ.selectWindow('TrackMate Results');
			IJ.saveAs("Measurements",os.path.join(output_dir,name+'_img'+str(l)+'.csv'));
			IJ.selectWindow(name+'_img'+str(l)+'.csv');
			IJ.run ("Close");
			
		j = first_stimuli
		k = frames
		IJ.selectWindow(str(name)+".tif");
		IJ.run("Make Substack...", "slices="+str(j)+"-"+str(k));
		IJ.selectWindow("Substack ("+str(j)+"-"+str(k)+")");
		IJ.run("Make Subset...", "slices=1 delete");
		img1= WindowManager.getImage("Substack ("+ str(j)+"-"+str(k)+")");
		img2= WindowManager.getImage("Substack (1)");	
		imp = ImageCalculator.run(img1, img2, "Subtract create stack");
		imp.show();
		imp.setTitle("img_for_TM");
		IJ.selectWindow("Substack ("+ str(j)+ "-"+str(k)+")");
		IJ.run ("Close");
		IJ.selectWindow("Substack (1)");
		IJ.run ("Close");
	
	#Trackmate model, detector, tracking and export of spots and tracks
		model = Model()
		settings = Settings(imp)
		radius = float(diameter)/2
	
		settings.detectorFactory = LogDetectorFactory()
		settings.detectorSettings = {
			'DO_SUBPIXEL_LOCALIZATION' : False,
			'RADIUS' : float(radius),
			'TARGET_CHANNEL' : 1,
			'THRESHOLD' : float(threshold),
			'DO_MEDIAN_FILTERING' : False,
			}
	
		settings.trackerFactory = SimpleSparseLAPTrackerFactory()
		settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
		settings.trackerSettings['LINKING_MAX_DISTANCE'] = float(link_distance)
		settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = float(gap_distance)
		settings.trackerSettings['MAX_FRAME_GAP'] = 0
		trackmate = TrackMate(model, settings)
	
		ok = trackmate.checkInput()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
	
		ok = trackmate.process()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
	
		selectionModel = SelectionModel(model)
		
		exportSpotsAsDots = False
		exportTracksOnly = True
		lblImg = LabelImgExporter.createLabelImagePlus( trackmate, exportSpotsAsDots, exportTracksOnly, False )
		lblImg.show()
		IJ.selectWindow('LblImg_img_for_TM');
		IJ.saveAs("Tiff",os.path.join(output_dir,name+'_lblImg_whole.tif'));
	
		ds = DisplaySettingsIO.readUserDefault()
	
		fm = model.getFeatureModel()
	
		rt_exist = WindowManager.getWindow("TrackMate Results")
	
		if rt_exist==None or not isinstance(rt_exist, TextWindow):
			table= ResultsTable()
		else:
			table = rt_exist.getTextPanel().getOrCreateResultsTable()
		table.reset
	
		for id in model.getTrackModel().trackIDs(True):
			v = fm.getTrackFeature(id, 'TRACK_MEAN_SPEED')
			model.getLogger().log('')
			model.getLogger().log('Track ' + str(id) + ': mean velocity = ' + str(v) + ' ' + model.getSpaceUnits() + '/' + model.getTimeUnits())
			track = model.getTrackModel().trackSpots(id)
	
			for spot in track:
				sid = spot.ID()
				x=spot.getFeature('POSITION_X')
				y=spot.getFeature('POSITION_Y')
				t=spot.getFeature('FRAME')
				q=spot.getFeature('QUALITY')
				snr=spot.getFeature('SNR')
				mean=spot.getFeature('MEAN_INTENSITY')
				model.getLogger().log('\tspot ID = ' + str(sid) + ': x='+str(x)+', y='+str(y)+', t='+str(t)+', q='+str(q))
				table.incrementCounter()
				table.addValue("TRACK_ID", id)
				table.addValue("SPOT_ID", sid)
				table.addValue("POSITION_X", x)
				table.addValue("POSITION_Y", y)
				table.addValue("FRAME", t)
				table.addValue("QUALITY", q)
		table.show("TrackMate Results")
		IJ.selectWindow('TrackMate Results');
		IJ.saveAs("Measurements",os.path.join(output_dir,name+'_whole.csv'));
		IJ.selectWindow(name+'_whole.csv');
		IJ.run ("Close");
		IJ.run("Close All");
	
			
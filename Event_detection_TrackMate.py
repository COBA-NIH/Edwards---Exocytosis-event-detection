import sys, os
import math

from ij import IJ, WindowManager, ImagePlus
from ij.io import DirectoryChooser
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



input_dir = '/Users/bdiazroh/Desktop/Projects/COBAProjects/EdwardsLab/Analysis/'  #folder were all time-lapse images are saved
output_dir = '/Users/bdiazroh/Desktop/Projects/COBAProjects/EdwardsLab/Analysis/' #folder were files created will be saved

#settings for image processing to improve signal/noise ratio
file_type = ".tif" #file type if using .tif files already comment out lanes 53 and 54 and uncomment lanes 56 and 57
frames = 16000  #length of time-lapse movie
step_size = 2000  #step-size is used to remove backgroud fluoresence should be 2-3 times the duration of the longest event 

#settings for TrackMate for event detection 
diameter = 0.5  #average diameter of the event in microns
threshold = 10  #threshold for the event detection larger values will result in less events detected, bright events being detected, 
                #smaller values will result in more event but this might include false events  
channel = 1 #trackmate can work on images with more then one channel if that is the case select the channel were the events are being detected
link_distance = 1 #this set the distance that an event can whitin a frame for static events this value should be set close to 0
gap_distance = 1 #this set the distance that an event can move from frame to frame, for static events this value should be set close to 0
gap_frame = 50 #number of frames that can have no event detected between two event and still be considered the same event 

ic =  ImageCalculator();
reload(sys)
sys.setdefaultencoding('utf-8')


#Process each movie and return a label image with each event as a spot numbered based on the trackId as well as a .csv table with x,y and frame position for each event and the track it belongs too

movies = os.listdir(input_dir)
print (movies)
for eachobj in movies:
	if eachobj[-4:]== file_type:
		name = eachobj.split(".")[0]
#comment following two lines for .tif files
#		IJ.run("Bio-Formats Windowless Importer","open="+os.path.join(input_dir,eachobj));
#		IJ.saveAs("Tiff",os.path.join(output_dir,name+'.tif'));
#uncomment following two lines for .tif files
		imp = IJ.openImage(os.path.join(input_dir,eachobj));
		imp.show();
		steps = int(frames/step_size)
		images_to_concatenate = " "

		for i in range (1, steps+1):
			j = ((i-1)*step_size)+1
			k = i * step_size
			IJ.selectWindow(str(name)+".tif"); 
			IJ.run("Make Substack...", "slices=" + str(j)+ "-"+str(k));
			IJ.run("Z Project...", "projection=Median");
			img1= WindowManager.getImage("Substack ("+ str(j)+ "-"+str(k)+")");
			img2= WindowManager.getImage("MED_Substack ("+ str(j)+ "-"+str(k)+")");
			img = ic.run("Subtract create stack", img1, img2,);
			img.show();
			img.setTitle("img"+str(i));
			IJ.selectWindow("Substack ("+ str(j)+ "-"+str(k)+")");
			IJ.run ("Close");
			IJ.selectWindow("MED_Substack ("+ str(j)+ "-"+str(k)+")");
			IJ.run ("Close");
			images_to_concatenate = images_to_concatenate + "image"+str(i)+"=[img"+str(i)+"] ";
		
		IJ.run("Concatenate...", images_to_concatenate);
		IJ.run("Despeckle", "stack");
		IJ.run("Subtract Background...", "rolling=20 stack");
		IJ.run("Z Project...", "projection=[Max Intensity]");
		IJ.run("Measure","");
		rt = ResultsTable.getResultsTable()
		max_pix = rt.getValue("Max", 0);
		div = math.ceil((max_pix**5)/65536)
		print(div)
		IJ.selectWindow("MAX_Untitled");
		IJ.run ("Close");
		IJ.selectWindow("Untitled");
		IJ.run("Macro...", "code=v=(v*v*v*v*v)/"+str(div)+" stack");
		IJ.run("Properties...", "channels=1 slices=1 frames=" +str(frames));
		imp = WindowManager.getCurrentImage();
		imp.setTitle(name+'_for_TM');
		IJ.selectWindow('Results'); 
		IJ.run ("Close");
		
		model = Model()
		settings = Settings(imp)
		radius = float(diameter)/2
		
		settings.detectorFactory = LogDetectorFactory()
		settings.detectorSettings = {
			'DO_SUBPIXEL_LOCALIZATION' : False,
			'RADIUS' : float(radius),
			'TARGET_CHANNEL' : int(channel),
			'THRESHOLD' : float(threshold),
			'DO_MEDIAN_FILTERING' : False,
			}
		
		settings.trackerFactory = SimpleSparseLAPTrackerFactory()
		settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap()
		settings.trackerSettings['LINKING_MAX_DISTANCE'] = float(link_distance)
		settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = float(gap_distance)
		settings.trackerSettings['MAX_FRAME_GAP'] = int(gap_frame)
		trackmate = TrackMate(model, settings)
		
		ok = trackmate.checkInput()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
		
		ok = trackmate.process()
		if not ok:
			sys.exit(str(trackmate.getErrorMessage()))
		
		selectionModel = SelectionModel(model)
		
		exportSpotsAsDots = True
		exportTracksOnly = True
		lblImg = LabelImgExporter.createLabelImagePlus(trackmate, exportSpotsAsDots, exportTracksOnly)
		lblImg.show()
		IJ.saveAs("Tiff",os.path.join(output_dir,name+'_lblImg.tif'));
		IJ.run ("Close");
		
		
		
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
		IJ.saveAs("Measurements",os.path.join(output_dir,name+'.csv'));
		IJ.selectWindow(name+'.tif'); 
		IJ.run ("Close");
		IJ.selectWindow(name+'_for_TM'); 
		IJ.run ("Close");
		IJ.selectWindow(name+'.csv'); 
		IJ.run ("Close");
		
IJ.run("Close All")
import subprocess
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.ticker as ticker
class VizCreator():
    @staticmethod
    # Creates the decorator that measures performance of the function, used for testing new functions
    def time_calls(func):
        def wrapper(*args,**kwargs):
            # start and end measures the current time so we run the function between the start and end timer and then 
            # just subract the to find times taken for a function to run.
            start = time.perf_counter()
            to_return = func(*args,**kwargs)
            end = time.perf_counter()
            print(f'The function {func.__name__} took {end-start} second')
            return to_return
        return wrapper
    # finds and connects to the database base using conn as our connector as a class variable throughout the class.

    
    @staticmethod
    @time_calls
    def video_making_1(file_name, data, sec_per_frame, tic_rate, unit, name):
        # setting up the figure
        fig, ax = plt.subplots()
        fig.patch.set_alpha(0.8)
        ax.patch.set_alpha(0.8)
        l, = ax.plot([], [], 'k-')
        p1, = ax.plot([], [], 'ko')
        
        # calculates the start frames, frames needed before the graph starts moving.
        start_frames = int(sec_per_frame / data['time'].max() * len(data))
        
        #Sets up the axis labels, limits and title
        ax.set_xlim(0, data['time'].iloc[start_frames])
        ax.set_ylim(data['values'].min() - data['values'].min() * 0.1, data['values'].max() + data['values'].max() * 0.1)
        ax.set_xlabel('time from the start')
        ax.set_ylabel(f'{name}({unit})')
        ax.set_title(f'{name} over time graph')
        
        # fps stands frames per second and used to make sure a second in the graph is a second in the video so when we make
        #the overlay then it matches up with the background video.  
        fps = len(data) / data['time'].max()
        metadata = dict(title='Movie', artist='Yash')

        # Creates our writer object which will make the video, extra_args allow us to have transparency in the video.
        writer = FFMpegWriter(fps=fps, metadata=metadata, codec='png',extra_args=['-pix_fmt', 'rgba'])    
        file_name = file_name + '.mov'
        
        # Lists to hold the x and y data points that will be graphed in the video
        xlist = []
        ylist = []
        
        with writer.saving(fig, file_name, 200):

            # Counter is there for the index of the dataframe so we can see if we need to start the moving the axis.
            counter = 0
            for index, val in data.iterrows():

                # Appends the x axis and y axis data to the lists
                xlist.append(val['time'])
                ylist.append(val['values'])

                # Logic to see if we should start moving the graph along
                if counter > start_frames:
                    # Now here for the main part of moving the graph along, what we do is while plotting the graph, 
                    # we change the axis as well so end_x is and start_x are the new x - axis limits where end-x is the current one 
                    # and start_x is "start_frames" ago.
                    end_x = data['time'].iloc[counter]
                    start_x = data['time'].iloc[counter - start_frames]
                    ax.set_xlim(start_x, end_x)
                    
                    # now we since we added a new point to the graph we need to remove the first point
                    # so the graph is showing new data while having the same amount of data points shown.
                    xlist.pop(0)
                    ylist.pop(0)
                counter = counter + 1
                # tic rates refers to the intervals in the x-axis, how many seconds between each mark in the x-acxis.
                ax.xaxis.set_major_locator(ticker.MultipleLocator(tic_rate))
                
                # draws the new frame
                l.set_data(xlist, ylist)
                p1.set_data(xlist, ylist)
                writer.grab_frame()

    @staticmethod
    @time_calls
    def overlayTwoLayers(file1, file2, output_file):
        # Shlex splits the command into a format that subprocess can use to run the command, the command is a basic 
        # ffmpeg command that takes in 2 videos as input and then overlays the second video on top of the first video
      command = ['ffmpeg', '-y','-i', file1,'-i', file2,'-c:v', 'h264_videotoolbox',
                '-b:v', '8000k','-filter_complex', '[1:v]scale=480:270[top]; [0:v][top]overlay',
                f'{output_file}.mp4']
      subprocess.run(command)

    

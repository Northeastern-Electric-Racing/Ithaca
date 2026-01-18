from tkinter import *
from tkinter import filedialog
print('tkinter imported')

from analysis.src.telemetry_overlay.video_builder import VizCreator
print('VizCreator imported')
root = Tk()
root.title('VIZZ')
root.geometry('800x400')
print('GUI started')

file_name = ''


def path_getter():
  # function to get the file path from the user and allow them to upload the video they want to overlay the telemetry on.
    global file_name
    file_name = filedialog.askopenfilename()
    file_name = file_name.split('/')[-1]
    path_label.config(text=file_name)
    file_name
    
def Video_creator():
  # function to create the video with the telemetry overlay, the .get() gets the user input from the entry boxes.
    global file_name
    x = VizCreator()
    print(sensor_e.get().strip(),start_time_e.get().strip(),ending_time_e.get().strip())
    df,unit,name = x.query_builder(sensor_e.get().strip(),start_time_e.get().strip(),ending_time_e.get().strip())
    x.video_making_1('Graph',df,int(sec_pf_e.get().strip()),int(tick_rate_e.get().strip()),unit,name)
    # x.video_making_1('Graph',df,4,1,unit,name)
    x.overlayTwoLayers(file_name,'Graph.mov',save_name_e.get())


#Creating items
Title = Label(root, text= 'Telemtry overlay')

sensor_l = Label(root, text= 'Sensor Name:',justify='left')
sensor_e = Entry(root)

start_time_l = Label(root, text= 'Start Time:',justify='left')
start_time_e = Entry(root)

ending_time_l = Label(root, text= 'Ending Time:',justify='left')
ending_time_e = Entry(root)

sec_pf_l = Label(root,text='Seconds per frame', justify = 'left')
sec_pf_e = Entry(root)

tick_rate_l = Label(root,text='Ticks per frame', justify = 'left')
tick_rate_e = Entry(root)

save_name_l = Label(root, text='Save file name',justify='left')
save_name_e = Entry(root)

upload = Button(text='Upload File',command=path_getter)
path_label = Label(root, text = '',justify='left')

create = Button(text='Create',command=Video_creator)

# Placing items in a grid
root.grid()
Title.grid(column=0,row=0)
sensor_l.grid(column=0,row=1)
sensor_e.grid(column=1,row=1)
start_time_l.grid(column=0,row=2)
start_time_e.grid(column=1,row=2)
ending_time_l.grid(column=0,row=3)
ending_time_e.grid(column=1,row=3)
sec_pf_l.grid(column=0,row=4)
sec_pf_e.grid(column=1,row=4)
tick_rate_l.grid(column=0,row=5)
tick_rate_e.grid(column=1,row=5)
save_name_l.grid(column=0,row=6)
save_name_e.grid(column=1,row=6)
upload.grid(column=0,row=7)
path_label.grid(column=1,row=7)
create.grid(column=0,row=8,columnspan=2)

root.mainloop()



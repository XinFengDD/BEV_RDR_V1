#!C:\Users\t4343xf\Anaconda3\python

from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import sys,os
import tkintermapview
from RDRevalHelper import *
os.environ['REQUESTS_CA_BUNDLE']=os.path.join(os.path.dirname(sys.argv[0]),'cacert.pem')

def GUI_OPEN():

    def quit():
        root.destroy
        sys.exit()

    root = Tk()
    root.geometry("1700x850")
    root.title("EV RDR and Routing Evaluation Tools (Beta 2.0)")
    MainFrame=LabelFrame(root)
    MainFrame.pack(side=LEFT,fill=BOTH,expand=True)
    Map_frame = LabelFrame(MainFrame)
    Map_frame.pack(side=TOP,fill=BOTH)
    mapwidget=tkintermapview.TkinterMapView(Map_frame,width=700,height=600)
    mapwidget.set_position(48.8367559,9.1570987)
    mapwidget.set_zoom(5)
    mapwidget.pack(fill=BOTH,expand=True)
    
    Command_frame = LabelFrame(MainFrame)
    Command_frame.pack(side=BOTTOM,fill=BOTH,expand=True)

    Channel_frame = ttk.Frame(Command_frame, padding="3",relief="groove")
    Channel_frame.pack(side=LEFT,fill=BOTH,expand=True)
    Input_Title = ttk.Frame(Channel_frame, padding="3")
    Input_Title.pack(side=TOP,fill=BOTH)
    Input_T0 = Label(Input_Title, text=" EV Trip Inputs and Settings ")
    Input_T0.pack(padx=15)

    db_frame1 = ttk.Frame(Channel_frame, padding="3")
    db_frame1.pack(side=TOP,fill=BOTH)
    Input_labels=["Starting point  ","  Destination  ","Initial Battery Level","Min Battery Level"]
    Input_widths=[20,25,15,10]
    InputLabel=[]
    for i in range(0,4):
        InputLabel.append(Label(db_frame1, text=Input_labels[i]))
        InputLabel[i].pack(side = LEFT,padx=Input_widths[i])
    
    db_frame2 = ttk.Frame(Channel_frame, padding="3")
    db_frame2.pack(side=TOP,fill=X)
    db_E=[]
    Widths=[20,20,12,12]
    for i in range(0,4):
        db_E.append(Entry(db_frame2, width=Widths[i]))
        db_E[i].pack(side = LEFT,padx=10)
    db_E[3].insert(0, str(10))
    API_B44 = Button(db_frame2, text=" Test ", command = lambda:APICompare(db_E,API_Summary,mapwidget,Figure1))
    
    API_B44.pack(side = RIGHT,padx=5)

    db_frame5 = ttk.Frame(Channel_frame, padding="3")
    db_frame5.pack(side=TOP,fill=X)
    db_L5 = Label(db_frame5, text="Car&User Profile")
    db_L5.pack(side = LEFT,padx=5)
    db_E.append(Entry(db_frame5, width=5))
    #db_E[4].pack(side = LEFT,padx=5)
    
    VehicleList=list(CC_dict.keys())
    ComboVehicle = ttk.Combobox(db_frame5,width= 13,values=VehicleList)
    ComboVehicle.current(0)
    ComboVehicle.pack(side = LEFT,padx=1)
    ComboVehicle.bind("<<ComboboxSelected>>", lambda event:update_vehicle(ComboVehicle.get(),db_E[4]))

    update_vehicle(ComboVehicle.get(),db_E[4])

    db_B51 = Button(db_frame5, text="Load Trip Log", command = lambda:OpenLog(db_E,mapwidget,API_Summary,Figure1))
    db_B51.pack(side = LEFT,padx=10)
    
    db_E.append(Entry(db_frame5, width=5))
    OptionList= ["Energy_km","Speed_km","Elevation_km","SOC_time","Speed_time","Histogram","Anxiety"]
    Combooperator = ttk.Combobox(db_frame5,width= 10,values=OptionList)
    Combooperator.current(0)
    Combooperator.pack(side = LEFT,padx=5)

    db_E.append(Entry(db_frame5, width=5))

    RetOpt=["RT Traffic Off","RT Traffic On"]
    db_E.append(Entry(db_frame5, width=5))
    db_E[7].insert(0, RetOpt[0])
    db_B4 = Button(db_frame5, text="Matrics Test", command = lambda:MatrixTest(db_E,mapwidget,API_Summary,Figure1))
    db_B4.pack(side = RIGHT,padx=5)
    db_B50 = Button(db_frame5, text=RetOpt[1], command = lambda:RetentOpt(db_E[7],db_B50,RetOpt))
    db_B50.pack(side = RIGHT,padx=5)

    db_frame4 = ttk.Frame(Channel_frame, padding="3")
    db_frame4.pack(side=TOP,fill=X)
    db_B41 = Button(db_frame4, text="Select a folder", command = lambda:SelectFolder(db_E[8],mapwidget))
    db_B41.pack(side = LEFT,padx=10)
    db_E.append(Entry(db_frame4, width=60))
    db_E[8].pack(side = LEFT,padx=10)
    db_B40 = Button(db_frame4, text="Batch Test", command = lambda:Simulation(db_E))
    db_B40.pack(side = RIGHT,padx=5)

    db_frame3 = ttk.Frame(Channel_frame, padding="3")
    db_frame3.pack(side=TOP,fill=X)
    db_E44 = Entry(db_frame3, width=30)
    db_E44.pack(side = LEFT,padx=5)
    db_B31 = Button(db_frame3, text="Charge Station nearby", command = lambda:ShowChargeStation(db_E44,mapwidget))
    db_B31.pack(side = LEFT,padx=5)
    db_B32 = Button(db_frame3, text="   Exit   ", command = quit)
    db_B32.pack(side = RIGHT,padx=5)
    db_B63 = Button(db_frame3, text="  Clear  ", command = lambda:clear(API_Summary,mapwidget,Figure1,db_E))
    db_B63.pack(side = RIGHT,padx=5)

    db_frame6 = ttk.Frame(Channel_frame, padding="3")
    db_frame6.pack(side=TOP,fill=X)
    WeightList=["Charging Weight","Driving Weight"]
    Weight_L =[]
    for i in range(2):
        Weight_L.append(Label(db_frame6, text=WeightList[i]))
        Weight_L[i].pack(side = LEFT,padx=5)
        db_E.append(Scale(db_frame6, from_=0, to=10,tickinterval=5, orient=HORIZONTAL))
        db_E[i+9].set(10)
        db_E[i+9].pack(side = LEFT,padx=15)
    db_E.append(db_B50)

    API_Summary={}

    API_SOC=[]
    API_Dur=[]
    API_ChDur=[]
    API_Dis=[]
    API_ChRat=[]
    API_TTRat=[]
    APIComp_frame = ttk.Frame(Command_frame, padding="3",relief="groove")
    APIComp_frame.pack(side=RIGHT,fill=BOTH,expand=True)
    API_Title = ttk.Frame(APIComp_frame, padding="3")
    API_Title.pack(side=TOP,fill=X)
    
    API_T0 = Label(API_Title, text="BEV Route Summury")
    API_T0.pack(side = TOP,padx=15)

    API_Name = ttk.Frame(APIComp_frame, padding="3")
    API_Name.pack(side=TOP,fill=X)
    Summary_L=[]
    label_list=[" ","TomTom","Iternio","GADP V0"," HERE ","Trip Log"]
    for i in range(0,len(label_list)):
        Summary_L.append(Label(API_Name, text=label_list[i]))
        Summary_L[i].pack(side = LEFT,padx=15)

    API_SOC_Disp = ttk.Frame(APIComp_frame, padding="3")
    API_SOC_Disp.pack(side=TOP,fill=X)
    API_L4 = Label(API_SOC_Disp, text="E (kWh)")
    API_L4.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_SOC.append(Label(API_SOC_Disp, text="     "))
        API_SOC[i].pack(side = LEFT,padx=23)

    API_Dur_Disp = ttk.Frame(APIComp_frame, padding="3")
    API_Dur_Disp.pack(side=TOP,fill=X)
    API_L5 = Label(API_Dur_Disp, text="Drv T (h)")
    API_L5.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_Dur.append(Label(API_Dur_Disp, text="     "))
        API_Dur[i].pack(side = LEFT,padx=22)

    API_ChDur_Disp = ttk.Frame(APIComp_frame, padding="3")
    API_ChDur_Disp.pack(side=TOP,fill=X)
    API_L7 = Label(API_ChDur_Disp, text="Chg T (h)")
    API_L7.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_ChDur.append(Label(API_ChDur_Disp, text="     "))
        API_ChDur[i].pack(side = LEFT,padx=22)

    API_Dis_Disp = ttk.Frame(APIComp_frame, padding="3")
    API_Dis_Disp.pack(side=TOP,fill=X)
    API_L6 = Label(API_Dis_Disp, text="Dis (km)")
    API_L6.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_Dis.append(Label(API_Dis_Disp, text="     "))
        API_Dis[i].pack(side = LEFT,padx=24)

    API_ChRating = ttk.Frame(APIComp_frame, padding="3")
    API_ChRating.pack(side=TOP,fill=X)
    API_L8 = Label(API_ChRating, text="Chg Score")
    API_L8.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_ChRat.append(Label(API_ChRating, text="     "))
        API_ChRat[i].pack(side = LEFT,padx=24)

    API_Rating = ttk.Frame(APIComp_frame, padding="3")
    API_Rating.pack(side=TOP,fill=X)
    API_L9 = Label(API_Rating, text="ToT Score ")
    API_L9.pack(side = LEFT,padx=5)
    for i in range(0,5):
        API_TTRat.append(Label(API_Rating, text="     "))
        API_TTRat[i].pack(side = LEFT,padx=24)

    API_Summary['SOC']=API_SOC
    API_Summary['DDur']=API_Dur
    API_Summary['ChDur']=API_ChDur
    API_Summary['Dis']=API_Dis
    API_Summary['ChRat']=API_ChRat
    API_Summary['TTRat']=API_TTRat
    Plot_frame = ttk.Frame(root)
    Plot_frame.pack(side=RIGHT,fill=BOTH,expand=True)


    Fig_frame1 = ttk.Frame(Plot_frame,borderwidth = 1, padding="3")
    Fig_frame1.pack(side=TOP,fill=BOTH)
    Fig_frame1['borderwidth'] = 2
    Fig_frame1['relief'] = 'sunken'
    Plot_size = (6, 8)
    Figure1 = plt.figure(1,figsize=Plot_size, dpi=100)
    SigPlot1 = FigureCanvasTkAgg(Figure1, Fig_frame1)
    SigPlot1.get_tk_widget().pack(side=TOP, padx=1, fill=BOTH)
    NavigationToolbar2Tk(SigPlot1, Fig_frame1)

    Combooperator.bind("<<ComboboxSelected>>", lambda event:update_plot(Combooperator.get(),db_E,Figure1))
    update_plot(Combooperator.get(),db_E,Figure1)

    print("RDR Evaluator Launching Successfully!")
    root.mainloop()

if __name__ == '__main__':
    GUI_OPEN()
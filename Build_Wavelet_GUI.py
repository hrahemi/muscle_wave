from Tkinter import *
from muscle_wave import *
from tkFileDialog import askdirectory
import tkMessageBox as tkm
import glob

global file_path
file_path = ''
# a base tab class
class Tab(Frame):
	def __init__(self, master, name):
		Frame.__init__(self, master)
		self.tab_name = name
		

# the bulk of the logic is in the actual tab bar
class TabBar(Frame):
	def __init__(self, master=None, init_name=None):
		Frame.__init__(self, master)
		self.tabs = {}
		self.buttons = {}
		self.current_tab = None
		self.init_name = init_name
	
	def show(self):
		self.pack(side=TOP, expand=YES, fill=X ,anchor=W)
		self.switch_tab(self.init_name or self.tabs.keys()[-1])       # switch the tab to the first tab
	
	def add(self, tab):
		tab.pack_forget()									# hide the tab on init
		
		self.tabs[tab.tab_name] = tab						# add it to the list of tabs
		b = Button(self, text=tab.tab_name, relief=RAISED,	           # basic button stuff
			command=(lambda name=tab.tab_name: self.switch_tab(name)))	# set the command to switch tabs
		b.pack(side=LEFT)												# pack the buttont to the left mose of self
		self.buttons[tab.tab_name] = b											# add it to the list of buttons
	
	def delete(self, tabname):
		
		if tabname == self.current_tab:
			self.current_tab = None
			self.tabs[tabname].pack_forget()
			del self.tabs[tabname]
			self.switch_tab(self.tabs.keys()[0])
		
		else: del self.tabs[tabname]
		
		self.buttons[tabname].pack_forget()
		del self.buttons[tabname] 
		
	
	def switch_tab(self, name):
		if self.current_tab:
			self.buttons[self.current_tab].config(relief=RAISED)
			self.tabs[self.current_tab].pack_forget()			# hide the current tab
		self.tabs[name].pack(side=TOP)							# add the new tab to the display
		self.current_tab = name									# set the current tab to itself
		
		self.buttons[name].config(relief=FLAT)		
			# set it to the selected style
def makeform_TAB1_init(root, fields):
   entries = {}
   for field in fields:
      row = Frame(root)
      ent = Entry(row)
      ent.insert(0,field[1])
      entries[field[0]] = ent
   return entries
   
def makeform_TAB1(root, fields):
   entries = {}
   for field in fields:
      row = Frame(root)
      lab = Label(row, width=width/45, text=field[0]+": ", anchor='w')
      ent = Entry(row)
      ent.insert(0,field[1])
      if field[0]=='Sampling Frequency (Hz)':
          ent.config(textvariable=ftext)
      if field[0]=='Number of Wavelets':
          ent.config(state='readonly',textvariable=ntext)
      if field[0]== 'Number of Wavelets'or field[0]=='Sampling Frequency (Hz)':
          row.pack(side=TOP, fill=X, padx=5, pady=2)
          lab.pack(side=LEFT)
          ent.pack(side=RIGHT, expand=YES, fill=X)
      entries[field[0]] = ent
   return entries

def makeform(root, fields):
   entries = {}
   for field in fields:
      row = Frame(root)
      lab = Label(row, width=width/30, text=field[0]+": ", anchor='w')
      ent = Entry(row)
      ent.insert(0,field[1])
      row.pack(side=TOP, fill=X, padx=5, pady=2)
      lab.pack(side=LEFT)
      ent.pack(side=RIGHT, expand=YES, fill=X)
      entries[field[0]] = ent
   return entries
   
class Checkbar(Frame):
   def __init__(self, master=None, picks=[], side=LEFT, anchor=W):
      Frame.__init__(self, master)
      self.vars = []
      for pick in picks:
         var = IntVar()
         chk = Checkbutton(self, text=pick, variable=var)
         chk.pack(side=side, anchor=anchor, expand=YES)
         self.vars.append(var)
   def state(self):
      return map((lambda var: var.get()), self.vars)


def TAB1_wavelet_number(entries,v):
    
    try:
        
        num=str(num_of_waves(entries))
        if v.get()==1:
            ntext.set("13")
            entries['Number of Wavelets'].delete(0,END)
            entries['Number of Wavelets'].insert(0, '13' )
        else:
            ntext.set(num)
            entries['Number of Wavelets'].delete(0,END)
            entries['Number of Wavelets'].insert(0, num )
    except:
        pass
    
def browse_path(root):
     entries = {}
     row = Frame(root)
     lab = Label(row, width=width/30, text="Please choose the directory containing EMG data files:\t\t\t", anchor='w')
     lab.pack(side=LEFT)
     row.pack(side=TOP, fill=X, padx=5, pady=2)
     row = Frame(root)
     ent = Entry(row)
     ent.insert(0,'')
     b= Button(row, text='Browse',width=15, command=lambda:open_path(ent))
     b.pack(side=LEFT,padx=5)
     ent.pack(side=RIGHT,expand=YES, fill=X )
     row.pack(side=TOP, fill=X, padx=5, pady=2)
     entries['Path'] = ent
     return entries
    
            
if __name__ == '__main__':
    
    def open_path(entry):
        global file_path 
        file_path = askdirectory()
        entry.delete(0, END)
        entry.insert(0, file_path)        
     
    def delim_pick(dl):
        switcher = {
        1: ',',
        2: '\t',
        3: ';',
        4: ' ',
        }
        return switcher.get(dl) 
     
    def write(x): print x    
        
    def get_filenames(path):
        filenames = glob.glob(path+"/*.*")
        return filenames
       
    def close_window (): root.destroy()
        
    def update_num(a,b,c):
       TAB1_wavelet_number(ents11,v)
       
    def run_build_wave(entries,chk):
       root.title("Build Wavelet Program (Running)")
       build_wave(entries,list(chk.state()))
       root.title("Build Wavelet Program")
       
    def run_calculate_intensities(e1,e2,e3,dl, dc):
       root.title("Build Wavelet Program (Running)")
       
       cdl = delim_pick(dl.get())
       dpc = dc.get()
       entries=dict(e1.items()+e2.items()+e3.items()) 
       if file_path == '':
           tkm.showinfo('Warning', 'Please select the folder of your EMG data files and try again.')
           return
       try:
           
           files=get_filenames(file_path)
           if files==[]:
               tkm.showinfo('Warning','No files in the selected folder. Please select a new folder and try again.')
               return
       except:
           tkm.showinfo('Warning', 'The folder you entered does not exist. Please try again.')
           return
           
       calculate_intensities(entries,files,cdl,dpc)
       
       
       root.title("Build Wavelet Program")

    root=Tk()
    root.title("Build Wavelet Program")
    
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    
    frame_label_1= """STEP 1: Building wavelets"""
    frame_label_2= """STEP 2: Calculating intensities for collected EMG"""

    about_txt="""This program is a signal processing tool allowing you to perform wavelet analysis on EMG signals"""
    tech_txt="""Please choose the technology you used to collect EMG:\t"""
    plt_choice_txt="""Please check the box to see the build wavelet plots: """
    
    tech_choices=[('Surface EMG electrodes',1), ('Finewire/Needle EMG electrodes',2)]
    decimal_choices=[('Period (.)',1),('Comma (,)',2)]
    delim_choices=[('Comma (,)',1) , ('Tab',2), ('Semicolon (;)',3) , ('Space',4) ]
    
    file_details_fields =[('Number of header lines in the file','0'),('Column number of channels to be processed (e.g. 3,4,5,7,9)','')] 
    simple_fields = [('Sampling Frequency (Hz)','5000'), ('Number of Wavelets','13'), ('Deviation from maximum (%)','1.0'), ('Max iterations for setting coefficients','5'),('Number of wavelet sampling points','8192')]
    advanced_fields = [('Sampling Frequency (Hz)','5000'), ('Number of Wavelets','24'), ('Deviation from maximum (%)','1.0'), ('Max iterations for setting coefficients','5'),('Number of wavelet sampling points','8192')]
    bar = TabBar(root, "Quick Setup")

    """""""""    TAB 1: Simple Setup    """""""""
        
    tab1 = Tab(root, "Quick Setup")

    bline=Frame(tab1, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=2) 
    
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=0, pady=2)    
    Label(row,text=frame_label_1,justify=LEFT, anchor='w',  \
#    height=2, 
    wraplength=width/3
    ).pack(anchor=W, side=TOP, expand=YES, fill=BOTH)
    
    bline=Frame(tab1, bg='black', relief=GROOVE)
    bline.pack(side=TOP, fill=X, padx=0, pady=2)
   
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=5, pady=2)    
    Label(row,text=tech_txt,justify=LEFT, anchor='w',  \
#    height=2, 
    wraplength=width/3
    ).pack(anchor=W, side=TOP, expand=YES, fill=BOTH)
     
    ntext = StringVar()
    ftext = StringVar()
    ntext.set('13')
    ftext.set('5000')
    ents11 = makeform_TAB1_init(tab1, simple_fields)
    
    
    v = IntVar()
    v.set(1)

    for txt, val in tech_choices:
        Radiobutton(tab1, 
                text=txt,
                padx = 20, 
                variable=v, 
                command=(lambda e=ents11,v=v:TAB1_wavelet_number(e,v)),
                value=val).pack(anchor=W)
                
    
    
    ents11 = makeform_TAB1(tab1, simple_fields)
        
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=5, pady=2)
    Label(row,text=plt_choice_txt,anchor='w', \
#    height=2, 
    wraplength=width/3
    ).pack(side=LEFT, expand=YES, fill=X)
    

    chk1=Checkbar(row, ['\t\t'])
    chk1.pack(side=LEFT,  fill=X,expand=YES)
    
    
    tab1.bind('<Return>', (lambda event, e=ents11: fetch(e)))
    
    ftext.trace('w',update_num)
    ntext.trace('w',update_num)
    
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=5, pady=2)
    
    b11 = Button(tab1, text='Build Wavelets',
    command=(lambda e=ents11,po=chk1 :run_build_wave(e,po)))
    b11.pack(padx=5, pady=5)
    
    
    bline=Frame(tab1, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=2) 
    
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=0, pady=2)    
    Label(row,text=frame_label_2,justify=LEFT, anchor='w',  \
#    height=2, 
    wraplength=width/3
    ).pack(anchor=W, side=TOP, expand=YES, fill=BOTH)
    
    bline=Frame(tab1, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=2)
   
#    file_path=str()
    path_entry_1=browse_path(tab1)
    tab1.bind('<Return>', (lambda event, p=path_entry_1: fetch(p)))
    
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=5, pady=2)
    
    Label(row,text='Column delimiter:\t',justify=LEFT, anchor='w' \
    ).pack(anchor=W, side=LEFT)
    
    delim=IntVar()
    delim.set(1)  
    
    for txt, val in delim_choices:
        Radiobutton(row, 
                text=txt,
                padx = 5, 
                variable=delim, 
                command=(),
                value=val).pack(side=LEFT)
   
    
    row=Frame(tab1)
    row.pack(side=TOP, fill=X, padx=5, pady=2)        
        
    Label(row,text='Decimal place character:',justify=LEFT \
    ).pack(anchor=W, side=LEFT)
    
    dec=IntVar()
    dec.set(1)
    
    for txt, val in decimal_choices:
        Radiobutton(row, 
                text=txt,
                padx = 5, 
                variable=dec, 
                command=(),
                value=val).pack(side=LEFT)
    
    ents12=makeform(tab1, file_details_fields)
    tab1.bind('<Return>', (lambda event, e2=ents12: fetch(e2)))
    
    b12 = Button(tab1, text='Calculate intensities', command=(lambda e1=ents11, e2=ents12, e3 = path_entry_1 , dl=delim ,dc=dec: run_calculate_intensities(e1,e2,e3,dl,dc)))
    b12.pack(side=LEFT, padx=10, pady=10)
    
    b13 = Button(tab1, text='Close', command=close_window)
    b13.pack(side=RIGHT, padx=5, pady=10)
    


    """""""""    TAB 2: Advanced Settings    """""""""
    
    tab2 = Tab(root, "Advanced Settings")
    
    bline=Frame(tab2, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=2) 
    
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=0, pady=2)    
    Label(row,text=frame_label_1,justify=LEFT, anchor='w',  \
#    height=2, 
    wraplength=width/3
    ).pack(anchor=W, side=TOP, expand=YES, fill=BOTH)
    
    bline=Frame(tab2, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=2)
    
    ents21 = makeform(tab2, advanced_fields)
        
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=5, pady=3)
    Label(row,text=plt_choice_txt,anchor='w', \
#    height=2, 
    wraplength=width/3
    ).pack(side=LEFT, expand=YES, fill=X)
    
   
    chk2=Checkbar(row, ['\t'])
    chk2.pack(side=LEFT,  fill=X,expand=YES)

    tab2.bind('<Return>', (lambda event, e=ents21: fetch(e)))

    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=5, pady=3)
    
    b12 = Button(tab2, text='Build Wavelets',
    command=(lambda e=ents21,po=chk2 :run_build_wave(e,po)))
    b12.pack(padx=5, pady=5)    
    
    bline=Frame(tab2, bg='black', relief=GROOVE)
    bline.pack(side=TOP, fill=X, padx=0, pady=3)
    
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=0, pady=3)
    
    Label(row,text=frame_label_2,justify=LEFT, anchor='w',  \
#    height=2, 
    wraplength=width/3
    ).pack(anchor=W, side=TOP, expand=YES, fill=BOTH)
    
    bline=Frame(tab2, bg='black', relief=GROOVE)
    bline.pack( side=TOP, fill=X, padx=0, pady=3)
    
    path_entry_2=browse_path(tab2)
    tab2.bind('<Return>', (lambda event, p=path_entry_2: fetch(p)))
    
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=5, pady=2)
    
    Label(row,text='Column delimiter:\t',justify=LEFT, anchor='w' \
    ).pack(anchor=W, side=LEFT)
    
    for txt, val in delim_choices:
        Radiobutton(row, 
                text=txt,
                padx = 5, 
                variable=delim, 
                command=(),
                value=val).pack(side=LEFT)
    
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=5, pady=2)        
        
    Label(row,text='Decimal place character:',justify=LEFT \
    ).pack(anchor=W, side=LEFT)
    
 
    for txt, val in decimal_choices:
        Radiobutton(row, 
                text=txt,
                padx = 5, 
                variable=dec, 
                command=(),
                value=val).pack(side=LEFT)    
    
    
    ents22=makeform(tab2, file_details_fields)
    tab2.bind('<Return>', (lambda event, e2=ents22: fetch(e2)))
    
    b22 = Button(tab2, text='Calculate intensities', command=close_window)
    b22.pack(side=LEFT, padx=5, pady=2)
    
    b23 = Button(tab2, text='Close', command=close_window)
    b23.pack(side=RIGHT, padx=10, pady=10)
    
    row=Frame(tab2)
    row.pack(side=TOP, fill=X, padx=5, pady=10)
    
    """""""""    TAB 3: About    """""""""
    
    tab3= Tab(root, "About")
    explan="""This program is a signal processing tool allowing you to perform wavelet analysis on EMG signals \n\n\n\n\n\n"""
    Label(tab3,text=about_txt,justify=LEFT, \
    height=2, wraplength=width/3).pack(side=TOP, expand=YES, fill=X)
  
    bar.add(tab1)                   # add the tabs to the tab bar
    bar.add(tab2)
    bar.add(tab3)
    bar.show()
    
    root.mainloop()
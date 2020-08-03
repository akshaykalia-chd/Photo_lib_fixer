import os, time, shutil, datetime, exifread, wx

# Get Dir dialog
def get_dir(what):
    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0, 0, 200, 50)
    open_file_dialog = wx.DirDialog(frame, what, "", style=wx.DD_DEFAULT_STYLE)
    open_file_dialog.ShowModal()
    return open_file_dialog.GetPath()

def get_size():
    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0, 0, 200, 50)
    open_file_dialog = wx.TextEntryDialog(frame, "Files below this Size will be removed. Enter a file size in bytes:", "Size")
    open_file_dialog.ShowModal()
    size = open_file_dialog.GetValue()
    size = int(size)
    return size

# Question dialog
def question(message):
    u_sel = wx.MessageBox(message, 'Question?', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
    return u_sel

def read_dateTaekn(file):
    months_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    cmy = []
    with open(file, 'rb') as fh:
        tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
        dateTaken = tags["EXIF DateTimeOriginal"]
        dateTaken = str(dateTaken)
        dateTaken = dateTaken.split(':')
        year = dateTaken[0]
        month = dateTaken[1]
        month_index = int(month) - 1
        month = months_name[month_index]
        cmy.append(month)
        cmy.append(year)
        return cmy

def get_files(directory):
    paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            paths.append(filepath)
    return paths

def get_cmy(file):
    cmy = []
    creat_time = os.path.getmtime(file)
    creat_time = time.ctime(creat_time)
    creat_time = creat_time.split()
    cmy.append(creat_time[1])
    cmy.append(creat_time[4])
    return cmy

def move_to_cmy_dir(file_list,path):
    fixed_path = path + "/" + "Structured/"
    for file in file_list:
        try:
            print("Current Location:", file)
            file_name = os.path.basename(file)
            creat_mon_yer = get_cmy_form_name(file)
            new_path = fixed_path+"/"+str(creat_mon_yer[1])+"/"+str(creat_mon_yer[0])+"/"+file_name
            print("New Location:", new_path)
            shutil.move(file, new_path)
        except PermissionError:
            continue

def pre_new_dir_struc(path):
    fixed_path = path+"/"+"Structured/"
    try:
        os.mkdir(fixed_path)
    except FileExistsError:
        print("file/Directory already exists")

    cmys=[]
    all_files = get_files(path)
    print("Reading file create times")
    for file in all_files:
        cmys.append(get_cmy_form_name(file))
    years = []
    months = []
    for cmy in cmys:
        years.append(cmy[1])
    years = unique_list(years)
    for year in years:
        m = []
        for cmy in cmys:
            if year in cmy:
                m.append(cmy[0])
        months.append(unique_list(m))
    if len(years) == len(months):
        print("Creating Directory Structure")
        i = len(years)
        while i > 0:
            i = i - 1
            year = years[i]
            month = months[i]
            try:
                os.mkdir(fixed_path+str(year))
            except FileExistsError:
                print("file/Directory already exists")
            for m in month:
                out_path = fixed_path+str(year)+"/"+m
                try:
                    os.mkdir(out_path)
                except:
                    print("file/Directory already exists")

def get_cmy_form_name(file):
    year = datetime.datetime.now().year
    months_num = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    months_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    file_name = os.path.basename(file)
    cmy = []
    cmy_set = False
    try:
        cmy = read_dateTaekn(file)
        cmy_set = True
    except:
        pass
    while(not cmy_set):
        if year >= 1981:
            for num in months_num:
                datestr = str(year)+num
                if datestr in file_name:
                    month_name_index = int(num) - 1
                    month = months_name[month_name_index]
                    cmy.append(month)
                    cmy.append(year)
                    cmy_set = True
                    break
        else:
            if len(cmy) == 0:
                cmy = get_cmy(file)
                break
        year = year - 1
    return cmy

def unique_list(list):
    unique_list = []
    for x in list:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

def remove_small_files(file_list, size):
    count = 0
    for file in file_list:
        file_szie = os.path.getsize(file)
        if file_szie <= size:
            print(file, ":", file_szie)
            count = count + 1
    print("Number of Files Found:", count)
    for file in file_list:
        file_szie = os.path.getsize(file)
        if file_szie <= size:
            os.remove(file)

app = wx.App()
app.MainLoop()
current_path = get_dir("Photo Library Location")
size = get_size()
message = "Are you sure you want to remove all files smaller than "+str(size)+" bytes?"
if question(message) == 2:
    remove_small_files(get_files(current_path), size)
pre_new_dir_struc(current_path)
move_to_cmy_dir(get_files(current_path), current_path)
app.ExitMainLoop()
exit()
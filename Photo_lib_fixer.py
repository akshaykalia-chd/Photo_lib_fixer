import datetime
import os
import shutil
import time

import exifread
import wx


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
    open_file_dialog = wx.TextEntryDialog(frame, "Files below this Size will be removed. Enter a file size in bytes:",
                                          "Size")
    open_file_dialog.ShowModal()
    size = open_file_dialog.GetValue()
    size = int(size)
    return size


# Question dialog
def question(message):
    u_sel = wx.MessageBox(message, 'Question?', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
    return u_sel


# warning dialog
def warning(message):
    wx.MessageBox(message, 'Warning', wx.OK | wx.ICON_WARNING)
    return


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


def move_to_cmy_dir(file_list, path, type):
    fixed_path = path + "/" + "Structured/" + type + "/"
    for file in file_list:
        try:
            print("Current Location:", file)
            file_name = os.path.basename(file)
            creat_mon_yer = get_cmy_form_name(file)
            new_path = fixed_path + "/" + str(creat_mon_yer[1]) + "/" + str(creat_mon_yer[0]) + "/" + file_name
            print("New Location:", new_path)
            shutil.move(file, new_path)
        except PermissionError:
            continue


def pre_new_dir_struc(path, file_list, type):
    fixed_path = path + "/" + "Structured/"
    try:
        os.mkdir(fixed_path)
    except FileExistsError:
        print("file/Directory already exists")

    fixed_path = fixed_path + type + "/"

    try:
        os.mkdir(fixed_path)
    except FileExistsError:
        print("file/Directory already exists")

    cmys = []
    all_files = file_list
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
                os.mkdir(fixed_path + str(year))
            except FileExistsError:
                print("file/Directory already exists")
            for m in month:
                out_path = fixed_path + str(year) + "/" + m
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
    while (not cmy_set):
        if year >= 1981:
            for num in months_num:
                datestr = str(year) + num
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
    for file in file_list:
        file_szie = os.path.getsize(file)
        if file_szie <= size:
            os.remove(file)


def small_file_count(file_list, size):
    count = 0
    for file in file_list:
        file_szie = os.path.getsize(file)
        if file_szie <= size:
            print(file, ":", file_szie)
            count = count + 1
    message = "Number of small files Found: " + str(count)
    warning(message)
    return count


def filter_image_files(file_list):
    image_files = list()
    ext_list = [".jpg", ".jpeg", ".jpe.jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw",
                ".arw", ".cr2", ".nrw", ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2",
                ".j2k", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps"]
    for file in file_list:
        file_ext = os.path.splitext(file)[1]
        if file_ext.lower() in ext_list:
            image_files.append(file)
    return image_files


def filter_video_files(file_list):
    video_files = list()
    ext_list = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".m4p", ".m4v", ".avi", ".wmv",
                ".mov", ".qt", ".flv", ".swf", ".mkv.", ".rm", ".3gp"]
    for file in file_list:
        file_ext = os.path.splitext(file)[1]
        if file_ext.lower() in ext_list:
            video_files.append(file)
    return video_files


def filter_other_files(file_list):
    other_files = list()
    ext_list = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".m4p", ".m4v", ".avi", ".wmv",
                ".mov", ".qt", ".flv", ".swf", ".mkv.", ".rm", ".3gp", ".jpg", ".jpeg", ".jpe.jif", ".jfif", ".jfi",
                ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw", ".k25", ".bmp",
                ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpx", ".jpm", ".mj2",
                ".svg", ".svgz", ".ai", ".eps"]
    for file in file_list:
        file_ext = os.path.splitext(file)[1]
        if file_ext.lower() not in ext_list:
            other_files.append(file)
    return other_files


app = wx.App()
app.MainLoop()
current_path = get_dir("Photo Library Location")
size = get_size()
file_list = get_files(current_path)
if small_file_count(file_list, size) > 0:
    message = "Are you sure you want to remove all files smaller than " + str(size) + " bytes?"
    if question(message) == 2:
        remove_small_files(file_list, size)
file_list = get_files(current_path)
file_type = "Photos"
image_files = filter_image_files(file_list)
pre_new_dir_struc(current_path, image_files, file_type)
move_to_cmy_dir(image_files, current_path, file_type)

file_type = "Videos"
video_files = filter_video_files(file_list)
pre_new_dir_struc(current_path, video_files, file_type)
move_to_cmy_dir(video_files, current_path, file_type)

file_type = "Other"
other_files = filter_other_files(file_list)
pre_new_dir_struc(current_path, other_files, file_type)
move_to_cmy_dir(other_files, current_path, file_type)
app.ExitMainLoop()
exit()

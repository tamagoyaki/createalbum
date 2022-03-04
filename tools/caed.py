''' Hide commandline prompt on windows
import sys
if sys.platform=="win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(),
                                    0 )
'''

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.recycleview import RecycleView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from functools import partial
import os
import imghdr
import threading


resource_add_path('c:/Windows/Fonts')
LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')

class ProgressDialog(FloatLayout):
    def __init__(self, get_progress=None, thread_body=None):
        '''
        Args:
            get_progress (func): function which returns value between 0 and 1
            thread_body (func): function which run as thread.
        '''
        FloatLayout.__init__(self)
        self.ids.pbar.max = 1
        self.ids.pbar.value = 0
        self.get_progress = get_progress
        self.thread_body = thread_body
        Clock.schedule_once(self.update, 0.1)

        self.popup = Popup(title='Progress', content=self, size_hint=(0.9, 0.3),
                           auto_dismiss=False)
        self.popup.open()

        self.threadevent = threading.Event()
        self.thread = threading.Thread(target=thread_body)
        self.thread.start()
        # print(f'progress: {thread_body} started')

    def update(self, dt):
            self.ids.pbar.value = self.get_progress()
            # print(f'update: {self.ids.pbar.value}')
            if self.ids.pbar.value < 1:
                Clock.schedule_once(self.update, 0.1)
            else:
                self.popup.dismiss()
                # print('clock stoped !!!!!!!!!!!!!!!!!!!!!!!!!!!!')


class SaveDialog(FloatLayout):
    def __init__(self, cbsave):
        FloatLayout.__init__(self)
        self.popup = Popup(title='save', content=self, size_hint=(0.9, 0.9),
                           auto_dismiss=False)
        self.popup.open()

        # callback wrapper. you can write 'self.save = cbsave' directly
        self.cbsave = cbsave
        self.cbcancel = self.popup.dismiss

        # set default path for M$ Windows
        self.ids.filechooser.path = os.path.join(os.environ['USERPROFILE'],
                                                 "Desktop")

    def save(self, path, filename):
        self.cbsave(path, filename)
        self.popup.dismiss()
        print('save complete')

    def cancel(self):
        self.cbcancel()
        print('save canceled')

    def selected(self, selection, filename):
        self.ids.filename.text = os.path.basename(selection[0])


class ImageFile():
    def __init__(self, fullpath=None):
        self.fullpath = fullpath
        self.rotate = 0
        self.comments = None

    def mkcomments(self, usepath, ign, usename):
        ''' Make comments from fullpath

        Args:
            usepath (bool): use fullpath as comments if True
            ign (str): num string only
            usename (bool): use filename as comment if True

        Return:
            (arry)
        '''
        if usepath:
            if self.comments is None:
                if usename:
                    path = self.fullpath
                else:
                    path = os.path.dirname(self.fullpath)

                self.comments = path.removeprefix('\\\\').split('\\')
                del self.comments[0:int(ign)]

        return self.comments

    def mkcsv(self):
        ''' Make a csv record

        Return:
            (string): csv format
        '''
        csv = f'{self.fullpath}, {self.rotate}'

        for cmt in self.comments:
            csv += f', {cmt}'

        return csv

    def ldcsv(self, csv):
        ''' Load a csv record

        Arg:
            csv (string): created by mkcsv().
        '''
        ary = csv.split(',')
        self.fullpath = ary[0]
        self.rotate = ary[1]
        self.comments = ary[2:]


class ImageFiles():
    def __init__(self):
        self.files = {}

    def __iter__(self):
        yield from self.files.values()

    def add(self, imgf):
        ''' add or recall an ImageFile

        Arg:
            imgf (ImageFile):

        Return:
            (ImageFile)
        '''
        if imgf.fullpath not in self.files:
            self.files[imgf.fullpath] = imgf

        return self.files[imgf.fullpath]

    def clear(self):
        self.files = {}

    def update(self, imgf):
        self.files[imgf.fullpath] = imgf

    def rvupdate(self, callback):
        ''' Make a array for recycleview widget

        Arg:
            callback (func): called by click on a recycleview
        '''
        from functools import partial

        ary = []
        for key, val in self.files.items():
            ary.append({'text': key, 'on_release': partial(callback, key)})
        return ary


class CaedLayout(Widget):
    def __init__(self):
        Widget.__init__(self)
        self.images = ImageFiles()
        self.curimage = None
        self.progress = 0

    def clr_current(self):
        ''' Clear current info on display.
        '''
        self.ids.my_image.source = ''
        self.clr_comments()
        self.curimage = None

    def clr_comments(self):
        ''' Clear comments widget
        '''
        ix = 0
        for key, val in self.ids.items():
            if key.startswith('comment'):
                val.text = ''
                ix += 1

    def set_comments(self, comments):
        ''' Set comments to comments widget
        '''
        self.clr_comments()

        ix = 0
        for key, val in self.ids.items():
            if key.startswith('comment') and comments and ix < len(comments):
                val.text = comments[ix]
                ix += 1

    def push_current(self):
        ''' Push current display info to recyclevies
        '''
        if self.curimage is None:
            return

        # textinput to comments
        ix = 0
        comments = []

        for key, val in self.ids.items():
            if key.startswith('comment'):
                comments.append(val.text)
                ix += 1

        self.curimage.comments = comments
        self.images.update(self.curimage)
        self.rv_update()

    def show_image(self, name):
        ''' Show image specified by name

        Arg:
            name (str): filename
        '''
        self.curimage = ImageFile(name)
        img = self.images.add(self.curimage)
        comments = img.mkcomments(self.ids.ck_usepath.active,
                                  self.ids.sp_ignore.text,
                                  self.ids.ck_usename.active)

        # show it
        # print(f'show image: {img.fullpath}')
        self.ids.my_image.source = img.fullpath
        self.set_comments(comments)

    def rv_update(self):
        self.ids.rv.data = self.images.rvupdate(self.onrv)
        self.ids.rv.scroll_y = 0  # scroll to the end of the list (why 0 ?)
        # print(f'rv update: {len(self.ids.rv.data)}')

    def rv_clear(self):
        self.ids.rv.data = []

    def get_progress(self):
        # print(f'get_pro: {self.progress}')
        return self.progress

    def load_prj(self, path):
        ''' Load projectfile (csv format)
        '''
        self.clr_current()
        self.images.clear()

        '''
        WARNING: The file must be shift-jis or cp932.

        readline(), readlines() and "while line in stream:" are reading
        file as string not file's raw data. the string are converted binary
        to utf-8 or something. So the total length of string is not the
        same as file size.

        1, open the file as binary
        2, read line until newline as binary
        3, the size of binary is equivalent  to the file size.
        4, decode binary as multibytes string.
        5, then process the sring
        '''
        with open(path, 'rb') as stream:
            totalsize = os.path.getsize(path)
            cursize = 0

            for line in stream:
                size = len(line)
                cursize += size
                self.progress = cursize / totalsize
                '''
                print(f'load_prj: {self.progress}, {size}, {cursize}, '
                      f'{totalsize}, {type(line)}')
                '''

                line = line.decode('cp932')
                img = ImageFile()
                line = line.replace('\r', '')
                line = line.replace('\n', '')
                img.ldcsv(line)
                self.images.add(img)

            # show the last img
            self.rv_update()
            self.show_image(img.fullpath)
    
        
    def dig_directory(self, path):
        ''' Searching for img files in path recurcivery
        '''
        self.clr_current()
        self.images.clear()

        totalnum = 0
        curnum = 0

        for root, dirs, files in os.walk(path):
            for file in files:
                totalnum += 1

        for root, dirs, files in os.walk(path):
            for file in files:
                curnum += 1
                self.progress = curnum / totalnum
                # print(f'dig_dir: {self.progress}, {curnum}, {totalnum}')

                fullpath = os.path.join(root, file)
                kind = self.kindof(fullpath)
                # print(f'{type(fullpath)}: {fullpath}, {kind}')

                if 'img' == kind:
                    img = ImageFile(fullpath)
                    img.mkcomments(self.ids.ck_usepath.active,
                                   self.ids.sp_ignore.text,
                                   self.ids.ck_usename.active)
                    self.images.add(img)

        # show the last img
        try:
            self.show_image(img.fullpath)
        except NameError:
            print('no images found')
        self.rv_update()
                    

    def kindof(self, path):
        ''' Check what kind of file.

        Arg:
            path (str): fullpath

        Return:
            (str): kind of file. ('img', 'dir', 'prj' or somethin)

        '''
        kind = 'unknown'

        if os.path.isdir(path):
            kind = 'dir'
        elif os.path.isfile(path):
            ik = imghdr.what(path)
            if 'jpeg' == ik or 'png' == ik:
                kind = 'img'
            elif path.lower().endswith(('csv', 'createalbum')):
                kind = 'prj'
        
        # print(f'kindof : {type(path)}, {path}, {kind}')
        return kind
        
    def ondrop(self, path):
        path = path.decode('utf-8')
        kind = self.kindof(path)

        if 'img' == kind:
            self.push_current()
            self.show_image(path)
        elif 'dir' == kind or 'prj' == kind:
            if 'dir' == kind:
                fn = self.dig_directory
            else:
                fn = self.load_prj

            self.progress = 0
            pd =ProgressDialog(get_progress=self.get_progress,
                               thread_body=partial(fn, path))
            # umm, image didn't show up from thread body. so reload it. :-(
            pd.thread.join()
            self.ids.my_image.reload()
        else:
            print(f'UNKNOWN PATH: {path}')

    def onok(self):
        self.push_current()

    def oncancel(self):
        self.clr_current()

    def onsave(self):
        self.push_current()
        SaveDialog(cbsave=self.cbsave)

    def cbsave(self, path, filename):
        ''' callback function for SaveDialog
        '''
        with open(os.path.join(path, filename), 'w') as stream:
            for img in self.images:
                csv = img.mkcsv()
                stream.write(csv + '\n')

    def onrv(self, fullpath):
        self.push_current()
        self.show_image(fullpath)

    def onusepath(self, active):
        if active is True:
            disabled = False
        else:
            disabled = True
            
        self.ids.lb_ignore.disabled = disabled
        self.ids.sp_ignore.disabled = disabled
        self.ids.ck_usename.disabled = disabled
        self.ids.lb_usename.disabled = disabled


class Caed(App):
    def __init__(self):
        App.__init__(self)
        
    def build(self):
        Window.size = (800, 600)
        Window.bind(on_dropfile=self.ondropfile)
        return CaedLayout()

    def ondropfile(self, window, path):
        self.root.ondrop(path)


Caed().run()

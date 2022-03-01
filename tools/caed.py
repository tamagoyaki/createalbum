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
import os
import imghdr


resource_add_path('c:/Windows/Fonts')
LabelBase.register(DEFAULT_FONT, 'msgothic.ttc')


class SaveDialog(FloatLayout):
    def __init__(self, cbsave):
        FloatLayout.__init__(self)
        self.popup = Popup(title='save', content=self, size_hint=(0.9, 0.9))
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
        csv = f'{self.fullpath}, {self.rotate}'

        for cmt in self.comments:
            csv += f', {cmt}'

        return csv

    def ldcsv(self, csv):
        '''
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
        from functools import partial

        ary = []
        for key, val in self.files.items():
            ary.append({'text': key, 'on_press': partial(callback, key)})
        return ary


class CaedLayout(Widget):
    def __init__(self):
        Widget.__init__(self)
        self.images = ImageFiles()
        self.curimage = None

    def clr_current(self):
        self.ids.my_image.source = ''
        self.clr_comments()
        self.curimage = None

    def clr_comments(self):
        ix = 0
        for key, val in self.ids.items():
            if key.startswith('comment'):
                val.text = ''
                ix += 1

    def set_comments(self, comments):
        self.clr_comments()

        ix = 0
        for key, val in self.ids.items():
            if key.startswith('comment') and comments and ix < len(comments):
                val.text = comments[ix]
                ix += 1

    def push_current(self):
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
        self.curimage = ImageFile(name)
        img = self.images.add(self.curimage)
        comments = img.mkcomments(self.ids.ck_usepath.active,
                                  self.ids.sp_ignore.text,
                                  self.ids.ck_usename.active)

        # show it
        self.ids.my_image.source = img.fullpath
        self.set_comments(comments)

    def rv_update(self):
        self.ids.rv.data = self.images.rvupdate(self.onrv)

    def rv_clear(self):
        self.ids.rv.data = []

    def load_prj(self, path):
        self.clr_current()
        self.images.clear()

        with open(path) as stream:
            for line in stream:
                img = ImageFile()
                line = line.replace('\n', '')
                img.ldcsv(line)
                self.images.add(img)

            # show the last img
            self.rv_update()
            self.show_image(img.fullpath)
    
        
    def dig_directory(self, path):
        self.clr_current()
        self.images.clear()

        for root, dirs, files in os.walk(path):
            for file in files:
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
        kind = 'unknown'

        if os.path.isdir(path):
            kind = 'dir'
        elif os.path.isfile(path):
            ik = imghdr.what(path)
            if 'jpeg' == ik or 'png' == ik:
                kind = 'img'
            elif path.lower().endswith(('csv', 'createalbum')):
                kind = 'createalbum'
        
        # print(f'kindof : {type(path)}, {path}, {kind}')
        return kind
        
    def ondrop(self, path):
        path = path.decode('utf-8')
        kind = self.kindof(path)

        if 'img' == kind:
            self.push_current()
            self.show_image(path)
        elif 'dir' == kind:
            self.dig_directory(path)
        elif 'createalbum' == kind:
            self.load_prj(path)
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

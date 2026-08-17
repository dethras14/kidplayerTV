import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import platform
os.environ['KIVY_NO_NETWORK'] = '1'
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE])
VIDEO_DIR = '/storage/emulated/0/Videos/Kids' if platform == 'android' else os.path.expanduser('~/Videos/Kids')
class CategoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.label = Label(text='Choose a Category', font_size='40sp', size_hint_y=0.15)
        self.layout.add_widget(self.label)
        self.grid = GridLayout(cols=3, spacing=10, padding=10)
        self.layout.add_widget(self.grid)
        self.load_categories()
    def load_categories(self):
        self.grid.clear_widgets()
        if not os.path.exists(VIDEO_DIR):
            os.makedirs(VIDEO_DIR)
            self.grid.add_widget(Label(text='Create subfolders in\n' + VIDEO_DIR, font_size='30sp'))
            return
        categories = [d for d in os.listdir(VIDEO_DIR) if os.path.isdir(os.path.join(VIDEO_DIR, d))]
        if not categories:
            self.grid.add_widget(Label(text='No categories. Add subfolders.', font_size='30sp'))
            return
        for cat in categories:
            btn = Button(text=cat, font_size='30sp', background_color=(1,0.7,0.3,1), size_hint=(None,None), size=(200,150))
            btn.bind(on_press=lambda x, c=cat: self.go_to_videos(c))
            self.grid.add_widget(btn)
    def go_to_videos(self, category):
        app = App.get_running_app()
        app.video_screen.load_videos(category)
        app.root.current = 'video_screen'
class VideoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        top_bar = BoxLayout(size_hint_y=0.12)
        self.back_btn = Button(text='⬅ Back', font_size='30sp')
        self.back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(self.back_btn)
        self.lock_btn = Button(text='🔒', font_size='30sp', size_hint_x=0.2)
        self.lock_btn.bind(on_press=self.toggle_orientation_lock)
        top_bar.add_widget(self.lock_btn)
        self.layout.add_widget(top_bar)
        self.grid = GridLayout(cols=3, spacing=10, padding=10)
        self.layout.add_widget(self.grid)
        self.video = Video(source='', state='stop')
        self.video.allow_stretch = True
        self.video.keep_ratio = False
        self.video.size_hint = (1, 1)
        self.video.opacity = 0
        self.video.disabled = True
        self.layout.add_widget(self.video)
        self.current_category = ''
        self.video_list = []
        self.current_index = 0
        self.orientation_locked = False
    def load_videos(self, category):
        self.current_category = category
        self.grid.clear_widgets()
        self.video.opacity = 0
        self.video.disabled = True
        self.video.state = 'stop'
        self.grid.opacity = 1
        self.grid.disabled = False
        folder = os.path.join(VIDEO_DIR, category)
        videos = [f for f in os.listdir(folder) if f.lower().endswith(('.mp4','.avi','.mov','.mkv','.webm'))]
        if not videos:
            self.grid.add_widget(Label(text='No videos here', font_size='30sp'))
            return
        self.video_list = sorted(videos)
        self.current_index = 0
        for vid in videos:
            btn = Button(text=vid, font_size='24sp', background_color=(0.5,0.8,0.5,1), size_hint=(None,None), size=(180,120))
            btn.bind(on_press=lambda x, v=vid: self.play_video(v))
            self.grid.add_widget(btn)
    def play_video(self, filename):
        full_path = os.path.join(VIDEO_DIR, self.current_category, filename)
        self.video.source = full_path
        self.video.state = 'play'
        self.video.opacity = 1
        self.video.disabled = False
        self.grid.opacity = 0
        self.grid.disabled = True
        self.video.unbind(on_eos=self.next_video)
        self.video.bind(on_eos=self.next_video)
    def next_video(self, *args):
        if not self.video_list:
            return
        self.current_index = (self.current_index + 1) % len(self.video_list)
        self.play_video(self.video_list[self.current_index])
    def go_back(self, instance):
        self.video.state = 'stop'
        self.video.opacity = 0
        self.video.disabled = True
        self.grid.opacity = 1
        self.grid.disabled = False
        App.get_running_app().root.current = 'category_screen'
    def toggle_orientation_lock(self, instance):
        self.orientation_locked = not self.orientation_locked
        if self.orientation_locked:
            if Window.width > Window.height:
                Window.rotation = 0
            else:
                Window.rotation = 90
            instance.text = '🔓'
        else:
            Window.rotation = -1
            instance.text = '🔒'
class KidApp(App):
    def build(self):
        Window.size = (800, 480)
        sm = ScreenManager()
        self.category_screen = CategoryScreen(name='category_screen')
        self.video_screen = VideoScreen(name='video_screen')
        sm.add_widget(self.category_screen)
        sm.add_widget(self.video_screen)
        return sm
if __name__ == '__main__':
    KidApp().run()

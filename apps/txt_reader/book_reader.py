from play32sys import app
from graphic import framebuf_helper, ubmfont, bmfont
from buildin_resource import font
from book import Book, Bookmark, get_text_utf8_length
import hal_screen, gc

BUFFER_SIZE = 4096 if app.has_big_memory() else 512
WHITE = framebuf_helper.get_white_color(hal_screen.get_format())
SCR_W, SCR_H = hal_screen.get_size()
FNT: ubmfont.FontDrawUnicode = font.get_font_16px()
FNT_W, FNT_H = FNT.get_font_size()

def gc_collect_small_memory():
    if not app.has_big_memory():
        gc.collect()

class BookReader():
    def __init__(self, commit_after_flip=1):
        self.bookmark = None
        self.bookmark_pos = 0
        self.bookmark_size = 0
        self.book = None
        self.book_size = 0
        self.__commit_after_flip = commit_after_flip
        self.__flipped = 0
    
    @property
    def book_loaded(self):
        return self.book != None

    @property
    def bookmark_loaded(self):
        return self.bookmark_size == self.book_size

    @property
    def bookmark_load_progress(self):
        return self.bookmark_size / self.book_size

    @property
    def bookmark_current_page(self):
        return self.bookmark.marked_page
    
    @property
    def bookmark_total_page(self):
        return len(self.bookmark)

    def flip_page_by(self, page_offset):
        bmk = self.bookmark
        old_page = bmk.marked_page
        new_page = old_page + page_offset
        if new_page in bmk:
            if old_page <= new_page:
                offset = bmk.get_page_offset_fast(old_page, new_page, BUFFER_SIZE//2)
            else:
                offset =  - bmk.get_page_offset_fast(new_page, old_page, BUFFER_SIZE//2)
            self.bookmark_pos += offset
            self.__flipped += 1
            if self.__flipped >= self.__commit_after_flip:
                bmk.update_marked_page(new_page, True)
                self.__flipped = 0
                gc.collect()
            else:
                bmk.update_marked_page(new_page, False)
                gc_collect_small_memory()
    
    def commit_bookmark_page(self):
        bmk = self.bookmark
        bmk.update_marked_page(bmk.marked_page, True)

    def load_book(self, txt_file_path):
        bmk = Bookmark(txt_file_path+'.bmk')
        self.bookmark = bmk
        self.bookmark_pos = bmk.get_page_offset_fast(0, bmk.marked_page, BUFFER_SIZE//2)
        self.bookmark_size = self.bookmark_pos + bmk.get_page_offset_fast(bmk.marked_page, len(bmk), BUFFER_SIZE)
        self.book = Book(txt_file_path, BUFFER_SIZE, self.bookmark_pos)
        self.book_size = len(self.book)
        self.__flipped = 0
        gc_collect_small_memory()

    def load_bookmark(self, max_pages=-1):
        if self.bookmark == None:
            return
        book = self.book
        if self.bookmark_size < self.book_size:
            book.seek_to(self.bookmark_size)
            page_list = []
            while max_pages != 0:
                txt = book.get_buffered_string()
                if len(txt) <= 0:
                    break
                count = bmfont.get_text_count(txt, SCR_W, SCR_H, FNT_W, FNT_H)
                txt_bytes_size = get_text_utf8_length(txt[:count])
                page_list.append(txt_bytes_size)
                book.seek_by(txt_bytes_size)
                max_pages -= 1
                gc_collect_small_memory()
            self.bookmark.append_pages(page_list)
            self.bookmark_size += sum(page_list)
            del page_list
        gc.collect()
        return self.bookmark_size == self.book_size # return if finished
    
    def render(self):
        book = self.book
        book.seek_to(self.bookmark_pos)
        txt = book.get_buffered_string()
        frame = hal_screen.get_framebuffer()
        frame.fill(0)
        FNT.draw_on_frame(txt, frame, 0, 0, WHITE, SCR_W, SCR_H)
        hal_screen.refresh()

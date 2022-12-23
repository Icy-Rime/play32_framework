from graphic.bmfont import get_text_count
from play32hw.cpu import sleep

sleep_time_ms = 15

class PagedText:
    def __init__(self, text, area_w, area_h, font_w, font_h, scroll_bar=None, style_inline=False):
        pages = []
        scroll_bar_width = font_w if style_inline else 4
        while len(text) > 0:
            if scroll_bar:
                page_size = get_text_count(text, area_w - scroll_bar_width, area_h, font_w, font_h)
            else:
                page_size = get_text_count(text, area_w, area_h, font_w, font_h)
                if scroll_bar == None and page_size < len(text):
                    # auto mode, need scroll_bar
                    scroll_bar = True
                    continue # lets start again
            pages.append(text[:page_size])
            text = text[page_size:]
        if len(pages) == 0:
            pages.append("")
        self.pages = pages
        self.mark = 0
        self.with_scroll_bar = True if scroll_bar else False
        self.style_inline = style_inline
    
    def __len__(self):
        return len(self.pages)

    def get_text(self):
        return self.pages[self.mark]
    
    def page_down(self):
        np = self.mark + 1
        self.mark = self.mark if (np >= len(self.pages)) else np

    def page_up(self):
        np = self.mark - 1
        self.mark = self.mark if np < 0 else np

    def draw(self, frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white):
        FW, FH = font_draw.get_font_size()
        if self.style_inline:
            HFW = FW // 2
            AW = frame_w - (FW if self.with_scroll_bar else 0)
            offset_x = ((AW % FW) // 2) + (FW // 2 if self.with_scroll_bar else 0)
            offset_y = (frame_h % FH) // 2
        else:
            AW = frame_w - (4 if self.with_scroll_bar else 0) # reserve for scroll bar
            offset_x = (AW % FW) // 2
            offset_y = (frame_h % FH) // 2
        font_draw.draw_on_frame(self.pages[self.mark], frame, frame_x + offset_x, frame_y + offset_y, color_white, AW, frame_h)
        if self.with_scroll_bar:
            if self.style_inline:
                root_y = frame_h // 2 - 1
                # left
                frame.line(frame_x, frame_y + root_y, frame_x + HFW - 1, frame_y, color_white)
                frame.line(frame_x, frame_y + root_y, frame_x + HFW - 1, frame_y + (root_y * 2), color_white)
                frame.vline(frame_x + HFW - 1, frame_y + 3, (root_y * 2) - 5, color_white)
                # right
                frame.line(frame_x + frame_w - 1, frame_y + root_y, frame_x + frame_w - HFW, frame_y, color_white)
                frame.line(frame_x + frame_w - 1, frame_y + root_y, frame_x + frame_w - HFW, frame_y + (root_y * 2), color_white)
                frame.vline(frame_x + frame_w - HFW, frame_y + 3, (root_y * 2) - 5, color_white)
            else:
                area_h = frame_h - 4
                total_pages = len(self.pages)
                scroll_h = max(int(area_h / total_pages), 1)
                scroll_start = int(self.mark * area_h / total_pages)
                frame.fill_rect(frame_x + frame_w - 3, frame_y + scroll_start + 2, 2, scroll_h, color_white)
                frame.hline(frame_x + frame_w - 4, frame_y, 4, color_white)
                frame.hline(frame_x + frame_w - 4, frame_y + frame_h - 1, 4, color_white)

def _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    FW, FH = font_draw.get_font_size()
    # draw text
    ava_w = frame_w - FW
    text_w = len(label) * FW
    if text_w > ava_w:
        label = label[:ava_w // FW]
        text_w = len(label) * FW
    text_offset_x = (FW // 2) + max((ava_w - text_w) // 2, 0)
    text_offset_y = max((frame_h - FH) // 2, 0)
    font_draw.draw_on_frame(label, frame, frame_x + text_offset_x, frame_y + text_offset_y, color_white, ava_w, FH)
    # let others draw decorate
    pass

def draw_button(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label)
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    # left
    frame.hline(frame_x + 1, frame_y, HFW - 1, color_white)
    frame.vline(frame_x, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + HFW - 2, frame_y + 2, frame_h - 4, color_white)
    frame.hline(frame_x + 1, frame_y + frame_h - 1, HFW - 1, color_white)
    # right
    frame.hline(frame_x + frame_w - HFW, frame_y, HFW - 1, color_white)
    frame.vline(frame_x + frame_w - 1, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + frame_w - HFW + 1, frame_y + 2, frame_h - 4, color_white)
    frame.hline(frame_x + frame_w - HFW, frame_y + frame_h - 1, HFW - 1, color_white)

def draw_label_nav(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label)
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    root_y = frame_h // 2 - 1
    # left
    frame.line(frame_x, frame_y + root_y, frame_x + HFW - 1, frame_y, color_white)
    frame.line(frame_x, frame_y + root_y, frame_x + HFW - 1, frame_y + (root_y * 2), color_white)
    frame.vline(frame_x + HFW - 1, frame_y + 3, (root_y * 2) - 5, color_white)
    # right
    frame.line(frame_x + frame_w - 1, frame_y + root_y, frame_x + frame_w - HFW, frame_y, color_white)
    frame.line(frame_x + frame_w - 1, frame_y + root_y, frame_x + frame_w - HFW, frame_y + (root_y * 2), color_white)
    frame.vline(frame_x + frame_w - HFW, frame_y + 3, (root_y * 2) - 5, color_white)

def draw_label_header(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label)
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    # left
    frame.vline(frame_x, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + HFW - 2, frame_y, frame_h - 2, color_white)
    frame.hline(frame_x + 3, frame_y + frame_h - 3, HFW - 3, color_white)
    frame.hline(frame_x + 1, frame_y + frame_h - 1, HFW - 1, color_white)
    # right
    frame.vline(frame_x + frame_w - 1, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + frame_w - HFW + 1, frame_y, frame_h - 2, color_white)
    frame.hline(frame_x + frame_w - HFW, frame_y + frame_h - 3, HFW - 3, color_white)
    frame.hline(frame_x + frame_w - HFW, frame_y + frame_h - 1, HFW - 1, color_white)

def draw_label_footer(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label)
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    # left
    frame.hline(frame_x + 1, frame_y, HFW - 1, color_white)
    frame.hline(frame_x + 3, frame_y + 2, HFW - 3, color_white)
    frame.vline(frame_x, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + HFW - 2, frame_y + 2, frame_h - 2, color_white)
    # right
    frame.hline(frame_x + frame_w - HFW, frame_y, HFW - 1, color_white)
    frame.hline(frame_x + frame_w - HFW, frame_y + 2, HFW - 3, color_white)
    frame.vline(frame_x + frame_w - 1, frame_y + 1, frame_h - 2, color_white)
    frame.vline(frame_x + frame_w - HFW + 1, frame_y + 2, frame_h - 2, color_white)

def draw_label_invert(frame, frame_x, frame_y, frame_w, frame_h, font_draw, color_white, label):
    frame.fill_rect(frame_x, frame_y, frame_w, frame_h, color_white)
    _draw_labeled_text(frame, frame_x, frame_y, frame_w, frame_h, font_draw, 0, label)
    frame.pixel(frame_x, frame_y, 0)
    frame.pixel(frame_x + frame_w - 1, frame_y, 0)
    frame.pixel(frame_x, frame_y + frame_h - 1, 0)
    frame.pixel(frame_x + frame_w - 1, frame_y + frame_h - 1, 0)

def draw_buttons_at_last_line(frame, frame_w, frame_h, font_draw, color_white, text_yes="YES", text_no="NO"):
    FW, FH = font_draw.get_font_size()
    HFW = FW // 2
    SINGLE = text_yes == text_no
    base_y = frame_h - FH
    if SINGLE:
        draw_button(frame, 0, base_y, frame_w, FH, font_draw, color_white, text_yes)
    else:
        draw_button(frame, 0, base_y, frame_w // 2 - 1, FH, font_draw, color_white, text_no)
        draw_button(frame, frame_w // 2 + 1, base_y, frame_w // 2 - 1, FH, font_draw, color_white, text_yes)

def sleep_save_power():
    sleep(sleep_time_ms)

def set_sleep_time(val_ms):
    global sleep_time_ms
    sleep_time_ms = val_ms

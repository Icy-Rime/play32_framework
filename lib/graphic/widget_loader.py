"""Example XML:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE WidgetLayout SYSTEM "http://ice-rime.tech/widget.dtd">
<WidgetLayout></WidgetLayout>

Example Useage:
root = xml.load_xml_string(xml_text)
ly = widget_loader.load_from_xml(root, frame, box)
ly.render()
"""

__class_map = {}

def register_class(name, cls):
    from graphic.widget import Widget
    if issubclass(cls, Widget):
        __class_map[name.encode("utf8")] = cls

def register_default_classes():
    from graphic.widget import Widget, WidgetLayout, Button, Text, ScrollText, PBMImage, FixedLayout, DevidedLayout
    __class_map[b"Widget"] = Widget
    __class_map[b"WidgetLayout"] = WidgetLayout
    __class_map[b"Button"] = Button
    __class_map[b"Text"] = Text
    __class_map[b"ScrollText"] = ScrollText
    __class_map[b"PBMImage"] = PBMImage
    __class_map[b"FixedLayout"] = FixedLayout
    __class_map[b"DevidedLayout"] = DevidedLayout

def load_from_xml(root, frame = None, box = (0, 0, 0, 0)):
    tag_name = root.value
    if tag_name not in __class_map:
        return None
    widget = __class_map[tag_name]()
    if frame != None:
        widget.set_frame(frame)
    widget.set_box(box)
    # set attr
    for b_name, b_value in root.iterate_attributes():
        if b_value != None:
            name = b_name.decode("utf8")
            value = b_value.decode("utf8")
        set_func = getattr(widget, "set_"+name, None)
        if callable(set_func):
            try:
                set_func(value)
            except: pass
        elif hasattr(widget, name):
            try:
                setattr(widget, name, value)
            except: pass
    # for layout
    append_child = getattr(widget, "append_child", None)
    if callable(append_child):
        for child in root.children:
            child_widget = load_from_xml(child, frame, box)
            append_child(child_widget) # None is filted in append_child method.
    return widget

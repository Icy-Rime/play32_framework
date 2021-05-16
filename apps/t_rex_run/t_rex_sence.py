import hal_screen
screen_width, screen_height = hal_screen.get_size()
# Sprites
roads = []
barriers = []
clouds = []
t_rexs = []
objects = []

def clear_sence():
    roads.clear()
    barriers.clear()
    clouds.clear()
    t_rexs.clear()
    objects.clear()

def render():
    frame = hal_screen.get_framebuffer()
    frame.fill(0)
    # render Sprites
    for cloud in clouds:
        cloud.draw(frame)
    for road in roads:
        road.draw(frame)
    for barrier in barriers:
        barrier.draw(frame)
    for t_rex in t_rexs:
        t_rex.draw(frame)
    for obj in objects:
        obj.draw(frame)
    hal_screen.refresh()
    pass
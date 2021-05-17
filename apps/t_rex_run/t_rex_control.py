from os import stat
import hal_screen, hal_keypad, gc
import t_rex_sence, t_rex_sprite, t_rex_sfx
from play32sys import app, path
from graphic import framebuf_helper
from utime import ticks_ms, ticks_diff
from uos import urandom
DEFAULT_SPEED = 40
DEFAULT_JUMP_SPEED = 100
DEFAULT_JUMP_GRAVITY = 160
DEFAULT_CLOUD_SPEED = 16
DEFAULT_CLOUD_SPEED_SLOW = 8
# other sprites:
score_sprite = None
gameover_sprite = None
high_score_sprite = None
# status
status = 0 # 0:ready 1:playing 2:gameover
score = 0
high_score = 0
speed = DEFAULT_SPEED # pixels per second
# object
t_rex = None
roads = None
clouds = None
barrier = None

class TRex():
    def __init__(self, t_rex_sprites):
        self.status = 0 # 0:stand 1:walk 2:jump 0xff:crash
        self.templates = t_rex_sprites # 0:stand 1:walk_l 2:walk_r 3:crash
        self.sprite = t_rex_sprites[0].clone()
        self.time_ms = 0
        self.speed = 0
        self.reset_position()
    def reset_position(self):
        x, y, w, h = self.sprite.box
        self.sprite.move_to(0, t_rex_sence.screen_height - h - 1)
    def stand(self):
        self.status = 0
        self.sprite.img = self.templates[0].img
        self.reset_position()
    def walk(self):
        self.status = 1
        self.reset_position()
    def jump(self):
        if self.status == 2:
            return
        self.status = 2
        self.speed = DEFAULT_JUMP_SPEED
        self.sprite.img = self.templates[0].img
        t_rex_sfx.press()
    def crash(self):
        self.status = 0xFF
        self.sprite.img = self.templates[3].img
    def update(self, time_ms):
        self.time_ms += time_ms
        if self.status == 1:
            # 8 steps per second, 125ms per step
            self.sprite.img = self.templates[((self.time_ms // 125) % 2) + 1].img
        elif self.status == 2:
            self.sprite.move(0, -(self.speed * time_ms / 1000))
            self.speed -= time_ms * DEFAULT_JUMP_GRAVITY // 1000
            _x, y, _w, h = self.sprite.box
            if y + h >= t_rex_sence.screen_height - 1:
                self.walk() # jump end
        t_rex_sence.t_rexs.clear()
        t_rex_sence.t_rexs.append(self.sprite)

class Barrier():
    def __init__(self, templates):
        self.templates = templates
        self.barrier_sprites = []
        self.speed = DEFAULT_SPEED # pixel per second
        self.time_ms = 0
        self.next_barrier_ms = 0
    def reset(self):
        self.barrier_sprites.clear()
        self.time_ms = 0
        self.next_barrier_ms = 0
    def get_random_barrier_sprite(self):
        rand = int.from_bytes(urandom(4), 'big') % len(self.templates)
        return self.templates[rand].clone()
    def append_barrier(self):
        x = t_rex_sence.screen_width
        barrier = self.get_random_barrier_sprite()
        _x, _y, _w, h = barrier.box
        y = t_rex_sence.screen_height - h - 1
        barrier.move_to(x, y)
        self.barrier_sprites.append(barrier)
        self.next_barrier()
    def next_barrier(self):
        # next cloud, time: [2, 6]
        during = int.from_bytes(urandom(4), 'big') % 4_000
        during += 2_000
        self.next_barrier_ms = self.time_ms + during
    def set_speed(self, speed):
        self.speed = speed
    def update(self, time_ms):
        self.time_ms += time_ms
        speed = self.speed
        if speed != 0:
            for barrier in self.barrier_sprites:
                barrier.move(-(speed * time_ms / 1000), 0)
        for barrier in self.barrier_sprites:
            x, _y, w, _h = barrier.box
            if x + w <= 0:
                self.barrier_sprites.remove(barrier)
            else:
                break
        if speed != 0 and self.time_ms >= self.next_barrier_ms:
            self.append_barrier()
        elif speed == 0:
            self.next_barrier()
        t_rex_sence.barriers.clear()
        t_rex_sence.barriers.extend(self.barrier_sprites)

class Road():
    def __init__(self, templates):
        self.templates = templates
        self.road_sprites = []
        self.speed = DEFAULT_SPEED # pixel per second
    def get_random_road_sprite(self):
        rand = int.from_bytes(urandom(4), 'big') % len(self.templates)
        return self.templates[rand].clone()
    def get_road_width(self):
        if len(self.road_sprites) > 0:
            last_road = self.road_sprites[-1]
            x, _y, w, _h = last_road.box
            x = x + w
            return x if x > 0 else 0
        else:
            return 0
    def append_road(self):
        x = self.get_road_width()
        road = self.get_random_road_sprite()
        _x, _y, _w, h = road.box
        y = t_rex_sence.screen_height - h
        road.move_to(x, y)
        self.road_sprites.append(road)
    def set_speed(self, speed):
        self.speed = speed
    def update(self, time_ms):
        speed = self.speed
        if speed != 0:
            for road in self.road_sprites:
                road.move(-(speed * time_ms / 1000), 0)
        for road in self.road_sprites:
            x, _y, w, _h = road.box
            if x + w <= 0:
                self.road_sprites.remove(road)
            else:
                break
        while self.get_road_width() <= t_rex_sence.screen_width:
            self.append_road()
        t_rex_sence.roads.clear()
        t_rex_sence.roads.extend(self.road_sprites)

class Cloud():
    def __init__(self, cloud_sprite):
        self.cloud_sprite = cloud_sprite
        _x, _y, _w, h = cloud_sprite.box
        self.cloud_height = h
        self.clouds = []
        self.speed = DEFAULT_CLOUD_SPEED
        self.time_ms = 0
        self.next_cloud_ms = 0
    def reset(self):
        self.clouds.clear()
        self.time_ms = 0
        self.next_cloud_ms = 0
    def append_cloud(self):
        # cloud height: [0, screen_height - 16]
        x = t_rex_sence.screen_width
        y = int.from_bytes(urandom(2), 'big') % (t_rex_sence.screen_height - 16 - self.cloud_height)
        cloud = self.cloud_sprite.clone()
        cloud.move_to(x, y)
        self.clouds.append(cloud)
        self.next_cloud()
    def next_cloud(self):
        # next cloud, time: [1, 10]
        during = int.from_bytes(urandom(4), 'big') % 9_000
        during += 1_000
        self.next_cloud_ms = self.time_ms + during
    def set_speed(self, speed):
        self.speed = speed
    def update(self, time_ms):
        speed = self.speed
        self.time_ms += time_ms
        for cloud in self.clouds:
            cloud.move(-(speed * time_ms / 1000), 0)
            x, _y, w, _h = cloud.box
            if x + w <= 0:
                self.clouds.remove(cloud)
        if speed != 0 and self.time_ms >= self.next_cloud_ms:
            self.append_cloud()
        elif speed == 0:
            self.next_cloud()
        t_rex_sence.clouds.clear()
        t_rex_sence.clouds.extend(self.clouds)

# global function
def _update_global(time_ms):
    global score, speed
    # update score
    score += (speed / 8) * (time_ms / 1000)
    score_sprite.img.fill(0)
    score_sprite.img.text(str(int(score)), 0, 0, t_rex_sprite.COLOR_WHITE)
    # update speed
    speed = speed + (1 * (time_ms / 1000))
    roads.set_speed(speed)
    barrier.set_speed(speed)
    # check collide
    rex_sprite = t_rex.sprite
    for barrier_sprite in barrier.barrier_sprites:
        if t_rex_sprite.is_sprite_collide(rex_sprite, barrier_sprite):
            _game_over()

def _game_over():
    global status, high_score
    status = 2
    t_rex.crash()
    roads.set_speed(0)
    barrier.set_speed(0)
    clouds.set_speed(DEFAULT_CLOUD_SPEED_SLOW)
    t_rex_sence.objects.append(gameover_sprite)
    if score > high_score:
        high_score = score
    t_rex_sfx.crash()

# export function
def init(app_path):
    global score_sprite, gameover_sprite, high_score_sprite
    global t_rex, roads, clouds, barrier
    t_rex_sfx.init(app_path)
    # load sprites
    t_rexs = []
    road_sprites = []
    barrier_sprites = []
    img_dir = path.join(app_path, "img")
    for name in [
        "t_rex_stand.pbm",
        "t_rex_walk_l.pbm",
        "t_rex_walk_r.pbm",
        "t_rex_crash.pbm",
    ]:
        img_path = path.join(img_dir, name)
        sprite = t_rex_sprite.load_sprite(img_path, t_rex_sprite.COLOR_WHITE)
        sprite.key = 0
        t_rexs.append(sprite)
    for name in [
        "road_0.pbm",
        "road_1.pbm",
        "road_2.pbm",
        "road_3.pbm",
        "road_4.pbm",
        "road_5.pbm",
        "road_6.pbm",
        "road_7.pbm",
    ]:
        img_path = path.join(img_dir, name)
        sprite = t_rex_sprite.load_sprite(img_path, t_rex_sprite.get_color_or_white(0xFF, 0x00, 0x00))
        sprite.key = 0
        road_sprites.append(sprite)
    for name in [
        "cactus_high.pbm",
        "cactus_middle.pbm",
        "cactus_low.pbm",
    ]:
        img_path = path.join(img_dir, name)
        sprite = t_rex_sprite.load_sprite(img_path, t_rex_sprite.get_color_or_white(0x00, 0xFF, 0x00))
        sprite.key = 0
        barrier_sprites.append(sprite)
    img_path = path.join(img_dir, "cloud.pbm")
    sprite = t_rex_sprite.load_sprite(img_path, t_rex_sprite.get_color_or_white(0x00, 0x8F, 0xFF))
    sprite.key = 0
    cloud_sprite = sprite
    # other sprites
    score_sprite = t_rex_sprite.new_sprite(t_rex_sence.screen_width, 8)
    score_sprite.key = 0
    gameover_sprite = t_rex_sprite.new_sprite(8*8, 8)
    gameover_sprite.key = 0
    gameover_sprite_x = (t_rex_sence.screen_width - 8*8) // 2
    gameover_sprite.move_to(gameover_sprite_x, 8)
    gameover_sprite.img.text("GameOver", 0, 0, t_rex_sprite.COLOR_WHITE)
    high_score_sprite = t_rex_sprite.new_sprite(t_rex_sence.screen_width, 16)
    high_score_sprite.key = 0
    high_score_sprite.img.text("HIGH:", 0, 0, t_rex_sprite.COLOR_WHITE)
    # object
    t_rex = TRex(t_rexs)
    roads = Road(road_sprites)
    clouds = Cloud(cloud_sprite)
    barrier = Barrier(barrier_sprites)

def ready():
    global status, speed
    # update high score
    high_score_sprite.img.fill_rect(0, 8, t_rex_sence.screen_width, 8, 0)
    high_score_sprite.img.text(str(int(high_score)), 0, 8, t_rex_sprite.COLOR_WHITE)
    # reset status
    status = 0
    speed = DEFAULT_SPEED
    t_rex.walk()
    roads.set_speed(speed)
    barrier.set_speed(0)
    barrier.reset()
    clouds.set_speed(DEFAULT_CLOUD_SPEED)
    clouds.reset()
    # put into sence
    t_rex_sence.objects.clear()
    t_rex_sence.objects.append(high_score_sprite)

def start():
    global status, speed, score
    status = 1
    speed = DEFAULT_SPEED
    score = 0
    t_rex.walk()
    roads.set_speed(speed)
    barrier.set_speed(speed)
    t_rex_sence.objects.clear()
    t_rex_sence.objects.append(score_sprite)

def main_loop():
    last_ticks = ticks_ms()
    while True:
        now = ticks_ms()
        time_ms = ticks_diff(now, last_ticks)
        last_ticks = now
        for event in hal_keypad.get_key_event():
            event_type, key = hal_keypad.parse_key_event(event)
            if event_type == hal_keypad.EVENT_KEY_PRESS:
                if key == hal_keypad.KEY_A:
                    if status == 0:
                        start()
                    elif status == 1:
                        t_rex.jump()
                    elif status == 2:
                        ready()
                elif key == hal_keypad.KEY_B:
                    if status == 1:
                        _game_over()
                    elif status == 2:
                        app.reset_and_run_app("")
        barrier.update(time_ms)
        roads.update(time_ms)
        t_rex.update(time_ms)
        clouds.update(time_ms)
        if status == 1:
            _update_global(time_ms)
        t_rex_sence.render()
        gc.collect()

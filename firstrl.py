import libtcodpy as tcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

LIMIT_FPS = 20

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

FOV_ALGO = 0 #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

MAX_ROOM_MONSTERS = 3

color_dark_wall = tcod.Color(0, 0, 100)
color_light_wall = tcod.Color(130, 110, 50)
color_dark_ground = tcod.Color(50, 50, 150)
color_light_ground = tcod.Color(200, 180, 50)

class Tile:
	#a tile of the map
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
		self.explored = False

		#if a tile is blocked, it also blocks sight by default
		block_sight = blocked if block_sight is None else None
		self.block_sight = block_sight

class Object:
	def __init__(self, x, y, char, name, color, blocks=False):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks = blocks

	def move(self, dx, dy):
		if not is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy

	def draw(self):
		if tcod.map_is_in_fov(fov_map, self.x, self.y):
			#set the color and then draw the character that represents this object at its position
			tcod.console_set_default_foreground(con, self.color)
			tcod.console_put_char(con, self.x, self.y, self.char, tcod.BKGND_NONE)

	def clear(self):
		#erase the character
		tcod.console_put_char(con, self.x, self.y, ' ', tcod.BKGND_NONE)

def is_blocked(x, y):
	#testing the map tile first
	if map[x][y].blocked:
		return True

	#testing for blocking objects now
	for object in objects:
		if object.blocks and object.x == x and object.y == y:
			return True

	return False

def place_objects(room):
	num_monsters = tcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
	#chooses a random number of monsters

	for i in range(num_monsters):
		x = tcod.random_get_int(0, room.x1, room.x2)
		y = tcod.random_get_int(0, room.y1, room.y2)

		if not is_blocked(x, y):
			if tcod.random_get_int(0, 0, 100) < 80:
				#creates an orc
				monster = Object(x, y, 'o', 'orc', tcod.desaturated_green,
					blocks=True)
			else:
				#creates a troll
				monster = Object(x, y, 'T', 'troll', tcod.darker_green,
					blocks=True)

			objects.append(monster)
class Rect:
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self. y2) // 2
		return (center_x, center_y)

	def intersect(self, other):

		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
			self.y1 <= other.y2 and self.y2 >= other.y1)

def create_room(room):
	global map

	for x in range(room.x1 + 1, room.x2 ):
		for y in range(room.y1 + 1, room.y2):
			map[x][y].blocked = False
			map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
	global map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
	global map

	for y in range(min(y1, y2), max(y1, y2) + 1):
		map[x][y].blocked = False
		map[x][y].block_sight = False

def make_map():
	global map

	map = [
		[Tile(True) for y in range(MAP_HEIGHT)]
		for x in range(MAP_WIDTH)
	]
	
	rooms = []
	num_rooms = 0

	for r in range(MAX_ROOMS):
		w = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = tcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)

		x = tcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
		y = tcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

		new_room = Rect(x, y, w, h)

		failed = False
		for other_room in rooms:
			if new_room.intersect(other_room):
				failed = True
				break
		if not failed:
			#room is valid, no intersections

			create_room(new_room)

			(new_x, new_y) = new_room.center()

			if num_rooms ==0:
				player.x = new_x
				player.y = new_y
		
			else:
				#all rooms after the first:
				#connecting them to the previous with a tunnel

				#center coords of previous room
				(prev_x, prev_y) = rooms[num_rooms-1].center()

				#get a random bool to decide if vertical or
				#horizontal tunnel gets created first
				if tcod.random_get_int(0, 0, 1) == 1:
					#first horizontal tunnel, then vertical
					create_h_tunnel(prev_x, new_x, prev_y)
					create_v_tunnel(prev_y, new_y, new_x)
				else:
					#first vertical tunnel, then horizontal
					create_v_tunnel(prev_y, new_y, prev_x)
					create_h_tunnel(prev_x, new_x, new_y)

			place_objects(new_room)
			rooms.append(new_room)
			num_rooms += 1

def handle_keys():
	global fov_recompute

	key = tcod.console_check_for_keypress()
	if key.vk == tcod.KEY_ENTER and key.lalt:
		#Alt+ENTER toggles Fullscreen
		tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

	elif key.vk == tcod.KEY_ESCAPE:
		return True
		#Exit game

	global player_x, player_y

	if tcod.console_is_key_pressed(tcod.KEY_UP):
		player.move(0, -1)
		fov_recompute = True

	elif tcod.console_is_key_pressed(tcod.KEY_DOWN):
		player.move(0, +1)
		fov_recompute = True
		
	elif tcod.console_is_key_pressed(tcod.KEY_LEFT):
		player.move(-1, 0)
		fov_recompute = True
		
	elif tcod.console_is_key_pressed(tcod.KEY_RIGHT):
		player.move(+1, 0)
		fov_recompute = True
		

def render_all():
	global fov_map, color_dark_wall, color_light_wall
	global color_dark_ground, color_light_ground
	global fov_recompute

	if fov_recompute:

		fov_recompute = False
		tcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				visible = tcod.map_is_in_fov(fov_map, x, y)
				wall = map[x][y].block_sight
				if not visible:
					if map[x][y].explored:
						if wall:
							tcod.console_set_char_background(con, x, y, color_dark_wall, tcod.BKGND_SET)
						else:
							tcod.console_set_char_background(con, x, y, color_dark_ground, tcod.BKGND_SET)
				else:
					if wall:
						tcod.console_set_char_background(con, x, y, color_light_wall, tcod.BKGND_SET)
					else: tcod.console_set_char_background(con, x, y, color_light_ground, tcod.BKGND_SET)
					map[x][y].explored = True
	for object in objects:
		object.draw()

	tcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


font_path = 'arial10x10.png'
font_flags = tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD
tcod.console_set_custom_font(font_path, font_flags)

window_title = 'Py3 Rogue'
fullscreen = False
tcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, window_title, fullscreen)
con = tcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
tcod.sys_set_fps(LIMIT_FPS)

player = Object(0, 0, '@', 'player', tcod.white, blocks=True)
objects = [player]

make_map()

fov_recompute = True
fov_map = tcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
	for x in range(MAP_WIDTH):
		tcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

while not tcod.console_is_window_closed():

	render_all()
	#renders thescreen

	tcod.console_flush()

	for object in objects:
		object.clear()
	#erases all the old chars


	exit = handle_keys()

	if exit:
		break
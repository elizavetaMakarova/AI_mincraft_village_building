import random

import mapUtils
import interfaceUtils
from worldLoader import WorldSlice

# x position, z position, x size, z size
area = (0, 0, 128, 128) # default build area

floor_materials = ["birch_planks","oak_planks","dark_oak_planks"]
wall_materials = ["birch_planks","oak_planks","dark_oak_planks","cobblestone","mossy_cobblestone"]
door_types = ["birch_door","oak_door","acacia_door","dark_oak_door",
         "spruce_door","crimson_door","warped_door"]
roof_materials = ["stripped_birch_log","acacia_log","oak_log","birch_log",
                  "dark_oak_log","spruce_log","bricks"]
directions = ["north","south","west","east"]
beds = ["yellow_bed","green_bed","red_bed","pink_bed"]
flora = ["sunflower","lilac","rose_bush","peony"]

# Do we send blocks in batches to speed up the generation process?
USE_BATCHING = True

# see if a build area has been specified
# you can set a build area in minecraft using the /setbuildarea command
buildArea = interfaceUtils.requestBuildArea()
doors=[]
if buildArea != -1:
    x1 = buildArea["xFrom"]
    z1 = buildArea["zFrom"]
    x2 = buildArea["xTo"]
    z2 = buildArea["zTo"]
    # print(buildArea)
    area = (x1, z1, x2-x1, z2-z1)

print("Build area is at position %s, %s with size %s, %s" % area)

# load the world data
# this uses the /chunks endpoint in the background
worldSlice = WorldSlice(area)
# heightmap = worldSlice.heightmaps["MOTION_BLOCKING"]
# heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
# heightmap = worldSlice.heightmaps["OCEAN_FLOOR"]
# heightmap = worldSlice.heightmaps["WORLD_SURFACE"]

# caclulate a heightmap that ignores trees:
heightmap = mapUtils.calcGoodHeightmap(worldSlice)

# show the heightmap as an image
# mapUtils.visualize(heightmap, title="heightmap")

# define a function for easier heightmap access
# heightmap coordinates are not equal to world coordinates!
def heightAt(x, z):
  return heightmap[(x - area[0], z - area[1])]

# a wrapper function for setting blocks
def setBlock(x, y, z, block):
    if USE_BATCHING:
        interfaceUtils.placeBlockBatched(x, y, z, block, 100)
    else:
        interfaceUtils.setBlock(x, y, z, block)

def landscaping(x1,y1,z1,x2,y2,z2):
    for y in range(y1-1, y2+50):
        for x in range(x1-6, x2+6):
            for z in range(z1-6, z2+6):
                    setBlock(x, y, z, "air")
    for x in range(x1-6, x2+6):
        for z in range(z1-6, z2+6):
            setBlock(x, y1, z, "grass_block")
    for x in range(x1-6, x2+6):
        num1 = random.randint(0,101)
        num2 = random.randint(0,101)
        if num1 < 30:
          setBlock(x,y1,z1-6,"air")
        if num2 < 20:
          setBlock(x,y1,z2+5,"air")
    for z in range(z1-6,z2+6):
        num1 = random.randint(0,101)
        num2 = random.randint(0,101)
        if num1 < 20:
          setBlock(x1-6,y1,z,"air")
        if num2 < 30:
          setBlock(x2+5,y1,z,"air")
    for x in range(x1-6,x2+6):
      for z in range(z1-6,z2+6):
        grass_chance = random.randint(0,101)
        if grass_chance < 40:
          setBlock(x,y1+1,z,"tall_grass[half=lower]")
          setBlock(x,y1+2,z,"tall_grass[half=upper]")

#  get all doors
#  select a pair of doors
#  find which door has bigger coordinates 
#  set intersaction point using doors coordinates 
#  check if the path will be overlaping with one of the houses
#  if not set biom appropriate blocks from door to intersection and from intersection to door two
#  if path points are too far from each other in height create a ladder

def pathFinding(housePaths, doors):
  intersection = []
  previousCoordnites = []
  for door in doors:
    for door2 in doors:
      intersection = [door[0], door2[1]]
      if (door[1]>intersection[1]):
        big = door[1]
        small = intersection[1]
      else:
        big = intersection[1]
        small = door[1]

      if (intersection[0]>door2[0]):
        big1 = intersection[0]
        small1 = door2[0]
      else:
        big1 = door2[0]
        small1 = intersection[0]
      overlapZ = False
      for z in range(small, big+1):
        for house in housePaths:
          if rectanglesOverlap(house,[door[0], z, 1,1], 0):
            overlapZ = True
      overlapX = False
      for x in range(small1, big1):
        for house in housePaths:
          if rectanglesOverlap(house, [x, door2[1], 1, 1], 0):
            overlapX = True
      for z in range(small, big+1):
        if not overlapX and not overlapZ:
          if len(previousCoordnites) != 0:
            if previousCoordnites[0][1] - (heightAt(door[0], z)-1)>1:
              createStairs(previousCoordnites[0], [door[0], heightAt(door[0], z)-1, z])
          setBiomBlock(door[0], heightAt(door[0], z)-1, z)
          setBiomBlock(door[0]+1, heightAt(door[0]+1, z)-1, z)
          setBiomBlock(door[0]-1, heightAt(door[0]-1, z)-1, z)
          previousCoordnites = [[door[0], heightAt(door[0], z)-1, z], [door[0]+1, heightAt(door[0]+1, z)-1, z], [door[0]-1, heightAt(door[0]-1, z)-1, z]]
      previousCoordnites = []
      for x in range(small1, big1):
        if not overlapX and not overlapZ:
          if len(previousCoordnites) != 0 :
            if previousCoordnites[2][1] - (heightAt(x,door2[1]+1)-1)>1:
              createStairs(previousCoordnites[2], [x, heightAt(x,door2[1]+1)-1, door2[1]+1])
          setBiomBlock(x, heightAt(x, door2[1])-1, door2[1])
          setBiomBlock(x, heightAt(x, door2[1]+2)-1, door2[1]+2)
          setBiomBlock(x, heightAt(x,door2[1]+1)-1, door2[1]+1)
          previousCoordnites = [[x, heightAt(x, door2[1])-1, door2[1]], [x, heightAt(x, door2[1]+2)-1, door2[1]+2], [x, heightAt(x,door2[1]+1)-1, door2[1]+1]]

#  get hight point and low point
#  select the facing direction
#  create ladder

def createStairs(prev, over):
  if prev[1] > over[1]:
    hight = prev
    low = over
  else:
    hight = over
    low = prev
  if prev[0] != over[0]:
    block = "ladder[facing=north]"
  else: 
    block = "ladder[facing=south]"
  for y in range(low[1]+1, hight[1]+1):
      setBlock(hight[0],y,hight[2], block)
      
#  get already existing block
#  set appropriate block
def setBiomBlock(x,y,z):
  block = interfaceUtils.getBlock(x,y,z)
  if(block == "minecraft:water" or block == "oak_planks"):
    setBlock(x,y,z, "oak_planks")
  elif (block == "minecraft:sand" or block == "red_sandstone"):
    setBlock(x,y,z, "red_sandstone")
  elif(block == "minecraft:stone" or block == "infested_stone_bricks"):
    setBlock(x,y,z, "infested_stone_bricks")
  else: setBlock(x,y,z, "grass_path")

#  check if coordinates intersacting with other structure on the map 
#  if not check if its not on the path
#  add light to the list of all structures
#  if not create a light
def streetLight(housePaths,x,z):
  y = heightAt(x, z)
  for house in housePaths:
    if not rectanglesOverlap(house, [x-1, z-1, 3, 3], 0):
      houses.append( [x-1, z-1, 3, 3])
      block = interfaceUtils.getBlock(x,y-1,z)
      if (block == "oak_planks" or block == "red_sandstone" or block == "infested_stone_bricks" or block == "grass_path"):
        print("nothing")
      else:  
        setBlock(x,y-1,z,"grass_block")            
        setBlock(x,y,z, "dark_oak_fence")
        setBlock(x,y+1,z, "dark_oak_fence")
        setBlock(x,y+2,z, "dark_oak_fence")
        setBlock(x,y+3,z, "glowstone")
    
#  check if coordinates intersacting with other structure on the map 
#  add barrels to the list of all structures
#  create barrels using random seed for direction

def barrels(housePaths,x,z, seed):
  y = heightAt(x, z)
  for house in housePaths:
    if not rectanglesOverlap(house, [x-1, z-1, 3, 3], 0):
      houses.append( [x-1, z-1, 3, 3])
      setBlock(x,y,z, "barrel[facing="+directions[seed]+"]")
      setBlock(x+1,y,z, "barrel[facing="+directions[seed]+"]")
      setBlock(x,y,z+1, "barrel[facing="+directions[seed]+"]")
      setBlock(x,y+1,z+1, "barrel[facing=up]")


def greenHouse(x1,y1,z1,x2,y2,z2):
  # ground
  for x in range(x1, x2):
        for z in range(z1, z2):
            setBlock(x, y1, z, "farmland")
  # greenhouse foundation/base frame
  for x in range(x2-x1):
    setBlock(x1+x,y1+1,z1,"dark_oak_log")
    setBlock(x1+x,y1+1,z2-1,"dark_oak_log")
  for z in range(z2-z1):
    setBlock(x1,y1+1,z1+z,"dark_oak_log")
    setBlock(x2-1,y1+1,z1+z,"dark_oak_log")
  # walls
  for y in range(y1+2, y2):
        for x in range(x1 + 1, x2 - 1):
            setBlock(x, y, z1, "glass")
            setBlock(x, y, z2 - 1, "glass")
        for z in range(z1 + 1, z2 - 1):
            setBlock(x1, y, z, "glass")
            setBlock(x2 - 1, y, z, "glass")
  # corners
  for dx in range(2):
      for dz in range(2):
          x = x1 + dx * (x2 - x1 - 1)
          z = z1 + dz * (z2 - z1 - 1)
          for y in range(y1, y2):
              setBlock(x, y, z, "dark_oak_log")
  # clear interior (twice just in case blocks fall down while building)
  for i in range(2):
    for y in range(y1 + 1, y2):
        for x in range(x1+1, x2-1):
            for z in range(z1+1, z2-1):
                setBlock(x, y, z, "air")
  # flowers inside
  for x in range(x1+1, x2-2):
      for z in range(z1+1, z2-1):
        indx = random.randint(0,len(flora)-1)        
        setBlock(x, y1+1, z, flora[indx]+"[half=lower]")
        setBlock(x, y1+2, z, flora[indx]+"[half=upper]")
  # roof
  if x2-x1 < z2-z1:
      for i in range(0, x2-x1, 2):
          halfI = int(i/2)
          for x in range(x1 + halfI, x2 - halfI):
              for z in range(z1, z2):
                if z % 2 == 0:
                  setBlock(x, y2 + halfI, z, "dark_oak_log")
                else:
                  setBlock(x, y2 + halfI, z, "glass")
      for z in range(1,z2-z1,2):
        setBlock((x2-x1)//2+x1,y2,z1+z,"lantern[hanging=true]")

  else:
      # same as above but with x and z swapped
      for i in range(0, z2-z1, 2):
          halfI = int(i/2)
          for z in range(z1 + halfI, z2 - halfI):
              for x in range(x1, x2):
                if x % 2 == 0:
                  setBlock(x, y2 + halfI, z, "dark_oak_log")
                else:
                  setBlock(x, y2 + halfI, z, "glass")
      for x in range(1,x2-x1,2):
        setBlock(x1+x,y2,(z2-z1)//2+z1,"lantern[hanging=true]")
  # upper frame 
  for x in range(x2-x1):
      setBlock(x1+x,y2,z1,"dark_oak_log")
      setBlock(x1+x,y2,z2-1,"dark_oak_log")
  for z in range(z2-z1):
      setBlock(x1,y2,z1+z,"dark_oak_log")
      setBlock(x2-1,y2,z1+z,"dark_oak_log")
  # door
  door_dir = random.randint(0,len(directions)-1)
  if directions[door_dir] == "north":
    setBlock((x2-x1)//2+x1, y1+1, z2-1,"jungle_door[facing=north,half=lower]")
    setBlock((x2-x1)//2+x1, y1+2, z2-1,"jungle_door[facing=north,half=upper]")
    doors.append([(x2-x1)//2+x1, z2])
  elif directions[door_dir] == "south":
    setBlock((x2-x1)//2+x1, y1+1, z1,"jungle_door[facing=south,half=lower]")
    setBlock((x2-x1)//2+x1, y1+2, z1,"jungle_door[facing=south,half=upper]")
    doors.append([(x2-x1)//2+x1, z1-3])
  elif directions[door_dir] == "west":
    setBlock(x2-1, y1+1, (z2-z1)//2+z1,"jungle_door[facing=west,half=lower]")  
    setBlock(x2-1, y1+2, (z2-z1)//2+z1,"jungle_door[facing=west,half=upper]") 
    doors.append([x2+1,(z2-z1)//2+z1])
  else:
    setBlock(x1, y1+1, (z2-z1)//2+z1,"jungle_door[facing=east,half=lower]")  
    setBlock(x1, y1+2, (z2-z1)//2+z1,"jungle_door[facing=east,half=upper]") 
    doors.append([x1,(z2-z1)//2+z1])

#  creat random seed for the bed generation
#  create a roof
#  clear space inside 
#  create floor
#  set bed
#  set door
#  create windows

def buildHobbitHouse(x1, y1, z1, x2, y2, z2):
    bedsRandom = random.randint(0,len(beds)-1)
    # roof
    for i in range(0, x2-x1, 2):
      halfI = int(i/2)
      for x in range(x1 + halfI, x2 - halfI):
        for z in range(z1, z2):
          setBlock(x, y1 + halfI+1, z, "dark_oak_log")
    # space inside
    for i in range(0, x2-x1, 2):
      halfI = int(i/2)
      for x in range(x1 + halfI, x2 - halfI):
        for z in range(z1+1, z2-1):
          setBlock(x, y1 + halfI, z, "air")
    # floor
    for x in range(x1, x2):
        for z in range(z1, z2):
            setBlock(x, y1, z, "cobblestone")
    setBlock(x1+1, y1 + 1, z1+1, beds[bedsRandom]+"[facing=north, part=head]")
    setBlock(x1+1, y1 + 1, z1+2, beds[bedsRandom]+"[facing=north, part=foot]")

    # door
    setBlock((x2-x1)//2+x1, y1+1, z2-1, "dark_oak_door[half=lower]")
    setBlock((x2-x1)//2+x1, y1+2, z2-1, "dark_oak_door[half=upper]")
    for i in range(0, x2-x1, 2):
      halfI = int(i/2)
      for x in range(x1 + halfI, x2 - halfI):
        for z in range(z2, z2+3):
          setBlock(x, y1 + halfI+1, z, "air")
    doors.append([(x2-x1)//2+x1, z2])
    if x2-x1 >= 9:
        setBlock(((x2-x1)//2+x1)+2,y1+2,z2-1, "glass_pane")
        setBlock(((x2-x1)//2+x1)-2,y1+2,z2-1, "glass_pane")
    setBlock(x1-3,y1+1,(z2-z1)//2+z1,"campfire")

# function that builds a big house
def buildBigHouse(x1, y1, z1, x2, y2, z2):
    floor = random.randint(0,len(floor_materials)-1)
    wall = random.randint(0,len(wall_materials)-1)
    roof = random.randint(0,len(roof_materials)-1)
    door = random.randint(0,len(door_types)-1)
    door_dir = random.randint(0,len(directions)-1)
    bedsRandom = random.randint(0,len(beds)-1)

    # floor
    for x in range(x1, x2):
        for z in range(z1, z2):
            setBlock(x, y1, z, floor_materials[floor])
    # walls
    for y in range(y1+1, y2):
        for x in range(x1 + 1, x2 - 1):
            setBlock(x, y, z1, wall_materials[wall])
            setBlock(x, y, z2 - 1, wall_materials[wall])
        for z in range(z1 + 1, z2 - 1):
            setBlock(x1, y, z, wall_materials[wall])
            setBlock(x2 - 1, y, z, wall_materials[wall])
    # corners
    for dx in range(2):
        for dz in range(2):
            x = x1 + dx * (x2 - x1 - 1)
            z = z1 + dz * (z2 - z1 - 1)
            for y in range(y1, y2):
                setBlock(x, y, z, wall_materials[wall])
    # clear interior
    for y in range(y1 + 1, y2):
        for x in range(x1+1, x2-1):
            for z in range(z1+1, z2-1):
                setBlock(x, y, z, "air")
    # interior
    setBlock(x1+1, y1 + 1, z1+1, beds[bedsRandom]+"[facing=north, part=head]")
    setBlock(x1+1, y1 + 1, z1+2, beds[bedsRandom]+"[facing=north, part=foot]")
    setBlock(x1+1, y2-1, z1+1, "glowstone")
    setBlock(x2-2, y2-1, z1+1, "glowstone")


    for x in range(x1+1, x2-1):
      setBlock(x, y, z2-2, "bookshelf")

    # roof
    if x2-x1 < z2-z1:
        for i in range(0, x2-x1, 2):
            halfI = int(i/2)
            for x in range(x1 + halfI, x2 - halfI):
                for z in range(z1, z2):
                    setBlock(x, y2 + halfI, z, roof_materials[roof])
    else:
        # same as above but with x and z swapped
        for i in range(0, z2-z1, 2):
            halfI = int(i/2)
            for z in range(z1 + halfI, z2 - halfI):
                for x in range(x1, x2):
                    setBlock(x, y2 + halfI, z, roof_materials[roof])
        # door and flower beds 
    indx = random.randint(0,len(flora)-1)
    flower = flora[indx]
    if directions[door_dir] == "north":
      setBlock((x2-x1)//2+x1, y1+1, z2-1, door_types[door]+"[facing=north,half=lower]")
      setBlock((x2-x1)//2+x1, y1+2, z2-1, door_types[door]+"[facing=north,half=upper]")
      doors.append([(x2-x1)//2+x1, z2])
      setBlock(x1-1,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-2,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2+1,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-1,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-2,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2+1,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      for z in range(z1+(z2-z1)//4,(z1+3*(z2-z1)//4)+1):
        setBlock(x2+2,y1+1,z,"mossy_cobblestone")
        setBlock(x1-3,y1+1,z,"mossy_cobblestone")
      for z in range((z1+(z2-z1)//4)+1,z1+3*(z2-z1)//4):
        setBlock(x2,y1,z,"farmland")
        setBlock(x2,y1+1,z,flower+"[half=lower]")
        setBlock(x2,y1+2,z,flower+"[half=upper]")
        setBlock(x2+1,y1,z,"farmland")
        setBlock(x2+1,y1+1,z,flower+"[half=lower]")
        setBlock(x2+1,y1+2,z,flower+"[half=upper]")
        setBlock(x1-1,y1,z,"farmland")
        setBlock(x1-1,y1+1,z,flower+"[half=lower]")
        setBlock(x1-1,y1+2,z,flower+"[half=upper]")
        setBlock(x1-2,y1,z,"farmland")
        setBlock(x1-2,y1+1,z,flower+"[half=lower]")
        setBlock(x1-2,y1+1,z,flower+"[half=upper]")     
    elif directions[door_dir] == "south":
      setBlock((x2-x1)//2+x1, y1+1, z1, door_types[door]+"[facing=south,half=lower]")
      setBlock((x2-x1)//2+x1, y1+2, z1, door_types[door]+"[facing=south,half=upper]")
      doors.append([(x2-x1)//2+x1, z1-3])
      setBlock(x1-1,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-2,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2+1,y1+1,z1+(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-1,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x1-2,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      setBlock(x2+1,y1+1,z1+3*(z2-z1)//4,"mossy_cobblestone")
      for z in range(z1+(z2-z1)//4,(z1+3*(z2-z1)//4)+1):
        setBlock(x2+2,y1+1,z,"mossy_cobblestone")
        setBlock(x1-3,y1+1,z,"mossy_cobblestone")
      for z in range((z1+(z2-z1)//4)+1,z1+3*(z2-z1)//4):
        setBlock(x2,y1,z,"farmland")
        setBlock(x2,y1+1,z,flower+"[half=lower]")
        setBlock(x2,y1+2,z,flower+"[half=upper]")
        setBlock(x2+1,y1,z,"farmland")
        setBlock(x2+1,y1+1,z,flower+"[half=lower]")
        setBlock(x2+1,y1+2,z,flower+"[half=upper]")
        setBlock(x1-1,y1,z,"farmland")
        setBlock(x1-1,y1+1,z,flower+"[half=lower]")
        setBlock(x1-1,y1+2,z,flower+"[half=upper]")
        setBlock(x1-2,y1,z,"farmland")
        setBlock(x1-2,y1+1,z,flower+"[half=lower]")
        setBlock(x1-2,y1+2,z,flower+"[half=upper]")
    elif directions[door_dir] == "west":
      setBlock(x2-1, y1+1, (z2-z1)//2+z1, door_types[door]+"[facing=west,half=lower]")  
      setBlock(x2-1, y1+2, (z2-z1)//2+z1, door_types[door]+"[facing=west,half=upper]") 
      doors.append([x2+1,(z2-z1)//2+z1])
      setBlock(x1+(x2-x1)//4,y1+1,z1-1,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z2,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z1-2,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z2+1,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z1-1,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z2,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z1-2,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z2+1,"mossy_cobblestone")
      for x in range(x1+(x2-x1)//4,(x1+3*(x2-x1)//4)+1):
        setBlock(x,y1+1,z1-3,"mossy_cobblestone")
        setBlock(x,y1+1,z2+2,"mossy_cobblestone")
      for x in range((x1+(x2-x1)//4)+1,(x1+3*(x2-x1)//4)):
        setBlock(x,y1,z1-1,"farmland")
        setBlock(x,y1+1,z1-1,flower+"[half=lower]")
        setBlock(x,y1+2,z1-1,flower+"[half=upper]")
        setBlock(x,y1,z1-2,"farmland")
        setBlock(x,y1+1,z1-2,flower+"[half=lower]")
        setBlock(x,y1+2,z1-2,flower+"[half=upper]")
        setBlock(x,y1,z2,"farmland")
        setBlock(x,y1+1,z2,flower+"[half=lower]")
        setBlock(x,y1+2,z2,flower+"[half=upper]")
        setBlock(x,y1,z2+1,"farmland")
        setBlock(x,y1+1,z2+1,flower+"[half=lower]")
        setBlock(x,y1+2,z2+1,flower+"[half=upper]")
    else:
      setBlock(x1, y1+1, (z2-z1)//2+z1, door_types[door]+"[facing=east,half=lower]")  
      setBlock(x1, y1+2, (z2-z1)//2+z1, door_types[door]+"[facing=east,half=upper]") 
      doors.append([x1,(z2-z1)//2+z1])
      setBlock(x1+(x2-x1)//4,y1+1,z1-1,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z2,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z1-2,"mossy_cobblestone")
      setBlock(x1+(x2-x1)//4,y1+1,z2+1,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z1-1,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z2,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z1-2,"mossy_cobblestone")
      setBlock(x1+3*(x2-x1)//4,y1+1,z2+1,"mossy_cobblestone")
      for x in range(x1+(x2-x1)//4,(x1+3*(x2-x1)//4)+1):
        setBlock(x,y1+1,z1-3,"mossy_cobblestone")
        setBlock(x,y1+1,z2+2,"mossy_cobblestone")
      for x in range((x1+(x2-x1)//4)+1,(x1+3*(x2-x1)//4)):
        setBlock(x,y1,z1-1,"farmland")
        setBlock(x,y1+1,z1-1,flower+"[half=lower]")
        setBlock(x,y1+2,z1-1,flower+"[half=upper]")
        setBlock(x,y1,z1-2,"farmland")
        setBlock(x,y1+1,z1-2,flower+"[half=lower]")
        setBlock(x,y1+2,z1-2,flower+"[half=upper]")
        setBlock(x,y1,z2,"farmland")
        setBlock(x,y1+1,z2,flower+"[half=lower]")
        setBlock(x,y1+2,z2,flower+"[half=upper]")
        setBlock(x,y1,z2+1,"farmland")
        setBlock(x,y1+1,z2+1,flower+"[half=lower]")
        setBlock(x,y1+2,z2+1,flower+"[half=upper]")
    
    # windows to the left and right of the door 
    if x2-x1 >= 7 and x2-x1 < 9 and y2-y1 >= 3:
        setBlock(((x2-x1)//2+x1)+2,y1+2,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)-2,y1+2,z2-1, "glass")
    if x2-x1 >= 9 and y2-y1 >= 4:
        setBlock(((x2-x1)//2+x1)+3,y1+2,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)+2,y1+3,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)+3,y1+3,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)-2,y1+3,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)-3,y1+2,z2-1, "glass")
        setBlock(((x2-x1)//2+x1)-3,y1+3,z2-1, "glass")
    # side house windows 
    setBlock((x2-1),(y2-y1)//2+y1,(z2-z1)//3+z1, "glass")
    setBlock((x2-1),((y2-y1)//2+y1)+1,(z2-z1)//3+z1, "glass")
    setBlock((x2-1),(y2-y1)//2+y1,2*(z2-z1)//3+z1, "glass")
    setBlock((x2-1),((y2-y1)//2+y1)+1,2*(z2-z1)//3+z1, "glass")
    setBlock((x1),(y2-y1)//2+y1,(z2-z1)//3+z1, "glass")
    setBlock((x1),((y2-y1)//2+y1)+1,(z2-z1)//3+z1, "glass")
    setBlock((x1),(y2-y1)//2+y1,2*(z2-z1)//3+z1, "glass")
    setBlock((x1),((y2-y1)//2+y1)+1,2*(z2-z1)//3+z1, "glass")

# remember the houses to avoid overlaps
def rectanglesOverlap(r1, r2, boundary):
    if (r1[0]>=r2[0]+r2[2]+boundary) or (r1[0]+r1[2]+boundary<=r2[0]) or (r1[1]+r1[3]+boundary<=r2[1]) or (r1[1]>=r2[1]+r2[3]+boundary):
        return False
    else:
        return True

houses = []
for i in range(3):
    houseSizeX = random.randrange(5,25)
    houseSizeZ = random.randrange(5,25)
    houseX = random.randrange(area[0] + houseSizeX + 1, area[0] + area[2] - houseSizeX - 1)
    houseZ = random.randrange(area[1] + houseSizeZ + 1, area[1] + area[3] - houseSizeZ - 1)
    houseRect = (houseX, houseZ, houseSizeX, houseSizeZ)

    overlapsExisting = False
    for house in houses:
        if rectanglesOverlap(houseRect, house, 10):
            overlapsExisting = True
            break
    
    if not overlapsExisting:
        houses.append(houseRect)
        print("building house at %i, %i with size %i,%i" % houseRect)

        houseY = min(
            heightAt(houseX, houseZ),
            heightAt(houseX + houseSizeX - 1, houseZ),
            heightAt(houseX, houseZ + houseSizeZ - 1),
            heightAt(houseX + houseSizeX - 1, houseZ + houseSizeZ - 1)
        ) - 1
        houseSizeY = random.randrange(4,7)
        landscaping(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)
        buildBigHouse(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)

for i in range(2):
    houseSizeX = random.randrange(5,20)
    houseSizeZ = random.randrange(5,20)
    houseX = random.randrange(area[0] + houseSizeX + 1, area[0] + area[2] - houseSizeX - 1)
    houseZ = random.randrange(area[1] + houseSizeZ + 1, area[1] + area[3] - houseSizeZ - 1)
    houseRect = (houseX, houseZ, houseSizeX, houseSizeZ)

    overlapsExisting = False
    for house in houses:
        if rectanglesOverlap(houseRect, house, 10):
            overlapsExisting = True
            break
    
    if not overlapsExisting:
        houses.append(houseRect)
        print("building hobbit house at %i, %i with size %i,%i" % houseRect)

        houseY = min(
            heightAt(houseX, houseZ),
            heightAt(houseX + houseSizeX - 1, houseZ),
            heightAt(houseX, houseZ + houseSizeZ - 1),
            heightAt(houseX + houseSizeX - 1, houseZ + houseSizeZ - 1)
        ) - 1
        houseSizeY = random.randrange(4,7)
        landscaping(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)
        buildHobbitHouse(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)
         
for i in range(3):
    houseSizeX = random.randrange(5,20)
    houseSizeZ = random.randrange(5,20)
    houseX = random.randrange(area[0] + houseSizeX + 1, area[0] + area[2] - houseSizeX - 1)
    houseZ = random.randrange(area[1] + houseSizeZ + 1, area[1] + area[3] - houseSizeZ - 1)
    houseRect = (houseX, houseZ, houseSizeX, houseSizeZ)

    overlapsExisting = False
    for house in houses:
        if rectanglesOverlap(houseRect, house, 10):
            overlapsExisting = True
            break
    
    if not overlapsExisting:
        houses.append(houseRect)
        print("building greenhouse at %i, %i with size %i,%i" % houseRect)

        houseY = min(
            heightAt(houseX, houseZ),
            heightAt(houseX + houseSizeX - 1, houseZ),
            heightAt(houseX, houseZ + houseSizeZ - 1),
            heightAt(houseX + houseSizeX - 1, houseZ + houseSizeZ - 1)
        ) - 1
        houseSizeY = random.randrange(4,7)
        landscaping(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)
        greenHouse(houseX, houseY, houseZ, houseX + houseSizeX, houseY + houseSizeY, houseZ + houseSizeZ)

         
newWorldSlice = WorldSlice(area)
heightmap = mapUtils.calcGoodHeightmap(newWorldSlice)
pathFinding(houses, doors)

for i in range(10):
    x = random.randrange(area[0] + 1, area[2] - 1)
    z = random.randrange(area[1] + 1, area[3] - 1)
    streetLight(houses,x,z)
  
for i in range(4):
    x = random.randrange(area[0] + 1, area[2] - 1)
    z = random.randrange(area[1] + 1, area[3] - 1)
    seed = random.randint(0,len(directions)-1)
    barrels(houses,x,z,seed)

if USE_BATCHING:
    # we need to send remaining blocks in the buffer at the end of the program, when using batching
    interfaceUtils.sendBlocks()

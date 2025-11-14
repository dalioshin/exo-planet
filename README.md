# Exoplanet Star Map

## Finished product
<iframe width="560" height="315" src="https://www.youtube.com/embed/TTXV3mgL7a4?si=SE7eVYKafCc9R9ot" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

 Youtube link: https://youtu.be/TTXV3mgL7a4

## What is this project for?
The main purpose is to capture and visualize how teeming with exoplanets our universe really is. To capture the wonder I first experienced looking at this data in a way that captures the imagination of a broader group of people than data alone can. When I first started becoming interested in studying exoplanets they were thought to be rare, but recently with improvements in sensing technologies we have discovered thousands. It is now estimated that more stars have exoplanets than not, which is truly incredible.

However, I also want to emphasize that despite all the planets we have discovered, so far the life on Earth is unique. Out of all these planetary systems, only ours has confirmed life and we need to be doing all we can to protect it. 

## How does this work?
NASA publishes a public dataset containing data on every confirmed exoplanet at the [Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/index.html). From this data as a base I followed the general steps below:

1. Pull the data from NASA Exoplanet Archive
2. Convert RA, declination, and distance into x, y, z coordinates and scale distances 
4. Use script within Blender to plot objects for each star system
5. Animate camera path in Blender
6. Render finished animation into video

Other first experiments using the Processing language are included as well

## Running the project
Assumption = macOS
### Dependencies
1. Blender 4.5.x
2. Python >= 3.10
3. poetry ([poetry install](https://python-poetry.org/docs/))

### Commands
| Command | Description |
| --- | --- |
| brew install jpeg zlib libtiff | (First time setup only) Install native image libraries required for rendering (macOS) |
| poetry install | Install Python dependencies defined in pyproject.toml using Poetry |
| poetry run python3 exo_planet/scale_transform_data.py [input csv] [ouput csv] | Run the data transformation script to convert RA/Dec/distance into scaled x,y,z coordinates |
| processing-java --sketch=pointfield --run | Run the Processing sketch |

### Within Blender

Notes on Blender usage
- Run Blender script -> open tab "Scripting" and paste script from blender_plot_script.py and click run. May take a while.
- make background black
	right side world -> background change rgb to black
- make things glow
	add material -> emission -> view in rendered mode
- camera to view
	click open hidden tab right under options to the left of the properties pane
	view -> camera to view 
- track camera on path
	constraints -> follow path target=curve, animate path
	track to -> select object or objects the camera should track
- apply materials
	ctrl L -> link material
	bpy.ops.object.select_all(action='SELECT') 
	bpy.ops.object.make_links_data(type='MATERIAL')
	sets active obj material to all selected
- Rendering -> top left "Render -> Render animation" (This will take a long time)

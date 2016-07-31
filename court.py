#%matplotlib inline
import math 
import requests
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from matplotlib.patches import Circle, Rectangle, Arc


def draw_court(ax=None, color='black', lw=2, outer_lines=False, x, y):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()
    # Create the various parts of an NBA basketball court
    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,linewidth=lw, color=color, fill=False)
    
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    ##NBA 3
    #corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,color=color)  #NBA 3
    #corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_a = Rectangle((-207.5, -47.5), 0, 47.5, linewidth=lw,color=color)  #NBA 3
    corner_three_b = Rectangle((207.5, -47.5), 0, 47.5, linewidth=lw, color=color)
    
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    #three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)  #NBA line
    three_arc = Arc((0, 0), 415, 415, theta1=0, theta2=180, linewidth=lw, color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, 
    bottom_free_throw, restricted, corner_three_a,
    corner_three_b, three_arc, center_outer_arc,
    center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    # create our jointplot
    joint_shot_chart = sns.jointplot(x,y, stat_func=None,
                                     kind='scatter', space=0, alpha=0.5)

    joint_shot_chart.fig.set_size_inches(12,11)

    # A joint plot has 3 Axes, the first one called ax_joint 
    # is the one we want to draw our court onto and adjust some other settings
    ax = joint_shot_chart.ax_joint
    draw_court(ax)

    # Adjust the axis limits and orientation of the plot in order
    # to plot half court, with the hoop by the top of the plot
    ax.set_xlim(-250,250)
    ax.set_ylim(422.5, -47.5)

    # Get rid of axis labels and tick marks
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(labelbottom='off', labelleft='off')

    return ax

def Shots():
    Team_Choice = str(raw_input("Pick a team."))
    teamshotfile = "Shots 2014-15/" + Team_Choice + ".csv"
    shots = pd.read_csv(teamshotfile, sep = '\t')
    distance = shots["distance"]  #feet from basket
    angle = shots["angle"]  #angle is in degrees, convert to radians
    leftside = shots["leftside"]
    made = shots["made"]
    player = shots["player"]
    x = []
    y = []
    for i in range(len(distance)):
        x1 = 10 * distance[i] * math.sin(math.radians(angle[i]))  #10 px = 1 foot
        y1 = 10 * distance[i] * math.cos(math.radians(angle[i]))
        if leftside[i] == 1:
            x1 = x1 * (-1)
        if made[i] == 1:
            #if player[i] == "Frank Kaminsky III":
            x.append(x1)
            y.append(y1)
    return x, y

# plt.figure(figsize=(12,11))
# draw_court(outer_lines=True)
# plt.xlim(-300,300)
# plt.ylim(-100,500)
# plt.show()

x, y = Shots()
plt.figure(figsize=(12,11))
plt.scatter(x, y)
draw_court()

# Adjust plot limits to just fit in half court
plt.xlim(-250,250)
# Descending values along th y axis from bottom to top
# in order to place the hoop by the top of plot
plt.ylim(422.5, -47.5)
# get rid of axis tick labels
# plt.tick_params(labelbottom=False, labelleft=False)
plt.show()
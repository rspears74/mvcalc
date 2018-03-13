#!/usr/local/bin/python3

import tkinter
from tkinter import ttk
from tkinter import messagebox
import operator
import os
import sys
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def calculate(*args):
    # Get values from input
    try:
        span_length = float(span_length_entry.get())
        x_loc = float(x_loc_entry.get())
        feet_or_frac = feet_or_frac_entry.get()
        x_loc = x_loc * span_length if feet_or_frac == 2 else x_loc
        incr = float(increment_entry.get())/12
        impact_factor = float(impact_factor_entry.get())
        dist_factor = float(dist_factor_entry.get())
    except ValueError:
        messagebox.showerror('Error', 'Invalid Input!')
        return

    # Cooper E-80 Axle Layout
    axle_loads = [40, 80, 80, 80, 80, 52, 52, 52, 52,
                  40, 80, 80, 80, 80, 52, 52, 52, 52,
                  8]

    axle_spaces = [0, 8, 5, 5, 5, 9, 5, 6, 5,
                   8, 8, 5, 5, 5, 9, 5, 6, 5,
                   5.5]

    # Add trailing live load up to length of span
    train_len = sum(axle_spaces)
    while (sum(axle_spaces) - train_len) < span_length:
        axle_spaces.append(1)
        axle_loads.append(8)

    num_axles = len(axle_loads)

    train_tot = sum(axle_spaces)

    # Initialize train positions array
    positions = []
    point = -span_length
    while point <= train_tot:
        positions.append(point)
        point += incr

    # Initialize arrays to hold total moment and shear values.
    # These arrays will be used to store the moment and shear values per
    # position of the train. We will run the "max" function to find max
    # values in these arrays
    m_array = []
    v_array = []

    for i in range(len(positions)):
        # a and b arrays store a and b values or each axle
        # r1 and r2 arrays store reactions at ends 1 and 2 for each axle
        # m and v arrays store m and v caused by each axle
        a = []
        b = []
        r1 = []
        r2 = []
        m = []
        v = []

        # This loop calculates individual values for each of the above
        # arrays and appends each value to the array.
        for j in range(num_axles):
            a_val = span_length + positions[i] - sum(axle_spaces[:j+1])
            a.append(a_val)

            b_val = span_length - a_val
            b.append(b_val)

            if 0 < b_val < span_length and a_val > x_loc:
                m_val = axle_loads[j]*(a_val - x_loc)
            else:
                m_val = 0
            m.append(m_val)

            if 0 < b_val < span_length and a_val < x_loc:
                v_val = axle_loads[j]
            else:
                v_val = 0
            v.append(v_val)

            if 0 < b_val < span_length:
                r1_val = axle_loads[j]*b_val/span_length
            else:
                r1_val = 0
            r1.append(r1_val)

            if 0 < a_val < span_length:
                r2_val = axle_loads[j]*a_val/span_length
            else:
                r2_val = 0
            r2.append(r2_val)

        # Calculate the moment and shear at the respective x location
        # caused by the train at position i and push these values to the
        # global moment and shear arrays
        m_tot = sum(r2)*(span_length-x_loc) - sum(m)
        v_tot = abs(sum(r1) - sum(v))
        m_array.append(m_tot)
        v_array.append(v_tot)

    # Find max and position of train to cause max
    m_loc_index, m_max = max(enumerate(m_array), key=operator.itemgetter(1))
    v_loc_index, v_max = max(enumerate(v_array), key=operator.itemgetter(1))
    m_max = m_max*(1 + impact_factor)*dist_factor
    v_max = v_max*(1 + impact_factor)*dist_factor
    m_max_loc = positions[m_loc_index]
    v_max_loc = positions[v_loc_index]

    # Set values in GUI to calculated values
    max_moment_disp.set(round(m_max, 2))
    max_shear_disp.set(round(v_max, 2))
    max_moment_loc_disp.set(round(m_max_loc, 2))
    max_shear_loc_disp.set(round(v_max_loc, 2))


def clear(*args):

    # Set all "settable" labels in GUI to nothing
    max_moment_disp.set('')
    max_shear_disp.set('')
    max_moment_loc_disp.set('')
    max_shear_loc_disp.set('')


def show_plot_moment(*args):

    # Get input
    try:
        span_length = float(span_length_entry.get())
        x_loc = float(x_loc_entry.get())
        feet_or_frac = feet_or_frac_entry.get()
        x_loc = x_loc * span_length if feet_or_frac == 2 else x_loc
    except ValueError:
        messagebox.showerror('Error', 'Invalid Input!')
        return

    try:
        axle_pos = float(max_moment_loc_disp.get())
    except ValueError:
        messagebox.showerror('Error', 'Train position not calculated!')
        return

    # Plot span
    span = plt.plot([0, span_length], [0, 0])
    plt.setp(span, color='b')

    # Add boundaries to span
    # tri_width = (span_length*1.2+20)/120
    # bound1 = plt.plot([0, -tri_width, tri_width, 0], [0, -2, -2, 0])
    bound1 = plt.plot(0, -0.7)
    plt.setp(bound1, color='b', marker='^')
    bound2 = plt.plot(span_length, -0.7)
    plt.setp(bound2, color='b', marker='o')

    axle_pos += span_length

    # Cooper E-80 Axle Layout
    axle_loads = [40, 80, 80, 80, 80, 52, 52, 52, 52,
                  40, 80, 80, 80, 80, 52, 52, 52, 52,
                  8]

    axle_spaces = [0, 8, 5, 5, 5, 9, 5, 6, 5,
                   8, 8, 5, 5, 5, 9, 5, 6, 5,
                   5.5]

    train_len = sum(axle_spaces)
    while (sum(axle_spaces) - train_len) < span_length:
        axle_spaces.append(1)
        axle_loads.append(8)

    for pos, spac in enumerate(axle_spaces):
        axle_pos = axle_pos - spac
        axle_load = 1 + axle_loads[pos] / 4
        axle = plt.plot([axle_pos, axle_pos], [1, axle_load])
        plt.setp(axle, color='r')
        axle_end = plt.plot(axle_pos, 1)
        plt.setp(axle_end, color='r', marker='v')
    xplot = plt.plot([x_loc, x_loc], [-1, -5])
    xplotarr = plt.plot(x_loc, -1)
    plt.setp(xplot, color='y')
    plt.setp(xplotarr, color='y', marker='^')
    plt.axis([-20, span_length + 20, -30, 60])
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    plt.title('Train Position for Max Moment')
    plt.show()


def show_plot_shear(*args):
    try:
        span_length = float(span_length_entry.get())
        x_loc = float(x_loc_entry.get())
        feet_or_frac = feet_or_frac_entry.get()
        x_loc = x_loc * span_length if feet_or_frac == 2 else x_loc
    except ValueError:
        messagebox.showerror('Error', 'Invalid Input!')
        return

    try:
        axle_pos = float(max_shear_loc_disp.get())
    except ValueError:
        messagebox.showerror('Error', 'Train position not calculated!')
        return

    # Plot span
    span = plt.plot([0, span_length], [0, 0])
    plt.setp(span, color='b')

    # Add boundaries to span
    # tri_width = (span_length*1.2+20)/120
    # bound1 = plt.plot([0, -tri_width, tri_width, 0], [0, -2, -2, 0])
    bound1 = plt.plot(0, -0.7)
    plt.setp(bound1, color='b', marker='^')
    bound2 = plt.plot(span_length, -0.7)
    plt.setp(bound2, color='b', marker='o')

    axle_pos += span_length

    # Cooper E-80 Axle Layout
    axle_loads = [40, 80, 80, 80, 80, 52, 52, 52, 52,
                  40, 80, 80, 80, 80, 52, 52, 52, 52,
                  8]

    axle_spaces = [0, 8, 5, 5, 5, 9, 5, 6, 5,
                   8, 8, 5, 5, 5, 9, 5, 6, 5,
                   5.5]

    train_len = sum(axle_spaces)
    while (sum(axle_spaces) - train_len) < span_length:
        axle_spaces.append(1)
        axle_loads.append(8)

    for pos, spac in enumerate(axle_spaces):
        axle_pos = axle_pos - spac
        axle_load = 1 + axle_loads[pos] / 4
        axle = plt.plot([axle_pos, axle_pos], [1, axle_load])
        plt.setp(axle, color='r')
        axle_end = plt.plot(axle_pos, 1)
        plt.setp(axle_end, color='r', marker='v')
    xplot = plt.plot([x_loc, x_loc], [-1, -5])
    xplotarr = plt.plot(x_loc, -1)
    plt.setp(xplot, color='y')
    plt.setp(xplotarr, color='y', marker='^')
    plt.axis([-20, span_length + 20, -30, 60])
    cur_axes = plt.gca()
    cur_axes.axes.get_xaxis().set_visible(False)
    cur_axes.axes.get_yaxis().set_visible(False)
    plt.title('Train Position for Max Shear')
    plt.show()


def nth_point_moment(*args):
    # Get values from input
    try:
        span_length = float(span_length_entry.get())
        n = int(nth_points_entry.get())
        incr = float(increment_entry.get())/12
        impact_factor = float(impact_factor_entry.get())
        dist_factor = float(dist_factor_entry.get())
    except ValueError:
        messagebox.showerror('Error', 'Invalid Input!')
        return

    x_locs = [i*span_length/n for i in range(n+1)]

    # Cooper E-80 Axle Layout
    axle_loads = [40, 80, 80, 80, 80, 52, 52, 52, 52,
                  40, 80, 80, 80, 80, 52, 52, 52, 52,
                  8]

    axle_spaces = [0, 8, 5, 5, 5, 9, 5, 6, 5,
                   8, 8, 5, 5, 5, 9, 5, 6, 5,
                   5.5]
    train_len = sum(axle_spaces)
    while (sum(axle_spaces) - train_len) < span_length:
        axle_spaces.append(1)
        axle_loads.append(8)

    num_axles = len(axle_loads)

    train_tot = sum(axle_spaces)
    # Initialize train positions array
    positions = []
    point = -span_length
    while point <= train_tot:
        positions.append(point)
        point += incr

    # Initialize arrays to hold total moment and shear values.
    # These arrays will be used to store the moment and shear values per
    # position of the train. We will run the "max" function to find max
    # values in these arrays
    m_maxs = []

    for loc in x_locs:
        m_array = []

        for i in range(len(positions)):
            # a and b arrays store a and b values or each axle
            # r1 and r2 arrays store reactions at ends 1 and 2 for each axle
            # m and v arrays store m and v caused by each axle
            a = []
            b = []
            r2 = []
            m = []

            # This loop calculates individual values for each of the above
            # arrays and appends each value to the array.
            for j in range(num_axles):
                a_val = span_length + positions[i] - sum(axle_spaces[:j+1])
                a.append(a_val)

                b_val = span_length - a_val
                b.append(b_val)

                if 0 < b_val < span_length and a_val > loc:
                    m_val = axle_loads[j]*(a_val - loc)
                else:
                    m_val = 0
                m.append(m_val)

                if 0 < a_val < span_length:
                    r2_val = axle_loads[j]*a_val/span_length
                else:
                    r2_val = 0
                r2.append(r2_val)

            # Calculate the moment and shear at the respective x location
            # caused by the train at position i and push these values to the
            # global moment and shear arrays
            m_tot = sum(r2)*(span_length-loc) - sum(m)
            m_array.append(m_tot)

        # Find max and position of train to cause max
        m_max = max(m_array)
        m_max = m_max*(1 + impact_factor)*dist_factor
        m_maxs.append(m_max)

    plt.plot(x_locs, m_maxs)
    plt.ylabel('Maximum Moment, kip-ft')
    plt.xlabel('Span Position, ft')
    plt.title('Maximum Moment at '+str(n)+'th Points Along Span')
    plt.show()


def nth_point_shear(*args):
    # Get values from input
    try:
        span_length = float(span_length_entry.get())
        n = int(nth_points_entry.get())
        incr = float(increment_entry.get())/12
        impact_factor = float(impact_factor_entry.get())
        dist_factor = float(dist_factor_entry.get())
    except ValueError:
        messagebox.showerror('Error', 'Invalid Input!')
        return

    x_locs = [i*span_length/n for i in range(n+1)]

    # Cooper E-80 Axle Layout
    axle_loads = [40, 80, 80, 80, 80, 52, 52, 52, 52,
                  40, 80, 80, 80, 80, 52, 52, 52, 52,
                  8]

    axle_spaces = [0, 8, 5, 5, 5, 9, 5, 6, 5,
                   8, 8, 5, 5, 5, 9, 5, 6, 5,
                   5.5]
    train_len = sum(axle_spaces)
    while (sum(axle_spaces) - train_len) < span_length:
        axle_spaces.append(1)
        axle_loads.append(8)

    num_axles = len(axle_loads)

    train_tot = sum(axle_spaces)
    # Initialize train positions array
    positions = []
    point = -span_length
    while point <= train_tot:
        positions.append(point)
        point += incr

    # Initialize arrays to hold total moment and shear values.
    # These arrays will be used to store the moment and shear values per
    # position of the train. We will run the "max" function to find max
    # values in these arrays
    v_maxs=[]

    for loc in x_locs:
        v_array = []

        for i in range(len(positions)):
            # a and b arrays store a and b values or each axle
            # r1 and r2 arrays store reactions at ends 1 and 2 for each axle
            # m and v arrays store m and v caused by each axle
            a = []
            b = []
            r1 = []
            v = []

            # This loop calculates individual values for each of the above
            # arrays and appends each value to the array.
            for j in range(num_axles):
                a_val = span_length + positions[i] - sum(axle_spaces[:j+1])
                a.append(a_val)

                b_val = span_length - a_val
                b.append(b_val)

                if 0 < b_val < span_length and a_val < loc:
                    v_val = axle_loads[j]
                else:
                    v_val = 0
                v.append(v_val)

                if 0 < b_val < span_length:
                    r1_val = axle_loads[j]*b_val/span_length
                else:
                    r1_val = 0
                r1.append(r1_val)

            # Calculate the moment and shear at the respective x location
            # caused by the train at position i and push these values to the
            # global moment and shear arrays
            v_tot = abs(sum(r1) - sum(v))
            v_array.append(v_tot)

        # Find max and position of train to cause max
        v_max = max(v_array)
        v_max = v_max*(1 + impact_factor)*dist_factor
        v_maxs.append(v_max)

    plt.plot(x_locs, v_maxs)
    plt.ylabel('Maximum Shear, kips')
    plt.xlabel('Span Position, ft')
    plt.title('Maximum Shear at '+str(n)+'th Points Along Span')
    plt.show()

# Shorten notation for sticky values
N = tkinter.N
S = tkinter.S
E = tkinter.E
W = tkinter.W

# Initialize root window, title, and give it weight
root = tkinter.Tk()
root.title('Cooper E-80 Max Shear/Moment Calculator')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Initialize main frame inside root window
mainframe = ttk.Frame(root, padding="5 5 12 12")
mainframe.grid(column=0,
               row=0,
               sticky=N+S+E+W)

for i in range(1, 4):
    for j in range(1, 3):
        mainframe.columnconfigure(j, weight=1)
        mainframe.rowconfigure(i, weight=1)

# Create frame for inputs
inputframe = ttk.Frame(mainframe,
                       padding="8 8 8 8",
                       borderwidth=2,
                       relief=tkinter.RIDGE)
inputframe.grid(column=1, row=1, sticky=N + S + E + W)

for i in range(1, 8):
    for j in range(1, 4):
        inputframe.columnconfigure(j, weight=1)
        inputframe.rowconfigure(i, weight=1)

# Create frame for n-th point analysis
nframe = ttk.Frame(mainframe,
                   padding='8 8 10 10',
                   borderwidth=2,
                   relief=tkinter.RIDGE)
nframe.grid(column=2, row=1, sticky=N+S+E+W)

for i in range(1, 3):
    for j in range(1, 3):
        nframe.columnconfigure(j, weight=1)
        nframe.rowconfigure(i, weight=1)

# Create frame for results
resultframe = ttk.Frame(mainframe,
                        padding='8 8 8 8',
                        borderwidth=2,
                        relief=tkinter.RIDGE)
resultframe.grid(column=1, row=2, columnspan=2, sticky=N+S+E+W)

for i in range(1, 3):
    for j in range(1, 8):
        resultframe.columnconfigure(j, weight=1)
        resultframe.rowconfigure(i, weight=1)

# Create frame for buttons
buttonframe = ttk.Frame(mainframe, padding='8 8 8 8')
buttonframe.grid(column=1, row=3, columnspan=2, sticky=N+S+E+W)

for i in range(1, 2):
    for j in range(1, 5):
        buttonframe.columnconfigure(j, weight=1)
        buttonframe.rowconfigure(i, weight=1)

# Initialize changeable variables
span_length_entry = tkinter.StringVar()
x_loc_entry = tkinter.StringVar()
feet_or_frac_entry = tkinter.IntVar()
increment_entry = tkinter.StringVar()
impact_factor_entry = tkinter.StringVar()
dist_factor_entry = tkinter.StringVar()
max_moment_disp = tkinter.StringVar()
max_moment_loc_disp = tkinter.StringVar()
max_shear_disp = tkinter.StringVar()
max_shear_loc_disp = tkinter.StringVar()

# Create labels for each input box and assign them to grid spaces
ttk.Label(inputframe, text='Inputs',
          font='-weight bold',
          padding='0 0 0 5').grid(row=1,
                                    column=1,
                                    columnspan=3,
                                    sticky=N+S)
ttk.Label(inputframe,
          text='Span Length:').grid(column=1,
                                    row=2,
                                    sticky=W+E)
ttk.Label(inputframe,
          text='x-Location:').grid(column=1,
                                   row=3,
                                   rowspan=2,
                                   sticky=W+E)
ttk.Label(inputframe,
          text='Increment:').grid(column=1,
                                  row=5,
                                  sticky=W+E)
ttk.Label(inputframe,
          text='Impact Factor:').grid(column=1,
                                      row=6,
                                      sticky=W+E)
ttk.Label(inputframe,
          text='Distribution Factor:').grid(column=1,
                                            row=7,
                                            sticky=W+E)

# Create entry boxes and assign them to grid spaces
span_length_entry_box = ttk.Entry(inputframe,
                                  width=7,
                                  textvariable=span_length_entry)
span_length_entry_box.grid(column=2,
                           row=2,
                           sticky=W+E)
x_loc_entry_box = ttk.Entry(inputframe,
                            width=7,
                            textvariable=x_loc_entry)
x_loc_entry_box.grid(column=2,
                     row=3,
                     rowspan=2,
                     sticky=W+E)
increment_entry_box = ttk.Entry(inputframe,
                                width=7,
                                textvariable=increment_entry)
increment_entry_box.grid(column=2,
                         row=5,
                         sticky=W+E)
impact_factor_entry_box = ttk.Entry(inputframe,
                                    width=7,
                                    textvariable=impact_factor_entry)
impact_factor_entry_box.grid(column=2,
                             row=6,
                             sticky=W+E)
dist_factor_entry_box = ttk.Entry(inputframe,
                                  width=7,
                                  textvariable=dist_factor_entry)
dist_factor_entry_box.grid(column=2,
                           row=7,
                           sticky=W+E)

# Give impact and distribution factors and increment default values
impact_factor_entry_box.insert(tkinter.END, '0')
dist_factor_entry_box.insert(tkinter.END, '1')
increment_entry_box.insert(tkinter.END, '1')

# Create unit labels for entry boxes and radio button for x location
# option, set default radiobutton, and assign them all grid positions
ttk.Label(inputframe, text='feet').grid(column=3,
                                       row=2,
                                       sticky=W)
rad1 = ttk.Radiobutton(inputframe,
                       text='feet',
                       variable=feet_or_frac_entry,
                       value=1)
rad1.grid(column=3,
          row=3,
          sticky=W)
rad1.invoke()
rad2 = ttk.Radiobutton(inputframe,
                       text='span fraction',
                       variable=feet_or_frac_entry,
                       value=2)
rad2.grid(column=3,
          row=4,
          sticky=W)
ttk.Label(inputframe, text='inches').grid(column=3,
                                         row=5,
                                         sticky=W)

# Create output text strings and locations for moment output
# and assign them grid positions
ttk.Label(resultframe, text='The maximum moment').grid(column=1,
                                                     row=1,
                                                     sticky=E)
ttk.Label(resultframe,
          textvariable=max_moment_disp,
          font='-weight bold').grid(column=2,
                                    row=1,
                                    sticky=E)
ttk.Label(resultframe,
          text='kip-ft',
          font='-weight bold').grid(column=3,
                                    row=1,
                                    sticky=W)
ttk.Label(resultframe,
          text=' occurs when the front of the train is ').grid(column=4,
                                                               row=1,
                                                               sticky=W)
ttk.Label(resultframe,
          textvariable=max_moment_loc_disp,
          font='-weight bold').grid(column=5,
                                    row=1,
                                    sticky=E)
ttk.Label(resultframe,
          text='feet',
          font='-weight bold').grid(column=6,
                                    row=1,
                                    sticky=W)
ttk.Label(resultframe,
          text=' past the last support.').grid(column=7,
                                               row=1,
                                               sticky=W)

# Create output text strings and locations for shear output
# and assign them grid positions
ttk.Label(resultframe,
          text='The maximum shear').grid(column=1,
                                         row=2,
                                         sticky=E)
ttk.Label(resultframe,
          textvariable=max_shear_disp,
          font='-weight bold').grid(column=2,
                                    row=2,
                                    sticky=E)
ttk.Label(resultframe,
          text='kips',
          font='-weight bold').grid(column=3,
                                    row=2,
                                    sticky=W)
ttk.Label(resultframe,
          text=' occurs when the front of the train is ').grid(column=4,
                                                               row=2,
                                                               sticky=W)
ttk.Label(resultframe,
          textvariable=max_shear_loc_disp,
          font='-weight bold').grid(column=5,
                                    row=2,
                                    sticky=E)
ttk.Label(resultframe,
          text='feet',
          font='-weight bold').grid(column=6,
                                    row=2,
                                    sticky=W)
ttk.Label(resultframe,
          text=' past the last support.').grid(column=7,
                                               row=2,
                                               sticky=W)

# Create buttons
ttk.Button(buttonframe,
           text='Calculate',
           command=calculate).grid(column=1,
                                   row=1,
                                   sticky=E+W)
ttk.Button(buttonframe,
           text='Reset',
           command=clear).grid(column=2,
                               row=1,
                               sticky=E+W)
ttk.Button(buttonframe,
           text='Moment Train Position',
           command=show_plot_moment).grid(column=3,
                                          row=1,
                                          sticky=E+W)
ttk.Button(buttonframe,
           text='Shear Train Position',
           command=show_plot_shear).grid(column=4,
                                         row=1,
                                         sticky=E + W)

# Create elements inside nframe
ttk.Label(nframe,
          text='Number of points for n-th point plots:').grid(column=1,
                                                              row=1,
                                                              sticky=W+E)
nth_points_entry = tkinter.StringVar()
nth_points_entry_box = ttk.Entry(nframe,
                                 width=7,
                                 textvariable=nth_points_entry)
nth_points_entry_box.grid(column=2,
                          row=1,
                          sticky=W)
ttk.Button(nframe,
           text='N-th Point Max Moment Plot',
           command=nth_point_moment).grid(column=1,
                                          row=2,
                                          sticky=W+E)
ttk.Button(nframe,
           text='N-th Point Max Shear Plot',
           command=nth_point_shear).grid(column=2,
                                         row=2,
                                         sticky=W+E)

# Make cursor open in first box on open
span_length_entry_box.focus()

# Set Return key to calculate function
root.bind('<Return>', calculate)

# Make sure python is in front when opened on OS X
if sys.platform == 'darwin':
    os.system('''/usr/bin/osascript -e 'tell app "Finder"\
              to set frontmost of process "Python" to true' ''')

# Begin main loop (open window)
root.mainloop()
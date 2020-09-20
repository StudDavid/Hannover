import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
# ********************************************************************************************
# imports
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse
from scipy.spatial.transform import Rotation as R

# custom libraries
from src.constants import Constants as C


def write_log_template(info_file_path):
    constants = C()
    with open(info_file_path, 'w+') as json_file:
        data = {'BACTERIA': {}, 'CONSTANTS': {}}
        members = [attr for attr in dir(constants) if
                   not callable(getattr(constants, attr)) and not attr.startswith("__")]
        constants_dic = {}
        for constant in members:
            constants_dic.update({constant: str(getattr(constants, constant))})
        data['CONSTANTS'].update(constants_dic)
        json.dump(data, json_file, indent=4)


def read_in_log(info_file_path) -> Dict:
    with open(info_file_path, "r") as json_file:
        data = json.load(json_file)
    return data


def bacteria_as_pandas(info_file_path) -> pd.DataFrame:
    data = read_in_log(info_file_path)
    return pd.DataFrame(data['BACTERIA']).transpose()


def constants_as_pandas(info_file_path):
    data = read_in_log(info_file_path)
    return pd.DataFrame(data['CONSTANTS']).transpose()


def save_dict_as_json(data: Dict, info_file_path: Path):
    with open(str(info_file_path), 'w') as json_file:
        json.dump(data, json_file)


def get_data_to_parameter(data: pd.DataFrame, key: str, exact: bool = False):
    """
    Gets complete bacteria data as a DataFrame.
    Resorts data to parameters 'key' into another DataFrame:
        bacteria_0_parameter    ... bacteria_N_parameter
    0       100                         NaN
    1       12                          NaN
    2       13                          10
    .
    .
    .

    If the key is position or velocity, calculates the absolute value first.
    Returned Data is sorted according to the iteration step.
    """
    dic = {}
    for index, bacteria in data.iterrows():
        df_bac = pd.DataFrame(bacteria).loc[key, :]
        for vectors in df_bac:
            if (key == 'velocity' or key == 'position') and (exact is False):
                # calculate norm for velocity and position
                vectors = get_euclid_norm(vectors)
            dic.update({str(index) + '_' + key: vectors})
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in dic.items()]))

    def isnan(vector):
        if np.isnan(np.min(vector)):
            return False
        else:
            return True

    df = df.transform(lambda x: sorted(x, key=isnan, reverse=True))
    return df


def get_euclid_norm(array):
    """ returns the norm of each vector in parameter array"""
    for i in range(len(array)):
        array[i] = np.linalg.norm(array[i])
    return array


def plot_velocities(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    """
    Plots velocities of each bacteria and the mean velocity of all bacteria
    over the iteration step.
    """
    plot_data = get_data_to_parameter(data, 'velocity')
    means = plot_data.mean(axis=1, skipna=True)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    for bacteria in plot_data:
        ax1.plot(plot_data.loc[:, bacteria], '--', alpha=0.3)

    ax1.set_title('Velocities')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('velocity')
    ax2.plot(means)
    ax2.set_title('Mean Velocity')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('velocity')

    if save_fig:
        path = Path(save_path).parent / 'velocity_plot.png'
        fig.savefig(str(path))
    else:
        plt.show()


def animate_positions(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    plot_data = get_data_to_parameter(data, 'position', exact=True)
    living_data = get_data_to_parameter(data, 'living')

    fig, ax = plt.subplots()
    lines = []
    data = []
    living = []

    for bacteria in plot_data:
        x_data = [vector[0] for vector in plot_data[bacteria] if not np.isnan(np.min(vector))]
        y_data = [vector[1] for vector in plot_data[bacteria] if not np.isnan(np.min(vector))]
        lines.append(ax.plot(x_data, y_data, ), )
        data.append([x_data, y_data])
        living.append([living_data[bacteria.replace('position', 'living')]])

    def update(num, line_plots, dataLines, living_data):
        for line, dataLine, alive in zip(line_plots, dataLines, living_data):
            # update data for line plot: dataLine[0] = x data, dataLine[1] y data
            line[0].set_data(dataLine[0][:num], dataLine[1][:num])
            if alive[0] is False:
                line[0].set_color('black')
                line[0].set_alpha(0.5)

        return lines,

    anim = animation.FuncAnimation(fig, update, frames=len(plot_data['bacteria_0_position']),

                                   interval=200, repeat=False, fargs=[lines, data, living])

    if save_fig:
        writer = animation.FFMpegWriter(fps=30, metadata=dict(artist='Me'), bitrate=-1)
        path = Path(save_path).parent / '2d_animation.mp4'
        anim.save(str(path), writer=writer)
    else:
        plt.show()


def animate_3d(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    plot_data = get_data_to_parameter(data, 'position', exact=True)

    fig = plt.figure()
    ax = p3.Axes3D(fig)
    lines = []
    data = []
    for bacteria in plot_data:
        x_data = [vector[0] for vector in plot_data[bacteria] if not np.isnan(np.min(vector))]
        y_data = [vector[1] for vector in plot_data[bacteria] if not np.isnan(np.min(vector))]
        z_data = [vector[2] for vector in plot_data[bacteria] if not np.isnan(np.min(vector))]
        lines.append(ax.plot(x_data, y_data, z_data, alpha=0.9), )
        data.append([x_data, y_data, z_data])

    def update(num, line_plots, dataLines):
        for line, dataLine in zip(line_plots, dataLines):
            # update data for line plot: dataLine[0] = x data, dataLine[1] y data
            line[0].set_data(dataLine[0][:num], dataLine[1][:num])
            line[0].set_3d_properties(dataLine[2][:num])
        return lines,

    anim = animation.FuncAnimation(fig, update, frames=len(plot_data['bacteria_0_position']),
                                   interval=200, repeat=False, fargs=[lines, data])
    if save_fig:
        writer = animation.FFMpegWriter(fps=50, metadata=dict(artist='Me'), bitrate=-1)
        path = Path(save_path).parent / '3d_animation.mp4'
        anim.save(str(path), writer=writer)
    else:
        plt.show()


def plot_as_ellipse(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    pos_data = get_data_to_parameter(data, 'position')
    angle_data = get_data_to_parameter(data, 'angle')
    length_data = get_data_to_parameter(data, 'length')
    fig, ax = plt.subplots(1, 1)
    ells = []
    for bacteria in pos_data:
        patch = Ellipse(xy=pos_data.loc[0, bacteria], width=1,
                        height=length_data.loc[0, bacteria],
                        angle=angle_data.loc[0, bacteria][0])
        ells.append(patch)

    for e in ells:
        ax.add_artist(e)
        e.set_clip_box(ax.bbox)
        e.set_alpha(0.4)
    plt.show()

    if save_fig:
        fig.savefig(save_path / 'ellipse_plot.jpeg')


def plot_positions(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    """
    Plots positions (as lengths of location vectors) of each bacteria and the mean position of all bacteria
    over the iteration step.
    """
    plot_data = get_data_to_parameter(data, 'position')
    means = plot_data.mean(axis=1, skipna=True)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    for bacteria in plot_data:
        ax1.plot(plot_data.loc[:, bacteria], '--', alpha=0.3)

    ax1.set_title('Position')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('distance')
    ax2.plot(means)
    ax2.set_title('Mean position')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('distance')

    if save_fig:
        path = Path(save_path).parent / 'positions_plot.png'
        fig.savefig(path)
    else:
        plt.show()


def plot_force(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    """
    Plots force acting on each bacteria and the mean force acting on all bacteria
    over the iteration step.
    """
    plot_data = get_data_to_parameter(data, 'total_force')
    means = plot_data.mean(axis=1, skipna=True)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    for bacteria in plot_data:
        ax1.plot(plot_data.loc[:, bacteria], '--', alpha=0.3)

    ax1.set_title('Total force')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('force')
    ax2.plot(means)
    ax2.set_title('Mean force')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('force')

    if save_fig:
        path = Path(save_path).parent / 'force_plot.png'
        fig.savefig(path)
    else:
        plt.show()


def plot_size(data: pd.DataFrame, save_path: Path, save_fig: bool = False):
    """
    Plots force acting on each bacteria and the mean force acting on all bacteria
    over the iteration step.
    """
    width_data = get_data_to_parameter(data, 'width')
    length_data = get_data_to_parameter(data, 'length')
    width_means = width_data.mean(axis=1, skipna=True)
    length_means = length_data.mean(axis=1, skipna=True)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    for bacteria in width_data:
        ax1.plot(width_data.loc[:, bacteria], '--', alpha=0.3)
        ax2.plot(length_data.loc[:, bacteria.replace('width', 'length')], '--', alpha=0.3)
    ax1.set_title('width')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('width')
    ax2.set_title('length')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('length')
    ax3.plot(width_means)
    ax4.plot(length_means)
    ax3.set_title('width mean')
    ax3.set_xlabel('Step')
    ax3.set_ylabel('width')
    ax4.set_title('length mean')
    ax4.set_xlabel('Step')
    ax4.set_ylabel('length')

    if save_fig:
        path = Path(save_path).parent / 'size_plot.png'
        fig.savefig(path)
    else:
        plt.show()


def get_info_file_path():
    date_time = str(datetime.now().hour) + 'h' + str(datetime.now().minute) + 'min_' + \
                str(datetime.now().day) + str(datetime.now().month) + \
                str(datetime.now().year)

    path_out = C.OUTPUT_PATH / f'log_{date_time}'
    path_out.mkdir()
    info_file_name = path_out / f'log_{date_time}.json'
    return info_file_name


def prompt_log_at_start(save_dir: str):
    return (f"********************* BIOFILM MODELING *********************\n"
            "NUMBER OF INITIAL BACTERIA\t {number_bacteria}\n"
            "==================================================\n"
            "INITIAL DIMENSIONS (LENGTH, WIDTH)\t {BSUB_LENGTH},\t{BSUB_WIDTH}\n"
            "MASS\t {BSUB_MASS}\n"
            "GROWTH FACTOR\t {BSUB_GROWTH_FACTOR}\n"
            "CRITICAL LENGTH\t {BSUB_CRITICAL_LENGTH}\n\n"
            "SAVING AS \t {saving_dir}"
            .format(number_bacteria=C.NUM_INITIAL_BACTERIA,
                    type="B. subtilius", BSUB_LENGTH=C.BSUB_LENGTH,
                    BSUB_WIDTH=C.BSUB_WIDTH, BSUB_MASS=C.BSUB_MASS,
                    BSUB_CRITICAL_LENGTH=C.BSUB_CRITICAL_LENGTH,
                    BSUB_GROWTH_FACTOR=C.BSUB_GROWTH_FACTOR, saving_dir=save_dir))


def stokes_drag_force(radius: float, velocity: np.ndarray, viscosity=C.EFFECTIVE_VISCOSITY_EPS) -> np.ndarray:
    # Calculates Stokes' drag for a sphere with Reynolds number < 1.
    # [um * Pa * s 1/1E-6 * um / s] = [um * kg / (um * s **2) * s  * um / s] = [um kg / (s ** 2)]
    return - 6 * np.pi * radius * viscosity * 1E-12 * velocity


def gravitational_force(mass: float) -> np.ndarray:
    # calculates gravitational force on a mass
    # F = m * g * e_z
    # [kg * um / s ** 2]
    return mass * 9.81 * 1E6 * np.asarray([0, 0, -1])


def simulation_duration(func):
    def inner1(*args, **kwargs):
        # storing time before function execution
        begin = time.time()

        func(*args, **kwargs)

        # storing time after function execution
        end = time.time()
        print("Duration : ", func.__name__, end - begin)

    return inner1


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy


def rotation_matrix_x(theta: float):
    # return numpy array with rotation matrix around x axis with angle theta
    r = R.from_euler('x', theta)
    return r


def rotation_matrix_y(theta: float):
    # return numpy array with rotation matrix around y axis with angle theta
    r = R.from_euler('y', theta)
    return r


def rotation_matrix_z(theta: float):
    # return numpy array with rotation matrix around z axis with angle theta
    r = R.from_euler('z', theta)
    return r


def apply_rotation(vector: np.ndarray, matrix: R):
    return matrix.apply(vector)

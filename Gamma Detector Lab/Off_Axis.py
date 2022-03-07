#Importing Libraries

import matplotlib.pyplot as plt
import numpy as np
import json
from datetime import datetime

def read_json(file_path):
    """Function for reading-in saved parameters contained in JSON file"""
    fin = open(file_path, "r")
    jdata = fin.read()
    data = json.loads(jdata)
    fin.close()

    return data

def read_off_axis_energies(isotope_dict):
    energy = isotope_dict['Energies']
    f = isotope_dict['Decay Frac.']
    t_half = isotope_dict['T1/2']
    A0 = isotope_dict['Activity']
    
    return A0, t_half, f, energy

def adding_errors(x, δx, y, δy, z):
    """Function to calculate errors when adding two measurements
    
    Used specifically for adding errors in isotope spectra
    and background counts when subtracting background."""
    #z = x/y
    δz = z * np.sqrt((δx/x)**2 + (δy/y)**2)
    return δz


def time_in_years(recorded_time, detector):
    if detector == 'HpGe':
        reference_time = datetime(1979, 2, 1, 12, 0)
    else:
        reference_time = datetime(1979, 12, 1, 12, 0)
    
    duration = recorded_time - reference_time
    duration_in_s = duration.total_seconds()
    return duration_in_s/(365.25*24*60*60)


def activity(A0, f, T_half, t):
    return A0 * f * 2**(-t/T_half)
    

def estimate_activity(A0_and_err, T_half_and_err, f, t, N):
    A0, A0_err = A0_and_err[0], A0_and_err[1]
    T_half, T_half_err = T_half_and_err[0], T_half_and_err[1]
    
    A0_list = np.random.normal(A0, A0_err, N)
    T_half_list = np.random.normal(T_half, T_half_err, N)
    
    A = activity(A0_list, f, T_half_list, t)
    
    A_mean, A_std = np.mean(A), np.std(A)
    
    return A_mean, A_std


def geometric_factor(r, h, d, shape, angle):
    """Function for calculating geometric factor as a function of angle"""
    
    angle = np.radians(angle)
    if shape == 'square':
        area = (((2*r)**2)*np.abs(np.cos(angle))) + 2*r*h*(np.abs(
            np.sin(angle)))
    else:
        area = (np.pi*(r**2))*np.abs(np.cos(angle)) + 2*r*h*(np.abs(
            np.sin(angle)))
    return (4*np.pi*d**2)/area


def read_detector_dimensions(detector):
    dimensions = read_json('Data/Detector_Dimensions.json')
    r = dimensions[detector]['Diameter']/2
    h = dimensions[detector]['Height']
    l = dimensions[detector]['Distance']
    shape = dimensions[detector]['Shape']
    return [r, h, l, shape]


def read_off_axis_energies(isotope_dict):
    energy = isotope_dict['Energies']
    f = isotope_dict['Decay Frac.']
    t_half = isotope_dict['T1/2']
    A0 = isotope_dict['Activity']
    
    return A0, t_half, f, energy

def extract_data_for_efficiencies(detector):
    off_axis_params = read_json('Data/%s_off_axis_params.json' % detector)
    off_axis_energies = read_json('Data/Off_axis_energies.json')
    results_dict = {}
    for isotope in off_axis_params:
        isotope_dict = {}
        energy_dict = off_axis_energies[detector][isotope]
        angles = []
        areas = []
        area_errs = []
        acts = []
        act_errs = []
        for angle in off_axis_params[isotope]:
            angle_value = int(angle[:-3])
            angles.append(angle_value)

            params_dict = off_axis_params[isotope][angle][0]
            if 'A' in params_dict:
                areas.append(params_dict['A'][0])
                area_errs.append(params_dict['A'][1])

                date = datetime.strptime(params_dict['Date'],
                                         "%m/%d/%Y, %H:%M:%S")
                t = time_in_years(date, detector)
            elif 'A2' in params_dict:
                areas.append(params_dict['A2'][0])
                area_errs.append(params_dict['A2'][1])

                date = datetime.strptime(params_dict['Date'],
                                         "%m/%d/%Y, %H:%M:%S")
                t = time_in_years(date, detector)

            A0, t_half, f, energy = read_off_axis_energies(energy_dict)
            act, act_err = estimate_activity(A0, t_half, f, t, 10000)
            acts.append(act)
            act_errs.append(act_err)
        results_dict[isotope] = {'Areas':[areas, area_errs],
                            'Activities': [acts, act_errs],
                            'Angles' : angles}
    return results_dict


def calculate_total_efficiency(a_dict):
    for isotope in a_dict:
        areas, area_errs = np.asarray(a_dict[isotope]['Areas'])
        acts, act_errs = np.asarray(a_dict[isotope]['Activities'])
        absolute_eff = (areas/acts)*100
        absolute_eff_errs = adding_errors(areas, area_errs,
                                          acts, act_errs, absolute_eff)
        a_dict[isotope]['Abs. Efficiencies'] = [absolute_eff,
                                                absolute_eff_errs]
    return a_dict


def plot_off_axis_abs_efficiencies(a_dict, ax):
    for isotope in a_dict:
        abs_effs, abs_effs_errs = a_dict[isotope]['Abs. Efficiencies']
        angles = a_dict[isotope]['Angles']
        
        ax.errorbar(angles, abs_effs, yerr = abs_effs_errs, label=isotope)
        ax.legend()
        ax.set_ylabel('$\epsilon_{abs}$ (%)')
        ax.grid(True)
    return ax


def plot_off_axis_int_efficiencies(a_dict, ax):
    for isotope in a_dict:
        abs_effs, abs_effs_errs = a_dict[isotope]['Int. Efficiencies']
        angles = a_dict[isotope]['Angles']
        
        ax.errorbar(angles, abs_effs, yerr = abs_effs_errs, label=isotope)
        ax.legend()
        ax.set_xlabel('Source Angle (°)')
        ax.set_ylabel('$\epsilon_{int}$ (%)')
        ax.grid(True)
    return ax


def plot_geometric_factor(dimensions, ax):
    angle_array = np.linspace(0, 150, 1000)
    geo_factor = geometric_factor(*dimensions, angle_array)
    ax.plot(angle_array, geo_factor)
    ax.set_ylabel('Geometric Factor')
    ax.grid(True)
    return ax


def plot_off_axis_intrinsic_effs(a_dict, detector):
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(8, 12))
    detector_dimensions = read_detector_dimensions(detector)
    for isotope in a_dict:
        abs_eff, abs_eff_errs = a_dict[isotope]['Abs. Efficiencies']
        angles = np.asarray(a_dict[isotope]['Angles'])
        geo_factor = geometric_factor(*detector_dimensions, angles)
        int_effs, int_errs = [abs_eff, abs_eff_errs]*geo_factor
        a_dict[isotope]['Int. Efficiencies'] = [int_effs, int_errs]
        
    plot_off_axis_abs_efficiencies(a_dict, ax1)
    plot_geometric_factor(detector_dimensions, ax2)
    plot_off_axis_int_efficiencies(a_dict, ax3)
    fig.tight_layout()
    return a_dict

def off_axis_efficiency_comp_plot(detector):
    
    params_for_efficiencies = extract_data_for_efficiencies(detector)
    efficiencies_dict = calculate_total_efficiency(params_for_efficiencies)
    
    results_dict = plot_off_axis_intrinsic_effs(efficiencies_dict, detector)
    return results_dict
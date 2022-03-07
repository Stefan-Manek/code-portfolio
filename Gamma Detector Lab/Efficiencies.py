#Importing Libraries

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import json
from datetime import datetime

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

def read_json(file_path):
    """Function for reading-in saved parameters contained in JSON file"""
    fin = open(file_path, "r")
    jdata = fin.read()
    data = json.loads(jdata)
    fin.close()

    return data

def filter_lists(a, b, c, d, e, f):
    a1, a2, a3, a4, a5, a6 = [], [], [], [], [], []
    index = 0
    for i in a:
        if a[index] != 0:
            a1.append(a[index])
            a2.append(b[index])
            a3.append(c[index])
            a4.append(d[index])
            a5.append(e[index])
            a6.append(f[index])
        index +=1
    return a1, a2, a3, a4, a5, a6

def colour_map(detector_name):
    if detector_name == 'HpGe':
        colour = 'green'
    elif detector_name == 'NaI':
        colour = 'red'
    elif detector_name == 'BGO':
        colour = 'blue'
    elif detector_name == 'CdTe':
        colour = 'black'
    return colour

def convert_to_arrays(list_of_lists):
    list_of_arrays = []
    for _list in list_of_lists:
        list_of_arrays.append(np.asarray(_list))
    return list_of_arrays


def activities_params(fit_params, energies_dict, activies_dict, detector):
    activity_params_dict = {}
    for isotope in fit_params:
        temp_dict = {}
        for energy in list(zip(*energies_dict[isotope])):
            f = energy [2]
            A0_ = activies_dict[isotope]['Activity']
            T_half_ = activies_dict[isotope]['T1/2']
            date_time_string = fit_params[isotope][0]['Date']
            date = datetime.strptime(date_time_string, "%m/%d/%Y, %H:%M:%S")
            t = time_in_years(date, detector)
            entry = [A0_, f, t, T_half_]
            temp_dict[str(energy[0])] = entry
        activity_params_dict[isotope] = temp_dict
    return activity_params_dict

def calculate_all_activities(activity_params_dict):
    activities_dict = {}
    for isotope in activity_params_dict:
        temp_dict = {}
        for energy in activity_params_dict[isotope]:
            A0_params = activity_params_dict[isotope][energy][0]
            f = activity_params_dict[isotope][energy][1]
            t = activity_params_dict[isotope][energy][2]
            T_half_params = activity_params_dict[isotope][energy][3]
            A, A_err = estimate_activity(A0_params, T_half_params, f, t, 10000)
            temp_dict[energy] = [A, A_err]
        activities_dict[isotope] = temp_dict
    return activities_dict

def total_efficiency_arrays(params_dict, activity_dict, energies_dict):
    areas = []
    area_errs = []
    activities = []
    activity_errs = []
    energies = []
    energy_errs = []

    for isotope in params_dict:
        for fit_params in params_dict[isotope]:
            if 'A' in fit_params:
                areas.append(fit_params['A'][0])
                area_errs.append(fit_params['A'][1])
            elif 'A1' in fit_params:
                areas.append(fit_params['A1'][0])
                areas.append(fit_params['A2'][0])
            
                area_errs.append(fit_params['A1'][1])
                area_errs.append(fit_params['A2'][1])
                
        for energy in activity_dict[isotope]:
            activities.append(activity_dict[isotope][energy][0])
            activity_errs.append(activity_dict[isotope][energy][1])
        energies += energies_dict[isotope][0]
        energy_errs += energies_dict[isotope][1]
    return {'Areas':[areas, area_errs],
           'Activities': [activities, activity_errs],
           'Energies' : [energies, energy_errs]}


def calculate_total_efficiency(a_dict):
    
    acts_areas_energies = filter_lists(*a_dict['Activities'],
                                       *a_dict['Areas'], *a_dict['Energies'])
    acts_areas_energies = convert_to_arrays(acts_areas_energies)
    
    total_eff = (acts_areas_energies[2]/acts_areas_energies[0])*100
    total_eff_errs = adding_errors(*acts_areas_energies[:4], total_eff)
    energies, energy_errs = acts_areas_energies[4], acts_areas_energies[5]
    return [[energies, energy_errs], [total_eff, total_eff_errs]]


def plot_efficiency_curve(energies, energy_errs, effs, eff_errs, ax, colour):
    ax.loglog(energies, effs, '.', c= colour)
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('Absolute Efficiency (%)')
    ax.errorbar(energies, effs, xerr=energy_errs, yerr=eff_errs, fmt='none',
                   ecolor=colour, alpha=0.5)
    ax.grid(True, which='both')
    return ax


def efficiency_fit(x, a, b, c):
    ln_x = np.log(x)
    return np.e**(a + b*ln_x + c*(ln_x**2))


def fitting_efficiencies(ax, x, x_err, y, y_err, name, colour):
    popt, pcov = curve_fit(efficiency_fit, x, y, sigma=y_err)
    
    fit_errors = np.sqrt(np.diag(pcov))
    ax = plot_efficiency_curve(x, x_err, y, y_err, ax, colour)
    
    limits = (np.log10(np.min(x)), np.log10(np.max(x)))
    x_points = np.logspace(*limits, 1000)
    y_points = efficiency_fit(x_points, *popt)
    ax.plot(x_points, y_points, label=name, c=colour)
    ax.legend()
    return {'Fit Params' : popt,
           'Errors' : fit_errors}


def energies_and_absolute_efficiencies(detector):
    params_dict = read_json('Data/%s_params.json' % detector)
    energies_dict = read_json('Data/%s_energies.json' % detector)
    activies_dict = read_json('Data/Source_Activities.json')
    
    activity_params_dict = activities_params(params_dict,
                                             energies_dict, activies_dict,
                                             detector)
    
    activities_dict = calculate_all_activities(activity_params_dict)
    
    areas_acts_energies_dict = total_efficiency_arrays(params_dict,
                                                       activities_dict,
                                                       energies_dict)
    
    energies, efficiencies = calculate_total_efficiency(areas_acts_energies_dict)
    energies  = energies[0]
    energy_errs = energies[1]
    effs  = efficiencies[0]
    eff_errs = efficiencies[1]
    return [energies, energy_errs, effs, eff_errs]


def absolute_efficiency_plot(detector, ax):
    energies_and_efficiencies = energies_and_absolute_efficiencies(detector)
    colour = colour_map(detector)
    ax = plot_efficiency_curve(*energies_and_efficiencies, ax, colour)
    
    fit_results = fitting_efficiencies(ax, *energies_and_efficiencies,
                                       detector, colour)
    return fit_results


def plot_all_abs_eff_curves(detector_list):
    fig, ax = plt.subplots(1, figsize=(10,7))
    params_dict = {}
    for detector in detector_list:
        fit_params = absolute_efficiency_plot(detector, ax)
        params_dict[detector] = fit_params
    return params_dict

def geometric_factor(r, h, d, shape, angle):
    """Function for calculating geometric factor as a function of angle"""
    angle = np.radians(angle)
    if shape == 'square':
        area = (((2*r)**2)*np.abs(np.cos(angle))) + 2*r*h*(np.abs(np.sin(angle)))
    else:
        area = (np.pi*(r**2))*np.abs(np.cos(angle)) + 2*r*h*(np.abs(np.sin(angle)))
    return (4*np.pi*d**2)/area

def read_detector_dimensions(detector):
    dimensions = read_json('Data/Detector_Dimensions.json')
    r = dimensions[detector]['Diameter']/2
    h = dimensions[detector]['Height']
    l = dimensions[detector]['Distance']
    shape = dimensions[detector]['Shape']
    return [r, h, l, shape]

def energies_intrinsic_efficiencies(energies_efficiency_arrays, detector):
    detector_dimensions = read_detector_dimensions(detector)
    angle = 0
    geo_factor = geometric_factor(*detector_dimensions, angle)
    
    energies = energies_efficiency_arrays[0]
    energy_errs = energies_efficiency_arrays[1]
    
    abs_efficiencies = energies_efficiency_arrays[2]
    abs_efficiency_errs = energies_efficiency_arrays[3]
    
    intrinsic_effs = abs_efficiencies*geo_factor
    intrinsic_eff_errs = abs_efficiency_errs*geo_factor
    
    return [energies, energy_errs, intrinsic_effs, intrinsic_eff_errs]

def intrinsic_efficiency_plot(detector, ax):
    energies_and_efficiencies = energies_and_absolute_efficiencies(detector)
    colour = colour_map(detector)
    
    ens_and_int_effs = energies_intrinsic_efficiencies(energies_and_efficiencies, detector)
    ax = plot_efficiency_curve(*ens_and_int_effs, ax, colour)
    
    fit_results = fitting_efficiencies(ax, *ens_and_int_effs, detector, colour)
    return fit_results

def plot_all_int_eff_curves(detector_list):
    fig, ax = plt.subplots(1, figsize=(10,7))
    params_dict = {}
    for detector in detector_list:
        fit_params = intrinsic_efficiency_plot(detector, ax)
        params_dict[detector] = fit_params
    return params_dict
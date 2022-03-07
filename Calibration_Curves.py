#Importing Libraries
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import json

def energy_channel_arrays(energies, fit_results):
    calibration_channel_no = []
    calibration_channel_errors = []
    calibration_energies = []
    calibration_energy_errors = []

    for isotope in fit_results:
        for fit_params in fit_results[isotope]:
            if 'mu' in fit_params:
                calibration_channel_no.append(fit_params['mu'][0])
                calibration_channel_errors.append(fit_params['mu'][1])
            elif 'mu1' in fit_params:
                calibration_channel_no.append(fit_params['mu1'][0])
                calibration_channel_no.append(fit_params['mu2'][0])
            
                calibration_channel_errors.append(fit_params['mu1'][1])
                calibration_channel_errors.append(fit_params['mu2'][1])
        calibration_energies += energies[isotope][0]
        calibration_energy_errors += energies[isotope][1]
    return {'Channels':[calibration_channel_no, calibration_channel_errors],
           'Energies': [calibration_energies, calibration_energy_errors]}

def polynomial_func(x, a, b, c):
    return a*x**2 + b*x + c

def slope_estimate(x, y):
    """Initial guess for slope of linear fit"""
    x1, x2 = x[0], x[-1]
    y1, y2 = y[0], y[-1]
    
    slope = (y2-y1)/(x2-x1)
    return slope

def intercept_estimate(x, y):
    """Initial guess for y-intercept of linear fit"""
    
    slope = slope_estimate(x, y)
    intercept = y[-1] - slope*x[-1]
    
    return intercept

def polynomial_initial_estimates(energies, channels):
    """Estimates of three polynomial parameters."""
    a = 0 #Assuming function is linear
    b = slope_estimate(energies, channels)
    c = intercept_estimate(energies, channels)
    
    return [a, b, c]

def calibration_curve(energies, channels, channel_errors):
    
    params = ('a', 'b', 'c')
    
    _p0 = polynomial_initial_estimates(energies, channels)
    popt, pcov = curve_fit(polynomial_func, energies, channels, sigma=channel_errors, p0 = _p0, absolute_sigma=True)
    perr = np.sqrt(np.diag(pcov))
    results = {p : (np.round(o,5), np.round(e,7)) for p, o, e in zip(params, popt, perr)}
    return results


def adding_errors(x, δx, y, δy, z):
    """Function to calculate errors when adding two measurements
    
    Used specifically for adding errors in isotope spectra and background counts
    when subtracting background."""
    #z = x/y
    δz = z * np.sqrt((δx/x)**2 + (δy/y)**2)
    return δz

def linear_func(x, m, c):
    return m*x + c
    
def energy_relation(results):
    """As the fit is done with channels on y-axis, to plot the calibration curve with energy on the y,
    the acquired fit must be inverted"""
    slope = 1/results['b'][0]
    slope_err = slope * (results['b'][1]/results['b'][0])
    
    intercept = -results['c'][0]/results['b'][0]
    intercept_err = adding_errors(*results['c'], *results['b'], intercept)
    
    return [[slope, slope_err], [intercept, intercept_err]]


def plot_cal_curve(linear_params, cal_Es, cal_E_errs, cal_channels, cal_channel_errs):
    fig, ax = plt.subplots(1)
    ax.scatter(cal_channels, cal_Es)
    ax.errorbar(cal_channels, cal_Es, xerr=cal_channel_errs, yerr=cal_E_errs, fmt='none',
               ecolor='black', alpha=0.8, capsize=4)
    
    slope = linear_params[0][0]
    intercept = linear_params[1][0]
    
    limits = (np.min(cal_channels), np.max(cal_channels))
    channel_array = np.linspace(*limits, int(limits[0]))
    energy_array = linear_func(channel_array, slope, intercept)
    ax.plot(channel_array, energy_array, '-')
    ax.grid()
    ax.set_xlabel('Channel No.')
    ax.set_ylabel('Energy (keV)')



def read_json(file_path):
    """Function for reading-in saved parameters contained in JSON file"""
    fin = open(file_path, "r")
    jdata = fin.read()
    data = json.loads(jdata)
    fin.close()

    return data

def save_json(data, file_path):
    fout = open(file_path, "w")
    json.dump(data, fout, indent=4)
    fout.close()
    
    
def produce_calibration_plot(detector_string):
    
    param_file_path = 'Data/%s_params.json' % (detector_string)
    param_dict = read_json(param_file_path)
    
    energies_file_path = 'Data/%s_energies.json' % (detector_string)
    energies_dict = read_json(energies_file_path)
    
    calibration_points_dict = energy_channel_arrays(energies_dict, param_dict)
    
    energies = calibration_points_dict['Energies'][0]
    energy_errs = calibration_points_dict['Energies'][1]
    channels = calibration_points_dict['Channels'][0]
    channel_errs = np.asarray(calibration_points_dict['Channels'][1])
    
    #Fitting with channels on y-axis to incorporate larger errors
    calibration_params = calibration_curve(energies, channels, channel_errs)
    linear_params = energy_relation(calibration_params)
    energies_dict['Calibration Params'] = linear_params
    save_json(energies_dict, energies_file_path)
    
    plot_cal_curve(linear_params, energies, energy_errs, channels,
                   channel_errs)
    
    title_string = '%s Calibration Curve' % detector_string
    plt.title(title_string)
    plt.savefig('Plots/%s.png' % title_string)
    return linear_params
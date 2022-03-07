#Importing libraries
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime
import json
from numpy import inf as INF


#Functions for reading data from spectra files

def data_arrays(filename):
    """Input: name of file containing spectrum data
    
    Output: Channel and counts arrays"""
    file = open(filename, 'r')
    file_lines = file.readlines()
    #Finding position of data in file lines
    start_line = 0
    for line in file_lines:
        start_line +=1
        if 'DATA' in line:
            break
    
    if filename.endswith('.Spe'):
        #Number of channels in detector e.g. 1024, 8192 etc
        channel_dimensions = [int(x) for x in 
                              file_lines[start_line].strip().split(' ')]
    
        #Count data in a list:
        data_lines = file_lines[start_line+1 : start_line+1+
                                channel_dimensions[1]]
    
        #Converting to array and getting channel array
        counts_array = np.asarray([max(int(x.strip()),1) for x in data_lines])
        channel_no_array = np.linspace(0, channel_dimensions[1]-1,
                                       channel_dimensions[1])
    
    elif filename.endswith('.mca'):
        data_lines = file_lines[start_line : start_line+2048]
        counts_array = np.asarray([max(int(x.strip()),1) for x in data_lines])
        channel_no_array = np.linspace(0, 2047, 2048)
        
    return channel_no_array, counts_array


def date_of_measurement(filename):
    """Input: spectrum file name
    
    Output: date and time the spectrum was taken in datetime object"""
    #Finding position of date-time in file lines
    file = open(filename, 'r')
    file_lines = file.readlines()
    start_line = 0
    if filename.endswith('.Spe'):
        for line in file_lines:
            start_line +=1
            if 'DATE' in line:
                break
        date_string = file_lines[start_line].strip()
    
    elif filename.endswith('.mca'):
        for line in file_lines:
            start_line +=1
            if 'START_TIME' in line:
                break
        date_string = file_lines[start_line-1].split('-')[1].strip()
        
    #Converting to datetime object
    date = datetime.strptime(date_string, "%m/%d/%Y %H:%M:%S")
    return date


def spectrum_live_time(filename):
    """Input: spectrum file name
    
    Output: live time of the detector for spectrum"""
    file = open(filename, 'r')
    file_lines = file.readlines()
    #Finding position of live time in file lines
    start_line = 0
    if filename.endswith('.Spe'):
        for line in file_lines:
            start_line +=1
            if 'MEAS_TIM' in line:
                break
        live_time = [int(x) for x in file_lines[start_line].strip().split(' ')]
        live_time = live_time[0]
    elif filename.endswith('.mca'):
        for line in file_lines:
            start_line+=1
            if 'REAL_TIME' in line:
                break
        live_time = float(file_lines[start_line-1].split('-')[1])
    return live_time


def calculate_count_rate(counts_array, live_time):
    """Simple function to convert the raw counts array into count rate"""
    return counts_array / live_time

def errors_in_quadrature(δx, δy):
    """Function to calculate errors when adding two measurements
    
    Used specifically for adding errors in isotope spectra
    and background counts when subtracting background."""
    #z = x + y
    δz = np.sqrt(δx**2 + δy**2)
    return δz
    
    
def extract_spectra_data(filename):
    """Function to extract all data from file in one function
    Input: Spectrum file name
    Output: Channel, count rate arrays with standard errors and
    datetime of spectrum"""
    
    #Live time is first entry in time array: [live time, full time]
    live_time = spectrum_live_time(filename)
    channels, counts = data_arrays(filename)
    
    count_rate_errs = np.sqrt(counts)/live_time
    date = date_of_measurement(filename)
    count_rates = calculate_count_rate(counts, live_time)
    return channels, count_rates, count_rate_errs, date


def background_count_rate(filename):
    """Function to extract count rates and errors for background spectra"""
    live_time = spectrum_live_time(filename)
    channels, counts = data_arrays(filename)
    
    count_rate_errs = np.sqrt(counts)/live_time
    count_rates = calculate_count_rate(counts, live_time)
    
    return count_rates, count_rate_errs

def subtract_background(count_rate, count_rate_err,
                        bkd_count_rate, bkd_count_rate_err):
    """Function to get net count rates and errors for
    background-subtracted spectra"""
    
    net_counts = count_rate - bkd_count_rate
    net_counts_err = errors_in_quadrature(count_rate_err, bkd_count_rate_err)
    
    #If count rates are negative due to background, they are taken to be 0
    net_counts = [0 if x<0 else x for x in net_counts]
    return net_counts, net_counts_err


##############################################################################

#Code to highlight region of interest

def in_interval(full_array, _min=-INF, _max=INF):
    """Boolean mask with value True for x in [start, stop)
    Input: Channel numbers array, lower and upper limit
    for region of interest
    
    Output: Array of same shape as input, with True entries 
    within region of interest
    
    Taken from: Fitting notebook by Robert Jeffrey"""
    
    return np.logical_and(_min <= full_array, full_array < _max) 

def filter_in_interval(x, y, errs, _min, _max):
    """Selects only elements of x and y where xmin <= x < xmax.
    
    Taken from: Fitting notebook by Robert Jeffrey"""
    _mask = in_interval(x, _min, _max)
    return [np.asarray(x)[_mask] for x in (x, y, errs)]

def colourmask(x, _min=-INF, _max=INF, cin='r', cout='gray'):
    """Colour cin if within region of interest, cout otherwise.
    
    Taken from: Fitting notebook by Robert Jeffrey"""
    _mask = np.array(in_interval(x, _min, _max), dtype=int)

    # convert to colours
    colourmap = np.array([cout, cin])
    return colourmap[_mask]


def plot_spectrum(ax, channel_no_array, counts_array, count_errs_array, roi,
                  xlabel='Channel No.', ylabel='Count Rate (/s)', 
                  **kwargs):
    """Function to plot spectra.
    Taken from: Fitting notebook by Robert Jeffrey"""
    #Colourmask on region of interest
    colours = colourmask(channel_no_array, *roi)
    #Specifying x limits
    limits = (roi[0]-50, roi[1]+50)
    
    ax.set_xlim(*limits)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    ax.scatter(channel_no_array, counts_array, c=colours, s=5, **kwargs)
    return ax.errorbar(channel_no_array, counts_array, yerr=count_errs_array,
                       xerr=None, fmt='none', ecolor='gray', alpha=0.6,
                       capsize=2, **kwargs)



#Defining individual functions:

def gaussian_func(x, μ, σ, A):
    """Defining Gaussian functon in terms of mean, stdev, area"""
    return A/(np.sqrt(2*np.pi)*σ)*np.e**(-(x-μ)**2/(2*σ**2))

def linear_func(x, m, c):
    """Defining linear function"""
    return m*x + c

def quadratic_func(x, a, b, c):
    """Defining quadratic function"""
    return a*x**2 + b*x + c

#Defining gaussian plus linear function:

def gaussian_plus_line_components(x, mu, sig, A, m, c):
    """Calculating individual componenets in a gaussian+linear fit"""
    components = [
        gaussian_func(x, mu, sig, A),
        linear_func(x, m, c),
    ]
    return components

def gaussian_plus_line(x, mu, sig, A, m, c):
    """Function to combine components and obtain
    gaussian on a linear background."""
    _components = gaussian_plus_line_components(x, mu, sig, A, m, c)
    return sum(_components)


#Defining double gaussian function:

def double_gaussian_components(x, mu1, sig1, A1,
                             mu2, sig2, A2):
    """Defining components of a double gaussian fit"""
    components = [
        gaussian_func(x, mu1, sig1, A1),
        gaussian_func(x, mu2, sig2, A2)
    ]
    return components

def double_gaussian(x, mu1, sig1, A1,
                             mu2, sig2, A2):
    """Function to combine two gaussian components in double gaussian fit."""
    components = double_gaussian_components(x, mu1, sig1, A1,
                             mu2, sig2, A2)
    return sum(components)

#Defining double gaussian plus quadratic function

def double_gaus_plus_quadratic_components(x, mu1, sig1, A1,
                             mu2, sig2, A2, a, b, c):
    """Defining components of a double gaussian fit
    on a quadratic background"""
    components = [
        gaussian_func(x, mu1, sig1, A1),
        gaussian_func(x, mu2, sig2, A2),
        quadratic_func(x, a, b, c)
    ]
    return components

def double_gaus_plus_quadratic(x, mu1, sig1,
                                   A1, mu2, sig2, A2,
                                   a, b, c):
    """Function to combine two gaussian and one quadratic components"""
    components = double_gaus_plus_quadratic_components(x, mu1, sig1,
                                                       A1, mu2, sig2, A2,
                                                       a, b, c)
    return sum(components)


def model_fit(model, channels, counts, errors, roi, **kwargs):
    """Least squares estimate of model parameters."""
    #Selecting relevant channels & counts (within roi)
    _channels, _counts, _errors = filter_in_interval(channels,
                                                     counts, errors, *roi)
    
    #Fit selected model to the data
    popt, pcov = curve_fit(model, _channels, _counts, sigma=_errors, **kwargs)
    return popt, pcov

def format_result(params, popt, pcov):
    """Display parameter best estimates and uncertainties."""
    #Extracting uncertainties from covariance matrix
    perr = np.sqrt(np.diag(pcov))
    #Rounding to 5 dec places
    results = {p : (np.round(o,5), np.round(e,5))
               for p, o, e in zip(params, popt, perr)}
    
    return results

def plot_model(ax, model, xrange, ps, npoints=10001, **kwargs):
    """Plots a 1d model on an Axes smoothly over xrange."""
    
    _channels = np.linspace(*xrange, npoints)
    _counts   = model(_channels, *ps)
    ax.plot(_channels, _counts, **kwargs)
    return ax.plot(_channels, _counts, **kwargs)

#############################################################################

#Finding initial guess parameters

def centroid_estimate(x, y):
    """Initial guess for mean of gaussian fit"""
    
    return np.sum(x * y) / np.sum(y)
    
def standard_dev_estimate(x, y):
    """Initial guess for stdev of gaussian fit"""
    
    x0 = centroid_estimate(x, y)
    
    return np.sqrt(np.sum((x-x0)**2 * y) / np.sum(y))

def slope_estimate(x, y):
    """Initial guess for slope of linear fit"""
    x1, x2 = x[0], x[-1]
    y1, y2 = y[0], y[-1]
    
    slope = (y2-y1)/(x2-x1)
    return slope

def intercept_estimate(x, y):
    """Initial guess for y-intercept of linear fit"""
    
    slope = slope_estimate(x, y)
    intercept = y[0] - slope*x[0]
    
    return intercept
    
def gaussian_initial_estimates(channels, counts):
    """Estimates of three parameters of the gaussian distribution,
    and two linear parameters."""
    mu0 = centroid_estimate(channels, counts)
    sig0 = standard_dev_estimate(channels, counts)
    a0 = np.sum(counts)
    m = slope_estimate(channels, counts)
    c = intercept_estimate(channels, counts)
    
    return (mu0, sig0, a0, m, c)

def double_gaussian_initial_estimates(channels, counts):
    """Estimates of six parameters of two gaussian distributions
    in double gaussian fit."""
    
    ch1 = channels[:(len(channels)//2)]
    ch2 = channels[len(channels)//2:]
    counts1, counts2 = counts[:len(counts)//2], counts[len(counts)//2:]
    
    mu1 = centroid_estimate(ch1, counts1)
    sig1 = standard_dev_estimate(ch1, counts1)
    a1 = np.sum(counts1)
    
    mu2 = centroid_estimate(ch2, counts2)
    sig2 = standard_dev_estimate(ch2, counts2)
    a2 = np.sum(counts2)
    
    return (mu1, sig1, a1, mu2, sig2, a2)

def double_gaus_quad_initial_estimates(channels, counts):
    """Estimates of 9 parameters for 2 gaussians and 1 quadratic"""
    double_g_guesses = double_gaussian_initial_estimates(channels, counts)
    
    a = 0.1
    b = slope_estimate(channels, counts)
    c = intercept_estimate(channels, counts)
    
    return double_g_guesses + (a, b, c)


def read_json(file_path):
    """Function for reading-in saved parameters contained in JSON file"""
    fin = open(file_path, "r")
    jdata = fin.read()
    data = json.loads(jdata)
    fin.close()

    return data


#Defining models in dictionaries

gaussian_model = {
    'model'     : gaussian_plus_line,
    'estimates' : gaussian_initial_estimates,
    'params'    : ('mu', 'sig', 'A', 'm', 'c'),
    'components': [linear_func, gaussian_func]
}

double_gaussian_model = {
    'model'     : double_gaussian,
    'estimates' : double_gaussian_initial_estimates,
    'params'    : ('mu1', 'sig1', 'A1', 'mu2', 'sig2', 'A2'),
    'components': [gaussian_func]
}

double_gaus_quad_model = {
    'model'     : double_gaus_plus_quadratic,
    'estimates' : double_gaus_quad_initial_estimates,
    'params'    : ('mu1', 'sig1', 'A1', 'mu2', 'sig2', 'A2', 'a', 'b', 'c'),
    'components': [gaussian_func, quadratic_func]
}


def fitting_function(model, channels, count_rates, rate_errs, roi, **kwargs):
    """Inputs: fitting model, channel and count rate arrays
    with errors and region of interest tuple.
    
    Output: Fitting parameters in dictionary format, and plots of fitted model 
    over spectral data, with componenets of each model
    also plotted individually"""
    
    params = model['params']
    _channels, _count_rates, _rate_errors = filter_in_interval(channels,
                                            count_rates, rate_errs, *roi)
    
    #Calculating initial estimates:
    _p0 = model['estimates'](_channels, _count_rates)
    
    #Fit parameteres:
    popt, pcov = model_fit(model['model'],
                           _channels, _count_rates, _rate_errors, roi, p0=_p0)
    
    #Formating fitted parameters into a dictionary:
    results = format_result(params, popt, pcov)
    
    fig, ax = plt.subplots(1)
    
    #Plotting spectrum and fit:
    plot_spectrum(ax, channels, count_rates, rate_errs, roi)
    plot_model(ax, model['model'], (0, len(channels)), popt, c='k')
    
    #Plotting individual components of each fitting model
    if model == gaussian_model:
        for ind_model in model['components']:
            if ind_model == linear_func:
                new_popt = popt[3:]
                plot_model(ax, ind_model, (0,len(channels)),
                           new_popt, alpha=0.6, linestyle='--', c='green')
            elif ind_model == gaussian_func:
                new_popt = popt[:3]
                plot_model(ax, ind_model, (0,len(channels)),
                           new_popt, alpha=0.6, linestyle='--', c='cyan')
    elif model == double_gaus_quad_model:
        for ind_model in model['components']:
            if ind_model == gaussian_func:
                new_popt1, new_popt2 = popt[0:3], popt[3:6]
                plot_model(ax, ind_model, (0,len(channels)),
                           new_popt1, alpha=0.6, linestyle='--', c='green')
                plot_model(ax, ind_model, (0,len(channels)),
                           new_popt2, alpha=0.6, linestyle='--', c='cyan')
            elif ind_model == quadratic_func:
                new_popt3 = popt[6:]
                plot_model(ax, ind_model, (0,len(channels)),
                           new_popt3, alpha=0.6, linestyle='--', c='orange')
    elif model == double_gaussian_model:
        for ind_model in model['components']:
            new_popt1, new_popt2 = popt[0:3], popt[3:6]
            plot_model(ax, ind_model, (0,len(channels)),
                       new_popt1, alpha=0.6, linestyle='--', c='green')
            plot_model(ax, ind_model, (0,len(channels)),
                       new_popt2, alpha=0.6, linestyle='--', c='cyan')
            
    #Defining y axis limits        
    max_counts = np.max(_count_rates)
    min_counts = np.min(_count_rates)
    plt.ylim(min_counts-0.1*min_counts, max_counts+0.1*max_counts)
    return results


def extract_details_from_file(filename):
    """Input: Spectrum file name
    
    Output: Detector name, isotope name and orientation
    of the acquired spectrum"""
    categories = filename.split('/')
    detector = categories[1]
    isotope = categories[2]
    geometry = filename.split('_')[-1].split('.')[0]
    return detector, isotope, geometry



def full_fitting_function(filename, bkd_filename, roi_list, **kwargs):
    """Function to extract data and plot fitted model over spectrum
    
    Inputs: File path, and background spectrum file path, and list containing 
    roi and fitting model to be used.
    
    Output: Plot of fitted peak(s) saved as a PNG file, and fit parameters"""
    results = []
    detector, isotope, geometry = extract_details_from_file(filename)
    for roi_and_model in roi_list:
        channels, count_rate, count_rate_errs, date = extract_spectra_data(
            filename)
        bkd_count_rate, bkd_count_err = background_count_rate(bkd_filename)
    
        net_count_rate, net_count_rate_err = subtract_background(count_rate,
                                            count_rate_errs, bkd_count_rate,
                                            bkd_count_err)
        
        roi = roi_and_model[0]
        
        #Reading model to be used
        if roi_and_model[1] == 'single':
            model = gaussian_model
        elif roi_and_model[1] == 'double':
            model = double_gaussian_model
        elif roi_and_model[1] == 'double+quad':
            model = double_gaus_quad_model
            
        results_dict = fitting_function(model, channels, net_count_rate, net_count_rate_err, roi)
        results_dict['Date'] = date.strftime("%m/%d/%Y, %H:%M:%S")
        name = detector+'-'+isotope+' @ '+geometry
        plt.title(name)
        plt.savefig('Plots/'+name+str(roi)+'.png')
        results.append(results_dict)
    return results


def fitting_on_axis_peaks(spectra_files, detector, ROI_dict, **kwargs):
    """Inputs: Filename dictionary, detector name and regions
    of interest dictionary
    
    Output: Dictionary containing fitted parameters, plots of all
    fitted peaks, saved as PNG files"""
    
    bkd_file = 'Data'+'/'+detector+'/'+spectra_files[detector]['Background']
    params_dict = {}
    for isotope in spectra_files[detector]:
        if isotope != 'Background':
            file_list = spectra_files[detector][isotope]
            file_list = ['Data'+'/'+detector+'/'+isotope+'/'+file
                         for file in file_list]
            roi_list = ROI_dict[detector][isotope]
            temp_dict = {}
            for file in [file_list[0]]:
                detector, element, geometry = extract_details_from_file(file)
                results = full_fitting_function(file, bkd_file, roi_list)
                temp_dict = results
            params_dict[isotope] = temp_dict
    return params_dict



def saving_on_axis_data(spectra_files, detector):
    """Input: Spectrum filename dictionary, detector name
    and regions of interest dictionary
    
    Output: Plots of fitted spectra peaks, Fitted parameters
    saved to JSON file"""
    
    ROI_dict = read_json('Data/ROIs.json')
    fitted_parameters = fitting_on_axis_peaks(spectra_files, detector, ROI_dict)
    file_path = 'Data/%s_%s.json' % (detector, 'params')        
    fout = open(file_path, "w")
    json.dump(fitted_parameters, fout, indent=4)
    fout.close()
    
    
def fitting_off_axis_peaks(spectra_files, detector, ROI_dict):
    """Inputs: Filename dictionary, detector name and
    regions of interest dictionary
    
    Output: Dictionary containing fitted parameters, plots of all
    fitted peaks, saved as PNG files"""
    
    bkd_file = 'Data'+'/'+detector+'/'+spectra_files[detector]['Background']
    params_dict = {}
    for isotope in ROI_dict[detector]:
        if isotope != 'Background':
            file_list = spectra_files[detector][isotope]
            file_list = ['Data'+'/'+detector+'/'+isotope+'/'+file for
                         file in file_list]
            roi_list = ROI_dict[detector][isotope]
            temp_dict = {}
            for file in file_list:
                detector, element, geometry = extract_details_from_file(file)
                results = full_fitting_function(file, bkd_file, roi_list)
                temp_dict[geometry] = results
            params_dict[isotope] = temp_dict
    return params_dict
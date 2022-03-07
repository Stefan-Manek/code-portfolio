# Gamma Detector Lab

The goal of the lab was to characterise the performance of four different gamma ray detectors, with the results for each detector displayed in separate Python notebooks.

The four detectors are as follows:
 Markup : * Bismuth Germanate (BGO)
          * Sodium Iodide (NaI)
          * Hyper-pure Germanium (HpGe)
          * Cadmium Telluride (CdTe)

Lab work included taking individual spectra for each detector, for various radioactive elements with emission lines at known energies. 
Code was hence required to fit a composite gaussian function to specific regions of interest within each of the taken spectra.
The mean energy, area and standard deviation of the fitted gaussian was returned for each spectrum.
The mean positions of these energy lines were then used to calibrate the dtector by plotting them against the known energy value.
The efficiencies were found by dividing the fitted area by the total counts detected in each spectrum.

As the spectra were also taken at varying incidence angles to the detector, their off-axis performance was also investigated. 
The efficiencies were plotted against angle, and corrected by a geometric factor.

The Python notebooks contain the final results of the analysis, including all plots.
The .py files are modules containing the functions required for specific parts of the analysis.

## Fitting_Spectra.py 
Contains functions required for fitting detector spectra within defined Regions of Interest and returns plots, and fitted parameters.

Returns plots of each spectra including line of best fit and highlighted region of interest.

## Calibration_Curves.py 

Utilises data returned from fitting to produce linear calibration plot for each detector including slope and intercept of line of best fit.

## Efficiencies.py 

Calculates absolute efficiency of each detector and produces logarithmic plot of absolute efficiency vs line energy.

## Off_Axis.py 

Calculates absolute efficiency for each detector at the various incidence angles sampled and returns plots of efficiency vs angle,
the geometric factor used to calculate the intrinsic efficiencies.

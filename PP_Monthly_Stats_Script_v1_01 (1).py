# ---------------------------------------------------------------------------------------------------------------------------
# Name: Global coverage analysis script
# Version: 1.1
# Created on: 01/07/2019
# Created by: Ed Lewis (edward.lewis@unep-wcmc.org)
# Description: A script based on an Esri model to calculate PA coverage globally, nationally and to calculate PAME statistics.
# Note: This is my first script....
# ----------------------------------------------------------------------------------------------------------------------------

# import arcpy module
import arcpy
from arcpy import env

# define workspace to house all outputs from the script we want to keep
arcpy.env.workspace = "C:\Users\EdwardL\Documents\ArcGIS\Default.gdb"
Workspace = "C:\Users\EdwardL\Documents\ArcGIS\Default.gdb"

# define the scratch workspace for outputs we dont want to keep
arcpy.env.scratchWorkspace = "C:\Users\EdwardL\Documents\ArcGIS\Modelbuilder_Primary.gdb"

# create the feature datasets in your workspace to help structure your outputs
# for initial outputs
arcpy.CreateFeatureDataset_management(Workspace,"a_initial_outputs", "[ENTER PROJECTION HERE]")
# for initial outputs
arcpy.CreateFeatureDataset_management(Workspace,"b_processed_outputs", "[ENTER PROJECTION HERE]")
# for outputs from the Union tool
arcpy.CreateFeatureDataset_management(Workspace,"c_initial_outputs", "[ENTER PROJECTION HERE]")
# for outputs in the Mollweide projection
arcpy.CreateFeatureDataset_management(Workspace,"d_initial_outputs", "[ENTER PROJECTION HERE]")
# for national outputs
arcpy.CreateFeatureDataset_management(Workspace,"e_initial_outputs", "[ENTER PROJECTION HERE]")
# for PAME national outputs
arcpy.CreateFeatureDataset_management(Workspace,"f_initial_outputs", "[ENTER PROJECTION HERE]")

#[I'M GOING TO HAVE TO DEFINE THESE FDs IN SHORT HAND SOMEHOW..]

# define the script's inputs
# WDPA Public points
input_points = ""
# WDPA Public polygons
input_polygons = ""
# Basemap_spatial
input_basemapspa = ""
# Basemap_tabular
input_basemaptab = ""
# PAME sites
input_pamesites = ""

# define the script's restricted inputs - only accessible for UNEP-WCMC
# Restricted CHN points
input_restrict_chn_pnt = ""
# Restricted CHN polygons
input_restrict_chn_poly = ""
# Restricted SHN polygons
input_restrict_shn_poly
# Restricted EST polygons
input_restrict_est_poly = ""

# define the merge outputs
all_points = ""
all_polygons = ""

# Combine the point inputs together
arcpy.Merge_management(input_points,input_restrict_chn_pnt, all_points)
# Combine the polygon inputs together
arcpy.Merge_management(input_polygons, input_restrict_chn_poly, input_restrict_shn_poly, input_restrict_shn_poly, input_restrict_est_poly, all_polygons,)

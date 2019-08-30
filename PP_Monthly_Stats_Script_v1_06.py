# Name: Global coverage analysis script
# Version: 1.3
# Created on: 01/07/2019
# Created by: Ed Lewis (edward.lewis@unep-wcmc.org)
# Description: A script based on an Esri model to calculate PA coverage globally and nationally as well as calculating national
# PAME statistics.

#--------------------------------------------------------------------------------------------------------------------------

# import arcpy module
import arcpy
import os
from arcpy import env

# enable the overwriting of outputs
arcpy.env.overwriteOutput = True

# define workspace to house all outputs from the script we want to keep
arcpy.env.workspace = "C:\Users\EdwardL\Documents\ArcGIS\Default.gdb"
workspace = "C:\Users\EdwardL\Documents\ArcGIS\Default.gdb"

# define the scratch workspace for outputs we dont want to keep
arcpy.env.scratchWorkspace = "C:\Users\EdwardL\Documents\ArcGIS\Modelbuilder_Primary.gdb"

# define the projection files used to define outputs/workspaces
in_mollweideprj = "C:\Users\EdwardL\Desktop\Temp_Files Of_Interest\moll_projection.prj"

# create the feature datasets in your workspace to help structure your outputs
# for initial outputs
in_fd1 = arcpy.CreateFeatureDataset_management(workspace,"a_merged_inputs")
# for outputs from the Union tool
in_fd2 = arcpy.CreateFeatureDataset_management(workspace,"b_processed_inputs")
# for outputs in the Mollweide projection
in_fd2 = arcpy.CreateFeatureDataset_management(workspace,"c_area_outputs", in_mollweideprj)
# for national outputs
in_fd3 = arcpy.CreateFeatureDataset_management(workspace,"d_national_outputs")
# for PAME national outputs
in_fd4 = arcpy.CreateFeatureDataset_management(workspace,"e_national_pame_outputs")


# define the script's inputs
# WDPA Public points
in_points = r"E:\2019\Major_Jobs_2019\08492_WDPA\1_Monthly_Updates\02_August_2019\WDPA_Aug2019_Public\WDPA_Aug2019_Public.gdb\WDPA_point_Aug2019"
# WDPA Public polygons
in_polygons = r"E:\2019\Major_Jobs_2019\08492_WDPA\1_Monthly_Updates\02_August_2019\WDPA_Aug2019_Public\WDPA_Aug2019_Public.gdb\WDPA_poly_Aug2019"
# Basemap_spatial
in_basemap_spat = r"C:\Users\EdwardL\Documents\Useful_Datasets\WVS_Jan_16\SDG_Basemap.gdb\EEZv8_WVS_DIS_V3_ALL_final_v7dis_with_SDG_regions_for_models"
# Basemap_tabular
in_basemap_tab = r"C:\Users\EdwardL\Documents\Useful_Datasets\WVS_Jan_16\SDG_Basemap.gdb\EEZv8_WVS_DIS_V3_ALL_final_v7dis_with_SDG_regions_for_models_tabular"
# PAME sites
in_pame_sites = r"C:\Users\EdwardL\Documents\ArcGIS\Restricted_Data.gdb\PAME_Sites"

# define the script's restricted inputs - only accessible for UNEP-WCMC
# restricted CHN points
in_restrict_chn_pnt = r"C:\Users\EdwardL\Documents\ArcGIS\Restricted_Data.gdb\CHN_restricted_Feb2018_NR_Point_Regions"
# restricted CHN polygons
in_restrict_chn_poly = r"C:\Users\EdwardL\Documents\ArcGIS\Restricted_Data.gdb\CHN_restricted_Feb2018_NNR_Poly_Regions"
# restricted SHN polygons
in_restrict_shn_poly = r"C:\Users\EdwardL\Documents\ArcGIS\Restricted_Data.gdb\SHN_restricted_July2018Poly_Regions"
# restricted EST polygons
in_restrict_est_poly = r"C:\Users\EdwardL\Documents\ArcGIS\Restricted_Data.gdb\EST_restricted_Aug2014_NewPoly_Regions"

# define the merge outputs
out_all_points = "all_wdpa_points"
out_all_polygons = "all_wdpa_polygons"

#--------------------------------------------------------------------------------------------------------------------------
# Stage 1: Global analysis
# combine the point inputs together
arcpy.Merge_management([in_points,in_restrict_chn_pnt], out_all_points)
# combine the polygon inputs together
arcpy.Merge_management([in_polygons, in_restrict_chn_poly, in_restrict_shn_poly, in_restrict_est_poly], out_all_polygons)

# repair geometries for newly merged files
arcpy.RepairGeometry_management("all_wdpa_points","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polygons","DELETE_NULL")

# remove the sites that have an uncertain status or have potentially very innacruate areas
arcpy.Select_analysis("all_wdpa_points", "all_wdpa_points_select","STATUS in ( 'Adopted', 'Designated', 'Inscribed') AND NOT DESIG_ENG = 'UNESCO-MAB Biosphere Reserve'")
arcpy.Select_analysis("all_wdpa_polygons", "all_wdpa_polygons_select","STATUS in ( 'Adopted', 'Designated', 'Inscribed') AND NOT DESIG_ENG = 'UNESCO-MAB Biosphere Reserve'")

#[how do i save these outputs to individual fds, or the scratch?]

# convert the point selection into a polygon by buffering by the REP_AREA
arcpy.AddField_management("all_wdpa_points_select","radius","DOUBLE")
arcpy.CalculateField_management("all_wdpa_points_select","radius","math.sqrt(!REP_AREA!/math.pi )*1000","PYTHON_9.3")
arcpy.Buffer_analysis("all_wdpa_points_select","all_wdpa_points_select_buff","radius","","","","","GEODESIC")

# combine the poly selection with the buffered point selection
arcpy.Merge_management(["all_wdpa_points_select_buff","all_wdpa_polygons_select"],"all_wdpa_polybuffpnt")

# this output (hereafter 'polybuffpnt') represents the starting point for the monthly release - it is all the sites we include
# in the analysis in one file
# repair it
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt","DELETE_NULL")

# split up the polybuffpnt using the Union tool - this splits up the WDPA like a Venn diagram
arcpy.Union_analysis("all_wdpa_polybuffpnt","all_wdpa_polybuffpnt_union")

# repair the output of the union
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union","DELETE_NULL")

# intersect the output of the union with a basemap of the world. This splits each part of the venn diagram by land and marine
# realms...there will be close to 1 million segments!
arcpy.Intersect_analysis(["all_wdpa_polybuffpnt_union",in_basemap_spat],"all_wdpa_polybuffpnt_union_intersect")

# repair the output of the intersect
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union_intersect","DELETE_NULL")

# add xy coordinates for each of the ~1 million segments
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_union_intersect","CENTROID")

# add a new field to concatenate the new x and y coordinate fields
arcpy.AddField_management("all_wdpa_polybuffpnt_union_intersect","XYco","TEXT")

# populate this new XYco field
arcpy.CalculateField_management("all_wdpa_polybuffpnt_union_intersect","XYco","!CENTROID_X! + !CENTROID_Y!","PYTHON_9.3")

# run a summary of the XYco field, showing how many instances there are of each XYyco, i.e. how many segments have
# exactly the same XYco, and by extension geometry.
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_union_intersect","xyco_count",[["XYco","COUNT"]],"XYco")

# join the xyco summary table back to the spatial data by XYco - adding the XYco COUNT field to the spatial data
arcpy.AddJoin_management("all_wdpa_polybuffpnt_union_intersect","XYco","xyco_count","XYco","KEEP_ALL")

# select out all of the segments which only have 1 XYco, i.e. the novel geometries with no overlaps within the WDPA
arcpy.Select_analysis("all_wdpa_polybuffpnt_union_intersect","all_wdpa_polybuffpnt_union_intersect_unique","COUNT_XYco = 1")

# select out all of the segments which have >1 XYco, i.e. geometries which overlap within the WDPA
arcpy.Select_analysis("all_wdpa_polybuffpnt_union_intersect","all_wdpa_polybuffpnt_union_intersect_duplicates","COUNT_XYco > 1")

# remove the overlaps within the duplicates
arcpy.Dissolve_management("all_wdpa_polybuffpnt_union_intersect_duplicates","all_wdpa_polybuffpnt_union_intersect_duplicates_diss","")

#[ADD BACK IN THE STATUS YR AS A STATISTIC FIELD ONCE THE SCRIPT IS FUNCTIONAL TO CREATE TIMESERIES DATA]

# repair the flattened duplicates
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union_intersect_duplicates_diss","DELETE_NULL")

# [MOVE THE XYco and duplicate identification before the intersect - fewer segments and removes the secondary intersect]

# recombine the unique geometries with the flattened duplicates
arcpy.Merge_management(["all_wdpa_polybuffpnt_union_intersect_duplicates_diss", "all_wdpa_polybuffpnt_union_unique"], "all_wdpa_polybuffpnt_union_intersect_merge")

# repair the recombined layer
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union_intersect_merge","DELETE_NULL")

# project it into mollweide, an equal area projection
arcpy.Project_management("all_wdpa_polybuffpnt_union_intersect_merge","all_wdpa_polybuffpnt_union_intersect_merge_project",in_mollweideprj)

# repair it again
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union_intersect_merge_project","DELETE_NULL")

# add and calculate a new area field
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_union_intersect_merge_project","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)

# run summary statistics on the layer
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_union_intersect_merge_project","_summary_statistics_",[["POLY_AREA","SUM"]],"type")




##-------------------------------------------------------------------------------------------------------------------------
#Stage 2: National analysis
#This stage starts from the repaired polybuffpnt.

# split the polybuffpnt depending on whether sites occur within one country or span multiple countries
arcpy.Select_analysis("all_wdpa_polybuffpnt","all_wdpa_polybuffpnt_nontransboundary","WDPA_ISO3 IN ('ABNJ', 'ABW', 'AFG', 'AGO', 'AIA', 'ALA', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATA', 'ATF', 'ATG', 'AUS', 'AUT', 'AZE', 'BDI', 'BEL', 'BEN', 'BES', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLM', 'BLR', 'BLZ', 'BMU', 'BOL', 'BRA', 'BRB', 'BRN', 'BTN', 'BVT', 'BWA', 'CAF', 'CAN', 'CCK', 'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CXR', 'CYM', 'CYP', 'CZE', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESH', 'ESP', 'EST', 'ETH', 'FIN', 'FJI', 'FLK', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GGY', 'GHA', 'GIB', 'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GRL', 'GTM', 'GUF', 'GUM', 'GUY', 'HKG', 'HMD', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IMN', 'IND', 'IOT', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JEY', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY', 'LCA', 'LIE', 'LKA', 'LSO', 'LTU', 'LUX', 'LVA', 'MAF', 'MAR', 'MCO', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL', 'MKD', 'MLI', 'MLT', 'MMR', 'MNE', 'MNG', 'MNP', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MWI', 'MYS', 'MYT', 'NAM', 'NCL', 'NER', 'NFK', 'NGA', 'NIC', 'NIU', 'NLD', 'NOR', 'NPL', 'NZL', 'OMN', 'PAK', 'PAN', 'PCN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRK', 'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'SAU', 'SDN', 'SEN', 'SGP', 'SGS', 'SHN', 'SJM', 'SLB', 'SLE', 'SLV', 'SPM', 'SRB', 'SSD', 'STP', 'SUR', 'SVK', 'SVN', 'SWE', 'SWZ', 'SXM', 'SYC', 'SYR', 'TCA', 'TCD', 'TGO', 'THA', 'TJK', 'TKL', 'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UGA', 'UKR', 'UMI', 'URY', 'USA', 'UZB', 'VCT', 'VEN', 'VGB', 'VIR', 'VNM', 'VUT', 'WLF', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE')")
arcpy.Select_analysis("all_wdpa_polybuffpnt","all_wdpa_polybuffpnt_transboundary","WDPA_ISO3 in ('BLM;GLP;MAF;MTQ', 'BLR;POL', 'CAN;USA', 'CHE;ITA', 'CIV;GIN', 'COG;CMR;CAF', 'CRI;PAN', 'FIN;SWE', 'FRA;ESP', 'FRA;ITA;MCO', 'LSO;ZAF', 'MNG;RUS', 'NLD;DEU;DNK', 'PRT;ESP', 'SVK;HUN', 'UKR;DEU;SVK', 'UZB;KGZ;KAZ', 'ZMB;ZWE')")

# repair the geometries of both subsets
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_nontransboundary","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary","DELETE_NULL")

# flatten each subset - transboundary sites aren't flattened by country as their ISO3 values span several countries and are
# unusable.....[RE-WRITE THIS]
arcpy.Dissolve_management("all_wdpa_polybuffpnt_nontransboundary","all_wdpa_polybuffpnt_nontransboundary_diss","ISO3")
arcpy.Dissolve_management("all_wdpa_polybuffpnt_transboundary","all_wdpa_polybuffpnt_transboundary_diss","")

# repair the geometries of both subsets
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_nontransboundary_diss","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary_diss","DELETE_NULL")

# erase the transboundary sites from the non-transboundary sites, identifying the novel area only they cover 
arcpy.Erase_analysis("all_wdpa_polybuffpnt_transboundary_diss","all_wdpa_polybuffpnt_nontransboundary_diss","all_wdpa_polybuffpnt_transboundary_diss_novelarea")

# repair the output from the erase
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea","DELETE_NULL")

# intersect the novel area transboundary sites and the non-transboundary sites
arcpy.Intersect_analysis(["all_wdpa_polybuffpnt_transboundary_novelarea",in_basemap_spat],"all_wdpa_polybuffpnt_transboundary_novelarea_intersect")
arcpy.Intersect_analysis(["all_wdpa_polybuffpnt_nontransboundary_diss",in_basemap_spat],"all_wdpa_polybuffpnt_nontransboundary_diss_intersect")

# repair the intersects
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_nontransboundary_diss_intersect","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","DELETE_NULL")

# add a new field, "typeISO3"
arcpy.AddField_management("all_wdpa_polybuffpnt_nontransboundary_diss_interect","typeISO3","TEXT")
arcpy.AddField_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_interect","typeISO3","TEXT")

# calculate typeISO3, by concatenating 'type' form the basemap with ISO3
# nontransboundary use the 'WDPA_ISO3' but transboundary use the 'GEO_ISO3' because they've been dissolved
arcpy.CalculateField_management("all_wdpa_polybuffpnt_nontransboundary_diss_intersect","typeISO3","!type! + !WDPA_ISO3!","PYTHON_9.3")
arcpy.CalculateField_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","typeISO3","!type! + !GEO_ISO3!","PYTHON_9.3")

# project both transboundary and nontransboundary features into Mollweide
arcpy.Project_management("all_wdpa_polybuffpnt_nontransboundary_diss_intersect","all_wdpa_polybuffpnt_nontransboundary_diss_intersect_project",in_mollweideprj)
arcpy.Project_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect_project",in_mollweideprj)                

# add and calculate a new area field
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_nontransboundary_diss_intersect","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)

# rename the GEO_ISO3 field in the transboundary subset back into WDPA_ISO3
arcpy.AlterField_management("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","GEO_ISO3","WDPA_ISO3","WDPA_ISO3")

# run summary statistics on each subset
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_nontransboundary_diss_intersect","non_transboundary_national_statistics",[["POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_transboundary_diss_novelarea_intersect","non_transboundary_national_statistics",[["POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3")

# merge the summary statistics from each subset
arcpy.Merge_management(["non_transboundary_national_statistics","transboundary_national_statistics"],"national_statistics_merge")

# join to the basemap to get fields reporting on basemap area
arcpy.JoinField_management("national_statistics_merge","typeISO3",in_basemap_spat,"GEO_typeISO3")

# run summary statistics again, now including the basemap area also
arcpy.Statistics_analysis("national_statistics_merge","national_statistics_merge_summary",[["SUM_POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3","AREA_KM2")

# rename the summarised PA area field
arcpy.AlterField_management("national_statistics_merge_summary","SUM_SUM_POLY_AREA","PA_AREA","PA_AREA")

# run a pivot table
arcpy.PivotTable_management("national_statistics_merge_summary","WDPA_ISO3","type","PA_AREA","national_statistics_merge_summary_pivot")

# join to a tabular version of the basemap
arcpy.JoinField_management("national_statistics_merge_summary_pivot","WDPA_ISO3",in_basemap_tab,"GEO_ISO3",["land_area", "marine_area"])

# rename several fields
arcpy.AlterField_management("national_statistics_merge_summary_pivot","WDPA_ISO3","iso33")
arcpy.AlterField_management("national_statistics_merge_summary_pivot","Land","pa_land_area")
arcpy.AlterField_management("national_statistics_merge_summary_pivot","EEZ","pa_marine_area")

# combine the ABNJ and EEZ area per country into the pa_marine_area field
arcpy.CalculateField_management("national_statistics_merge_summary_pivot","pa_marine_area","!ABNJ! + !pa_marine_area!","PYTHON_9.3")

# recalculate two fields so that there are '0' instead of blank cells
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","ABNJ","updateValue(!ABNJ!)","def updateValue(value): if value == None: return '0' else: return value")
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","ABNJ","updateValue(!pa_marine_area!)","def updateValue(value): if value == None: return '0' else: return value")
                                                                                                                     
# delete the now redudndant ABNJ field
arcpy.DeleteField_management("national_statistics_merge_summary_pivot","ABNJ")

# add the fields to calculate percentage coverage
arcpy.AddField_management("national_statistics_merge_summary_pivot","percentage_pa_land_cover","FLOAT")
arcpy.AddField_management("national_statistics_merge_summary_pivot","percentage_pa_marine_cover","FLOAT")

# calculate fields
arcpy.CalculateField_management("national_statistics_merge_summary_pivot","percentage_pa_land_area","(!pa_land_area! / !land_area!)*100","PYTHON_9.3")
arcpy.CalculateField_management("national_statistics_merge_summary_pivot","percentage_pa_marine_area","(!pa_marine_area! / !marine_area!)*100","PYTHON_9.3")

# run the ABNJ stats separately?




#-----------------------------------------------------------------------------------------------------------------------
#Stage 3: National PAME analysis 
#This stage also starts from the repaired polybuffpnt and repeats the national analysis using only those sites that have had a PAME analysis.

# join the polybuffpnt to the PAME sites 
arcpy.JoinField_management("all_wdpa_polybuffpnt","WDPAID",in_pame_sites,"wdpaid","ass_id")

# select out the sites that have had a pame assessment
arcpy.Select_analysis("all_wdpa_polybuffpnt", "all_wdpa_polybuffpnt_pamesites","ass_id >= 1")                          

# split the pame polybuffpnt depending on whether sites occur within one country or span multiple countries
arcpy.Select_analysis("all_wdpa_polybuffpnt_pamesites","all_wdpa_polybuffpnt_pamesites_nontransboundary","WDPA_ISO3 IN ('ABNJ', 'ABW', 'AFG', 'AGO', 'AIA', 'ALA', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATA', 'ATF', 'ATG', 'AUS', 'AUT', 'AZE', 'BDI', 'BEL', 'BEN', 'BES', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLM', 'BLR', 'BLZ', 'BMU', 'BOL', 'BRA', 'BRB', 'BRN', 'BTN', 'BVT', 'BWA', 'CAF', 'CAN', 'CCK', 'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CXR', 'CYM', 'CYP', 'CZE', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESH', 'ESP', 'EST', 'ETH', 'FIN', 'FJI', 'FLK', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GGY', 'GHA', 'GIB', 'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GRL', 'GTM', 'GUF', 'GUM', 'GUY', 'HKG', 'HMD', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IMN', 'IND', 'IOT', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JEY', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY', 'LCA', 'LIE', 'LKA', 'LSO', 'LTU', 'LUX', 'LVA', 'MAF', 'MAR', 'MCO', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL', 'MKD', 'MLI', 'MLT', 'MMR', 'MNE', 'MNG', 'MNP', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MWI', 'MYS', 'MYT', 'NAM', 'NCL', 'NER', 'NFK', 'NGA', 'NIC', 'NIU', 'NLD', 'NOR', 'NPL', 'NZL', 'OMN', 'PAK', 'PAN', 'PCN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRK', 'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'SAU', 'SDN', 'SEN', 'SGP', 'SGS', 'SHN', 'SJM', 'SLB', 'SLE', 'SLV', 'SPM', 'SRB', 'SSD', 'STP', 'SUR', 'SVK', 'SVN', 'SWE', 'SWZ', 'SXM', 'SYC', 'SYR', 'TCA', 'TCD', 'TGO', 'THA', 'TJK', 'TKL', 'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UGA', 'UKR', 'UMI', 'URY', 'USA', 'UZB', 'VCT', 'VEN', 'VGB', 'VIR', 'VNM', 'VUT', 'WLF', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE')")
arcpy.Select_analysis("all_wdpa_polybuffpnt_pamesites","all_wdpa_polybuffpnt_pamesites_transboundary","WDPA_ISO3 in ('BLM;GLP;MAF;MTQ', 'BLR;POL', 'CAN;USA', 'CHE;ITA', 'CIV;GIN', 'COG;CMR;CAF', 'CRI;PAN', 'FIN;SWE', 'FRA;ESP', 'FRA;ITA;MCO', 'LSO;ZAF', 'MNG;RUS', 'NLD;DEU;DNK', 'PRT;ESP', 'SVK;HUN', 'UKR;DEU;SVK', 'UZB;KGZ;KAZ', 'ZMB;ZWE')")

# repair the geometries of both subsets
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_nontransboundary","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_transboundary","DELETE_NULL")

# flatten each subset - transboundary sites aren't flattened by country as their ISO3 values span several countries and are
# unusable.....[RE-WRITE THIS]
arcpy.Dissolve_management("all_wdpa_polybuffpnt_pamesites_nontransboundary","all_wdpa_polybuffpnt_pamesites_nontransboundary_diss","ISO3")
arcpy.Dissolve_management("all_wdpa_polybuffpnt_pamesites_transboundary","all_wdpa_polybuffpnt_pamesites_transboundary_diss","")

# repair the geometries of both subsets
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss","DELETE_NULL")

# erase the transboundary sites from the non-transboundary sites, identifying the novel area only they cover 
arcpy.Erase_analysis("all_wdpa_polybuffpnt_pamesites_transboundary_diss","all_wdpa_polybuffpnt_pamesites_nontransboundary_diss","all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea")

# repair the output from the erase
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea","DELETE_NULL")

# intersect the novel area transboundary sites and the non-transboundary sites
arcpy.Intersect_analysis(["all_wdpa_polybuffpnt_pamesites_transboundary_novelarea",in_basemap_spat],"all_wdpa_polybuffpnt_pamesites_transboundary_novelarea_intersect")
arcpy.Intersect_analysis(["all_wdpa_polybuffpnt_pamesites_nontransboundary_diss",in_basemap_spat],"all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect")

# repair the intersects
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect","DELETE_NULL")
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","DELETE_NULL")

# add a new field, "typeISO3"
arcpy.AddField_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_interect","typeISO3","TEXT")
arcpy.AddField_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_interect","typeISO3","TEXT")

# calculate typeISO3, by concatenating 'type' form the basemap with ISO3
# nontransboundary use the 'WDPA_ISO3' but transboundary use the 'GEO_ISO3' because they've been dissolved
arcpy.CalculateField_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect","typeISO3","!type! + !WDPA_ISO3!","PYTHON_9.3")
arcpy.CalculateField_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","typeISO3","!type! + !GEO_ISO3!","PYTHON_9.3")

# project both transboundary and nontransboundary features into Mollweide
arcpy.Project_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect","all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect_project",in_mollweideprj)
arcpy.Project_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect_project",in_mollweideprj)                

# add and calculate a new area field
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)

# rename the GEO_ISO3 field in the transboundary subset back into WDPA_ISO3
arcpy.AlterField_management("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","GEO_ISO3","WDPA_ISO3","WDPA_ISO3")

# run summary statistics on each subset
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_pamesites_nontransboundary_diss_intersect","pame_non_transboundary_national_statistics",[["POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_pamesites_transboundary_diss_novelarea_intersect","pame_non_transboundary_national_statistics",[["POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3")

# merge the summary statistics from each subset
arcpy.Merge_management(["pame_non_transboundary_national_statistics","pame_transboundary_national_statistics"],"pame_national_statistics_merge")

# join to the basemap to get fields reporting on basemap area
arcpy.JoinField_management("pame_national_statistics_merge","typeISO3",in_basemap_spat,"GEO_typeISO3")

# run summary statistics again, now including the basemap area also
arcpy.Statistics_analysis("pame_national_statistics_merge","pame_national_statistics_merge_summary",[["SUM_POLY_AREA","SUM"]],["type","WDPA_ISO3","typeISO3","AREA_KM2")

# rename the summarised PA area field
arcpy.AlterField_management("pame_national_statistics_merge_summary","SUM_SUM_POLY_AREA","PA_AREA","PA_AREA")

# run a pivot table
arcpy.PivotTable_management("pame_national_statistics_merge_summary","WDPA_ISO3","type","PA_AREA","pame_national_statistics_merge_summary_pivot")

# join to a tabular version of the basemap
arcpy.JoinField_management("pame_national_statistics_merge_summary_pivot","WDPA_ISO3",in_basemap_tab,"GEO_ISO3",["land_area", "marine_area"])

# rename several fields
arcpy.AlterField_management("pame_national_statistics_merge_summary_pivot","WDPA_ISO3","iso33")
arcpy.AlterField_management("pame_national_statistics_merge_summary_pivot","Land","pame_pa_land_area")
arcpy.AlterField_management("pame_national_statistics_merge_summary_pivot","EEZ","pame_pa_marine_area")

# recalculate two fields so that there are '0' instead of blank cells
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","ABNJ","updateValue(!ABNJ!)","def updateValue(value): if value == None: return '0' else: return value")
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","ABNJ","updateValue(!pame_pa_marine_area!)","def updateValue(value): if value == None: return '0' else: return value")
                                                                                                                               
# combine the ABNJ and EEZ area per country into the pa_marine_area field
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","pame_pa_marine_area","!ABNJ! + !pame_pa_marine_area!","PYTHON_9.3")

# delete the now redudndant ABNJ field
arcpy.DeleteField_management("pame_national_statistics_merge_summary_pivot","ABNJ
# add the fields to calculate percentage coverage
arcpy.AddField_management("pame_national_statistics_merge_summary_pivot","pame_percentage_pa_land_cover","FLOAT")
arcpy.AddField_management("pame_national_statistics_merge_summary_pivot","pame_percentage_pa_marine_cover","FLOAT")

# join the final national stats with the pame national stats
arcpy.JoinField_management("national_statistics_merge_summary_pivot","ISO3","pame_national_statistics_merge_summary_pivot","ISO3","[pame_pa_marine_area,pame_pa_land_area,pame_perentage_pa_land_area,pame_percentage_pa_marine_area)

# calculate fields
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","pame_percentage_pa_land_area","(!pame_pa_land_area! / !pa_land_area!)*100","PYTHON_9.3")
arcpy.CalculateField_management("pame_national_statistics_merge_summary_pivot","pame_percentage_pa_marine_area","(!pame_pa_marine_area! / !pa_marine_area!)*100","PYTHON_9.3")

# Finish running scripts!
#----------------------------------------------------------------------------------------------------------------------



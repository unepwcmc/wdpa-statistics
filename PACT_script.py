# Name: Global coverage analysis script
# Purpose: A script based on an Esri model to calculate PA coverage globally, regionally and nationally as well as calculating national and PAME statistics.
# Author: Ed Lewis (edward.lewis@unep-wcmc.org)
# Created: 01/07/2019
# Last updated: 16/04/2020
# ArcGIS Version: Pro(2.1+)
# Python: 3.1+

#--------------------------------------------------------------------------------------------------------------------------
# Preamble: Define the script workspaces

# import arcpy modules
import arcpy
import os
import time
import urllib.request
import zipfile
import random
from arcpy import env

#start the stopwatch
start = time.clock()

# enable the overwriting of outputs
arcpy.env.overwriteOutput = True

# define root folder for all outputs
rootfolder = r"C:\Users\EdwardL\Downloads"
pactfolder = arcpy.CreateFolder_management(rootfolder,"PACT_script")
outputfolder = arcpy.CreateFolder_management(pactfolder,"PACT_outputs")
sbafolder = arcpy.CreateFileGDB_management(outputfolder,"SBA_outputs")
inputfolder = arcpy.CreateFolder_management(pactfolder,"PACT_inputs")

# create a new file geodatabase in the root folder for all the script outputs
workspace = arcpy.CreateFileGDB_management(outputfolder,"PACT_script_outputs")

# define the scratch workspace for outputs we dont want to keep, this will be deleted at the end of the script
scratchworkspace = arcpy.CreateFileGDB_management(outputfolder,"PACT_script_scratch_workspace")
#--------------------------------------------------------------------------------------------------------------------------

# Stage 0: Specify file paths and define access level
print ("Stage 0: Define the inputs and access level")

print ("Stage 0.1: Access level")
# do you have access to the restricted protected area data? If you do not then put False
restricted = True
if restricted == True:
    print("Access level = WCMC")
else:
    print("Access level = public")

# if you have access to the restricted data then copy the file paths here:
if restricted == True:
    # define location of restricted CHN points
    in_restrict_chn_pnt = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\Restricted_subset_model_testing.gdb\CHN_restricted_testing_for_model_pnt"
    # define location of restricted CHN polygons
    in_restrict_chn_poly = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\Restricted_subset_model_testing.gdb\CHN_restricted_testing_for_model"
    # define location of restricted SHN polygons
    in_restrict_shn_poly = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\Restricted_subset_model_testing.gdb\SHN_restricted_testing_for_model"
    # define location of restricted EST polygons
    in_restrict_cdda_poly = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\Restricted_subset_model_testing.gdb\EST_restricted_testing_for_model"

print ("Stage 0.2: PAME sites")
# define the list of protected areas that have pame assessments
in_pame_sites = r"I:\_Monthly_Coverage_Stats_\0_Tools\1_Basemap\Restricted_Data.gdb\PAME_Sites"

print ("Stage 0.3: OECM sites")
# define the input for the oecm data
in_oecmpoly = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\oecm_subset.gdb\oecm_subset"

print ("Stage 0.4 PA sites")
### THIS SECTION WORKS BUT IS MASKED OUT WHILST WE ARE RUNNING TESTS ####
# downloads the most recent version of the WDPA from Protected Planet and saves it in the root directory
#print ('Downloading the latest WDPA from Protected Planet....')

#url = r'http://wcmc.io/wdpa_current_release'
#filename = str(inputfolder) + r"\\WDPA_Latest.zip"
#targetfile = urllib.request.urlretrieve(url, filename)

#print ('Unzipping the WDPA...')
# unzips the folder to enable the file geodatabase to be queried, also in the root directory
#handle = zipfile.ZipFile(filename)
#handle.extractall(str(inputfolder))
#handle.close

#env.workspace = str(inputfolder)

# list the gdbs in the inputfolder
#gdbs = arcpy.ListWorkspaces("*", "FileGDB")

# for the gdb in the inputfolder, list the feature classes that are in the gdb
#for gdb in gdbs:
    #env.workspace = gdb
    #fcs = arcpy.ListFeatureClasses()

# concatenate the file paths to specify the exact inputs for the script
#in_points = gdb + "\\" + fcs[0]
#in_polygons = gdb + "\\" + fcs[1]
##########################################################################

# define the protected area point and polygon inputs [doing this manually or now]
in_points = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\tiny_subset.gdb\CHL_Test_Pnt"
in_polygons = r"I:\_Monthly_Coverage_Stats_\0_Tools\0_Test_Data\tiny_subset.gdb\BLM_model_testing_subset"

print ("Stage 0.5: Basemaps")
###### -  SCRIPTS TO AUTOMATE DOWNLOADING THE BASEMAPS - IGNORE FOR NOW####
#print('Downloading the basemaps from XXXX')

# download the basemaps from [INSERT PLACE]
#url = r'ENTER THE BASEMAP FILE PATH HERE'
#filename = str(inputfolder) + r"\\basemaps.zip"
#targetfile = urllib.request.urlretrieve(url, filename)

#print ('Unzipping the basemaps...')
# unzips the folder to enable the file geodatabase to be queried, also in the root directory
#handle = zipfile.ZipFile(filename)
#handle.extractall(str(inputfolder))
#handle.close
###################################################################################

# define spatial basemap input - country boundaries etc
in_basemap_spat = r"I:\_Monthly_Coverage_Stats_\0_Tools\1_Basemap\Basemap.gdb\EEZv8_WVS_DIS_V3_ALL_final_v7dis_with_SDG_regions_for_models"

# define tabular basemap input - just the attribute table of in_basemap_spat
in_basemap_tab = r"I:\_Monthly_Coverage_Stats_\0_Tools\1_Basemap\Basemap.gdb\EEZv8_WVS_DIS_V3_ALL_final_v7dis_with_SDG_regions_for_models_tabular"


print ("Stage 0.6: Supporting information from Github Repo")

# download the supporting files from the github repo
print('Downloading the supporting files from [Eds] GitHub repo....')

url = r'http://github.com/EdwardMLewis/wdpa-statistics/archive/master.zip'
filename = str(inputfolder) + r"\\Github_supporting_files.zip"
targetfile = urllib.request.urlretrieve(url, filename)

print ('Unzipping the supporting files...')
# unzips the folder to enable the file geodatabase to be queried, also in the root directory
handle = zipfile.ZipFile(filename)
handle.extractall(str(inputfolder))
handle.close

# rename the unzipped folder
arcpy.Rename_management(r"C:\Users\EdwardL\Downloads\PACT_script\PACT_inputs\wdpa-statistics-master",r"C:\Users\EdwardL\Downloads\PACT_script\PACT_inputs\Github_supporting_files")

print ("Stage 0.7: Projection files")

# define the projection files used to define outputs/workspaces
in_mollweideprj = str(inputfolder) + "\\Github_supporting_files\moll_projection.prj"

#--------------------------------------------------------------------------------------------------------------------------

# Stage 1: Global and Regional analysis

print ("Stage 1 of 2: Global and Regional analysis")

arcpy.env.workspace = str(workspace)

# combine the point inputs together depending on whether restricted data is included or not
if restricted == True:
    all_points = arcpy.Merge_management([in_points,in_restrict_chn_pnt], 'all_points')
    all_polygons = arcpy.Merge_management([in_oecmpoly, in_polygons, in_restrict_chn_poly, in_restrict_shn_poly, in_restrict_cdda_poly], 'all_polygons')
else:
    all_points = in_points
    all_polygons = in_polygons

# repair geometries for newly merged files
arcpy.RepairGeometry_management(all_points,"DELETE_NULL","OGC")
arcpy.RepairGeometry_management(all_polygons,"DELETE_NULL","OGC")

# remove the sites that have an uncertain status or have potentially very innacruate areas
arcpy.Select_analysis(all_points, r"in_memory\all_wdpa_points_select","STATUS in ('Adopted', 'Designated', 'Inscribed') AND NOT DESIG_ENG = 'UNESCO-MAB Biosphere Reserve'")
arcpy.Select_analysis(all_polygons, r"in_memory\all_wdpa_polygons_select","STATUS in ('Adopted', 'Designated', 'Inscribed') AND NOT DESIG_ENG = 'UNESCO-MAB Biosphere Reserve'")

# convert the point selection into a polygon by buffering by the REP_AREA
arcpy.AddField_management(r"in_memory\all_wdpa_points_select","radius","DOUBLE")
arcpy.CalculateField_management(r"in_memory\all_wdpa_points_select","radius","math.sqrt(!REP_AREA!/math.pi )*1000","PYTHON_9.3")
arcpy.PairwiseBuffer_analysis(r"in_memory\all_wdpa_points_select",r"in_memory\all_wdpa_points_select_buff","radius","","","GEODESIC","")

# combine the poly selection with the buffered point selection
# the output (hereafter 'polybuffpnt') represents the starting point for the monthly release - it is all the sites we include in the analysis in one file
## IF you want to do count analyses then do it on *this* file
arcpy.Merge_management([r"in_memory\all_wdpa_points_select_buff",r"in_memory\all_wdpa_polygons_select"],"all_wdpa_polybuffpnt")

# repair the polybuffpnt
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt","DELETE_NULL","OGC")

# randomly reassign a STATUS_YR value to those sites that dont have one
field = ['STATUS_YR']
with arcpy.da.UpdateCursor('all_wdpa_polybuffpnt',field) as cursor:
    for row in cursor:
        if row[0] == 0:
            row[0] = random.randint(1819,2020)
            cursor.updateRow(row)

# rename the ISO3 field in the WDPA to clarify it is the WDPA ISO3 and not a basemap ISO3
arcpy.AlterField_management("all_wdpa_polybuffpnt","ISO3","WDPA_ISO3")

# add a new field called PA_DEF_INT which is the PA_DEF field but as an integer
arcpy.AddField_management("all_wdpa_polybuffpnt","PA_DEF_INT","FLOAT")

# populate this new XYco field
arcpy.CalculateField_management("all_wdpa_polybuffpnt","PA_DEF_INT","!PA_DEF!","PYTHON_9.3")

# split up the polybuffpnt using the Union tool - this splits up the WDPA like a Venn diagram
arcpy.Union_analysis("all_wdpa_polybuffpnt","all_wdpa_polybuffpnt_union")

# repair the output of the union
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union","DELETE_NULL","OGC")

# add xy coordinates for each of the ~1 million segments
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_union","CENTROID")

# add a new field to concatenate the new x and y coordinate fields
arcpy.AddField_management("all_wdpa_polybuffpnt_union","XYco","TEXT")

# populate this new XYco field
arcpy.CalculateField_management("all_wdpa_polybuffpnt_union","XYco","str(!CENTROID_X!) + str(!CENTROID_Y!)","PYTHON_9.3")

# run a summary of the XYco field, showing how many instances there are of each XYyco, i.e. how many segments have
# exactly the same XYco, and by extension geometry.
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_union","xyco_count",[["XYco","COUNT"]],"XYco")

# join (add) the XYco field from the summary table to the output of the union
arcpy.JoinField_management("all_wdpa_polybuffpnt_union","XYco","xyco_count","XYco","COUNT_XYco")

# select out all of the segments which only have 1 XYco, i.e. the novel geometries with no overlaps within the WDPA
arcpy.Select_analysis("all_wdpa_polybuffpnt_union",r"in_memory\all_wdpa_polybuffpnt_union_unique","COUNT_XYco = 1")

# select out all of the segments which have >1 XYco, i.e. geometries which overlap within the WDPA
arcpy.Select_analysis("all_wdpa_polybuffpnt_union","all_wdpa_polybuffpnt_union_duplicates","COUNT_XYco > 1")

# run a summary report listing the lowest STATUS_YR for each duplicate area by XYco
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_union_duplicates",r"in_memory\all_wdpa_polybuffpnt_union_duplicates_earliest_sum",[["STATUS_YR","MIN"]],"XYco")

# run a summary report listing whether that XYco includes PA (1), OECMs (0) or both (if both the mean will be between 0 and 1)
arcpy.Statistics_analysis("all_wdpa_polybuffpnt_union_duplicates","all_wdpa_polybuffpnt_union_duplicates_padef",[["PA_DEF_INT","MEAN"]],"XYco")

# update the PA_DEF so that areas that cover both PA and OECM have a PA_DEF_INT of 2
in_codeblock0 = """
def updateValue(value):
  if value >0 and value <1:
   return '2'
  else: return value"""

arcpy.CalculateField_management("all_wdpa_polybuffpnt_union_duplicates_padef","MEAN_PA_DEF_INT","updateValue(!MEAN_PA_DEF_INT!)","PYTHON_9.3", in_codeblock0)

# join the pa_def summary report to the copied duplicates
arcpy.JoinField_management("all_wdpa_polybuffpnt_union_duplicates","XYco","all_wdpa_polybuffpnt_union_duplicates_padef","XYco","MEAN_PA_DEF_INT")

# recalculate PA_DEF_INT so that each XYco reflects if it includes PA (1), OECMs (0) or both (2)
arcpy.CalculateField_management("all_wdpa_polybuffpnt_union_duplicates","PA_DEF_INT","!MEAN_PA_DEF_INT!")

# remove the field
arcpy.DeleteField_management("all_wdpa_polybuffpnt_union_duplicates","MEAN_PA_DEF_INT")

# make a copy of the duplicates
arcpy.Copy_management("all_wdpa_polybuffpnt_union_duplicates","all_wdpa_polybuffpnt_union_duplicates_flat")

# delete all identical XYcos from the copied duplicates, we dont care about the values, just the geometreis and making it flat
arcpy.DeleteIdentical_management("all_wdpa_polybuffpnt_union_duplicates_flat","XYco")

# join the summary report to the copied duplicates
arcpy.JoinField_management("all_wdpa_polybuffpnt_union_duplicates_flat","XYco",r"in_memory\all_wdpa_polybuffpnt_union_duplicates_earliest_sum","XYco","MIN_status_yr")

# recalculate status_yr so that each XYco has the earliest status_yr that geometry had
arcpy.CalculateField_management("all_wdpa_polybuffpnt_union_duplicates_flat","STATUS_YR","!MIN_status_yr!")

# remove the field
arcpy.DeleteField_management("all_wdpa_polybuffpnt_union_duplicates_flat","MIN_status_yr")

# merge these site back into the unique geometries - creating a flat layer which has the whole WDPA schema populated still.
## If you want to do count analyses do it on the polybuffpnt, if you want to do spatial analyses, do it with this file.
arcpy.Merge_management(["all_wdpa_polybuffpnt_union_duplicates_flat",r"in_memory\all_wdpa_polybuffpnt_union_unique"],r"in_memory\all_wdpa_polybuffpnt_union_flat")

# repair the recombined layer
arcpy.RepairGeometry_management(r"in_memory\all_wdpa_polybuffpnt_union_flat","DELETE_NULL","OGC")

# intersect it with the basemap
arcpy.PairwiseIntersect_analysis([r"in_memory\all_wdpa_polybuffpnt_union_flat",in_basemap_spat],r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect")

# repair it
arcpy.RepairGeometry_management(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect","DELETE_NULL","OGC")

# project it into mollweide, an equal area projection
arcpy.Project_management(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect","all_wdpa_polybuffpnt_union_flat_intersect_project",in_mollweideprj)

# repair it
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_union_flat_intersect_project","DELETE_NULL","OGC")

# add and calculate a new area field
arcpy.AddGeometryAttributes_management("all_wdpa_polybuffpnt_union_flat_intersect_project","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)

# GLOBAL SUMMARY REPORTS

# create a new feature dataset in the workspace geodatabase for the different sets of sites (whole set, only PAs and only OECMs)
out_separate_feature_dataset = arcpy.CreateFeatureDataset_management(workspace,"separate_sets")

# select only sites outside of the ABNJ (they get treated separately)
arcpy.Select_analysis("all_wdpa_polybuffpnt_union_flat_intersect_project", r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj", "WDPA_ISO3 NOT IN ('ABNJ')")

# change the 'type' field in the non_abnj selection so that ABNJ is always changed to 'EEZ' (nationally designated sites go over into the geographic ABNJ)
arcpy.CalculateField_management(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj","type","!type!.replace('ABNJ','EEZ')", 'PYTHON3')

# run some summary stats on the Land + EEZ selection for the current year (current) and broken down per year (current)
arcpy.Statistics_analysis(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj","global_summary_statistics_current",[["AREA_GEO","SUM"]],"type")
arcpy.Statistics_analysis(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj","global_summary_statistics_temporal",[["AREA_GEO","SUM"]],["type", "STATUS_YR"])

# select out just the rows with an ISO3 of 'ABNJ'
arcpy.Select_analysis("all_wdpa_polybuffpnt_union_flat_intersect_project",r"in_memory\ABNJ_sites","WDPA_ISO3 = 'ABNJ'")

# run some global summary stats on the ABNJ selection for the current year (current) and broken down per year (temporal)
arcpy.Statistics_analysis(r"in_memory\ABNJ_sites",r"in_memory\abnj_global_summary_statistics_current",[["AREA_GEO","SUM"]],"type")
arcpy.Statistics_analysis(r"in_memory\ABNJ_sites",r"in_memory\abnj_global_summary_statistics_temporal",[["AREA_GEO","SUM"]],["type", "STATUS_YR"])

# pivot the global current, global temporal summary table and the abnj temporal summary tables
arcpy.PivotTable_management("global_summary_statistics_temporal",["STATUS_YR"],"type","SUM_AREA_GEO","global_summary_statistics_temporal_pivot")
arcpy.PivotTable_management(r"in_memory\abnj_global_summary_statistics_temporal",["STATUS_YR"],"type","SUM_AREA_GEO","abnj_summary_statistics_temporal_pivot")

# add the abnj tables into the global summary tables
arcpy.Append_management(r"in_memory\abnj_global_summary_statistics_current","global_summary_statistics_current","NO_TEST")
arcpy.JoinField_management("global_summary_statistics_temporal_pivot","STATUS_YR","abnj_summary_statistics_temporal_pivot","STATUS_YR", 'ABNJ')

# update the fields so that they show '0' as opposed to blank cells
# define the codeblock1

in_codeblock1 = """
def updateValue(value):
  if value == None:
   return '0'
  else: return value"""

arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","EEZ","updateValue(!EEZ!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","Land","updateValue(!Land!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","ABNJ","updateValue(!ABNJ!)","PYTHON_9.3", in_codeblock1)

# Add in three new fields, to track the cumulative area
arcpy.AddField_management("global_summary_statistics_temporal_pivot","EEZ_net","LONG")
arcpy.AddField_management("global_summary_statistics_temporal_pivot","Land_net","LONG")
arcpy.AddField_management("global_summary_statistics_temporal_pivot","ABNJ_net","LONG")

# Calculate the three net fields
# define codeblock2
in_codeblock2 = """
total = 0
def accumulate(increment):
 global total
 if total:
  total += increment
 else:
  total = increment
 return total"""

arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","EEZ_net","accumulate(!EEZ!)","PYTHON_9.3", in_codeblock2)
arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","Land_net","accumulate(!Land!)","PYTHON_9.3", in_codeblock2)
arcpy.CalculateField_management("global_summary_statistics_temporal_pivot","ABNJ_net","accumulate(!ABNJ!)","PYTHON_9.3", in_codeblock2)


# REGIONAL SUMMARY REPORTS

# run some summary stats on the regional for the current year (current) and broken down per year (temporal)
arcpy.Statistics_analysis(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj",r"in_memory\regional_summary_statistics_current",[["AREA_GEO","SUM"]],["sdg_region","type"])
arcpy.Statistics_analysis(r"in_memory\all_wdpa_polybuffpnt_union_flat_intersect_project_nonabnj", r"in_memory\regional_summary_statistics_temporal",[["AREA_GEO","SUM"]],["type", "STATUS_YR","sdg_region"])

# run some global summary stats on the ABNJ selection for the current year (current) and broken down per year (temporal)
arcpy.Statistics_analysis(r"in_memory\ABNJ_sites",r"in_memory\abnj_regional_summary_statistics_current",[["AREA_GEO","SUM"]],["type","sdg_region"])
arcpy.Statistics_analysis(r"in_memory\ABNJ_sites",r"in_memory\abnj_regional_summary_statistics_temporal",[["AREA_GEO","SUM"]],["type", "sdg_region", "STATUS_YR"])

# add in the abnj area to the regional summary tables
arcpy.Append_management(r"in_memory\abnj_regional_summary_statistics_current",r"in_memory\regional_summary_statistics_current","NO_TEST")
arcpy.Append_management(r"in_memory\abnj_regional_summary_statistics_temporal",r"in_memory\regional_summary_statistics_temporal","NO_TEST")

# pivot the regional temporal summary table and the ABNJ table
arcpy.PivotTable_management(r"in_memory\regional_summary_statistics_current",["sdg_region"],"type","SUM_AREA_GEO","regional_summary_statistics_current_pivot")
arcpy.PivotTable_management(r"in_memory\regional_summary_statistics_temporal",["STATUS_YR","sdg_region"],"type","SUM_AREA_GEO","regional_summary_statistics_temporal_pivot")

# update the fields so that they show '0' as opposed to blank cells
arcpy.CalculateField_management("regional_summary_statistics_current_pivot","EEZ","updateValue(!EEZ!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("regional_summary_statistics_current_pivot","Land","updateValue(!Land!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("regional_summary_statistics_current_pivot","ABNJ","updateValue(!ABNJ!)","PYTHON_9.3", in_codeblock1)

arcpy.CalculateField_management("regional_summary_statistics_temporal_pivot","EEZ","updateValue(!EEZ!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("regional_summary_statistics_temporal_pivot","Land","updateValue(!Land!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("regional_summary_statistics_temporal_pivot","ABNJ","updateValue(!ABNJ!)","PYTHON_9.3", in_codeblock1)

print ("The global and regional summary tables can now be used by themselves or copied into the monthly summary statistics templates for QC")

# run some count statistics
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_MARINE",[["WDPAID","COUNT"]],"MARINE")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_IUCNCAT",[["WDPAID","COUNT"]],"IUCN_CAT")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_GOVTYPE",[["WDPAID","COUNT"]],"GOV_TYPE")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_OWNTYPE",[["WDPAID","COUNT"]],"OWN_TYPE")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_DESIGENG",[["WDPAID","COUNT"]],"DESIG_ENG")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_DESIGTYPE",[["WDPAID","COUNT"]],"DESIG_TYPE")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_ISO3",[["WDPAID","COUNT"]],"WDPA_ISO3")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_STATUSYR",[["WDPAID","COUNT"]],"STATUS_YR")
arcpy.Statistics_analysis("all_wdpa_polybuffpnt","count_OWNTYPE",[["WDPAID","COUNT"]],"OWN_TYPE")

# calculate the no-take stats
arcpy.Select_analysis("all_wdpa_polybuffpnt", r"in_memory\notake_all","NO_TAKE = 'All'")
arcpy.Dissolve_management(r"in_memory\notake_all",r"in_memory\notake_all_diss")
arcpy.Project_management(r"in_memory\notake_all_diss","notakeall_diss_project",in_mollweideprj)
arcpy.AddGeometryAttributes_management("notakeall_diss_project","AREA_GEODESIC","","SQUARE_KILOMETERS",in_mollweideprj)
arcpy.Statistics_analysis("notakeall_diss_project","sum_NOTAKEall",[["AREA_GEO","SUM"]])

arcpy.Select_analysis("all_wdpa_polybuffpnt", r"in_memory\notake_part","NO_TAKE = 'Part'")
arcpy.Statistics_analysis(r"in_memory\notake_part","sum_NOTAKEpart",[["NO_TK_AREA","SUM"]])

elapsed_hours = (time.clock() - start)/3600
print(("Stage 1 took " + str(elapsed_hours) + " hours"))

##-------------------------------------------------------------------------------------------------------------------------
#Stage 2: National and National PAME analysis

print ("Stage 2 of 2: National & National PAME Analyses")

# create the summary tables for appending in individual natioanl summary statistics
out_national_current_schema = arcpy.CreateTable_management(workspace,"out_national_current_schema")
arcpy.AddFields_management(out_national_current_schema,[['WDPA_ISO3','TEXT'],['type','TEXT'],['FREQUENCY','LONG'],['SUM_AREA_GEO','DOUBLE']])

out_national_temporal_schema = arcpy.CreateTable_management(workspace,"out_national_temporal_schema")
arcpy.AddFields_management(out_national_temporal_schema,[['WDPA_ISO3','TEXT'],['MIN_STATUS_YR','DOUBLE'],['type','TEXT'],['FREQUENCY','LONG'],['SUM_AREA_GEO','DOUBLE']])

out_national_current_schema_pame = arcpy.CreateTable_management(workspace,"out_national_current_schema_pame")
arcpy.AddFields_management(out_national_current_schema_pame,[['WDPA_ISO3','TEXT'],['type','TEXT'],['FREQUENCY','LONG'],['SUM_AREA_GEO','DOUBLE']])

out_national_temporal_schema_pame = arcpy.CreateTable_management(workspace,"out_national_temporal_schema_pame")
arcpy.AddFields_management(out_national_temporal_schema_pame,[['WDPA_ISO3','TEXT'],['MIN_STATUS_YR','DOUBLE'],['type','TEXT'],['FREQUENCY','LONG'],['SUM_AREA_GEO','DOUBLE']])

# join pame list to polybuffpnt
arcpy.JoinField_management("all_wdpa_polybuffpnt","WDPAID",in_pame_sites,"wdpa_id","evaluation_id")

# update field (0) for those that don't have id
arcpy.CalculateField_management("all_wdpa_polybuffpnt","evaluation_id","updateValue(!evaluation_id!)","PYTHON_9.3", in_codeblock1)

# select transboundary sites and non transboundary sites
arcpy.Select_analysis("all_wdpa_polybuffpnt",r"in_memory\all_wdpa_polybuffpnt_nontransboundary","WDPA_ISO3 NOT LIKE '%;%'")
arcpy.Select_analysis("all_wdpa_polybuffpnt",r"in_memory\all_wdpa_polybuffpnt_transboundary","WDPA_ISO3 LIKE '%;%'")

# repair them
arcpy.RepairGeometry_management(r"in_memory\all_wdpa_polybuffpnt_nontransboundary","DELETE_NULL","OGC")
arcpy.RepairGeometry_management(r"in_memory\all_wdpa_polybuffpnt_transboundary","DELETE_NULL","OGC")

# erase the transboundary sites from the nontransboundary sites
arcpy.Erase_analysis(r"in_memory\all_wdpa_polybuffpnt_transboundary",r"in_memory\all_wdpa_polybuffpnt_nontransboundary","all_wdpa_polybuffpnt_transboundary_novelarea")

# repair the output of the erase
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary_novelarea","DELETE_NULL","OGC")

# intersect the erased output with the basemap
arcpy.PairwiseIntersect_analysis(["all_wdpa_polybuffpnt_transboundary_novelarea",in_basemap_spat],"all_wdpa_polybuffpnt_transboundary_novelarea_intersect")

# repair it
arcpy.RepairGeometry_management("all_wdpa_polybuffpnt_transboundary_novelarea_intersect","DELETE_NULL","OGC")

#  recalculate ISO3 based on the geo iso3
arcpy.CalculateField_management("all_wdpa_polybuffpnt_transboundary_novelarea_intersect","WDPA_ISO3","!GEO_ISO3!","PYTHON_9.3")

# rename the nontransboundary sites
#arcpy.Rename_management(r"in_memory\all_wdpa_polybuffpnt_nontransboundary",r"in_memory\all_wdpa_polybuffpnt_national")

# append back the erased and intersected transboundary sites back into the nontransboundary sites
arcpy.Append_management(r"in_memory\all_wdpa_polybuffpnt_nontransboundary","all_wdpa_polybuffpnt_transboundary_novelarea_intersect","NO_TEST")

# repair it
arcpy.RepairGeometry_management(r"in_memory\all_wdpa_polybuffpnt_nontransboundary","DELETE_NULL","OGC")

# split by attribute (wdpa_iso3) to create an individual fc for each iso3
arcpy.SplitByAttributes_analysis(r"in_memory\all_wdpa_polybuffpnt_nontransboundary",sbafolder, "WDPA_ISO3")

# change the location of the workspace to represent the location of the sba output
arcpy.env.workspace = str(sbafolder)
arcpy.env.overwriteOutput = True

out_sba = arcpy.ListFeatureClasses()

#  split the input into country specific subsets and do the analysis iso3 by iso3
for fc in out_sba:
    desc = arcpy.Describe(fc)

    # run a union, add in an xyco for each segment
    arcpy.Union_analysis(fc,r"in_memory\Union")
    arcpy.RepairGeometry_management(r"in_memory\union","DELETE_NULL","OGC")

    # assign a unique id to each parcel (XYco)
    arcpy.AddGeometryAttributes_management(r"in_memory\union","CENTROID")
    arcpy.AddField_management(r"in_memory\union","XYco","TEXT")
    arcpy.CalculateField_management(r"in_memory\union","XYco","str(!CENTROID_X!) + str(!CENTROID_Y!)","PYTHON_9.3")

    # run two summary reports per parcel, working out the minimum STATUS_YR and the maximum evaluation_id (i.e. whether assessed or not)
    arcpy.Statistics_analysis(r"in_memory\union",r"in_memory\out_styr_stats",[["STATUS_YR","MIN"]],"XYco")
    arcpy.Statistics_analysis(r"in_memory\union",r"in_memory\out_assid_stats",[["evaluation_id","MAX"]],"XYco")

    # delete identical (XYco) - (i.e. make it flat, removing intra-national overlaps), and repair it
    arcpy.DeleteIdentical_management(r"in_memory\union","XYco")
    arcpy.RepairGeometry_management(r"in_memory\union","DELETE_NULL","OGC")

    # split it up further by intersecting each country with the basemap
    arcpy.PairwiseIntersect_analysis([r"in_memory\union",in_basemap_spat],r"in_memory\intersect")
    arcpy.RepairGeometry_management(r"in_memory\intersect","DELETE_NULL","OGC")

    # add in the earliest designation date and whether it was assessed to each segment
    arcpy.JoinField_management(r"in_memory\intersect","XYco",r"in_memory\out_styr_stats","XYco", 'MIN_STATUS_YR')
    arcpy.JoinField_management(r"in_memory\intersect","XYco",r"in_memory\out_assid_stats","XYco", 'MAX_evaluation_id')

    # project the output into mollweide
    out_proj = desc.basename+"_union_intersect_project"
    arcpy.Project_management(r"in_memory\intersect",out_proj,in_mollweideprj)
    arcpy.RepairGeometry_management(out_proj,"DELETE_NULL","OGC")
    arcpy.AddGeometryAttributes_management(out_proj,"AREA","","SQUARE_KILOMETERS",in_mollweideprj)

    # for national reporting they can't report by ABNJ, so we treat areas in geographical ABNJ as actually being part of the ISO3's EEZ
    arcpy.CalculateField_management(out_proj,"type","!type!.replace('ABNJ','EEZ')", 'PYTHON3')

    # create national pa summary statistics
    arcpy.Statistics_analysis(out_proj,r"in_memory\out_styr_sum_current",[["POLY_AREA","SUM"]],["WDPA_ISO3","type"])
    out_styr_sum_temporal = desc.basename+"_summary"
    arcpy.Statistics_analysis(out_proj,r"in_memory\out_styr_sum_temporal",[["POLY_AREA","SUM"]],["WDPA_ISO3","MIN_STATUS_YR","type"])

    # pivot the national temporal pa summary
    arcpy.PivotTable_management(r"in_memory\out_styr_sum_temporal",["WDPA_ISO3","MIN_STATUS_YR"],"type","SUM_POLY_AREA",r"in_memory\out_styr_sum_temporal_pivot")

    # update current national field names (if they exist), replace <Null> with 0, add ABNJ area to EEZ field
    if len(arcpy.ListFields(r"in_memory\out_styr_sum_temporal_pivot","WDPA_ISO3"))!=0:
        arcpy.AlterField_management(r"in_memory\out_styr_sum_temporal_pivot","WDPA_ISO3","iso3")
    if len(arcpy.ListFields(r"in_memory\out_styr_sum_temporal_pivot","MIN_STATUS_YR"))!=0:
        arcpy.AlterField_management(r"in_memory\out_styr_sum_temporal_pivot","MIN_STATUS_YR","year")
    if len(arcpy.ListFields(r"in_memory\out_styr_sum_temporal_pivot","Land"))!=0:
        arcpy.AlterField_management(r"in_memory\out_styr_sum_temporal_pivot","Land","pa_land_area")
        arcpy.CalculateField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_land_area","updateValue(!pa_land_area!)","PYTHON_9.3", in_codeblock1)
    if len(arcpy.ListFields(r"in_memory\out_styr_sum_temporal_pivot","EEZ"))!=0:
        arcpy.AlterField_management(r"in_memory\out_styr_sum_temporal_pivot","EEZ","pa_marine_area")
        arcpy.CalculateField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_marine_area","updateValue(!pa_marine_area!)","PYTHON_9.3", in_codeblock1)
    if len(arcpy.ListFields(r"in_memory\out_styr_sum_temporal_pivot","NET_POLY_AREA"))!=0:
        arcpy.AddField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_land_area_net_km2","LONG")
        arcpy.CalculateField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_land_area_net_km2","accumulate(!pa_land_area!)","PYTHON_9.3", in_codeblock2)
        arcpy.AddField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_marine_area_net_km2","LONG")
        arcpy.CalculateField_management(r"in_memory\out_styr_sum_temporal_pivot","pa_marine_area_net_km2","accumulate(!pa_marine_area!)","PYTHON_9.3", in_codeblock2)

    # append each of the national pa coverage tables into a clean precooked schema and all of the temporal pivot tables into another clean precooked schema
    arcpy.Append_management(r"in_memory\out_styr_sum_current",out_national_current_schema,"NO_TEST")
    arcpy.Append_management(r"in_memory\out_styr_sum_temporal",out_national_temporal_schema,"NO_TEST")

    # select the areas where there has been a pame assessment to only run statistics on those areas
    arcpy.Select_analysis(out_proj,r"in_memory\out_ass_sites","MAX_evaluation_id >= 1")

    # create national pa PAME summary statistics
    arcpy.Statistics_analysis(r"in_memory\out_ass_sites",r"in_memory\out_ass_sum_current",[["POLY_AREA","SUM"]],["WDPA_ISO3","type"])
    arcpy.Statistics_analysis(r"in_memory\out_ass_sites",r"in_memory\out_ass_sum_temporal",[["POLY_AREA","SUM"]],["WDPA_ISO3","MIN_STATUS_YR","type"])

    # append each of the national pa PAME coverage tables into a clean precooked schema and all of the temporal PAME data into another clean precooked schema
    arcpy.Append_management(r"in_memory\out_ass_sum_current",out_national_current_schema_pame,"NO_TEST")
    arcpy.Append_management(r"in_memory\out_ass_sum_temporal",out_national_temporal_schema_pame,"NO_TEST")

    # delete the in_memory workspace before starting the next country
    arcpy.Delete_management(r"in_memory")


# we now return back to the original workspace
arcpy.env.workspace = str(workspace)


# NATIONAL CURRENT REPORTS
# create summary tables for national status

# pivot the current national summary tables
arcpy.PivotTable_management(out_national_current_schema,"WDPA_ISO3","type","SUM_AREA_GEO","national_summary_statistics_current_pivot")

# rename fields
arcpy.AlterField_management("national_summary_statistics_current_pivot","WDPA_ISO3","iso3")
arcpy.AlterField_management("national_summary_statistics_current_pivot","Land","pa_land_area")
arcpy.AlterField_management("national_summary_statistics_current_pivot","EEZ","pa_marine_area")

# add the current national fields to calculate percentage coverage
arcpy.AddField_management("national_summary_statistics_current_pivot","percentage_pa_land_cover","FLOAT")
arcpy.AddField_management("national_summary_statistics_current_pivot","percentage_pa_marine_cover","FLOAT")

# join current national to the basemap
arcpy.JoinField_management("national_summary_statistics_current_pivot","iso3",in_basemap_tab,"GEO_ISO3",["land_area", "marine_area"])

# calculate current national fields and replace <Null> values with 0
arcpy.CalculateField_management("national_summary_statistics_current_pivot","percentage_pa_land_cover","(!pa_land_area! / !land_area!)*100","PYTHON_9.3")
arcpy.CalculateField_management("national_summary_statistics_current_pivot","percentage_pa_marine_cover","(!pa_marine_area! / !marine_area!)*100","PYTHON_9.3")
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pa_land_area","updateValue(!percentage_pa_land_cover!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pa_marine_area","updateValue(!percentage_pa_marine_cover!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","percentage_pa_land_cover","updateValue(!percentage_pa_land_cover!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","percentage_pa_marine_cover","updateValue(!percentage_pa_marine_cover!)","PYTHON_9.3", in_codeblock1)

# pivot the current national pame summary tables
arcpy.PivotTable_management(out_national_current_schema_pame,"WDPA_ISO3","type","SUM_AREA_GEO","national_summary_statistics_current_pivot_pame")

# rename fields
arcpy.AlterField_management("national_summary_statistics_current_pivot_pame","WDPA_ISO3","iso3")
arcpy.AlterField_management("national_summary_statistics_current_pivot_pame","Land","pame_pa_land_area")
arcpy.AlterField_management("national_summary_statistics_current_pivot_pame","EEZ","pame_pa_marine_area")

# Join the current national pame table to the current natioanl table
arcpy.JoinField_management("national_summary_statistics_current_pivot","iso3","national_summary_statistics_current_pivot_pame","iso3",["pame_pa_land_area", "pame_pa_marine_area"])

# calculate pame percentage fields
arcpy.AddField_management("national_summary_statistics_current_pivot","pame_percentage_pa_land_cover","FLOAT")
arcpy.AddField_management("national_summary_statistics_current_pivot","pame_percentage_pa_marine_cover","FLOAT")
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_percentage_pa_land_cover","(!pame_pa_land_area! / !land_area!)*100","PYTHON_9.3")
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_percentage_pa_marine_cover","(!pame_pa_marine_area! / !marine_area!)*100","PYTHON_9.3")

# update all pame fields so that <Null> is replaced by 0
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_pa_marine_area","updateValue(!pame_pa_marine_area!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_pa_land_area","updateValue(!pame_pa_land_area!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_percentage_pa_land_cover","updateValue(!pame_percentage_pa_land_cover!)","PYTHON_9.3", in_codeblock1)
arcpy.CalculateField_management("national_summary_statistics_current_pivot","pame_percentage_pa_marine_cover","updateValue(!pame_percentage_pa_marine_cover!)","PYTHON_9.3", in_codeblock1)

elapsed_minutes = (time.clock() - start)/60
elapsed_hours = (time.clock() - start)/3600

print ("scripts finished - all good")
print ("Outputs are here: " + str(workspace))
print ("Total running time: " + str(elapsed_minutes) + " minutes (" + str(elapsed_hours) + " hours)")

# clean up the worksapce a bit to remove intermediate subfolders
arcpy.Delete_management(scratchworkspace)
arcpy.Delete_management(sba_folder)

# Finish running scripts
#----------------------------------------------------------------------------------------------------------------------

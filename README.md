## A repository for analytical tools on the World Database on Protected Areas (WDPA) and World Database on Other Effective Areas-Based Measures (WDOECM).

***
#### Date: May 2021
#### Note: It was hoped that this repo would be a more comprehensive and active space by mid 2021. The COVID pandemic has resulted in a delay for some workstreams at UNEP-WCMC and unfortunately improving our coding and analytical capabilities for the WDPA and WDOECM was one of them. The Esri geoprocessing model used to calculate global and national statistics using the WDPA and WDOECM is available in a zipped file above. There is the full intention to transition to a python script in the near future. A python script version of the model is also available above, though it should still be considered a work in progress. If you would like to use either the script or the model then it would be well worth talking to edward.lewis@unep-wcmc to discuss the work.

***
#### Author: Ed Lewis
#### Date: October 2019
#### Purpose: A centralised, comprehensive and public repository for WDPA analytical tools.

See the Wiki for a comprehensive introduction to the repo's content.

Steps to undertake the monthly update of PA statistics:
1. Run the PACT python script;
2. QC the results using the PACT-QC python script (yet to be made);
3. Copy values from the 'global_summary_statistics' output table from the PACT script into the global summary working doc in this repo.;
4. Format the global results in the summary working doc as per the instructions;
5. Copy these formatted global results into the global reporting template;
6. Copy the national results into the national reporting template;
7. Send the Informatics team the global and national reporting stats for the month.


Future ideas of things to embed/test:
In python we're no longer limited to one iterator - so can we use multiple for/list loops to process the countries/pame together and-or faster?
how to speed it up even more?
test the windows timed activity ability to run this at a specified interval / embed the ability to test when the WDPA is updated or changed? - e.g. full automation.
maximise the types of tabular/statistical outputs that are made - e.g. timeseries, gov types etc. 
Make and then automate the QC checks for the global, national and pame stats

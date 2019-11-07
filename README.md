## A repository for analytical tools on the World Database on Protected Areas.

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

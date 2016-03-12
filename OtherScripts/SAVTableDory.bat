::REM
::Iterate through folders within folder, save folder name in variable
::Run Illumina SAV viewer from the command line
::Save the output table to a file (.csv)
::It's a bit basic so just change the filepaths to where you need to load the data from and where you want to save it to

::"C:\Illumina\Illumina Sequencing Analysis Viewer\Sequencing Analysis Viewer.exe" <RunFolder> <outputFile> -t

@echo off
set curr_dir=%cd%
cd "C:\Users\Sara\ownCloud\SAV Files\Dory"
SETLOCAL ENABLEDELAYEDEXPANSION
for /D %%s in (.\*) do (
    set folder=%%s
    set outp=^C:\\Users\\Sara\\Dropbox\\Bioinformatics Clinical Science\\OLAT rotations\\Years Two-Three\\SAVWork\\SAVViewerTables\\Dory\\!folder:~2,34!.csv
    call "C:\\Illumina\\Illumina Sequencing Analysis Viewer\\Sequencing Analysis Viewer.exe" !folder! "!outp!" -t 
    )   
ENDLOCAL
echo Script complete
cd /d %~dp0
goto :eof

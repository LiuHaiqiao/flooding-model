import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import csv
import re
import os

#eventid = [1]
#eventdate = ['2011-08-26']

#read the event id and date
df = pd.read_csv("F:/YIFAN/2023/InsuranceData/WaterData/NJfloods1977to2021.csv")
# Extract unique eventidx values
eventid = df['eventIdx'].unique().tolist()
df['eventDate'] = pd.to_datetime(df['eventDate'], format='%d-%b-%y').dt.strftime('%Y-%m-%d')
eventdate = df['eventDate'].unique().tolist()

for i, value in enumerate(eventid[2026:2037]):
    print(value)
    print(eventdate[value-1])
    DT=datetime.strptime(eventdate[value-1], "%Y-%m-%d").date()
    date_before = DT - timedelta(days=5)
    date_after = DT + timedelta(days=5)
    date_before_str = date_before.strftime("%Y-%m-%d")
    date_after_str = date_after.strftime("%Y-%m-%d")
    stlist="F:/YIFAN/2023/InsuranceData/WaterData/event"+str(value)+"_stlist.csv"
    #create station list csv file first
    print(date_before_str,date_after_str)

    url = "https://nwis.waterservices.usgs.gov/nwis/iv/?format=rdb&stateCd=nj&startDT="+date_before_str+"T01:00-0400&endDT="+date_after_str+"T01:00-0400&parameterCd=00065&siteType=OC,ES,ST&siteStatus=all"
    response1 = requests.get(url)
    response1.raise_for_status()
    outtxt1="F:/YIFAN/2023/InsuranceData/WaterData/event"+str(value)+"_stlist.txt"
    with open(outtxt1, "w", encoding="utf-8") as file:
        file.write(response1.text)
    # Read the text file into a DataFrame
    # Adjust the delimiter if necessary (e.g., "\t" for tabs)
    with open(outtxt1, "r") as file:
    # Iterate over each line with its line number (starting from 1)
        for line_num, line in enumerate(file, start=1):
            # Check if the line starts with the string "agency_cd"
            if line.startswith("# Data for the following"):
                ln1=line_num
                continue
            if line.startswith("# -----------------------------------------------------------------------------------"):
                ln2=line_num
                break
    extracted_lines = []
    # Open the .txt file in read mode
    with open(outtxt1, "r") as txt_file:
        try:
            ln1
            print("some sites found matching criteria.")
        except NameError:
            print("NO SITES FOUND MATCHING!.")
            continue
        # Iterate over each line with its line number (starting from 1)
        for line_num, line in enumerate(txt_file, start=1):
            # Check if the current line number is within the desired range
            if ln1 < line_num < ln2:
            # Split the line by whitespace (or any other delimiter) and add to the list
                #split_line = re.split(r'\s+', line.strip(), maxsplit=2)
                #extracted_lines.append(split_line)
                _, usgs, station_id, station_name = line.strip().split(None, 3)
                extracted_lines.append([usgs, station_id, station_name])
    with open(stlist, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        writer.writerow(["USGS", "Station_ID", "Station_Name"])
        writer.writerows(extracted_lines)
    print("created station list file")
    

    df = pd.read_csv(stlist)
    # Extract the second column and convert it to a list
    stations = df.iloc[:, 1].tolist()
    max_gh=[] #maximum gage height
    for j,value2 in enumerate(stations):

        url = "https://waterservices.usgs.gov/nwis/iv/?format=rdb&sites=0"+str(stations[j])+"&startDT="+date_before_str+"T00:00-0400&endDT="+date_after_str+"T00:00-0400&parameterCd=00065&siteType=OC,ES,ST&siteStatus=all"
        response = requests.get(url)
        response.raise_for_status()
        outtxt="F:/YIFAN/2023/InsuranceData/WaterData/st"+str(stations[j])+"_event"+str(value)+".txt"
        with open(outtxt, "w", encoding="utf-8") as file:
            file.write(response.text)
        output_file = "F:/YIFAN/2023/InsuranceData/WaterData/st"+str(stations[j])+"_event"+str(value)+".csv"
        
        with open(outtxt, "r") as file:
        # Iterate over each line with its line number (starting from 1)
            for line_num, line in enumerate(file, start=1):
                # Check if the line starts with the string "agency_cd"
                if line.startswith("agency_cd"):
                    #print(f"The line starting with 'agency_cd' is on line number {line_num}")
                    headers = line.strip().split()
                    break
        print(headers)
        if len(headers) < 4:
            max_gage_height=-9999
            max_gh.append(max_gage_height)
            continue
        data = []
        with open(outtxt, "r") as file:
            for line in file.readlines()[line_num:]:
                fields = line.strip().split()
                datetime_str = fields[2] + " " + fields[3]
                new_fields = fields[:2] + [datetime_str] + fields[4:]
                print(new_fields)
                while len(new_fields) < len(headers):
                    new_fields.insert(4, 'NaN')  # Insert NaN values at the appropriate position
                data.append(new_fields)

        df = pd.DataFrame(data, columns=headers)
        df.to_csv(output_file, index=False)

        skip_rows = line_num
        ##df = pd.read_csv(outtxt, delimiter=r"\s+", engine='python',skiprows=skip_rows)
        # Save the DataFrame to a CSV file
        ##df.to_csv(output_file, index=False)
        # Load the CSV file into a DataFrame
        df = pd.read_csv(output_file)
        # Convert the column to numeric, coercing any non-numeric values to NaN
        df.iloc[:, 4] = pd.to_numeric(df.iloc[:, 4], errors='coerce')
        max_gage_height = df.iloc[:, 4].max()
        max_gh.append(max_gage_height)
    

        # Check if the file exists and then delete it, release memory
        if os.path.exists(outtxt):
            os.remove(outtxt)
            print(f"File '{outtxt}' deleted successfully!")
        else:
            print(f"File '{outtxt}' not found!")
        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"File '{output_file}' deleted successfully!")
        else:
            print(f"File '{output_file}' not found!")


    result_df = pd.DataFrame({"siteID": stations,"Max_gh": max_gh})
    event_outcsv="F:/YIFAN/2023/InsuranceData/WaterData/stations_max_gh_event"+str(value)+".csv"
    result_df.to_csv(event_outcsv,index=False)
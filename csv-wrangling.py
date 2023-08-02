import pandas as pd
import numpy as np
import re

def read_zählstellen(filename):
    """
    Returns a single dataframe from the traffic Zähstelle csvs, which have data in multiple tables 
    separated by irregular headings. See calling function below "import_export_multiple".
    """

    lst = []
    i=0
    
    with open(filename, newline='') as csvfile:
        while True:
            # Continue reading lines until empty str is returned, then print EOF and number of lines
            newline = csvfile.readline()
            i +=1 
            if not newline:
                print("EOF, line: ", i)
                break    
            
            #Split the newline into list of strings based on ',' delimiter
            newline = newline.rstrip('\n').replace('"',"").split(",")
            
            # a line starts with Zählstelle -> implies that a new table of 24hrs is starting
            if bool(re.match(r"Z.*?hlstelle",newline[0])):
                # Record the number of the zähstelle
                zählstelle = re.match(r"Z.*?hlstelle",newline[0]).string.split()[1]

                ### Some day/month strings are in the format 1.1, some are in the format 1,1. 
                # Use this try-except block to find day and month
                try:
                    [day,mon] = newline[2].replace(' ','').split(".")
                    year   = newline[3][:4]
                except:
                    [day,mon] = newline[2:4]
                    year   = newline[4][:4]

                #Pad the numbers with 0s after removing spaces   
                day = day.replace(" ","").zfill(2)
                mon = mon.replace(" ","").zfill(2) 

                ## Make datestring in format DD.MM.YYYY
                datestr = day + '.' +  mon + '.' + year

            # Collect entries from the table, which start either with format H:00 or HH:00
            if bool(re.match(r"\d{1,2}:00",newline[0])):
                lst.append([zählstelle] + [datestr] +  newline)

            


    ## Make into dataframe with appropriate columns
    df = pd.DataFrame(lst, columns = ['Zählstelle','Date','Time','PKW','LKW','Gesamt'])

    ## Replace times with irregular numbers of digits
    df.Time.where(df.Time != '24:00:00', '24:00', inplace=True)
    ## Convert end of time to middle of hour
    df.Time = df.Time.transform(lambda x: str(int(x.split(":")[0]) - 1).zfill(2) + ':30')
    df['datetime'] = pd.to_datetime(df.Date + ' ' + df.Time, format='%d.%m.%Y %H:%M')
    ## Add one day to midnight values
    # df.Datetime.where(df.Datetime.dt.hour != 0, df.Datetime + pd.DateOffset(days=1), inplace=True)
    df.drop(['Date','Time'],axis=1, inplace=True)
    df.set_index('datetime', inplace=True)


    return df

def import_export_multiple(list_cvs, outfile):
    ''' 
    Imports mutiple csvs using read_zähstellen function, concatenates and writes to a single csv.
    '''
    lst_dataframes = []
    for filename in list_cvs:
        print(f'Processing {filename}')
        df = read_zählstellen(filename)
        lst_dataframes.append(df)

    df = pd.concat(lst_dataframes)

    df.to_csv(outfile)


if __name__ == "__main__":
    list_files = ['./data/Anfrage_SWiesner_' + str(year) + '.csv' for year in range(2012,2023)]
    import_export_multiple(list_files, './data/compiled-zähstellen.csv')




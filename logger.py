import os
from datetime import datetime

def createLog():   #Check to see if a logfile exists (/LOGS/logfile.txt), if not create one, if so, append to it "New Run Date-Time"
  print("Creating Log File")
  if os.path.exists("LOGS/logfile.txt"):
    print("Log File Exists")
    with open("LOGS/logfile.txt", "a") as logfile:
      logfile.write(f"\nNew Run {datetime.now()}")
  else:
    print("Log File Does Not Exist")
    with open("LOGS/logfile.txt", "a") as logfile:
      logfile.write(f"\nNew Run {datetime.now()}")


def addLogEntry(entry): #Add an entry to the logfile
  print("Adding Log Entry")
  logFile = open("LOGS/logfile.txt", "a")
  logFile.write("\n"+entry)
  logFile.close()


def createIMEILog(IMEI): #Create a new log file for the specific IMEI being tested
    print("Creating IMEI Log")
    with open(f"LOGS/{IMEI}.txt", "a") as logfile:
        logfile.write(f"\nNew Run {datetime.now()}")
    return IMEI



#Add an entry to the IMEI log file in the following format
#addTestEntry({"IMEI": "123456789012345", "Test": "GREEN", "Result": "Fail"})
def addToIMEILog(IMEI, ResultDict): 
    print("Adding IMEI Log Entry")
    #Append to the IMEI log file
    with open(f"LOGS/{IMEI}.txt", "a") as logfile:
        try:
            logfile.write(f"\nIMEI: {ResultDict['IMEI']} Test: {ResultDict['Test']} Result: {ResultDict['Result']}")
        except:
            print("Error: Invalid ResultDict")
            logfile.write(f"\nError: Invalid ResultDict Given for Screen Test")






if __name__ == "__main__":
    pass

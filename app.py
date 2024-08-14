import streamlit as st
import pandas as pd
import numpy as np
import re
from skpy import Skype, SkypeGroupChat, SkypeUser
from skpy import SkypeTextMsg
import pytz
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Insphere Solutions Pvt. Ltd.", 
    page_icon=None, 
    layout="wide", 
    initial_sidebar_state="auto",
)

st.title("Insphere Solutions Pvt. Ltd")

# Create an empty container
placeholder = st.empty()

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

# Insert a form in the container
exportData = []
with st.form(key='login'):
    c1, c2, c3 = st.columns(3)
    with c1:
        email = st.text_input("Skype ID / Email", autocomplete="off")
        
    with c2:
        password = st.text_input("Password", type="password",autocomplete="off")
    with c3:
        date = st.date_input("Till Date(DD-MM-YYYY)", format="DD-MM-YYYY")
   
    with c1:
        ISPL_GROUP_ID = st.text_input("Skype Group ID")
    
    submit = st.form_submit_button("Generate Report")
    
    if submit:
        hasValid = True
        if email == "":
            hasValid = False
            st.error("Sorry, Your skype ID / email cannot be blank.")
            exit()
            
        if password == "":
            hasValid = False
            st.error("Sorry, Your password cannot be blank.")
            exit()
        
        if date is not None and  date != "":
            input_date_obj = datetime.strptime(str(date), "%Y-%m-%d")
            current_date_object = datetime.now()

            if input_date_obj > current_date_object:
                hasValid = False
                st.error("Currently we support current or previous dates only.")
                exit()

            previous_date = current_date_object - timedelta(days=15)
            previous_date = datetime.strptime(previous_date.strftime("%Y-%m-%d"), "%Y-%m-%d")

            if input_date_obj < previous_date:
                hasValid = False
                st.error("Currently we support previous 15 days only!.")
                exit()
                
        if ISPL_GROUP_ID == "":
            hasValid = False
            st.error("Sorry, Skype group ID cannot be blank.")
            exit()
                
        if hasValid:
            
            try:

                current_date_object = datetime.now()
                if input_date_obj is None or input_date_obj == "":
                    previous_date = current_date_object - timedelta(days=16)
                    from_date = datetime.strptime(previous_date.strftime("%Y-%m-%d"), '%Y-%m-%s')
                else:
                    previous_date = input_date_obj - timedelta(days=1)       
                    from_date = datetime.strptime(previous_date.strftime("%Y-%m-%d"), '%Y-%m-%d')
        
        
                current_date = current_date_object.strftime("%Y-%m-%d")
                
                
                messages_by_date = {}
                while previous_date.strftime("%Y-%m-%d") < current_date:
                    messages_by_date[current_date] = {}
                    
                    current_date_object += timedelta(days=-1)
                    current_date = current_date_object.strftime("%Y-%m-%d")
            
            
        
                sk = Skype(email, password)
                IST = pytz.timezone('Asia/Kolkata')
                
                # Get Group User Data
                groupMembers = sk.chats[ISPL_GROUP_ID]
                group_contacts = groupMembers.userIds

                userData = {}
                for contact in group_contacts:
                    contacts = sk.contacts[contact]
                    try:
                        userData[contacts.id] = contacts.name.first + " "+ contacts.name.last
                    except Exception as e:
                        pass

                # Get Group Chat Information
                group = sk.chats.chat(ISPL_GROUP_ID)
                
                data = {}
                looping = True
        
                while looping:

                    messages = group.getMsgs()

                    # Group messages by date
                    for message in messages:
                        
                        msg_time_utc = message.time.replace(tzinfo=pytz.utc)
                        msg_time_ist = msg_time_utc.astimezone(IST)
                        msg_date_ist = msg_time_ist.date()

                        loopDate = msg_date_ist.strftime("%d-%m-%Y")
                        if input_date_obj is None or input_date_obj == "":
                            
                            comparison_date = datetime.strptime(previous_date.strftime("%d-%m-%Y"), '%d-%m-%Y')
                            
                            target_date = datetime.strptime(loopDate, '%d-%m-%Y')
                            
                            if comparison_date > target_date:
                                looping = False
                                break
                        else:
                            previous_date = input_date_obj - timedelta(days=1)
                            
                            comparison_date = datetime.strptime(previous_date.strftime("%d-%m-%Y"), '%d-%m-%Y')
                            target_date = datetime.strptime(loopDate, '%d-%m-%Y')
                            
                            print("comparison_date-",  comparison_date.strftime('%d-%m-%Y'))
                            print("target_date-",  target_date.strftime('%d-%m-%Y'))
                            
                            if comparison_date > target_date:
                                looping = False
                                break
                            

                        if looping and loopDate not in messages_by_date:
                            messages_by_date[loopDate] = []
                            
                        if looping:
                            messages_by_date[loopDate].append(message)
                            
                for date, msgs in messages_by_date.items():

                    sorted_messages_items = sorted(msgs, key=lambda msg: msg.time)
                    for msg in sorted_messages_items:
                        
                        msg_time_utc1 = msg.time.replace(tzinfo=pytz.utc)
                        msg_time_ist1 = msg_time_utc1.astimezone(IST)
                        
                        # messageDate =  msg_time_ist1.strftime('%d-%m-%Y')
                        # if messageDate < 
                        

                        name = ""
                        if msg.userId in userData:
                            name = userData[msg.userId]

                        if date not in data:
                            data[date] = {}

                        if msg.userId not in data[date]:
                            data[date][msg.userId] = {
                                "userId": msg.userId,
                                "Name": name,
                                "Date": date,
                                "Time1": "",
                                "Time1_Message":  "",
                                "Time2": "",
                                "Time2_Message": "",
                                "Time3": "",
                                "Time3_Message": "",
                                "Time4": "",
                                "Time4_Message": "",
                            }


                        
                        
                        if data[date][msg.userId]['Time1'] == "":
                            data[date][msg.userId]['Time1'] = msg_time_ist1.strftime('%H:%M')
                            data[date][msg.userId]['Time1_Message'] = msg.content

                        elif data[date][msg.userId]['Time2'] == "":
                            time2 = msg_time_ist1.strftime('%H:%M')
                            if data[date][msg.userId]['Time1'] == time2:
                                continue
                            
                            data[date][msg.userId]['Time2'] = time2
                            data[date][msg.userId]['Time2_Message'] = msg.content

                        elif data[date][msg.userId]['Time3'] == "":
                            time3 = msg_time_ist1.strftime('%H:%M')
                            if data[date][msg.userId]['Time2'] == time3:
                                continue
                            data[date][msg.userId]['Time3'] = msg_time_ist1.strftime('%H:%M')
                            data[date][msg.userId]['Time3_Message'] = msg.content

                        elif data[date][msg.userId]['Time4'] == "":
                            
                            time4 = msg_time_ist1.strftime('%H:%M')
                            if data[date][msg.userId]['Time3'] == time4:
                                continue
                            data[date][msg.userId]['Time4'] = msg_time_ist1.strftime('%H:%M')
                            data[date][msg.userId]['Time4_Message'] = msg.content
                                
                            
                    
                    
                exportData = []
                for date, detailData in data.items():
                    for userId, details in detailData.items():
                            # Generate data for a new row
                        row = {
                            "userId": str(details['userId']),
                            "Name": str(details['Name']),
                            "Date": str(details['Date']),
                            "Time1": str(details['Time1']),
                            "Time1_Message": str(details['Time1_Message']),

                            "Time2": str(details['Time2']),
                            "Time2_Message": str(details['Time2_Message']),

                            "Time3": str(details['Time3']),
                            "Time3_Message": str(details['Time3_Message']),

                            "Time4": str(details['Time4']),
                            "Time4_Message": str(details['Time4_Message']),
                        }
                        
                        # Append the new row to the DataFrame
                        exportData.append(row)
                        
                df = pd.concat([pd.DataFrame([row]) for row in exportData], ignore_index=True)  
                st.table(df)   
                
                
            except Exception as e:
                print(e)
                st.error("Error!! "+ e.args[0])


# Create a two-column layout
if exportData is not None and len(exportData) > 0:
    df = pd.concat([pd.DataFrame([row]) for row in exportData], ignore_index=True)  
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download File",
        data=csv,
        file_name="skype_attendance_report.csv",
        mime="text/csv"
    )
 
    

       




                
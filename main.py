import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Step 1: Read Data from CSV
def read_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# Step 2: Send Initial Email
def send_email(to_email, subject, body):
    from_email = "your_email@example.com"
    password = "your_password"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def request_time_slots(p1_email, p2_email):
    subject = "Please choose your available 20-minute time slots"
    body = """
    Hi,

    Please choose your available 20-minute time slots in the next week using the following format:
    [Day of Week] [Time Range]

    Thank you!
    """
    send_email(p1_email, subject, body)
    send_email(p2_email, subject, body)

# Step 4: Find Common Time Slot
def find_common_slot(p1_slots, p2_slots):
    common_slots = set(p1_slots).intersection(p2_slots)
    if common_slots:
        return common_slots.pop()  # Get one common slot
    else:
        return None

# Step 5: Send Calendar Invite
def create_calendar_event(service, summary, description, start_time, end_time, attendees):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [{'email': attendee} for attendee in attendees],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# Main function
def main():
    csv_path = 'path_to_your_csv_file.csv'
    data = read_csv(csv_path)
    
    for index, row in data.iterrows():
        request_time_slots(row['P1email'], row['P2email'])
        # Assume responses are collected manually or via another script
        p1_slots = ["Monday 10:00-10:20", "Tuesday 11:00-11:20"]
        p2_slots = ["Monday 10:00-10:20", "Wednesday 12:00-12:20"]
        common_slot = find_common_slot(p1_slots, p2_slots)
        
        if common_slot:
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'
            
            credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('calendar', 'v3', credentials=credentials)
            
            start_time = "2023-06-20T10:00:00-07:00"  # Replace with the actual common slot start time
            end_time = "2023-06-20T10:20:00-07:00"  # Replace with the actual common slot end time
            attendees = [row['P1email'], row['P2email']]
            
            create_calendar_event(service, "Meeting", "Discussion on the topic", start_time, end_time, attendees)
        else:
            print(f"No common slots available for {row['P1name']} and {row['P2name']}")

if __name__ == "__main__":
    main()

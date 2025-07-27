from imapclient import IMAPClient  # Remove imaplib import since we're not using it

def process_new_emails():
    """Function to process new emails when they arrive"""
    print("Processing new emails...")
    # Your AI agent processing logic here
    
def monitor_with_idle():
    server = IMAPClient('imap.gmail.com', use_uid=True, ssl=True)
    server.login('user@gmail.com', 'password')  # Use app-specific password
    server.select_folder('INBOX/')
    
    # IDLE command - waits for new emails
    server.idle()
    print("Waiting for new emails...")
    
    while True:
        # This blocks until new email arrives
        responses = server.idle_check(timeout=30)
        
        if responses:
            print("New email detected!")
            # Process new emails here
            process_new_emails()
            
        server.idle_done()
        server.idle()  # Resume IDLE mode

# Run the monitor
if __name__ == "__main__":
    monitor_with_idle()
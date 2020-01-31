This is a project developed to browse a list of symbols, determine SMA50 and SMA200 crosses for each symbol then add respective crosses 
to Accrue API.
To add new symbols :
main.py : create_symbols()
To update new symbols : 
main.py : update_success_file(type='now')
To delete events : 
delete events/delete_events.py (will delete events_ids.csv ids)

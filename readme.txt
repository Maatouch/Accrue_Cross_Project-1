This is a project developed to browse a list of symbols, determine SMA50 and SMA200 crosses for each symbol then add respective crosses 
to Accrue API.
It can also update events every day at 4pm EST
To add new symbols :
main.py : update_symbols_from_file('symbols.csv', type='now', with_header=0)
To update new dates : 
main.py : update_symbols_from_file()
To delete events : 
main.py : delete_events_from_file()

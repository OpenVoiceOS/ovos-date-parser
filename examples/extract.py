"""Extract datetimes and durations from natural language."""
from datetime import datetime

from ovos_date_parser import extract_datetime, extract_duration

anchor = datetime(2023, 1, 15, 12, 0)  # a sunday

# absolute and relative dates
print(extract_datetime("lets meet next friday at 8am", "en", anchorDate=anchor))
print(extract_datetime("11 de agosto de 1998", "es", anchorDate=anchor))
print(extract_datetime("amanhã às 15h30", "pt", anchorDate=anchor))
print(extract_datetime("em 2 horas", "pt", anchorDate=anchor))

# no date -> None
print(extract_datetime("this has no date", "en", anchorDate=anchor))

# durations
print(extract_duration("set a timer for 5 minutes", "en"))
print(extract_duration("3 days 8 hours and 10 minutes", "en"))
print(extract_duration("nothing here", "en"))

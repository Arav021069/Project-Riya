from datetime import datetime


class TimeTool:
    """
    Returns the current local date, time, and day of the week.
    Use this tool whenever the user asks about the current date,
    current time, today, tomorrow, yesterday, or day of the week.
    """

    name = "time"

    def execute(self):
        now = datetime.now()
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M %p"),
            "day": now.strftime("%A")
        }


tool = TimeTool()

print(tool.execute())

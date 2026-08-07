from datetime import datetime


class TimeTool:

    name = "time"

    def execute(self):
        return datetime.now().strftime("%I:%M %p")


tool = TimeTool()

print(tool.execute())

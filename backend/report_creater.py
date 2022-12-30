from linebot.models import FlexSendMessage
import json


class ReportCreater:
    def __init__(self, call_type=0) -> None:
        self.call_type = call_type
        with open("backend/assets/report_template.json", 'r', encoding='utf-8') as f:
            self.report_template = json.load(f)

    def get_report(self) -> FlexSendMessage:
        report_dict = self.report_template.copy()
        return FlexSendMessage(alt_text="Rabbit's House Report", contents=report_dict)

from rest_framework import throttling

import datetime


class WorkingHoursRateThrottle(throttling.BaseThrottle):

    def allow_request(self, request, view):
        now = datetime.datetime.now().hour
        if 5 < now >= 3:
            return False
        return True

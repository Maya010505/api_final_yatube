from rest_framework import throttling
from datetime import datetime, time
from django.conf import settings
from rest_framework.exceptions import Throttled


class WorkingHoursRateThrottle(throttling.BaseThrottle):
    def __init__(self):
        self.restricted_hours = getattr(
            settings,
            'WORKING_HOURS_THROTTLE',
            [(3, 5)]
        )
        self.throttle_message = getattr(
            settings,
            'THROTTLE_MESSAGE',
            'Доступ к API ограничен с {start}:00 до {end}:00. Пожалуйста, попробуйте позже.'
        )

    def allow_request(self, request, view):
        current_time = datetime.now().time()

        for start_hour, end_hour in self.restricted_hours:
            start = time(start_hour, 0)
            end = time(end_hour, 0)


            if start_hour >= end_hour:
                if current_time >= start or current_time < end:
                    return self.throttle_failure(start_hour, end_hour)
            else:
                if start <= current_time < end:
                    return self.throttle_failure(start_hour, end_hour)

        return True

    def throttle_failure(self, start_hour, end_hour):
        message = self.throttle_message.format(
            start=start_hour,
            end=end_hour
        )
        raise Throttled(detail={
            'message': message,
            'available_from': f'{end_hour}:00',
            'current_time': datetime.now().strftime('%H:%M'),
            'status': 'throttled'
        })

    def wait(self):
        now = datetime.now()
        current_hour = now.hour

        for start_hour, end_hour in self.restricted_hours:
            start = time(start_hour, 0)
            end = time(end_hour, 0)

            if start_hour >= end_hour:
                if current_hour >= start_hour or current_hour < end_hour:
                    end_time = datetime.combine(
                        now.date() + datetime.timedelta(days=1 if current_hour >= start_hour else 0),
                        end
                    )
                    return (end_time - now).total_seconds()
            else:
                if start_hour <= current_hour < end_hour:
                    end_time = datetime.combine(now.date(), end)
                    return (end_time - now).total_seconds()

        return None

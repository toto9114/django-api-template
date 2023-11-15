from timeit import default_timer as timer


def time_measure(app_name: str):
    def time_measure_decorator(cls):
        class TimeMeasure(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.time_measure: dict = dict()

            def __getattribute__(self, name):
                attribute = super().__getattribute__(name)

                if callable(attribute):

                    def timed_method(*args, **kwargs):
                        start_time = timer()
                        result = attribute(*args, **kwargs)
                        end_time = timer()

                        self.time_measure[f"{app_name}.{name}"] = end_time - start_time

                        return result

                    return timed_method

                return attribute

        return TimeMeasure

    return time_measure_decorator
